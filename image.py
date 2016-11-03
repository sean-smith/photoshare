from PIL import Image
from cStringIO import StringIO
from resizeimage import resizeimage
import os, base64

def resize(img, x,y):
	image_string = StringIO(img.decode('base64'))
	with Image.open(image_string) as image:
		if image.size[0] > 200 and image.size[1] > 200:
			cover = resizeimage.resize_cover(image, [x,y])
			return base64.standard_b64encode(cover)
		else:
			return img

