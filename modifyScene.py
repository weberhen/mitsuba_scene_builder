from mitsuba.core import *
from mitsuba.render import RenderQueue, RenderJob, SceneHandler, Scene
import multiprocessing

def createSensor(pmgr, config, index):
	# Create a sensor, film & sample generator
	newSensor = pmgr.create({
		'type' : str(config["camera"]),
		'toWorld' : Transform.lookAt(
			Point(config["cameraLookat"][index][0], config["cameraLookat"][index][1], config["cameraLookat"][index][2]),
			Point(config["cameraLookat"][index][3], config["cameraLookat"][index][4], config["cameraLookat"][index][5]),
			Vector(config["cameraLookat"][index][6], config["cameraLookat"][index][7], config["cameraLookat"][index][8])
		),
		'fov' : float(config["fov"][index]),
		'film' : {
			'type' : 'hdrfilm',
			'width' : int(config["width"]),
			'height' : int(config["height"]),
			'banner' : False,
			'cropOffsetX' : 0,
			'cropOffsetY' : 25,
			'cropWidth' : 25,
			'cropHeight' : 25,
			#'label[10, 10]' : str(str(config["sampler_type"]) + " " + str(config["sampler_sampleCount"]))
		},
		'sampler' : {
		 	'type' : str(config["sampler_type"]),
		 	'sampleCount' : int(config["sampler_sampleCount"])
		},
	})
	return newSensor

def modifyScene(scene, index, config, pmgr):

	#for i in range(number_of_renderings):
	destination = 'result_%03i' % index
	
	# Create a shallow copy of the scene so that the queue can tell apart the two
	# rendering processes. This takes almost no extra memory
	newScene = Scene(scene)
	
	# # # Create a sensor, film & sample generator
	# newSensor = createSensor(pmgr, config, index)

	# newSensor.configure()
	# newScene.addSensor(newSensor)
	# newScene.setSensor(newSensor)
	# newScene.setSampler(scene.getSampler())
	newScene.setDestinationFile(destination)
	newScene.configure()

	return(newScene)