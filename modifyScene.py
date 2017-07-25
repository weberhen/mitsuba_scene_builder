from mitsuba.core import *
from mitsuba.render import RenderQueue, RenderJob, SceneHandler, Scene
import multiprocessing

from addEnvmap import addEnvmap

def createSensor(pmgr, config, index):
	# Create a sensor, film & sample generator
	newSensor = pmgr.create({
		'type' : str(config["sensor"]["type"]),
		'toWorld' : Transform.lookAt(
			Point(config["sensor"]["lookAt"]["origin"][index][0], 
				  config["sensor"]["lookAt"]["origin"][index][1], 
				  config["sensor"]["lookAt"]["origin"][index][2]),
			Point(config["sensor"]["lookAt"]["target"][index][0], 
				  config["sensor"]["lookAt"]["target"][index][1], 
				  config["sensor"]["lookAt"]["target"][index][2]),
			Vector(config["sensor"]["lookAt"]["up"][index][0], 
				   config["sensor"]["lookAt"]["up"][index][1], 
				   config["sensor"]["lookAt"]["up"][index][2])
		),
		'fov' : float(config["sensor"]["fov"][index]),
		'film' : {
			'type' : str(config["film"]["type"]),
			'width' : int(config["film"]["width"]),
			'height' : int(config["film"]["height"]),
			'banner' : False,
			# 'cropOffsetX' : 0,
			# 'cropOffsetY' : 25,
			# 'cropWidth' : 25,
			# 'cropHeight' : 25,
			#'label[10, 10]' : str(str(config["sampler_type"]) + " " + str(config["sampler_sampleCount"]))
		},
		'sampler' : {
		 	'type' : str(config["sampler"]["type"]),
		 	'sampleCount' : int(config["sampler"]["sampleCount"])
		},
	})
	return newSensor

def modifyScene(scene, index, config, pmgr, destinationFolder):

	#for i in range(number_of_renderings):
	destination = destinationFolder + '-result_%03i' % index
	
	# Create a shallow copy of the scene so that the queue can tell apart the two
	# rendering processes. This takes almost no extra memory
	newScene = Scene(scene)

	# Create a sensor, film & sample generator
	newSensor = createSensor(pmgr, config, index)	
	newSensor.configure()
	newScene.addSensor(newSensor)
	newScene.setSensor(newSensor)
	newScene.setDestinationFile(destination)

	# if 'envmap' in config:
	# 	addEnvmap(newScene, config, pmgr)
	
	newScene.configure()

	return(newScene)