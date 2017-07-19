import json
import random
import argparse
import cv2
import numpy as np

from vpls import loadVPLS, renderVPLSFromTop

class Camera:
	fov = 90.
	width = 128
	height = 128
	origin = [0.,8.,0.]
	target = [0.,0.,0.]
	up = [1.,0.,0.]


def initializeData():
	data = {}
	data['sensor'] = {}
	data['sensor']['lookAt'] = {}
	data['sensor']['lookAt']['origin'] = {}
	data['sensor']['lookAt']['target'] = {}
	data['sensor']['lookAt']['up'] = {}
	data['sensor']['fov'] = {}
	data['sampler'] = {}
	data['film'] = {}

	return data

def imageToWorldCoordinateSystem(cam, points):
	''' take the 2D coordinates in the image frame and convert to world coords'''
	points = points.astype(float)

	for i in range(0,(points.shape[0])):
		x = points[i][1]
		z = points[i][0]
		x = cam.origin[1] * (float(cam.width/2-x)/(cam.width/2))
		z = cam.origin[1] * (float(z-cam.height/2)/(cam.height/2))
		points[i][1] = x
		points[i][0] = z

	return points

def generateObjectPositions(rangeVPLS, numberOfScenes):

	cam = Camera()

	# get the possible locations the 3D object can have during the
	# rendering
	rangeObjectValues = cv2.findNonZero(rangeVPLS)

	# get all 2D positions (x,z) where the object could be placed in the scene
	nPossibleObjectPositions, height = rangeObjectValues.shape[:2]

	# we want to generante #numberOfScenes positions for the object, so we define a
	# stepsize to take one 2D position from the possible locations and skip the 
	# next #stepsize other 2D position candidates in the array
	stepSize = nPossibleObjectPositions / numberOfScenes

	# make sure we have enough 2D positions
	assert stepSize > 1, 'there are not enough poses for this scene'
	
	# get the indexes of the 2D positions we will pick
	ind_pos = np.linspace (0,nPossibleObjectPositions-1,num=numberOfScenes).astype(int)
	
	# copy the selected 2D positions to the output variable
	objPositions = rangeObjectValues[ind_pos].squeeze()
	

	# since we were until now working in the image frame, we need to go back to
	# the world coordinate systemm
	objPositionsWorldFrame = imageToWorldCoordinateSystem(cam,objPositions)
	
	y = np.random.uniform(.5, 1.9, numberOfScenes)

	objPositions = np.empty(shape=(numberOfScenes, 3), dtype=float)
	
	# organize the (x,y,z) coordinates to return them 
	objPositions[:,0] = objPositionsWorldFrame[:,1] #x
	objPositions[:,1] = y #y 
	objPositions[:,2] = objPositionsWorldFrame[:,0] #z

	return objPositions 


def generateFOVs(numberOfScenes, fovMin, fovMax):
	
	# a field of view is generated randomly between the given interval of 
	# fovmin and fovmax
	fovs = [random.randint(fovMin, fovMax) for x in xrange(numberOfScenes)]

	return fovs

def generateCameraTargets(numberOfScenes):

	target = np.empty(shape=(numberOfScenes, 3), dtype=float)
	target[:,0] = [random.uniform(0,1) for x in xrange(numberOfScenes)]
	target[:,1] = [random.uniform(0,1) for x in xrange(numberOfScenes)]
	target[:,2] = [random.uniform(0,1) for x in xrange(numberOfScenes)]

	return target

def getRegionAroundPoint(img, point, radius, thickness):

	circle_img = np.zeros(img.shape, np.uint8)
	
	# create an image with a circle around the point
	cv2.circle(circle_img, (point[0],point[1]), radius, 255, thickness)

	# get the intersection between the blob in the input image and the circle
	regionAroundPoint = cv2.bitwise_and(img,circle_img)

	return regionAroundPoint

def findRangeVPLS(vpls, radius):
	'''outputs all possible 2D locations the camera and object can have
	in the scene'''

	cam = Camera()
	
	renderVPLSFromTop(vpls, cam)

	# read the output from the renderer
	renderVPLSFromTopImg = cv2.imread('renderVPLSFromTop.png',0)

	kernel = np.ones((25,25),np.uint8)

	width, height = renderVPLSFromTopImg.shape[:2]
	
	# center of the image, which corresponds to the origin in the camera 
	# coordinate system
	point = (width/2, height/2)

	# erode the rendered image to be sure the object will be rendered inside 
	# the 3D environment
	erodedRenderVPLSFromTopImg = cv2.erode(renderVPLSFromTopImg, kernel, iterations = 1)

	rangeVPLSImg = getRegionAroundPoint(erodedRenderVPLSFromTopImg, point, radius, -1)	
	
	return rangeVPLSImg


def main():
	parser = argparse.ArgumentParser(description='Generate json configuration files for mitsuba')
	parser.add_argument('-v', '--vpls_location', help="<location to>data_vpls.txt", required=True)
	
	args = parser.parse_args()

	data = initializeData()
	
	numberOfScenes = 100
	# minimum and maximum field of view
	fovMin = 40
	fovMax = 90
	# minimum and maximum distance in pixels between camera and object
	distBetweenCameraObjectMin = 5 
	distBetweenCameraObjectMax = 20
	# radius around the camera location in pixels where an object can be placed
	radius = 30

	# generate random field of views
	fovs = generateFOVs(numberOfScenes, fovMin, fovMax)

	camTarget = generateCameraTargets(numberOfScenes)

	data['numberOfScenes'] = numberOfScenes

	vpls = loadVPLS(args.vpls_location)
	#vpls = {}

	# find the range where the virtual points are in x-z coordinates
	rangeVPLS = findRangeVPLS(vpls, radius)

	objPositions = generateObjectPositions(rangeVPLS, numberOfScenes)

	data['vpls'] = 'example/data_vpls.txt'
	data['sensor']['type'] = 'spherical'
	data['sensor']['transform'] = 'toWorld'
	# TODO render with the camera looking at the object
	data['sensor']['lookAt']['origin'] = objPositions.tolist() 
	data['sensor']['lookAt']['target'] = camTarget.tolist()
	data['sensor']['lookAt']['up'] = np.tile([0,1,0],(numberOfScenes,1)).tolist()
	data['sensor']['fov'] = fovs
	data['sampler']['type'] = 'stratified'
	data['sampler']['sampleCount'] = 1024
	data['film']['type'] = 'ldrfilm'
	data['film']['width'] = 256
	data['film']['height'] = 128
	
	with open('example/config2.json', 'w') as outfile:
		json.dump(data, outfile, sort_keys=True, indent=4, separators=(',', ': '))

if __name__ == "__main__":
    main()