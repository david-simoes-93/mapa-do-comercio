from collections import defaultdict

from model import *
from api_local import *
from api_html import *


def run_stats():
    companies: dict[str, CompanySource] = {}
    with open("db/einforma.txt", 'r', encoding='utf-8') as file:
        for line in file.readlines():
            company = CompanyPage.model_validate_json(line)
            companies[company.url] = company.src
    print(f"run_stats on a total of {len(companies)} from .txt")

    companies_per_district: dict[str, int] = defaultdict(lambda: 0)
    for src in companies.values():
        companies_per_district[src.distrito] += 1
    for distrito, qty in companies_per_district.items():
        print(f" - Found {qty} companies for {distrito}")

    companies_without_details = len([c for c in COMPANY_PAGES.values() if c.details is None])
    print(f"Missing {companies_without_details} details!")

    companies_without_coords = len([c for c in COMPANY_PAGES.values() if c.coords is None])
    print(f"Missing {companies_without_coords} coordinates!")

# Load data
load()
run_stats()

# Fetch 600k company pages from eInforma
# NOTE: already collected
# fetch_company_pages()

# Fetch details for each company page from eInforma
# NOTE: already collected for 260k companies
# fetch_company_details()

# Fetch (and save) coords for each company with details
# NOTE: only doing CACIA companies
fetch_company_coords()
save_coords_json()


