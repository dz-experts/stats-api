from fastapi import FastAPI
import requests

app = FastAPI()


@app.get("/")
def read_root():
    from starlette.responses import RedirectResponse
    response = RedirectResponse(url='/docs')
    return response


@app.get("/stats")
def read_stats():
    url = "https://api.coronatracker.com/v2/analytics/country"
    r = requests.get(url=url)
    data = r.json()
    return list(filter(lambda element: element["countryName"] == "Algeria", data))[0]


@app.get("/history")
def read_history():
    url = "https://corona.lmao.ninja/historical/Algeria"
    r = requests.get(url=url)
    return r.json()['timeline']
