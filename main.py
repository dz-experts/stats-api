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
