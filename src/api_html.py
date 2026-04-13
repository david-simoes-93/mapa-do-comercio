import requests
import threading
import html
import os

from model import *
from api_local import *

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0'
}

def fetch_html(url: str):
    """Grabs the HTML page off a given url."""
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error fetching the URL: {e}"


def fetch_coords_from_mapbox(address: str) -> Coordinates|None:
    """Uses MapBox to convert an address into GPS coordinates.
    
    Uses the MAPBOX_TOKEN environment variable.
    NOTE: MapBox doesn't seem super accurate.
    """
    mapbox_token=os.environ.get('MAPBOX_TOKEN')
    mapbox_url=f"https://api.mapbox.com/geocoding/v5/mapbox.places/{address}.json?access_token={mapbox_token}"

    response = requests.get(mapbox_url, headers=HEADERS)
    data = response.json()

    if data:
        return Coordinates(lat= float(data["features"][0]["center"][1]), lon=float(data["features"][0]["center"][0]))
    else:
        print("Address not found.")
    return None


def fetch_from_einforma(base_url: str, child_url_prefix: str | None, skip_fetch:bool=False):
    """Grab a list of company pages from a given list in eInforma.
    
    eInforma provides lists of companies by districts, categories, etc.
    """
    page_no = 1
    company_set = set()
    while True:
        url = base_url.replace(".html", f"/Empresas-{page_no}.html")

        html_code = fetch_html(url)
        if "foram encontrados resultados para a sua pesquisa" in html_code or skip_fetch:
            break
        
        company_links = [html_snippet for html_snippet in html_code.split("\"") if "/Ficha_" in html_snippet]
        for company_link in company_links:
            company_set.add("https://empresas.einforma.pt"+company_link)

        page_no += 1
        if page_no % 10 == 0:
            print(".", end="", flush=True)
        # break

    child_urls = [html_snippet for html_snippet in html_code.split("\"") if child_url_prefix and child_url_prefix in html_snippet]
    print()
    print(f"{base_url} ({len(company_set)})")
    return company_set, child_urls


def visited_source(base_url:str, district_url:str|None=None, concelho:str|None=None, freguesia:str|None=None):
    return CompanySource(base=base_url, distrito=district_url, concelho=concelho, freguesia=freguesia) in VISITED_SOURCES


def fetch_district_company_pages(base_url: str, district:str):
    """Grab a list of company pages from a given district in eInforma.
    
    Runs multiple threads, one for each District.
    """
    district_url = "https://empresas.einforma.pt"+district
    companies_district, concelhos = fetch_from_einforma(district_url, "/Concelho_", skip_fetch=visited_source(base_url, district_url))
    add_companies([CompanyPage(url=c, src=CompanySource(base=base_url, distrito=district_url)) for c in companies_district])


def fetch_company_pages():
    """Grab a list of company pages from eInforma.
    
    Runs multiple threads, one for each District.
    """
    base_url = "https://empresas.einforma.pt.html"
    _, districts = fetch_from_einforma(base_url, "/Distrito_", skip_fetch=True)

    # get each distrito in a thread    
    threads = []
    for district in districts:
        thread = threading.Thread(target=fetch_district_company_pages, args=(base_url,district))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()


def fetch_company_batch_details(companies: list[CompanyPage]):
    """Grab details for each company in given list, and updates them.
    
    Saves progress in batches.
    """
    BATCH_SIZE = 1000
    updated_companies: list[CompanyPage] = []
    for company in companies:
        if company.details is not None:
            continue
        
        html_code = [html_code for html_code in fetch_html(company.url).split("\n") if "NIF de" in html_code]
        if not html_code:
            print(f"Company {company.url} not found")
            continue
        else:
            html_code=html_code[0]
        
        name: str|None = None
        activity: str|None = None
        address: str|None = None
        postalcode: str|None = None
        locality: str |None = None
        telephone: str|None = None
        email: str|None = None
        site: str|None = None

        html_fields = html_code.split("\"")
        for i in range(len(html_fields)):
            if html_fields[i] == "fn localbusiness":
                name = (html.unescape(html_fields[i+2]))
            if html_fields[i] == "category":
                activity = (html.unescape(html_fields[i+1]))
            if html_fields[i] == "street-address":
                address = (html.unescape(html_fields[i+2]))
            if html_fields[i] == "postal-code":
                postalcode = (html_fields[i+2])
            if html_fields[i] == "locality":
                locality = (html_fields[i+2])
            if html_fields[i] == ">Telefone:</td><td><a href=":
                telephone = (html_fields[i+5])
            if html_fields[i] == ">Email:</td><td><a href=":
                email = (html_fields[i+5])
            if html_fields[i] == "website":
                site = (html_fields[i+4])
        
        if not name or not activity or not address or not postalcode or not locality or not telephone or not email:
            continue

        details=CompanyDetails(name=name, activity=activity, address=address, postalcode=postalcode, locality=locality, telephone=telephone, email=email, site=site)
        updated_companies.append(CompanyPage(url=company.url, src=company.src, details=details, coords=company.coords))

        if len(updated_companies)%10 == 0:
            print(".", end="", flush=True)

        if len(updated_companies)%BATCH_SIZE == 0:
            add_companies(updated_companies)
            updated_companies = []
            #break #
    add_companies(updated_companies)


def fetch_company_details():
    """Grab details for each company in COMPANY_PAGES, and updates them.
    
    Runs multiple threads.
    """

    thread_count = 5
    batch_size = int(len(COMPANY_PAGES)/thread_count)

    companies = list(COMPANY_PAGES.values())

    # 20 threads, each collecting details on its share    
    threads = []
    for i in range(thread_count):
        thread = threading.Thread(target=fetch_company_batch_details, args=(companies[i*batch_size:(i+1)*batch_size],))
        threads.append(thread)
        thread.start()
    fetch_company_batch_details(companies[thread_count*batch_size:])
    
    for thread in threads:
        thread.join()


def fetch_company_coords():
    """Grab coords for each company in COMPANY_PAGES, and updates them.
    
    Saves progress in batches.
    """
    BATCH_SIZE = 1000

    updated_companies: list[CompanyPage] = []
    for company in COMPANY_PAGES.values():
        # NOTE: for PoC, only doing CACIA companies
        if company.coords is not None or company.details is None or "CACIA" not in company.details.address:
            continue
        
        coords = fetch_coords_from_mapbox(company.details.address)
        if coords is None:
            continue
        
        updated_companies.append(CompanyPage(url=company.url, src=company.src, details=company.details, coords=coords))

        if len(updated_companies)%10 == 0:
            print(".", end="", flush=True)

        if len(updated_companies)%BATCH_SIZE == 0:
            add_companies(updated_companies)
            updated_companies = []
            #break #
    add_companies(updated_companies)
