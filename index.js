const {StringStream} = require("scramjet");

const {country, hostname, port} = require('./config.json');

var express = require('express');

var app = express();

var myRouter = express.Router();


myRouter.route('/stats').get(function (req, res) {
    let types = ['Confirmed', 'Deaths', 'Recovered'];
    let data = {};

    function getData(type) {
        console.log(type)
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
                return res.json(data);
            })
        }
    }

    function getAllData() {
        return getData(0);
    }

    getAllData();
})

app.use(myRouter);
app.listen(port, hostname, function () {
    console.log("http://" + hostname + ":" + port);
});