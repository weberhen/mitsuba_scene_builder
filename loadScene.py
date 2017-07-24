import mitsuba
from mitsuba.core import *
from mitsuba.render import SceneHandler

def loadScene(filename, vpls_location):
	# Get a reference to the thread's file resolver
	fileResolver = Thread.getThread().getFileResolver()

	# Optional: supply parameters that can be accessed
	# by the scene (e.g. as $myParameter)
	paramMap = StringMap()
	
	paramMap['mesh'] = str(vpls_location[:-13] + 'mesh.ply')
	paramMap['envmap'] = str(vpls_location[:-14] + '.exr')

	# Load the scene from an XML file
	scene = SceneHandler.loadScene(fileResolver.resolve(filename), paramMap)

	return(scene)