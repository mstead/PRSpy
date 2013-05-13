import os
import gtk

IMAGE_FILE_PATH = os.path.join(os.path.dirname(__file__), "img")

LOADING_IMAGE = gtk.gdk.PixbufAnimation(os.path.join(IMAGE_FILE_PATH,"loading.gif"))