import json
import random
import argparse
import cv2
import numpy as np
import os
from collections import Counter

from vpls import loadVPLS, renderVPLS


class Camera:
    fov = 90.
    width = 128
    height = 128
    origin = [0., 8, 0.]
    target = [0., 0., 0.]
    up = [1., 0., 0.]


class Scene:
    HeightFloor = 0
    HeightRoof = 2.4
    referenceStructure = 'roof'

    def get_distance_to_camera(self):
        cam = Camera()
        if (self.referenceStructure == 'roof'):
            return cam.origin[1] - self.HeightRoof
        else:
            return cam.origin[1] - self.HeightFloor


def initialize_data():
    data = {'sensor': {}}
    data['sensor']['lookAt'] = {}
    data['sensor']['lookAt']['origin'] = {}
    data['sensor']['lookAt']['target'] = {}
    data['sensor']['lookAt']['up'] = {}
    data['sensor']['fov'] = {}
    data['sampler'] = {}
    data['film'] = {}

    return data


def image_to_world_coord_system(cam, points, scene):
    # take the 2D coordinates in the image frame and convert to world coords
    points = points.astype(float)

    for i in range(0, (points.shape[0])):
        x = points[i][1]
        z = points[i][0]
        x = scene.get_distance_to_camera() * (float(cam.width / 2 - x) / (cam.width / 2))
        z = scene.get_distance_to_camera() * (float(z - cam.height / 2) / (cam.height / 2))
        points[i][1] = x
        points[i][0] = z

    return points


def generate_object_positions(rangeVPLS, numberOfScenes, scene):
    cam = Camera()

    # get the possible locations the 3D object can have during the
    # rendering
    rangeObjectValues = cv2.findNonZero(rangeVPLS)

    # get all 2D positions (x,z) where the object could be placed in the scene
    nPossibleObjectPositions, height = rangeObjectValues.shape[:2]

    # get the indexes of the 2D positions we will pick
    ind_pos = np.linspace(0, nPossibleObjectPositions - 1, num=numberOfScenes).astype(int)

    # copy the selected 2D positions to the output variable
    objPositions = rangeObjectValues[ind_pos].squeeze()

    # since we were until now working in the image frame, we need to go back to
    # the world coordinate system
    objPositionsWorldFrame = image_to_world_coord_system(cam, objPositions, scene)

    # render only close to the floor if the scene was modeling from the floor, or
    # render close to the roof otherwise
    if (scene.referenceStructure == 'floor'):
        y = np.random.uniform(scene.HeightFloor + .3, scene.HeightFloor + 1.4, numberOfScenes)
    else:
        y = np.random.uniform(scene.HeightRoof - 1, scene.HeightRoof - .2, numberOfScenes)

    objPositions = np.empty(shape=(numberOfScenes, 3), dtype=float)

    # organize the (x,y,z) coordinates to return them
    objPositions[:, 0] = objPositionsWorldFrame[:, 1]  # x
    objPositions[:, 1] = y  # y
    objPositions[:, 2] = objPositionsWorldFrame[:, 0]  # z

    return objPositions


def generateFOVs(numberOfScenes, fovMin, fovMax):
    # a field of view is generated randomly between the given interval of
    # fovmin and fovmax
    fovs = [random.randint(fovMin, fovMax) for x in xrange(numberOfScenes)]

    return fovs


def generateCameraTargets(numberOfScenes):
    target = np.empty(shape=(numberOfScenes, 3), dtype=float)
    target[:, 0] = [random.uniform(0, 1) for x in xrange(numberOfScenes)]
    target[:, 1] = [random.uniform(0, 1) for x in xrange(numberOfScenes)]
    target[:, 2] = [random.uniform(0, 1) for x in xrange(numberOfScenes)]

    return target


def getRegionAroundPoint(img, point, radius, thickness):
    circle_img = np.zeros(img.shape, np.uint8)

    # create an image with a circle around the point
    cv2.circle(circle_img, (point[0], point[1]), radius, 255, thickness)

    # get the intersection between the blob in the input image and the circle
    regionAroundPoint = cv2.bitwise_and(img, circle_img)

    return regionAroundPoint


def findHeightRoof(vpls):
    # the height of the roof can be different among 3d models since the users that model them
    # used distinct height deppennding on the scene. Therefore we need to find the roof height
    # for each scene
    VPLSCount = int(vpls[0][1]) * 4
    HeightPoints = []

    for i in xrange(1, VPLSCount, 4):
        # exclude height of zero since it corresponds to the floor
        if (float(vpls[i][2]) != 0.):
            HeightPoints.append(vpls[i][2])
    data = Counter(HeightPoints)
    # use the mode to find the most common height value (which corresponds to the roof)
    HeightRoof = float(data.most_common(1)[0][0])
    
    return HeightRoof


