#!/usr/bin/python
import pyrebase
import cgi
from time import gmtime, strftime
from calamities import calamities_list

print "Content-type: text/html"
print ""

config = {
"apiKey": "AIzaSyCMoO7CX52RaO5CqSBWTZ67PiLiigAh4jM",
"authDomain": "calamity-control-1478121312942.firebaseapp.com",
"databaseURL": "https://calamity-control-1478121312942.firebaseio.com",
"storageBucket": "calamity-control-1478121312942.appspot.com"
}
firebase = pyrebase.initialize_app(config)
db = firebase.database()
form = cgi.FieldStorage()
import csv
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
knn = KNeighborsClassifier()


lat = form.getvalue('lat')
lon = form.getvalue('lon')

db = firebase.database()
db = db.child("reports")

with open('coords.csv', 'w') as csvfile:
        fieldnames = ['lat', 'lng','calamity']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        json_content = db.get()
        for child in json_content.each():
                item = {}
                item['lat'] = child.val()['lat']
                item['lng'] = child.val()['lng']
                cal  = child.val()['calamity'].encode('ascii')
                item['calamity'] = calamities_list.index(cal.lower())
                writer.writerow(item)


ds = np.loadtxt("coords.csv", delimiter=",")

features = ds[:,:2]
labels = ds[:,2]
knn.fit(features, labels)

calamity = calamities_list[knn.predict([lat,lon]).astype(int)]

db.child("reports").push({"calamity":calamity,"lat":lat,"lng":lon,"time": strftime("%Y-%m-%d %H:%M:%S", gmtime())})

