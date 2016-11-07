
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
limit = float("inf")
before = ""
after = ""
content = []
urls = []
latestTimestamp = ""
count = 0

def get_user_params():
	global tag
	global limit
	global before
	global title
	global after
	choice = ""
	while (tag == ""):
		tag = raw_input("What tag would you like to scrape? ")
	title = tag.replace(" ", "_")
	tag = tag.replace(" ", "+")
	while (choice == ""):
		choice = raw_input("Would you like to limit by number of posts starting with current date (enter p) or limit by date (enter d)? ")
	if choice == "p":
		while (limit == ""):
			limit = raw_input("How many images would you like to scrape?  " )
	else:
		print("Keep in mind that this scraper works in reverse chronological order.")
		while (before == ""):
			before = raw_input("What date would you like to start scraping on?\n(Note that this day will be included in the scrape. Enter in the format YYYY-MM-DD) ")
		while (after == ""):
			after = raw_input("What date would you like to finish scraping on?\n(Note that this day will be included in the scrape. Enter in the format YYYY-MM-DD) ")
		before = str(get_epoch_timestamp(before + " 23:59:59"))
		after = get_epoch_timestamp(after + " 00:00:00")

def get_epoch_timestamp(date_time):
	pattern = '%Y-%m-%d %H:%M:%S'
	epoch = int(time.mktime(time.strptime(date_time, pattern)))
	return epoch 

def scrape_captions_using_dates():
	global tag
	global before
	global after
	global count
	global urls
	global title
	url = 'https://api.tumblr.com/v2/tagged?tag='+ tag +'&before='+ before +'&api_key=p71Lr3B68z5H7AWMF95cbfZz08Kp7WexlgUwoEv2BmRGwowxVa'
	latestTimestamp = before
	urlLoaded = urllib2.urlopen(url)
	data = json.load(urlLoaded)
	if len(data['response']) == 0:
		return
	print count
	for item in data['response']:
		latestTimestamp = item['timestamp']
		if latestTimestamp < after:
			return
		if 'image_permalink' in item:
			i = item['trail']
			for val in i:
				count += 1
				if count > limit:
					return
				if 'content_raw' in val:
					c = val['content_raw']
					soup = BeautifulSoup(c, "lxml")
					soup = soup.get_text()
					content.append([item['timestamp'], item['date'], item['image_permalink'], soup.encode('ascii', 'ignore')])
					urls.append([item['image_permalink']])
				else:
					content.append([item['timestamp'], item['date'], item['image_permalink'], ""])
					urls.append([item['image_permalink']])
	if latestTimestamp >= after:
		before = str(latestTimestamp)
		scrape_captions_using_dates()

def scrape_captions_using_limit():
	global tag
	global limit
	global count
	global urls
	global title
	url = 'https://api.tumblr.com/v2/tagged?tag='+ tag +'&limit='+ limit +'&api_key=p71Lr3B68z5H7AWMF95cbfZz08Kp7WexlgUwoEv2BmRGwowxVa'
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
	if count < limit:
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
	global limit
	get_user_params()
	if limit != float("inf"):
		scrape_captions_using_limit()
	else:
		scrape_captions_using_dates()
	write_content_to_csv(content)
	write_urls_to_csv(urls)

main()
