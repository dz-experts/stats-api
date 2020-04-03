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
    url = "https://services8.arcgis.com/yhz7DEAMzdabE4ro/arcgis/rest/services/COVID_Death_Cumul/FeatureServer/2/query?f=json&" \
	"where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=Report%20asc&" \
	"outSR=102100&resultOffset=0&resultRecordCount=1000&cacheHint=false"
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
    creation_date_in_seconds = round(data["features"][-1]["attributes"]["Report"]/1000)

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
    url = "https://services8.arcgis.com/yhz7DEAMzdabE4ro/ArcGIS/rest/services/Cas_confirme_view/FeatureServer/0" \
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
                'new_cases': wilaya['attributes']['new_cases'],
                'sex': {
                    'female': wilaya['attributes']['Femelle'],
                    'male': wilaya['attributes']['Males']
                },
                'origin': {
                    'local': 0,
                    'imported': 0,
                    'note': 'deprecated'
                },
                'ages': {
                    '-1': wilaya['attributes']['A1_25'],
                    '1-14': wilaya['attributes']['a25_34'],
                    '15-24': wilaya['attributes']['a35_44'],
                    '25-49': wilaya['attributes']['a45_59'],
                    '50-59': wilaya['attributes']['A_60'],
                    '+60': wilaya['attributes']['cinqantneuf']
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
                    '-1': sum(item['ages']['-1'] if item['ages']['-1'] else 0 for item in wilayas),
                    '1-14': sum(item['ages']['1-14'] if item['ages']['1-14'] else 0 for item in wilayas),
                    '15-24': sum(item['ages']['15-24'] if item['ages']['15-24'] else 0 for item in wilayas),
                    '25-49': sum(item['ages']['25-49'] if item['ages']['25-49'] else 0 for item in wilayas) ,
                    '50-59': sum(item['ages']['50-59'] if item['ages']['50-59'] else 0 for item in wilayas),
                    '+60': sum(item['ages']['+60'] if item['ages']['+60'] else 0 for item in wilayas)
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
        'note': 'deprecated'
    }
    return data

