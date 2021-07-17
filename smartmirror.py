# smartmirror.py
# requirements
# requests, feedparser, traceback, Pillow

import tkinter as tk
import locale
import threading
import time
import requests
import json
import traceback
import feedparser

from PIL import Image, ImageTk
from contextlib import contextmanager

LOCALE_LOCK = threading.Lock()

ui_locale = '' # e.g. 'fr_FR' fro French, '' as default
time_format = 12 # 12 or 24
date_format = "%b %d, %Y" # check python doc for strftime() for options
weather_lang = 'en' # see https://darksky.net/dev/docs/forecast for full list of language parameters values
weather_unit = 'us' # see https://darksky.net/dev/docs/forecast for full list of unit parameters values
latitude = "42.34"
longitude = "-71.12" 
xlarge_text_size = 94
large_text_size = 48
medium_text_size = 28
small_text_size = 18

@contextmanager
def setlocale(name): #thread proof function to work with locale
    with LOCALE_LOCK:
        saved = locale.setlocale(locale.LC_ALL)
        try:
            yield locale.setlocale(locale.LC_ALL, name)
        finally:
            locale.setlocale(locale.LC_ALL, saved)

# maps open weather icons to
# icon reading is not impacted by the 'lang' parameter
icon_lookup = {
    'Mostly Sunny': "assets/Sun.png",  # clear sky day
    'wind': "assets/Wind.png",   #wind
    'cloudy': "assets/Cloud.png",  # cloudy day
    'partly-cloudy-day': "assets/PartlySunny.png",  # partly cloudy day
    'rain': "assets/Rain.png",  # rain day
    'snow': "assets/Snow.png",  # snow day
    'snow-thin': "assets/Snow.png",  # sleet day
    'fog': "assets/Haze.png",  # fog day
    'clear-night': "assets/Moon.png",  # clear sky night
    'partly-cloudy-night': "assets/PartlyMoon.png",  # scattered clouds night
    'thunderstorm': "assets/Storm.png",  # thunderstorm
    'tornado': "assests/Tornado.png",    # tornado
    'hail': "assests/Hail.png"  # hail
}


font = "Helvetica"

class Clock(tk.Frame):
    def __init__(self, parent, *args, **kwargs):

        tk.Frame.__init__(self, parent, bg='black')
        # initialize time label
        self.time1 = ''
        self.timeLbl = tk.Label(self, font=(font, large_text_size), fg="white", bg="black")
        self.timeLbl.pack(side=tk.TOP, anchor=tk.E)
        # initialize day of week
        self.day_of_week1 = ''
        self.dayOWLbl = tk.Label(self, text=self.day_of_week1, font=(font, small_text_size), fg="white", bg="black")
        self.dayOWLbl.pack(side=tk.TOP, anchor=tk.E)
        # initialize date label
        self.date1 = ''
        self.dateLbl = tk.Label(self, text=self.date1, font=(font, small_text_size), fg="white", bg="black")
        self.dateLbl.pack(side=tk.TOP, anchor=tk.E)
        self.tick()

    def tick(self):
        with setlocale(ui_locale):
            if time_format == 12:
                time2 = time.strftime('%I:%M %p') #hour in 12h format
            else:
                time2 = time.strftime('%H:%M') #hour in 24h format

            day_of_week2 = time.strftime('%A')
            date2 = time.strftime(date_format)
            # if time string has changed, update it
            if time2 != self.time1:
                self.time1 = time2
                self.timeLbl.config(text=time2)
            if day_of_week2 != self.day_of_week1:
                self.day_of_week1 = day_of_week2
                self.dayOWLbl.config(text=day_of_week2)
            if date2 != self.date1:
                self.date1 = date2
                self.dateLbl.config(text=date2)
            # calls itself every 200 milliseconds
            # to update the time display as needed
            # could use >200 ms, but display gets jerky
            self.timeLbl.after(200, self.tick)


