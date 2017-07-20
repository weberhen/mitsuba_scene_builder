import sys
import argparse
import json

from mitsuba.core import *
from mitsuba.render import RenderQueue, RenderJob, SceneHandler, Scene
import multiprocessing

from loadScene import loadScene
from modifyScene import modifyScene
from renderScene import renderScene
from vpls import loadVPLS, addVPLS
from addEnvmap import addEnvmap

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Generate mitsuba scene files')
	parser.add_argument('-b', '--basicSceneFile', help="*basicSceneFile*.xml", required=True)
	parser.add_argument('-c', '--configFile', help="*configFile*.json", required=True)
	args = parser.parse_args()

	pmgr = PluginManager.getInstance()

	scheduler = Scheduler.getInstance()

	# Start up the scheduling system with one worker per local core
	for i in range(0, multiprocessing.cpu_count()):
		scheduler.registerWorker(LocalWorker(i, 'wrk%i' % i))
	scheduler.start()

	#load json with desired configuration
	with open(args.configFile) as configFile:    
		config = json.load(configFile)

	scene = loadScene(args.basicSceneFile,config['vpls'])

	if 'vpls' in config:
		vpls = loadVPLS(config["vpls"])
		scene = addVPLS(scene,config, pmgr, vpls)

	sceneResID = scheduler.registerResource(scene)
	
	scene.initialize()

	destinationFolder = args.configFile[:-11] 

	for i in range(config["numberOfScenes"]):
	 	mscene = modifyScene(scene, i, config, pmgr, destinationFolder)
		renderScene(mscene, i, sceneResID)