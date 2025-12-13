# Plasma Weather 7 

A Frutiger Aero–style weather widget for KDE Plasma 6

![Screenshot](screenshot.png)

## Usage

This weather widget is inspired by [Theldus/Windy](https://github.com/Theldus/windy), and unlike most traditional weather widgets, it does not embed any specific weather API directly within the widget itself. Instead, it delegates the task of fetching weather data to an external script or program specified by the user.

The widget works by invoking the user-defined script and reading JSON output from its standard output (stdout). This JSON data is then parsed and displayed in the widget’s interface. In essence, this widget acts as a graphical frontend for any external weather data source.

By default, the widget calls `curl`, which fetches weather data using the ColorfulClouds API. However, this fork provides a weather.py script which will use the OpenMateo protocol to fetch weather data. Simply go into the plasmoid settings and point to this script to have it fetch accurate weather data.

For more details about the expected JSON format and available APIs, please visit: [Weather | ColorfulClouds](https://docs.caiyunapp.com/weather-api/v2/v2.6/6-weather.html)

Other changes from the main fork include an updated 3 hour scheduling, a day/night schedule, and precipitation chances.

## Install

You'll need `kpackagetool6`

```shell
kpackagetool6 --type "Plasma/Applet" --install package # For installing
kpackagetool6 --type "Plasma/Applet" --upgrade package # For upgrading
```

change the latitude and longitude in weather.py to be your cities lat/long. doesn't have to be exact, just needs to be your city.