class Weather(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, bg='black')
        self.temperature = ''
        self.forecast = ''
        self.location = ''
        self.currently = ''
        self.icon = ''
        self.degreeFrm = tk.Frame(self, bg="black")
        self.degreeFrm.pack(side=tk.TOP, anchor=tk.W)
        self.temperatureLbl = tk.Label(self.degreeFrm, font=(font, xlarge_text_size), fg="white", bg="black")
        self.temperatureLbl.pack(side=tk.LEFT, anchor=tk.N)
        self.iconLbl = tk.Label(self.degreeFrm, bg="black")
        self.iconLbl.pack(side=tk.LEFT, anchor=tk.N, padx=20)
        self.currentlyLbl = tk.Label(self, font=(font, medium_text_size), fg="white", bg="black")
        self.currentlyLbl.pack(side=tk.TOP, anchor=tk.W)
        self.forecastLbl = tk.Label(self, font=(font, small_text_size), fg="white", bg="black")
        self.forecastLbl.pack(side=tk.TOP, anchor=tk.W)
        self.locationLbl = tk.Label(self, font=(font, small_text_size), fg="white", bg="black")
        self.locationLbl.pack(side=tk.TOP, anchor=tk.W)
        self.get_weather()

    def get_weather(self):
        try:

            location2 = ""
            # get the correct weather station url for the latitude and longitude
            nws_points_url = f"https://api.weather.gov/points/{latitude},{longitude}"
            nws_points = requests.get(nws_points_url).json()            
            nws_forecast_url = nws_points['properties']['forecast']

            # pull the forecast from the national weather service
            nws_forecast = requests.get(nws_forecast_url).json()['properties']['periods']

            temperature = f"{nws_forecast[0]['temperature']}\N{DEGREE SIGN}"
            currently = nws_forecast[0]['shortForecast']
            forecast2 = f"{nws_forecast[1]['name']}: {nws_forecast[1]['detailedForecast']}"

            # icon_id = 
            icon2 = None
            print(currently)
            if currently in icon_lookup:
                icon2 = icon_lookup[currently]

            if icon2 is not None:
                if self.icon != icon2:
                    self.icon = icon2
                    image = Image.open(icon2)
                    image = image.resize((100, 100), Image.ANTIALIAS)
                    image = image.convert('RGB')
                    photo = ImageTk.PhotoImage(image)

                    self.iconLbl.config(image=photo)
                    self.iconLbl.image = photo
            else:
                # remove image
                self.iconLbl.config(image='')

            if self.currently != currently:
                self.currently = currently
                self.currentlyLbl.config(text=currently)
            if self.forecast != forecast2:
                self.forecast = forecast2
                self.forecastLbl.config(text=forecast2)
            if self.temperature != temperature:
                self.temperature = temperature
                self.temperatureLbl.config(text=temperature)
            if self.location != location2:
                if location2 == ", ":
                    self.location = "Cannot Pinpoint Location"
                    self.locationLbl.config(text="Cannot Pinpoint Location")
                else:
                    self.location = location2
                    self.locationLbl.config(text=location2)
        except Exception as e:
            traceback.print_exc()
            print(f"Error: {e}. Cannot get weather.")

        self.after(600000, self.get_weather)

    @staticmethod
    def convert_kelvin_to_fahrenheit(kelvin_temp):
        return 1.8 * (kelvin_temp - 273) + 32


