# Mapa do Comércio

This repo had a somewhat simple goal:
- map all the commercial buildings in Portugal by category and put them in a map

The goal was to allow categorical filtering over an area, so you could search for businesses of some type (e.g., carpentries) near you.
Each pin would then link to the company's website, so you could make an informed decision.

## Sources and Technologies

For a PoC, we used [Leafjet](https://leafletjs.com/index.html) to display the map and pins.

Company data was crawled from [eInforma](https://empresas.einforma.pt/).
[Empresite](https://empresite.jornaldenegocios.pt/) had too many bot protection services, and [Google](https://developers.google.com/maps/documentation/places/web-service/nearby-search) quickly ran into free-tier limits.
We also considered using official Government Notary data-bases, but found none for public use.

Addresses were converted into latitude/longitude coordinates with [MapBox](https://docs.mapbox.com/api/search/geocoding/#geocoding-api-pricing).

## Problems

We got to the conclusion that this is actually an impossible problem to solve.

From a computer engineering perspective, it has its set of challenges, but those can be worked around.
You define your sources of truth, you build your database of companies/locations/coordinates, you show them in a map (possibly clustering, filtering, etc to account for the hundreds of thousands of companies).

The issue is more fundamental though: how do you know what company is in what building?
- A database of commercial companies shows their headquarters, not their locations
- A company/person can rent a building to another company
- Not all companies have websites with accurate up-to-date addresses, and websites for dead companies remain for a long time

So in the end, even if we solved all the other problems, we found it was never going to be that accurate.
We'd have to rely on crowd-driven APIs (like Google Maps), which again, not that reliable, and that was unmotivating enough that we abandoned the project.

## Instructions

Extract `db/einforma.zip`, and then setup with

    python3 -m venv venv
    source venv/bin/activate.sh
    pip install -r reqs.txt

To run this, simply

    export MAPBOX_TOKEN=<insert your API token here>
    python3 src/main.py

When satisfied, open `web/index.html` to see the current map.

If you see CORS errors, you might need to change your browser permissions to load the json.
On Firefox, 

    about:config -> security.fileuri.strict_origin_policy -> False