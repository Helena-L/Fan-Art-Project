import numpy as np
import os
from PIL import Image, ImageDraw
import struct
import scipy
import scipy.misc
import scipy.cluster
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import hcluster

def to_rgb3b(im):
	# as 3a, but we add an extra copy to contiguous 'C' order
	return np.dstack([im.astype(np.uint8)] * 3).copy(order='C')

def get_im_list(im_dir):
	os.chdir(im_dir)
	imlist = []
	allfiles=os.listdir(im_dir)
	for filename in allfiles:
		if filename[-4:] in [".png",".PNG"] or filename[-4:] in [".jpg",".JPG"] or filename[-5:] in [".jpeg",".JPEG"]:
			imlist.append(filename)
	return imlist

def get_avg_im(imlist, fname):
	
	max_w = max(Image.open(im).size[0] for im in imlist)
	max_h = max(Image.open(im).size[1] for im in imlist)
	print 'max w, h: ', max_w, max_h
	N=len(imlist)

	# Create a numpy array of floats to store the average (assume RGB images)
	arr=np.zeros((max_h,max_w,3),np.float)

	# Build up average pixel intensities, casting each image as an array of floats
	for im in imlist:
		print 'working on ' + im
		old_im = Image.open(im)
		old_size = old_im.size
		new_size = (max_w, max_h)

		new_im = Image.new("RGB", new_size) 
		new_im.paste(old_im, ((new_size[0]-old_size[0])/2,
							  (new_size[1]-old_size[1])/2))
		imarr=np.array(new_im,dtype=np.float)
		arr=arr+imarr/N
	# Round values in array and cast as 8-bit integer
	arr=np.array(np.round(arr),dtype=np.uint8)

	# Generate, save and preview final image
	out=Image.fromarray(arr,mode="RGB")
	out.save(fname+"-average.png")
	print 'saved average image '

def get_average_color(im_fname, NUM_CLUSTERS=5, resize_w=150):
	try:
		print 'reading image ' + im_fname
		im = Image.open(im_fname)
		w, h = im.size
		ratio = w*1.0/500
		new_w = int(round(w/ratio))
		new_h = int(round(h/ratio))
		im = im.resize((new_w, new_h))     
		ar = scipy.misc.fromimage(im)
		shape = ar.shape
		if shape[-1] == 1:
			ar = to_rgb3b(im)
			shape = ar.shape
		ar = ar.reshape(scipy.product(shape[:2]), shape[2]).astype('float')
		codes, dist = scipy.cluster.vq.kmeans(ar, NUM_CLUSTERS)
		vecs, dist = scipy.cluster.vq.vq(ar, codes)         # assign codes
		counts, bins = scipy.histogram(vecs, len(codes))    # count occurrences
		index_max = scipy.argmax(counts)                    # find most frequent
		peak = codes[index_max]
		peak = peak.astype(int)
		colour = ''.join(chr(c) for c in peak).encode('hex')[0:6]
		print 'most frequent is %s (#%s)' % (peak, colour)
		return colour
	except IndexError as e:
		print e
		return 'ffffff'

def draw_average_colors(imlist, fname, DRAW=False):
	hexes = []
	for im in imlist:
		hexcode = get_average_color(im)
		hexes.append(hexcode)
		if DRAW:
			fig1 = plt.figure(figsize=(1,1))
			ax1 = fig1.add_subplot(111, aspect='equal')
			ax1.add_patch(
				patches.Rectangle(
					(0, 0),   # (x,y)
					1,          # width
					1,          # height
					facecolor = '#'+str(hexcode),
					edgecolor = "none"
				)
			)
			plt.axis('off')
			plt.show()
	totalsquares = len(hexes)
	side = int(np.ceil(np.sqrt(totalsquares)))
	fig = plt.figure(figsize=(side,side))
	ax1 = fig.add_subplot(111, aspect='equal')
	i = 0
	j = 0
	patchlen = 1.0/side
	print hexes
	for hexcolor in hexes:
		ax1.add_patch(
			patches.Rectangle(
				(i, j),     # (x,y)
				patchlen,          # width
				patchlen,          # height
				facecolor = '#'+str(hexcolor),
				edgecolor = "none"
			)
		)
		i += patchlen
		if i >= 1:
			i = 0
			j += patchlen
	plt.axis('off')
	plt.savefig(fname+'-colorblocks.png', bbox ='tight')
	print "saved as "+fname+'-colorblocks.png'

def get_folder_clusters(imlist):
	n = len(imlist)
	#extract feature vector for each image
	features = np.zeros((n,3))
	for i in range(n):
		print 'working on ', imlist[i]
		im = np.array(Image.open(imlist[i]))
		if im.shape[-1] > 3:
			im = to_rgb3b(im)
		R = np.mean(im[:,:,0].flatten())
		G = np.mean(im[:,:,1].flatten())
		B = np.mean(im[:,:,2].flatten())
		features[i] = np.array([R,G,B])
	tree = hcluster.hcluster(features)
	print 'finished generating image clusters'
	return tree 

def draw_clusters(tree, imlist, fname):
	drawdendrogram(tree, imlist,fname+'-dendrogram.png')
	print 'saved cluster dendrogram'
	total_width = 0
	max_height = 0
	indices = get_cluster_elements(tree)
	for i in indices:
		nodeim = Image.open(imlist[i])
		ns = nodeim.size
		total_width += ns[0]
		if max_height < ns[1]:
			max_height = ns[1]

	img=Image.new('RGB',(total_width,max_height),(255,255,255))
	w_run = 0

	for i in indices:
		print imlist[i]
		nodeim = Image.open(imlist[i])
		ns = nodeim.size
		img.paste(nodeim, (w_run, 0))
		w_run += ns[0]

	img.save(fname+'-clustermontage.png', quality=100)
	print 'saved cluster montage'
		
def __main__():
	im_dir = ""
	while (im_dir == ""):
		im_dir = raw_input("What folder has the images?")
	fname = ""
	while (fname == ""):
		fname = raw_input("What fandom for the output filenames?")
	imlist = get_im_list(im_dir)
	print 'got the list of images'
	# get_avg_im(imlist, fname)
	draw_average_colors(imlist, fname)
	tree = get_folder_clusters(imlist)
	draw_clusters(tree, imlist, fname)
	print 'all done!'

__main__()
