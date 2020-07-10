
# Data processing backend for the FIT5120 Capstone Project

This is the back-end program for of our project titled: Reducing Transport Injuries - Fighting Fatigue

It is developed using the Flask web framework.

View the product video for this project: 

[![product video](https://img.youtube.com/vi/9ksR8vJijpg/3.jpg)](https://www.youtube.com/watch?v=9ksR8vJijpg "Fighting Fatigue")

https://www.youtube.com/watch?v=9ksR8vJijpg

## Features

  - Implementation of the Psychomotor Vigilance Test (PVT) for measuring
    fatigue
  - Alternative route discovery. Routes are tagged as Safest, Fastest,
    and Shortest

## System Overview

![Application Architecture](Data%20Plan.png)

## Usage

→ Prepare the application

``` r
$ git clone https://github.com/cigarplug/fit5120.git
$ cd fit5120
```

→ Create your heroku application

``` r
$ heroku create <your-app-name>
```

→ Declare environment variables

The vars are stored in the .env file in your app directory

``` r
user : database username
password : database password
host : link to the database host
gcp_key : client key of your Google Maps Directions API project
mapbox_tile : url and access key from your MapBox account
```

→ Run the application on local machine

``` r
$ heroku local
```

→ To deploy the application, (in your app directory) run:

``` r
$ git push heroku master
```

→ The application is now deployed. Ensure that at least one instance of the app is running:

``` r
$ heroku ps:scale web=1
```

## API Docs

<div class="kable-table">

| Type       | Location          | Description                         | Return Type |
| :--------- | :---------------- | :---------------------------------- | :---------- |
| HTTPS POST | /map              | HTML map: route + accident clusters | html        |
| HTTPS POST | pvt\_data/summary | Fatigue: star rating + description  | json        |
| HTTPS POST | pvt\_data/chart   | Visualization of PVT response times | image/png   |

</div>

For the /map endpoint, the request data is in json format with the
following structure:

``` 
{
    "origin": {
        "qry_type": "txt",
        "query": "Melbourne"
    },
    "dest": {
        "qry_type": "latLon",
        "query": {
            "lat": "-37.8847163",
            "lon": "145.0695384",
            "address": "Chadstone SC"
        }
    },
    "tags": "safest"
}
 
```

For the fatigue test result endpoint i.e, /pvt\_data the request json
data structure is:

``` r
{
  "reaction_times": [0.67, 1.23, 1.07, 1.22, 1.11, 0.7, 1.43],
  "test_times": [5, 10, 8, 8, 6, 9, 5],
  "false_clicks": 3
}
```
