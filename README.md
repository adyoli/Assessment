# SweepSouth

For this assessment I decided to go with something current and something that would be useful to anyone given the times we're living in. I went with a Covid-19 Dashboard.
The user can enter the name of any country in the world and after pressing the submit button they will have access to over 600 days worth of data, data back to 2020 of how 
that particular country has been doing in death cases.

For this exercise I decided to go with the media group api with API base "https://covid-api.mmediagroup.fr/v1"

I went with the dash framework on this one, because its the easiest way to produce dynamic, plots with python.

The db of choice was sqlite3, this his allows for data persistence which will hwlp in minimizing API call

I then dockerized the application for your convenience.

NB: Due to time constraints I was unable to comprehensively test the application, however I hope you enjoy going through the code.

PS: Be careful about the port, the application sometimes requires binding to the 0.0.0.0 port.
