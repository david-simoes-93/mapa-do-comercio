import threading
import json

from model import *

COMPANY_PAGES: dict[str, CompanyPage] = {}
VISITED_SOURCES: set[CompanySource] = set()

FILE_LOCK = threading.Lock()
def add_companies(companies: list[CompanyPage]):
    """Write COMPANY_PAGES into einforma.txt. Thread-safe."""
    with FILE_LOCK:
        prev_size = len(COMPANY_PAGES)
        for company in companies:
            COMPANY_PAGES[company.url]=company

        new_unique_comps = len(COMPANY_PAGES)-prev_size
        print(f"Adding {len(companies)} companies ({new_unique_comps} new unique ones), for a total of {len(COMPANY_PAGES)}")

        with open("db/einforma.txt", 'w', encoding='utf-8') as file:
            for comp in COMPANY_PAGES.values():
                file.write(comp.model_dump_json()+"\n")


def load():
    """Load einforma.txt into COMPANY_PAGES and VISITED_SOURCES."""
    with open("db/einforma.txt", 'r', encoding='utf-8') as file:
        for line in file.readlines():
            company = CompanyPage.model_validate_json(line)
            COMPANY_PAGES[company.url] = company
            VISITED_SOURCES.add(company.src)
    print(f"Loaded a total of {len(COMPANY_PAGES)} from .txt ({len(VISITED_SOURCES)} different sources)")


def save_coords_json():
    """Saves all companies with coordinates onto markers.json."""
    companies_with_coords = [FrontEndObj(lat=c.coords.lat, lng=c.coords.lon, popup=c.details.name).model_dump() for c in COMPANY_PAGES.values() if c.coords is not None]

    with open("db/markers.json", "w") as f:
        json.dump(companies_with_coords, f, indent=4)
