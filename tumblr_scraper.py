import urllib
import re
import os
import csv

def get_picture_with_time(subdomain, start=0, chunk=50, resolution=1280) :
	api_url = 'http://#subdomain#.tumblr.com/api/read?type=photo&num=#chunk#&start=#start#'
	api_url = api_url.replace("#subdomain#", subdomain)
	api_url = api_url.replace("#chunk#", str(50))
	api_url = api_url.replace("#start#", str(start))

	site = api_url
	file = urllib.urlopen(site)
	data = file.read()

	#regex_pic_with_time = ur"<post id=(.+?)date-gmt=\"(.+?)\" date=(.+?)<photo-url max-width=\"" + "1280" + "\">(.+?)</photo-url>(.+?)</post>"
	
	regex_post = ur"<post id=(.+?)</post>"
	post_list = re.findall(regex_post, data)
	
	#only download images of the certain resolution
	regex_image = ur"<photo-url max-width=\"" + str(resolution) + "\">(.+?)</photo-url>"
	regex_time = ur"date-gmt=\"(.+?) GMT\""
	regex_tag = ur"<tag>(.+?)</tag>"
	
	picture_with_time_list = []

	for post in post_list :
		image_list = re.findall(regex_image, post)
		time = re.findall(regex_time, post)
		tag_list = re.findall(regex_tag, post)
		for image in image_list :
			picture_with_time_list.append([time[0], tag_list, image])
	file.close()

	return picture_with_time_list

def save_record(subdomain, record) :
	fname = subdomain + "_" + "record.txt"
	file =open(fname,'w')
	file.write(str(record))
	file.close()

def download_images(subdomain, record) :
	if not os.path.exists(subdomain):
	 		os.makedirs(subdomain)
	image_list = [each_record[2] for each_record in record]
	print "Start downloading images from " + subdomain + "......"
	for each in image_list:
		name = each.split('/')[-1]
		if len(name) > 35 :
			name = name[(len(name)-35):]
		print name
		dest = os.path.join(subdomain, name)
		print "Downloading " + name + "......"
		urllib.urlretrieve(each, dest)
	print "All the images are saved."

	
def get_all_images(subdomain) :
	api_url = 'http://#subdomain#.tumblr.com/api/read?type=photo&num=#chunk#&start=0'
	api_url = api_url.replace("#subdomain#", subdomain)
	api_url = api_url.replace("#chunk#", str(50))

	site = api_url
	file = urllib.urlopen(site)
	data = file.read()
	file.close()

	#### all the images on the page
	regex_image   = ur"<photo-url max-width=\"" + "1280" + "\">(.+?)</photo-url>"
	image_list = re.findall(regex_image, data)
	return len(image_list)


def tumblr_scraper(subdomain, chunk=50, start=0, resolution=1280) :
	total = get_all_images(subdomain)
	start_point = 0
	record = []
	while True :
		data = get_picture_with_time(subdomain, start_point, chunk, resolution)
		if not data :
			break
		for post in data :
			record.append(post)
		total -= len(data)
		if total <= 0 :
			break
		start_point += chunk
	### write record to a file
	save_record(subdomain, record)
	### download images to a certain folder
	download_images(subdomain, record)

def read_col(filename, mark) :
	with open(filename + "/" + mark + ".csv",'rb') as csvfile:
		reader = csv.reader(csvfile)
		column = [row[0] for row in reader]
	return column


def download_url(filename, mark) :
	post_list = read_col(filename, mark)
	image_list = post_to_image(post_list)
	print "Start downloading images from " + filename + "......"
	for each in image_list:
		name = each.split('/')[-1]
		if len(name) > 35 :
			name = name[(len(name)-35):]
		dest = os.path.join(filename, name)
		print "Downloading " + name + "......"
		urllib.urlretrieve(each, dest)
	print "All the images are saved."

def post_to_image(post_list) :
	image_list = []
	for url in post_list :
		site = url
		file = urllib.urlopen(site)
		data = file.read()
		regex_image = ur"<img id=(.+?)data-src=\"(.+?)\" data-height=(.+?)data-width=(.+?)>"
		image = re.findall(regex_image, data)
		image_list.append(image[0][1])
	return image_list


