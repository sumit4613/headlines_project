import datetime
import feedparser
import json
from flask import Flask  # imports Flask from the package flask
from flask import make_response
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
    'city': 'Noida, IN',
    'currency_from': 'USD',
    'currency_to': 'INR'
}

WEATHER_URL = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=90184a7ba6f44d5ff6d08e1bf23ed475'

CURRENCY_URL = "https://openexchangerates.org//api/latest.json?app_id=25481102dd0246278a67a80eeaf9c65e"

# Flask uses decorators for URL routing
# function directly below it should be called whenever a user vists root page


@app.route("/")
def home():
    # get customized headlines, based on user input or default
    publication = get_value_with_fallback('publication')
    articles = get_news(publication)

    # get customized weather based on user input or default
    city = get_value_with_fallback('city')
    weather = get_weather(city)

    # get customized currency based on user input or default
    currency_from = get_value_with_fallback('currency_from')
    currency_to = get_value_with_fallback('currency_to')
    rate, currencies = get_rates(currency_from, currency_to)

    # save cookies and return template
    response = make_response(render_template(
        'home.html',
        articles=articles,
        publication=publication.upper(),
        RSS_FEEDS=RSS_FEEDS,
        weather=weather,
        currency_from=currency_from,
        currency_to=currency_to,
        rate=rate,
        currencies=sorted(currencies)
    ))
    expires = datetime.datetime.now() + datetime.timedelta(days=365)
    response.set_cookie("publication", publication, expires=expires)
    response.set_cookie("city", city, expires=expires)
    response.set_cookie("currency_from", currency_from, expires=expires)
    response.set_cookie("currency_to", currency_to, expires=expires)
    return response


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


def get_rates(frm, to):
    all_currency = urlopen(CURRENCY_URL).read()
    parsed = json.loads(all_currency).get('rates')
    frm_rate = parsed.get(frm.upper())
    to_rate = parsed.get(to.upper())
    return (to_rate/frm_rate, parsed.keys())


def get_value_with_fallback(key):
    if request.args.get(key):
        return request.args.get(key)
    if request.cookies.get(key):
        return request.cookies.get(key)
    return DEFAULTS[key]


if __name__ == '__main__':
    app.run(port=5000, debug=True)
