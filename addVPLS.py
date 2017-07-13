from io import StringIO
import numpy as np

import mitsuba
from mitsuba.core import *
from mitsuba.render import SceneHandler

def load(fname):
    ''' load the file using std open'''
    f = open(fname,'r')

    data = []
    for line in f.readlines():
        data.append(line.replace('\n','').split(' '))

    f.close()

    return data

def addVPLS(scene,config, pmgr):
	
	vpls = load(config["vpls"])
	
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
