from mitsuba.core import *
from mitsuba.render import RenderQueue, RenderJob, SceneHandler, Scene
import multiprocessing

def createSensor(pmgr, config, index):
	# Create a sensor, film & sample generator
	newSensor = pmgr.create({
		'type' : str(config["sensor"]["type"]),
		'toWorld' : Transform.lookAt(
			Point(config["sensor"]["transform"]["lookat"]["origin"][index][0], 
				  config["sensor"]["transform"]["lookat"]["origin"][index][1], 
				  config["sensor"]["transform"]["lookat"]["origin"][index][2]),
			Point(config["sensor"]["transform"]["lookat"]["target"][index][0], 
				  config["sensor"]["transform"]["lookat"]["target"][index][1], 
				  config["sensor"]["transform"]["lookat"]["target"][index][2]),
			Vector(config["sensor"]["transform"]["lookat"]["up"][index][0], 
				   config["sensor"]["transform"]["lookat"]["up"][index][1], 
				   config["sensor"]["transform"]["lookat"]["up"][index][2])
		),
		'fov' : float(config["sensor"]["fov"][index]),
		'film' : {
			'type' : str(config["sensor"]["film"]["type"]),
			'width' : int(config["sensor"]["film"]["width"]),
			'height' : int(config["sensor"]["film"]["height"]),
			'banner' : False,
			# 'cropOffsetX' : 0,
			# 'cropOffsetY' : 25,
			# 'cropWidth' : 25,
			# 'cropHeight' : 25,
			#'label[10, 10]' : str(str(config["sampler_type"]) + " " + str(config["sampler_sampleCount"]))
		},
		'sampler' : {
		 	'type' : str(config["sensor"]["sampler"]["type"]),
		 	'sampleCount' : int(config["sensor"]["sampler"]["sampleCount"])
		},
	})
	return newSensor

def modifyScene(scene, index, config, pmgr):

	#for i in range(number_of_renderings):
	destination = 'result_%03i' % index
	
	# Create a shallow copy of the scene so that the queue can tell apart the two
	# rendering processes. This takes almost no extra memory
	newScene = Scene(scene)

	# Create a sensor, film & sample generator
	newSensor = createSensor(pmgr, config, index)	
	newSensor.configure()
	newScene.addSensor(newSensor)
	newScene.setSensor(newSensor)
	newScene.setDestinationFile(destination)	
	
	newScene.configure()

	return(newScene)