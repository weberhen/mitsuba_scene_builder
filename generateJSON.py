import json
import random
import argparse

from vpls import loadVPLS, findRangeVPLS

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

def main():
	parser = argparse.ArgumentParser(description='Generate json configuration files for mitsuba')
	parser.add_argument('-v', '--vpls_location', help="<location to>data_vpls.txt", required=True)
	
	args = parser.parse_args()

	data = initializeData()
	
	# variables 
	nScenes = 2
	fovMin = 40
	fovMax = 90

	# generate random field of views
	fovs = random.sample(xrange(fovMin,fovMax), nScenes)

	data['nScenes'] = nScenes

	vpls = loadVPLS(args.vpls_location)
	
	# find the range where the virtual points are in x-z coordinates
	range = findRangeVPLS(vpls)

	
	data['vpls'] = 'data_vpls.txt'
	data['sensor']['type'] = 'perspective'
	data['sensor']['transform'] = 'toWorld'
	data['sensor']['lookAt']['origin'][0] = [0,0,-3]
	data['sensor']['lookAt']['origin'][1] = [0,0,-4]
	data['sensor']['lookAt']['target'][0] = [0,0,0]
	data['sensor']['lookAt']['target'][1] = [0,0,0]
	data['sensor']['lookAt']['up'][0] = [0,1,0]
	data['sensor']['lookAt']['up'][1] = [0,1,0]
	data['sensor']['fov'][0] = 90
	data['sensor']['fov'][1] = 40
	data['sampler']['type'] = 'stratified'
	data['sensor']['sampleCount'] = 4
	data['film']['type'] = 'hdrfilm'
	data['film']['width'] = 512
	data['film']['height'] = 512
	
	with open('data.json', 'w') as outfile:
		json.dump(data, outfile, sort_keys=True, indent=4, separators=(',', ': '))

if __name__ == "__main__":
    main()