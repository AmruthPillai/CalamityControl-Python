import tweepy
import json
import re

from time import gmtime, strftime

import geocoder
import pyrebase

from calamities import calamity_list

from google.cloud import language
client = language.Client()

from oauth2client.client import GoogleCredentials
credentials = GoogleCredentials.get_application_default()

from googleapiclient import discovery
language = discovery.build('language', 'v1', credentials=credentials)

# Authentication details. To  obtain these visit dev.twitter.com
consumer_key = "qjdZSrFT84qsfLEdUJjatYtc8"
consumer_secret = "NAbS1CcrfLKZrvDZxqbQWmVJKAOsqjplCUnaaYEMqGzgL59vG2"

access_token = "1109726539-9n4dR45ZsvQbpSzkz3Ww5A7DjfjMmAJbKBmi4PI"
access_token_secret = "9KXyCvK1v7PGdYpc8lctlTCcrCmgEvFk62LDgIL1Z9DEw"

config = {
  "apiKey": "AIzaSyCMoO7CX52RaO5CqSBWTZ67PiLiigAh4jM",
  "authDomain": "calamity-control-1478121312942.firebaseapp.com",
  "databaseURL": "https://calamity-control-1478121312942.firebaseio.com",
  "storageBucket": "calamity-control-1478121312942.appspot.com"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

# This is the listener, resposible for receiving data
class StdOutListener(tweepy.StreamListener):
    def on_data(self, data):
        # Twitter returns data in JSON format - we need to decode it first
        decoded = json.loads(data)

        # Also, we convert UTF-8 to ASCII ignoring all bad characters sent by users
        tweet = decoded['text'].encode('ascii', 'ignore')
        tweet_clean = re.sub(r"http\S+", "", tweet)

        print tweet_clean
        print '-------------'

        body = {
            'document': {
                'type': 'PLAIN_TEXT',
                'content': tweet_clean,
            },
            'encoding_type': 'UTF8',
        }

        request = language.documents().analyzeEntities(body=body)
        response = request.execute()

        tweet_to_report = {}
        tweet_to_report['source'] = 'twitter'

        for k,v in enumerate(response['entities']):
            if v['type'] == 'EVENT' or v['type'] == 'OTHER':
                if any(calamity_name in v['name'].lower() for calamity_name in calamity_list):
                    tweet_to_report['calamity'] =  v['name']
            if v['type'] == 'LOCATION':
                tweet_to_report['lat'],tweet_to_report['lng'] = geocoder.google(v['name']).latlng
	
	tweet_to_report['time'] = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        db.child('reports').push(tweet_to_report)
        print "Pushed to Firebase!"

        return True

    def on_error(self, status):
        print status

if __name__ == '__main__':
    l = StdOutListener()
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    print "Showing all new tweets for #calamity:"

    stream = tweepy.Stream(auth, l)
    stream.filter(languages=["en"], track=['#calamity'])
