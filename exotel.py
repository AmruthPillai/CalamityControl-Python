#!/usr/bin/python

import cgi
import json
import requests
import pyrebase
import csv
import geocoder
import numpy as np
from sklearn.neighbors import KNeighborsClassifier

# i have no clue why this is required.. probably we'll remove this later

print "Content-type: text/plain"
print ""

# config for firebase
config = {
    "apiKey": "AIzaSyCMoO7CX52RaO5CqSBWTZ67PiLiigAh4jM",
    "authDomain": "calamity-control-1478121312942.firebaseapp.com",
    "databaseURL": "https://calamity-control-1478121312942.firebaseio.com",
    "storageBucket": "calamity-control-1478121312942.appspot.com"
}
firebase = pyrebase.initialize_app(config)
db = firebase.database()

# getting the parameters from ivrs call - number and time
form = cgi.FieldStorage()
number = form.getvalue('From')
time = form.getvalue('CurrentTime')
condition = form.getvalue('condition')

# getting the state from number
phone_number = "+91" + number

url = "http://apilayer.net/api/validate"
parameters = {
    'access_key': 'a9d72f843b7d292cbb82fb2e299fd4b5',
    'number': phone_number,
    'format': '1'
}

response = requests.get(url, params=parameters)
resp_data = json.loads(response.text)

lat, lng = geocoder.google(resp_data['location']).latlng

# creating the csv of present data
calamitiesArray= [
    'undefined',
    'cyclone',
    'earthquake',
    'tsunami',
    'hurricane',
    'tornado',
    'floods',
    'drought',
    'others'
]
with open('coords.csv', 'w') as csvfile:
        fieldnames = ['lat', 'lng','calamity']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        json_content = db.child("reports").get()
        for child in json_content.each():
                item = {}
                item['lat'] = child.val()['lat']
                item['lng'] = child.val()['lng']
                cal  = child.val()['calamity'].encode('ascii')
                item['calamity'] = calamitiesArray.index(cal.lower())
                writer.writerow(item)
                writer.writerow(item)
                writer.writerow(item)


# k nearest neighbour
knn = KNeighborsClassifier()

ds = np.loadtxt("coords.csv", delimiter=",")

features = ds[:,:2]
labels = ds[:,2]
knn.fit(features, labels)

# gives the calamity
if knn.predict([lat,lng]).astype(int) != 0:
	calamityName = calamitiesArray[knn.predict([lat,lng]).astype(int)]
    	if condition:
    		data = {"lat":lat, "lng":lng,"calamity":calamityName,"time":time,"number":number,"level":condition}
    	else:
    		data = {"lat":lat, "lng":lng,"calamity":calamityName,"time":time,"number":number}

	db.child("reports").push(data)
