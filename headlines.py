import feedparser
from flask import Flask  # imports Flask from the package flask
import json
from flask import render_template
from flask import request
from urllib.request import urlopen
from urllib.parse import quote

app = Flask(__name__)  # creates an instance of the Flask object


RSS_FEEDS = {
    'thehindu': 'https://www.thehindu.com/news/feeder/default.rss',
    'bbc': 'https://feeds.bbci.co.uk/news/rss.xml',
    'cnn': 'http://rss.cnn.com/rss/edition.rss',
    'fox': 'http://feeds.foxnews.com/foxnews/latest',
    'iol': 'http://www.iol.co.za/cmlink/1.640'
}

DEFAULTS = {
    'publication': 'thehindu',
    'city': 'Noida, IN'
}

WEATHER_URL = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=90184a7ba6f44d5ff6d08e1bf23ed475'

# Flask uses decorators for URL routing
# function directly below it should be called whenever a user vists root page
@app.route("/")
def home():
    # get customized headlines, based on user input or default
    publication = request.args.get('publication')
    if not publication:
        publication = DEFAULTS['publication']
    articles = get_news(publication)

    # get customized weather based on user input or default
    city = request.args.get('city')
    if not city:
        city = DEFAULTS['city']
    weather = get_weather(city)

    return render_template(
        'home.html',
        articles=articles,
        publication=publication.upper(),
        RSS_FEEDS=RSS_FEEDS,
        weather=weather
    )


def get_news(query):
    if not query or query.lower() not in RSS_FEEDS:
        publication = DEFAULTS['publication']
    else:
        publication = query.lower()
    feed = feedparser.parse(RSS_FEEDS[publication])
    return feed['entries']


def get_weather(query):
    query = quote(query)
    url = WEATHER_URL.format(query)
    data = urlopen(url).read()
    parsed = json.loads(data)
    weather = None
    if parsed.get('weather'):
        weather = {
            'description': parsed['weather'][0]['description'],
            'temperature': parsed['main']['temp'],
            'city': parsed['name'],
            'country': parsed['sys']['country']
        }
    return weather


if __name__ == '__main__':
    app.run(port=5000, debug=True)
