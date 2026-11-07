# Downloads the CSV files (2023 onwards) from the Telangana Open Data Portal into data/raw/
# Run:  python download_data.py     (files that already exist are skipped)

import json
import os
import re
import urllib.parse
import urllib.request

PORTAL = "https://data.telangana.gov.in"
FIRST_YEAR = 2023

# folder name -> text used to search the dataset on the portal
DATASETS = {
    "transactions": "fp-shop-wise-transactions-data",
    "card_status": "fair-price-shop-card-status",
    "locations": "fair-price-shop-status-latitude",
}


def read_url(url):
    url = urllib.parse.quote(url, safe=":/%?=&")
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(request, timeout=120).read()


for folder, search_text in DATASETS.items():
    os.makedirs("data/raw/" + folder, exist_ok=True)
    result = json.loads(read_url(PORTAL + "/api/1/search?fulltext=" + search_text + "&page-size=5"))["results"]
    files = list(result.values())[0]["distribution"]          # the first result is the dataset we want

    for item in files:
        url = item["downloadURL"]
        years = re.findall(r"(20\d\d)", item["title"] + " " + url)
        if folder != "locations" and (not years or int(years[-1]) < FIRST_YEAR):
            continue                                            # skip the years before 2023
        path = "data/raw/" + folder + "/" + os.path.basename(urllib.parse.unquote(url))
        if os.path.exists(path):
            print("already there:", path)
            continue
        with open(path, "wb") as f:
            f.write(read_url(url))
        print("saved:", path)
