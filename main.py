import requests

from fastapi import FastAPI
from starlette.responses import RedirectResponse

app = FastAPI(
    title="Algeria COVID19 API",
    description="A simple RESTful API to get stats about COVID19 spread in Algeria (confirmed, recovered and deaths)",
    version="0.0.5",
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
    import dateutil.parser
    date = dateutil.parser.isoparse(last_data['dateAsOf'])
    timeline.append({
        "date": date.strftime('%Y-%m-%d'),
        "confirmed": last_data['confirmed'],
        "deaths": last_data['deaths'],
        "recovered": last_data['recovered']
    })
    return timeline


@app.get("/wilayas")
def read_history():
    """
       Get stats per wilaya
    """
    url = "https://services9.arcgis.com/jaH8KnBq5el3w2ZR/arcgis/rest/services/Merge_Cas_confirm%C3%A9s_Alger_wilaya/FeatureServer/0/query?" \
          "f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects" \
          "&inSR=102100&outFields=*&outSR=102100&resultType=tile"
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
                'active': wilaya['attributes']['active'],
                'recovered': wilaya['attributes']['Récupér'],
                'confirmed': wilaya['attributes']['Cas_confirm'],
                'Female': wilaya['attributes']['Femelle'],
                'Male': wilaya['attributes']['Males']
            }
    return [data[x] for x in sorted(data)]


@app.get("/ages")
def read_ages():
    """
       Get stats per age
    """
    url = "https://services9.arcgis.com/jaH8KnBq5el3w2ZR/arcgis/rest/services/Merge_Cas_confirm%C3%A9s_Alger_wilaya" \
          "/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects" \
          "&outFields=*&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22A1_25%22%2C" \
          "%22outStatisticFieldName%22%3A%22A1_25%22%7D%2C%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22" \
          "%3A%22a25_34%22%2C%22outStatisticFieldName%22%3A%22a25_34%22%7D%2C%7B%22statisticType%22%3A%22sum%22%2C" \
          "%22onStatisticField%22%3A%22a35_44%22%2C%22outStatisticFieldName%22%3A%22a35_44%22%7D%2C%7B" \
          "%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22a45_59%22%2C%22outStatisticFieldName%22%3A" \
          "%22a45_59%22%7D%2C%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22A_60%22%2C" \
          "%22outStatisticFieldName%22%3A%22A_60%22%7D%2C%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22" \
          "%3A%22cinqantneuf%22%2C%22outStatisticFieldName%22%3A%22cinqantneuf%22%7D%2C%7B%22statisticType%22%3A" \
          "%22sum%22%2C%22onStatisticField%22%3A%22soixantedix%22%2C%22outStatisticFieldName%22%3A%22soixantedix%22" \
          "%7D%2C%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22plus%22%2C%22outStatisticFieldName" \
          "%22%3A%22plus%22%7D%5D&outSR=102100"
    r = requests.get(url=url)
    data = dict()
    raw_data = r.json()["features"][0]
    data["1-24"] = raw_data['attributes']["A1_25"]
    data["25-34"] = raw_data['attributes']["a25_34"]
    data["35-44"] = raw_data['attributes']["a35_44"]
    data["45-59"] = raw_data['attributes']["cinqantneuf"]
    data["60-70"] = raw_data['attributes']["soixantedix"]
    data["70"] = raw_data['attributes']["plus"]
    return data


@app.get("/sex")
def read_ages():
    """
       Get stats per sex
    """
    url = "https://services9.arcgis.com/jaH8KnBq5el3w2ZR/arcgis/rest/services/Merge_Cas_confirm%C3%A9s_Alger_wilaya" \
          "/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects" \
          "&outFields=*&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22Femelle%22" \
          "%2C%22outStatisticFieldName%22%3A%22Femelle%22%7D%2C%7B%22statisticType%22%3A%22sum%22%2C" \
          "%22onStatisticField%22%3A%22Males%22%2C%22outStatisticFieldName%22%3A%22Males%22%7D%5D&cacheHint=true "
    r = requests.get(url=url)
    data = dict()
    raw_data = r.json()["features"][0]
    data["Female"] = raw_data['attributes']["Femelle"]
    data["Male"] = raw_data['attributes']["Males"]
    return data

