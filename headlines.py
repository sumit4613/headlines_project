import feedparser
from flask import Flask  # imports Flask from the package flask
from flask import render_template

app = Flask(__name__)  # creates an instance of the Flask object


RSS_FEEDS = {
    'thehindu': 'https://www.thehindu.com/news/feeder/default.rss',
    'bbc': 'https://feeds.bbci.co.uk/news/rss.xml',
    'cnn': 'http://rss.cnn.com/rss/edition.rss',
    'fox': 'http://feeds.foxnews.com/foxnews/latest',
    'iol': 'http://www.iol.co.za/cmlink/1.640'
}

# Flask uses decorators for URL routing
@app.route("/")  # function directly below it should be called whenever a user vists root page
@app.route("/<publication>")
def get_news(publication='bbc'):
    ''' This function is called by Flask when a user visits our application'''
    feed = feedparser.parse(RSS_FEEDS[publication])
    return render_template('home.html', articles=feed['entries'])


if __name__ == '__main__':
    app.run(port=5000, debug=True)
