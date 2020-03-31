![Build and deploy Docker Image CI](https://github.com/dz-experts/stats-api/workflows/Build%20and%20deploy%20Docker%20Image%20CI/badge.svg)

# covid19-simple-api
A simple api to return Confirmed, Deaths and Recovered history for a country

The data are from [Ministère de la Santé - Algérie](http://http://covid19.sante.gov.dz)

To run the web application in debug use:
```
uvicorn main:app --reload
```


## Endpoints

check [docs](https://stats-api.covid19dz.com/docs)

## Web routes

All routes are available on [docs](https://stats-api.covid19dz.com/docs) or [redoc](https://stats-api.covid19dz.com/redoc) paths with Swagger or ReDoc.


## Deployment with Docker

You must have ``docker`` and ``docker-compose`` tools.
Then just run:

```
docker-compose up -d 
```

Application will be available on ``localhost`` in your browser.
