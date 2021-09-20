# SweepSouth 👋

This is a covid-19 dashboard. You enter the name of the country of your choosing in the search bar, press the
submit button and it will display the daily death case of that country and the cummulative recoveries below.

I used a media group api for this, the base for the api is 

```sh
"https://covid-api.mmediagroup.fr/v1"
 ```
## Some architectural choices:

* I used the Dash framework for this, because its the easiest way to produce dynamic, plots with python.

* The db of choice was sqlite3, this allows for data persistence which will help in minimizing API call, allow for offline use and optimize loading time.

* For static data, like the names of countries, I used json.

## Folder structure

 ```
Assessment
│   .env
│   country_names.json
│   covid_dash.log
│   covid_dash.py
│   covid_data.db
│   Dockerfile
│   README.md
│   requirements.txt
│
├───.github
│   └───workflows
│           github-actions-.yml
│
└───Tests
        Test_Covid.py
```
* The requirements.txt contains the configuration of all packages to be installed, created by:
 ``` pip freeze > requirements.txt ``` 

## Deploymnt

I built a docker image

```sh
docker build -t dash .

docker run -it --name services -p 5040:5040 dash
```

## To acces the dashboard page

Go to `http://localhost:5040` in browser.

## CI/CD and Unit testing

The unittests are run with github actions.

*"And so it goes ..."*



