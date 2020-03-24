import requests

from fastapi import FastAPI
from starlette.responses import RedirectResponse

app = FastAPI(
    title="Algeria COVID19 API",
    description="A simple RESTful API to get stats about COVID19 spread in Algeria (confirmed, recovered and deaths)",
    version="0.0.4",
)


@app.get("/", include_in_schema=False)
def read_root():
    response = RedirectResponse(url="/docs")
    return response


@app.get("/stats")
def read_stats():
    """
    Get stats
    """
    url = "https://api.coronatracker.com/v2/analytics/country"
    r = requests.get(url=url)
    data = r.json()
    return list(filter(lambda element: element["countryName"] == "Algeria", data))[0]


@app.get("/history")
def read_history():
    url = "https://corona.lmao.ninja/historical/Algeria"
    r = requests.get(url=url)
    return r.json()["timeline"]



@app.get("/wilayas")
def read_history():
    """
       Get stats per wilaya
    """
    url = "https://services9.arcgis.com/jaH8KnBq5el3w2ZR/arcgis/rest/services/COVID_wilaya/FeatureServer/0/" \
          "query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*" \
          "&orderByFields=Report%20asc&resultOffset=0&resultRecordCount=1000&cacheHint=true "
    r = requests.get(url=url)
    data = list()
    raw_data = list(r.json()["features"])

    for wilaya in raw_data:
        if(wilaya['attributes']['NOM_WILAYA']):
            data.append({
                'name' : wilaya['attributes']['NOM_WILAYA'],
                'code' : wilaya['attributes']['WILAYA'],
                'deaths' : wilaya['attributes']['Décés'],
                'recovered' : wilaya['attributes']['Récupéré'],
                'confirmed' : wilaya['attributes']['confirmé'],
                'Female': wilaya['attributes']['Femelle'],
                'Male': wilaya['attributes']['Male']
            })
    return data