class News(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.config(bg='black')
        self.title = 'News' # 'News' is more internationally generic
        self.newsLbl = tk.Label(self, text=self.title, font=(font, medium_text_size), fg="white", bg="black")
        self.newsLbl.pack(side=tk.TOP, anchor=tk.W)
        self.headlinesContainer = tk.Frame(self, bg="black")
        self.headlinesContainer.pack(side=tk.TOP)
        self.get_headlines()

    def get_headlines(self):
        try:
            # remove all children
            for widget in self.headlinesContainer.winfo_children():
                widget.destroy()

            headlines_url = "https://www.economist.com/united-states/rss.xml"

            feed = feedparser.parse(headlines_url)

            for post in feed.entries[0:5]:
                headline = NewsHeadline(self.headlinesContainer, post.title)
                headline.pack(side=tk.TOP, anchor=tk.W)
                
        except Exception as e:
            traceback.print_exc()
            print (f"Error: {e}. Cannot get news.")

        self.after(600000, self.get_headlines)


class NewsHeadline(tk.Frame):
    def __init__(self, parent, event_name=""):
        tk.Frame.__init__(self, parent, bg='black')

        image = Image.open("assets/Newspaper.png")
        image = image.resize((25, 25), Image.ANTIALIAS)
        image = image.convert('RGB')
        photo = ImageTk.PhotoImage(image)

        self.iconLbl = tk.Label(self, bg='black', image=photo)
        self.iconLbl.image = photo
        self.iconLbl.pack(side=tk.LEFT, anchor=tk.N)

        self.eventName = event_name
        self.eventNameLbl = tk.Label(self, text=self.eventName, font=(font, small_text_size), fg="white", bg="black")
        self.eventNameLbl.pack(side=tk.LEFT, anchor=tk.N)


class Calendar(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, bg='black')
        self.title = 'Calendar Events'
        self.calendarLbl = tk.Label(self, text=self.title, font=(font, medium_text_size), fg="white", bg="black")
        self.calendarLbl.pack(side=tk.TOP, anchor=tk.E)
        self.calendarEventContainer = tk.Frame(self, bg='black')
        self.calendarEventContainer.pack(side=tk.TOP, anchor=tk.E)
        self.get_events()

    def get_events(self):
        #TODO: implement this method
        # reference https://developers.google.com/google-apps/calendar/quickstart/python

        # remove all children
        for widget in self.calendarEventContainer.winfo_children():
            widget.destroy()

        calendar_event = CalendarEvent(self.calendarEventContainer)
        calendar_event.pack(side=tk.TOP, anchor=tk.E)
        pass


class CalendarEvent(tk.Frame):
    def __init__(self, parent, event_name="Event 1"):
        tk.Frame.__init__(self, parent, bg='black')
        self.eventName = event_name
        self.eventNameLbl = tk.Label(self, text=self.eventName, font=(font, small_text_size), fg="white", bg="black")
        self.eventNameLbl.pack(side=tk.TOP, anchor=tk.E)


class FullscreenWindow:

    def __init__(self):
        self.tk = tk.Tk()
        self.tk.configure(background='black')
        self.topFrame = tk.Frame(self.tk, background = 'black')
        self.bottomFrame = tk.Frame(self.tk, background = 'black')
        self.topFrame.pack(side = tk.TOP, fill=tk.BOTH, expand = tk.YES)
        self.bottomFrame.pack(side = tk.BOTTOM, fill=tk.BOTH, expand = tk.YES)
        self.state = False
        self.tk.bind("<Return>", self.toggle_fullscreen)
        self.tk.bind("<Escape>", self.end_fullscreen)
        # clock
        self.clock = Clock(self.topFrame)
        self.clock.pack(side=tk.RIGHT, anchor=tk.N, padx=100, pady=60)
        # weather
        self.weather = Weather(self.topFrame)
        self.weather.pack(side=tk.LEFT, anchor=tk.N, padx=100, pady=60)
        # news
        self.news = News(self.bottomFrame)
        self.news.pack(side=tk.LEFT, anchor=tk.S, padx=100, pady=60)
        # calender - removing for now
        # self.calender = Calendar(self.bottomFrame)
        # self.calender.pack(side = tk.RIGHT, anchor=tk.S, padx=100, pady=60)

    def toggle_fullscreen(self, event=None):
        self.state = not self.state  # Just toggling the boolean
        self.tk.attributes("-fullscreen", self.state)
        return "break"

    def end_fullscreen(self, event=None):
        self.state = False
        self.tk.attributes("-fullscreen", False)
        return "break"

if __name__ == '__main__':
    w = FullscreenWindow()
    w.tk.mainloop()
