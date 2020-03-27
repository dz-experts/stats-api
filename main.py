import requests

from fastapi import FastAPI
from starlette.responses import RedirectResponse
import dateutil.parser
import datetime


app = FastAPI(
    title="Algeria COVID19 API",
    description="A simple RESTful API to get stats about COVID19 spread in Algeria (confirmed, recovered and deaths)",
    version="0.0.9",
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
    url = "https://services8.arcgis.com/yhz7DEAMzdabE4ro/arcgis/rest/services/DZ_COVID/FeatureServer/2/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=Report%20asc&outSR=102100&resultOffset=0&resultRecordCount=1000&cacheHint=true"
    r = requests.get(url=url)
    data = r.json()
    confirmed = max(filter(None, (item["attributes"]["Cumul"] for item in data["features"])))
    wilayas = read_wilayas()
    deaths = recovered = male = female = 0
    for item in wilayas:
        deaths += item['deaths']
        recovered += item['recovered']
        male += item['sex']['male'] if item['sex']['male'] else 0
        female += item['sex']['female'] if item['sex']['female'] else 0
    creation_date_in_seconds = round(data["features"][-1]["attributes"]["CreationDate"]/1000)

    return {
        'countryCode': 'DZ',
        'countryName': 'Algeria',
        'confirmed': confirmed,
        'recovered': recovered,
        'deaths': deaths,
        'gender': {
            'male': male,
            'female': female
        },
        'dateAsOf': datetime.datetime.fromtimestamp(creation_date_in_seconds).isoformat()
    }


@app.get("/history")
def read_history():
    url = "https://corona.lmao.ninja/v2/historical/Algeria"
    r = requests.get(url=url)
    return r.json()["timeline"]


@app.get("/v2/history")
def read_history_v2():
    """
        Get timeline
    """
    url = "https://pomber.github.io/covid19/timeseries.json"
    r = requests.get(url=url)
    timeline = list(r.json()["Algeria"])

    url_last = "https://api.coronatracker.com/v2/analytics/country"
    r_last = requests.get(url=url_last)
    last_data = list(filter(lambda element: element["countryName"] == "Algeria", r_last.json()))[0]
    date = dateutil.parser.isoparse(last_data['dateAsOf'])
    timeline.append({
        "date": date.strftime('%Y-%m-%d'),
        "confirmed": last_data['confirmed'],
        "deaths": last_data['deaths'],
        "recovered": last_data['recovered']
    })
    return timeline


@app.get("/wilayas")
def read_wilayas():
    """
       Get stats per wilaya
    """
    url = "https://services8.arcgis.com/yhz7DEAMzdabE4ro/ArcGIS/rest/services/Cas_confirme_wilaya/FeatureServer/0" \
          "/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*" \
          "&orderByFields=WILAYA%20ASC&outSR=102100"
    r = requests.get(url=url)
    data = dict()
    raw_data = list(r.json()["features"])
    for wilaya in raw_data:
        if wilaya['attributes']['NOM_WILAYA']:
            data[wilaya['attributes']['WILAYA']] = {
                'name': wilaya['attributes']['NOM_WILAYA'],
                'name_ar': wilaya['attributes']['wilayat'],
                'code': wilaya['attributes']['WILAYA'],
                'deaths': wilaya['attributes']['Décés'],
                'actives': wilaya['attributes']['active'],
                'recovered': wilaya['attributes']['Récupér'],
                'confirmed': wilaya['attributes']['Cas_confirm'],
                'suspects': wilaya['attributes']['Cas_suspects'],
                'sex': {
                    'female': wilaya['attributes']['Femelle'],
                    'male': wilaya['attributes']['Males']
                },
                'origin': {
                    'local': wilaya['attributes']['Local'],
                    'imported': wilaya['attributes']['Imported']
                },
                'ages': {
                    '-5': wilaya['attributes']['A1_25'],
                    '5-14': wilaya['attributes']['a25_34'],
                    '15-24': wilaya['attributes']['a35_44'],
                    '25-34': wilaya['attributes']['a45_59'],
                    '35-44': wilaya['attributes']['A_60'],
                    '45-59': wilaya['attributes']['cinqantneuf'],
                    '60-70': wilaya['attributes']['soixantedix'],
                    '+70': wilaya['attributes']['plus']
                }
            }
    return [data[x] for x in sorted(data)]


@app.get("/ages")
def read_ages():
    """
       Get stats per age
    """
    wilayas = read_wilayas()
    data = {
                    '-5': sum(item['ages']['-5'] if item['ages']['-5'] else 0 for item in wilayas),
                    '5-14': sum(item['ages']['5-14'] if item['ages']['5-14'] else 0 for item in wilayas),
                    '15-24': sum(item['ages']['15-24'] if item['ages']['15-24'] else 0 for item in wilayas),
                    '25-34': sum(item['ages']['25-34'] if item['ages']['25-34'] else 0 for item in wilayas) ,
                    '35-44': sum(item['ages']['35-44'] if item['ages']['35-44'] else 0 for item in wilayas),
                    '45-59':sum(item['ages']['45-59'] if item['ages']['45-59'] else 0 for item in wilayas),
                    '60-70': sum(item['ages']['60-70'] if item['ages']['60-70'] else 0 for item in wilayas),
                    '+70': sum(item['ages']['+70'] if item['ages']['+70'] else 0 for item in wilayas)
                }
    return data


@app.get("/sex")
def read_sex():
    """
       Get stats per sex
    """
    wilayas = read_wilayas()
    data = {
        'male': sum(item['sex']['male'] if item['sex']['male'] else 0 for item in wilayas),
        'female': sum(item['sex']['female'] if item['sex']['female'] else 0 for item in wilayas),
    }
    return data


@app.get("/origins")
def read_origins():
    """
       Get stats per origin
    """
    wilayas = read_wilayas()
    data = {
        'local': sum(item['origin']['local'] if item['origin']['local'] else 0 for item in wilayas),
        'imported': sum(item['origin']['imported'] if item['origin']['imported'] else 0 for item in wilayas),
    }
    return data

