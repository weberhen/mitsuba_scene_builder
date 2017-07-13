import sys
import argparse
import json

from mitsuba.core import *
from mitsuba.render import RenderQueue, RenderJob
import multiprocessing

from loadScene import loadScene
from modifyScene import modifyScene
from renderScene import renderScene
from addVPLS import addVPLS
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

	#load basic scene
	scene = loadScene(args.basicSceneFile)

	#add VPLS
	scene = addVPLS(scene,config, pmgr)

	#scene = addEnvmap(scene,config,pmgr)

	sceneResID = scheduler.registerResource(scene)
	
	scene.initialize()

	for i in range(config["nScenes"]):
		mscene = modifyScene(scene, i, config, pmgr)
		renderScene(mscene, i, sceneResID)