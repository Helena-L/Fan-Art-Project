
# Authenticate via API Key 'p71Lr3B68z5H7AWMF95cbfZz08Kp7WexlgUwoEv2BmRGwowxVa'
# Example timestamp: before=1346822071

from bs4 import BeautifulSoup
import urllib2
import json
import requests
import sys
import csv

tag = ""
limit = ""
before = ""
content = []
latestTimestamp = ""
count = 0

def get_user_params():
	global tag
	global limit
	global before
	while (tag == ""):
		tag = raw_input("What tag would you like to scrape? ")
	while (limit == ""):
		limit = raw_input("How many posts would you like to scrape?  " )
	while (before == ""):
		before = raw_input("Would you like to include a time constraint? (to use current date, enter 0) ")

def scrape_image_captions():
	global tag
	global limit
	global before
	global count
	url = 'https://api.tumblr.com/v2/tagged?tag='+ tag +'&limit='+ limit +'&api_key=p71Lr3B68z5H7AWMF95cbfZz08Kp7WexlgUwoEv2BmRGwowxVa'
	if before != '0':
		url += '&before=' + before
		latestTimestamp = before
	urlLoaded = urllib2.urlopen(url)
	data = json.load(urlLoaded)
	for item in data['response']:
		count += 1
		if count > limit:
			break
		latestTimestamp = item['timestamp']
		if 'image_permalink' in item:
			i = item['trail']
			for val in i:
				if 'content_raw' in val:
					c = val['content_raw']
					soup = BeautifulSoup(c, "lxml")
					soup = soup.get_text()
					content.append([item['timestamp'], item['date'], soup.encode('ascii', 'ignore')])
				else:
					content.append([item['timestamp'], item['date'], ""])
	print count
	if count < int(limit):
		before = str(latestTimestamp)
		scrape_image_captions()
	print latestTimestamp

def write_to_csv(content):
	with open(tag + ".csv", 'a') as csvfile:
	    wr = csv.writer(csvfile, delimiter=',')
	    for c in content:
	    	wr.writerow(c)

def main():
	get_user_params()
	scrape_image_captions()
	write_to_csv(content)

main()
