from io import StringIO
import numpy as np
import multiprocessing
import cv2

import mitsuba
from mitsuba.core import *
from mitsuba.render import SceneHandler, Scene, RenderQueue, RenderJob


def loadVPLS(fname):
    ''' load the file using std open'''
    f = open(fname,'r')

    data = []
    for line in f.readlines():
        data.append(line.replace('\n','').split(' '))

    f.close()

    return data

def addVPLS(scene,config, pmgr, vpls):
		
	nVPLS = int(vpls[0][1])*4
	
	for i in xrange(1, nVPLS, 4):
		# Add one virtual point light
		areapointlight = pmgr.create({
			'type' : 'sphere',
			'center' : Point(float(vpls[i][1]),float(vpls[i][2]),float(vpls[i][3])),
			'radius' : .02,
			'emitter': pmgr.create({
						'type' : 'area',
						'radiance' : Spectrum([float(vpls[i+2][1]),float(vpls[i+2][2]),float(vpls[i+2][3])]),
						'samplingWeight': float(vpls[i+3][1])
						})
		})
				
		scene.addChild(vpls[i][0],areapointlight)
		
	return(scene)

def renderVPLS(vpls, cam, target):
	''' render VPLS having the camera at looking at the desired target the scene. The result will 
	be an image that will be used to define the 3D space where the camera and
	object can be placed in the environment. Target can be either be 'roof' or 'floor' '''

	pmgr = PluginManager.getInstance()
	scheduler = Scheduler.getInstance()

	if(target == 'roof'):
		target_height = 2.4
	else:
		target_height = 0

	# Start up the scheduling system with one worker per local core
	for i in range(0, multiprocessing.cpu_count()):
		scheduler.registerWorker(LocalWorker(i, 'wrk%i' % i))
	scheduler.start()

	# Create a queue for tracking render jobs
	queue = RenderQueue()
	
	nVPLS = int(vpls[0][1])*4
	
	scene = Scene()

	for i in xrange(1, nVPLS, 4):
		if(float(vpls[i][2]) == target_height):
			scene.addChild(pmgr.create({
				'type' : 'sphere',
				'center' : Point(float(vpls[i][1]),float(vpls[i][2]),float(vpls[i][3])),
				'radius' : 1.0,
				'emitter': pmgr.create({
						'type' : 'area',
						'radiance' : Spectrum(10.),
						})
				}))

	scene.addChild(pmgr.create({
		'type' : 'perspective',
		'toWorld' : Transform.lookAt(
			Point(cam.origin[0], cam.origin[1], cam.origin[2]),
			Point(cam.target[0], cam.target[1], cam.target[2]),
			Vector(cam.up[0], cam.up[1], cam.up[2])
		),
		'fov' : cam.fov,
		'film' : {
			'type' : 'ldrfilm',
			'width' : cam.width,
			'height' : cam.height,
			'banner' : False,
		},
		'sampler' : {
		 	'type' : 'halton',
		 	'sampleCount' : 1
		},
	}))

	scene.addChild(pmgr.create({
		'type' : 'direct'
		}))
	scene.configure()

	if(target == 'roof'):
		filename = 'renderVPLSRoof'
	else:
		filename = 'renderVPLSFloor'
	
	scene.setDestinationFile(filename)

	# Create a render job and insert it into the queue
	job = RenderJob('myRenderJob', scene, queue)
	job.start()

	# Wait for all jobs to finish and release resources
	queue.waitLeft(0)
	queue.join()

	scheduler.stop()


