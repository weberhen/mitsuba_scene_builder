from mitsuba.core import *
from mitsuba.render import RenderQueue, RenderJob

def renderScene(scene, index, sceneResID):
	
	# Create a queue for tracking render jobs
	queue = RenderQueue()

	# Create a render job and insert it into the queue. Note how the resource
	# ID of the original scene is provided to avoid sending the full scene
	# contents over the network multiple times.
	job = RenderJob('myRenderJob' + str(index), scene, queue, sceneResID)
	job.start()
	# Wait for all jobs to finish and release resources
	queue.waitLeft(0)
	queue.join()
