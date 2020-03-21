const {StringStream} = require("scramjet");

const {country, hostname, port} = require('./config.json');

var express = require('express');

var app = express();

var myRouter = express.Router();


myRouter.route('/history').get(function (req, res) {
    let types = ['Confirmed', 'Deaths', 'Recovered'];
    let data = {};

    function getData(type) {
        const request = require("request");
        var prom = request.get("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-" + types[type] + ".csv")   // fetch csv
            .pipe(new StringStream())
            .CSVParse({
                delimiter: ",",
                header: true,
            })
            .consume(object => {

                if (object['Country/Region'] == country) {
                    data[types[type]] = object;
                }
            });
        if (type < 3) {
            return prom.then(() => {
                return getData(type + 1);
            })
        } else {
            return prom.then(() => {
                res.setHeader("Content-Type", "application/json");
                return res.json(data);
            })
        }
    }

    function getAllData() {
        return getData(0);
    }
    getAllData();
})



myRouter.route('/stats').get(function (req, res) {
    const request = require("request");
        let url = "https://api.coronatracker.com/v2/analytics/country";
        request(url, function (error, response, body) {
            var response = JSON.parse( body ).find(element => element.countryCode == "DZ")
            res.setHeader("Content-Type", "application/json");
            res.json(response);
        });
})

app.use(myRouter);
app.listen(port, hostname, function () {
    console.log("http://" + hostname + ":" + port);
});