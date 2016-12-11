#!/usr/bin/python
import tweepy
import cgi
from twicreds import twitter_creds

print "Content-type: text/html"
print ""

form = cgi.FieldStorage()
tweet = form.getvalue('tweet')

auth = tweepy.OAuthHandler(twitter_creds['consumer_key'], twitter_creds['consumer_secret'])
auth.set_access_token(twitter_creds['access_token'], twitter_creds['access_token_secret'])
api = tweepy.API(auth)

status = api.update_status(status=tweet)
print(status)
