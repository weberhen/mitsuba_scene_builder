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
	origin = [0,8,0]
	target = [0,0,0]
	up = [1,0,0]


# { 
#   "nScenes" : 2,
#   "vpls" : "data_vpls.txt",
#   "sensor" : {
#     "type" : "perspective",
#     "transform" : {
#       "name" : "toWorld",
#       "lookat" : {
#         "origin" : [
#           [0,0,-3],
#           [0,0,-4]
#         ],
#         "target" : [
#           [0,0,0],
#           [0,0,0]
#         ],
#         "up" : [
#           [0,1,0],
#           [0,1,0]
#         ]
#       }             
#     },
#     "fov" : [
#       90,
#       40
#     ],
#     "sampler" : {
#       "type" : "stratified",
#       "sampleCount" : 4
#     },
#     "film" : {
#       "type" : "hdrfilm",
#       "width" : 512,
#       "height" : 512
#     }
#   }
# }

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

def generateCameraPosition(rangeCamera):

	cam = Camera()

	rangeCameraValues = cv2.findNonZero(rangeCamera)

	nPossibleCameraPositions, height = rangeCameraValues.shape[:2]

	randomIndex = random.randint(0, nPossibleCameraPositions - 1)

	#generate a random (x,z) coordinate to form the vector where the camera will be
	z,x = rangeCameraValues[randomIndex].squeeze()

	#generate a random (y) coordinate to form the vector where the camera will be
	y = random.uniform(0, 2.4) 
	
	#transform to the camera coordinate system
	print(x)
	print(y)
	print(z)
	img = np.zeros(rangeCamera.shape, np.uint8)	
	img[(x,z)] = 255
	cv2.imshow('camPose',img)
	print(cam.origin[1]*(float(cam.width/2-x)/(cam.width/2)))
	print(y)
	print(cam.origin[1]*(float(z-cam.height/2)/(cam.height/2)))

	#TODO go from screen coordinate to camera coordinates and get a value in the vector (x,y,z)

	camPose = [x,y,z]

	return camPose



def generatePoses(rangeVPLS, nScenes, distMin, distMax):

	# get the possible locations the camera and 3D object can have during the
	# rendering
	rangeObjectValues = cv2.findNonZero(rangeVPLS)

	width, height = rangeObjectValues.shape[:2]

	stepSize = width / nScenes

	assert stepSize > 1, 'there are not enough poses for this scene'

	for i in range(1,width,stepSize):
		radius = random.randint(distMin, distMax)
		
		objPose = rangeObjectValues[i][0]
		
		img = np.zeros(rangeVPLS.shape, np.uint8)	
		

		rangeCamera = getRegionAroundPoint(rangeVPLS, objPose, radius, distMin)
		
		camPose = generateCameraPosition(rangeCamera)
		img[(objPose[1],objPose[0])] = 255
		#img[(camPose[1],camPose[0])] = 100
		rangeVPLS[(objPose[1],objPose[0])] = 0
		rangeVPLS[64,64] = 0
		
		cv2.imwrite('objLoc.png',img)
		cv2.imshow('objLoc.png',img)
		cv2.imshow('rangeVPLS',rangeVPLS)
		cv2.imwrite('rangeCamera.png',rangeCamera)
		cv2.waitKey()


def generateFOVs(nScenes, fovMin, fovMax):
	
	fovs = [random.randint(fovMin, fovMax) for x in xrange(nScenes)]

	return fovs

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
	
	#renderVPLSFromTop(vpls, cam)

	# read the output from the renderer
	renderVPLSFromTopImg = cv2.imread('renderVPLSFromTop.png',0)

	kernel = np.ones((15,15),np.uint8)

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
	
	''' variables  '''

	numberOfScenes = 1
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

	data['nScenes'] = numberOfScenes

	#vpls = loadVPLS(args.vpls_location)
	vpls = {}

	# find the range where the virtual points are in x-z coordinates
	rangeVPLS = findRangeVPLS(vpls, radius)

	generatePoses(rangeVPLS, 
				  numberOfScenes, 
				  distBetweenCameraObjectMin, 
				  distBetweenCameraObjectMax
				  )
	
	data['vpls'] = 'example/data_vpls.txt'
	data['sensor']['type'] = 'perspective'
	data['sensor']['transform'] = 'toWorld'
	data['sensor']['lookAt']['origin'] = [	[-.3,1.2,0], 
											[-2,1.2,0]	]
	data['sensor']['lookAt']['target'] = [	[0,1.2,0], 
											[0,1.2,0]	]
	data['sensor']['lookAt']['up'] = [	[0,1,0], 
										[0,1,0]	]
	data['sensor']['fov'] = [90,40]
	data['sampler']['type'] = 'stratified'
	data['sampler']['sampleCount'] = 8192
	data['film']['type'] = 'hdrfilm'
	data['film']['width'] = 256
	data['film']['height'] = 256
	
	with open('example/config2.json', 'w') as outfile:
		json.dump(data, outfile, sort_keys=True, indent=4, separators=(',', ': '))

if __name__ == "__main__":
    main()