def findRangeVPLS(vpls, radius, scene, scene_count):
    '''outputs all possible 2D locations the camera and object can have
    in the scene'''

    camera = Camera()
    scene = Scene()

    scene.HeightRoof = findHeightRoof(vpls)

    renderVPLS(vpls, camera, scene, 'floor')
    renderVPLS(vpls, camera, scene, 'roof')

    # read the output from the renderer
    renderVPLSFloor = cv2.imread('renderVPLSFloor.png', 0)

    # read the output from the renderer
    renderVPLSRoof = cv2.imread('renderVPLSRoof.png', 0)

    # the vpls range must be defined according to the smallest surface in area (roof or floor)
    if (cv2.countNonZero(renderVPLSFloor) > cv2.countNonZero(renderVPLSRoof)):
        # if the roof is smallest in size we set it as the structure to be used to define the range
        scene.referenceStructure = 'roof'
    else:
        scene.referenceStructure = 'floor'

    renderVPLSCombined = cv2.bitwise_and(renderVPLSRoof, renderVPLSFloor)

    kernel_size = 30
    enough_render_positions = False

    while(not enough_render_positions):

        kernel = np.ones((kernel_size, kernel_size), np.uint8)

        width, height = renderVPLSCombined.shape[:2]

        # center of the image, which corresponds to the origin in the camera
	    # coordinate system
        point = (width / 2, height / 2)

        # erode the rendered image to be sure the object will be rendered inside
        # the 3D environment
        erodedRenderVPLSFromTopImg = cv2.erode(renderVPLSCombined, kernel, iterations=1)

        rangeVPLSImg = getRegionAroundPoint(erodedRenderVPLSFromTopImg, point, radius, -1)

        rangeObjectValues = cv2.findNonZero(rangeVPLSImg)

        # get all 2D positions (x,z) where the object could be placed in the scene
        nPossibleObjectPositions, height = rangeObjectValues.shape[:2]

        if(nPossibleObjectPositions >= scene_count ):
            enough_render_positions = True

        kernel_size = kernel_size - 5

    cv2.imwrite('rangeVPLSImg.png', rangeVPLSImg)

    return rangeVPLSImg, scene


def main():
    parser = argparse.ArgumentParser(description='Generate json configuration files for mitsuba')
    parser.add_argument('-v', '--vpls_location', help="<location to>data_vpls.txt", required=True)
    parser.add_argument('-o', '--output_location', help="folder to store the dataset", required=True)
    parser.add_argument('-s', '--skip_existing_render', dest='skip_existing_render', action='store_true')

    args = parser.parse_args()

    data = initialize_data()
    scene = Scene()

    scene_count = 5
    # minimum and maximum field of view
    fov_min = 40
    fov_max = 90
    # radius around the camera location in pixels where an object can be placed
    radius = 20

    # generate random field of views
    fovs = generateFOVs(scene_count, fov_min, fov_max)

    camTarget = generateCameraTargets(scene_count)

    data['numberOfScenes'] = scene_count

    vpls = loadVPLS(args.vpls_location)
    # vpls = {}

    # find the range where the virtual points are in x-z coordinates
    rangeVPLS, scene = findRangeVPLS(vpls, radius, scene, scene_count)

    objPositions = generate_object_positions(rangeVPLS, scene_count, scene)
    camTarget[:, 1] = objPositions[:, 1]

    data['vpls'] = args.vpls_location
    data['sensor']['type'] = 'spherical'
    data['sensor']['transform'] = 'toWorld'
    data['sensor']['lookAt']['origin'] = objPositions.tolist()
    data['sensor']['lookAt']['target'] = camTarget.tolist()
    data['sensor']['lookAt']['up'] = np.tile([0, 1, 0], (scene_count, 1)).tolist()
    data['sensor']['fov'] = fovs
    data['sampler']['type'] = 'stratified'
    data['sampler']['sampleCount'] = 1024
    data['film']['type'] = 'hdrfilm'
    data['film']['width'] = 256
    data['film']['height'] = 128
    data['envmap'] = args.vpls_location[:-14] + '.exr'

    # generate folder to put the data
    data_location = args.output_location
    command = 'mkdir ' + data_location
    
    output = os.popen(command).read()
    if (output == '' or (output != '' and args.skip_existing_render == True)):
        with open(data_location + '/config.json', 'w') as outfile:
            json.dump(data, outfile, sort_keys=True, indent=4, separators= \
                (',', ': '))


if __name__ == "__main__":
    main()
