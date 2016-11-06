
# Authenticate via API Key 'p71Lr3B68z5H7AWMF95cbfZz08Kp7WexlgUwoEv2BmRGwowxVa'
# Example timestamp: before=1346822071

from bs4 import BeautifulSoup
import urllib2
import json
import requests
import sys
import csv
import time

title = ""
tag = ""
limit = ""
before = ""
content = []
urls = []
latestTimestamp = ""
count = 0

def get_user_params():
	global tag
	global limit
	global before
	global title
	while (tag == ""):
		tag = raw_input("What tag would you like to scrape? ")
	title = tag.replace(" ", "_")
	tag = tag.replace(" ", "+")
	while (limit == ""):
		limit = raw_input("How many images would you like to scrape?  " )
	while (before == ""):
		before = raw_input("Would you like to include a time constraint?\n(Note that this is the day that the scrape will start on. Enter in the format YYYY-MM-DD or enter 0 for current date) ")
	if before != '0':
		before = get_epoch_timestamp(before + " 23:59:59 GMT")

def get_epoch_timestamp(date_time):
	pattern = '%Y-%m-%d %H:%M:%S GMT'
	epoch = int(time.mktime(time.strptime(date_time, pattern)))
	return epoch 

def scrape_image_captions():
	global tag
	global limit
	global before
	global count
	global urls
	global title
	url = 'https://api.tumblr.com/v2/tagged?tag='+ tag +'&limit='+ limit +'&api_key=p71Lr3B68z5H7AWMF95cbfZz08Kp7WexlgUwoEv2BmRGwowxVa'
	if before != '0':
		url += '&before=' + str(before)
		latestTimestamp = before
	urlLoaded = urllib2.urlopen(url)
	data = json.load(urlLoaded)
	if len(data['response']) == 0:
		return
	print count
	for item in data['response']:
		latestTimestamp = item['timestamp']
		if 'image_permalink' in item:
			i = item['trail']
			for val in i:
				count += 1
				if count > limit:
					break
				if 'content_raw' in val:
					c = val['content_raw']
					soup = BeautifulSoup(c, "lxml")
					soup = soup.get_text()
					content.append([item['timestamp'], item['date'], item['image_permalink'], soup.encode('ascii', 'ignore')])
					urls.append([item['image_permalink']])
				else:
					content.append([item['timestamp'], item['date'], item['image_permalink'], ""])
					urls.append([item['image_permalink']])
	if count < int(limit):
		before = str(latestTimestamp)
		scrape_image_captions()

def write_content_to_csv(content):
	with open(title + ".csv", 'a') as csvfile:
	    wr = csv.writer(csvfile, delimiter=',')
	    for c in content:
	    	wr.writerow(c)

def write_urls_to_csv(urls):
	with open(title + "_urls.csv", 'a') as csvfile:
		wr = csv.writer(csvfile, delimiter=',')
		for u in urls:
			wr.writerow(u)

def main():
	get_user_params()
	scrape_image_captions()
	write_content_to_csv(content)
	write_urls_to_csv(urls)

main()
