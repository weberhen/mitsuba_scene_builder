import mitsuba
from mitsuba.core import *
from mitsuba.render import SceneHandler

def loadScene(filename):
	# Get a reference to the thread's file resolver
	fileResolver = Thread.getThread().getFileResolver()

	# Register any searchs path needed to load scene resources (optional)
	fileResolver.appendPath('<path to scene directory>')

	# Load the scene from an XML file
	scene = SceneHandler.loadScene(fileResolver.resolve(filename))#, paramMap)

	return(scene)