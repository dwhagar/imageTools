#!/usr/bin/env python3

# This script will check all the images in a directory and make sure they 
# are proper images for use as backgrounds.  It will NOT remove non-image
# files.

import sys
from os import path, listdir, remove
from PIL import Image

types = ['jpg', 'jpeg', 'png']
params = {
	'mp': 6,   # Minimum Megapixels
	'ar': 4/3 # Minimum width/height aspect ratio 4:3
}

def readDirectory(p):
	"""
	This reads that from the path (p) and finds files of the specified
	types (t).
	"""
	result = []
	
	fileList = listdir(p)
	for f in fileList:
		f = path.join(p, f)
		if path.isfile(f):
			ext = f[f.find(".") + 1:]
			if ext in types:
				result.append(f)			
	
	return result

def checkImage(i):
	"""
	Checks an image file (i) for the parameters in the params variable. If the
	function detects the image should be deleted, it will return False (bad)
	if the image is ok it will return True (good).
	"""
	result = True
	
	try:
		im = Image.open(i)
	except:
		return result
	
	mp = round((im.width * im.height) / 1000000)
	ar = im.width / im.height
	
	if mp < params['mp'] or ar < params['ar']:
		result = False
	
	im.close()
	return result

def main():
	# Make sure it's there and it's a directory.
	if len(sys.argv) < 2:
		print("You need to specify a directory.")
		return 1
	if not path.exists(sys.argv[1]):
		print("Directory does not exist.")
		return 1
	if not path.isdir(sys.argv[1]):
		print("That is not a directory.")
		return 1
	
	dirPath = sys.argv[1]
	
	fileList = readDirectory(dirPath)
	deleteList = []
	
	if len(fileList) < 1:
		print("Did not find any image files.")
		return 0
		
	print("Found ", str(len(fileList)), " files to look at.")
	
	for f in fileList:
		if not checkImage(f):
			deleteList.append(f)
	
	if len(deleteList) < 1:
		print("Found nothing to delete.")
		return 0
	
	for f in deleteList:
		remove(f)
	
	print("Deleted ", str(len(deleteList)), " files.")
		
	return 0

err = main()

sys.exit(int(err))