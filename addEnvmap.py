from io import StringIO
import numpy as np

import mitsuba
from mitsuba.core import *
from mitsuba.render import SceneHandler

def addEnvmap(scene,config, pmgr):
	
	envmap = pmgr.create({
		'type' : 'envmap',
		'filename' : str(config["envmap"])
		})
			
	scene.addChild(envmap)
		
	return(scene)