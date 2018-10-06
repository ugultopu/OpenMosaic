import json
import numpy
import cv2
import math
import sys
import features
import random
from science_birds_level_constructor import construct_level
from collections import deque

INDEX_PATH = "./index/"
IMAGES_TO_USE_PER_IMAGE = 5

def readIndex():
    json_data = open(INDEX_PATH + "histogram.index").read()
    return json.loads(json_data)

def preparInputImage(path, tileSize):
    i = cv2.imread(path)
    (h, w, _) = i.shape
    i = cv2.resize(i, (w / tileSize * tileSize, h / tileSize * tileSize))
    return i

def preparePatch(path, tileSize):
    image = cv2.imread(INDEX_PATH + path)
    image = cv2.resize(image, (tileSize, tileSize))
    return image

def calcDistance(fts1, fts2, vectors):
    distance = 0
    for vec in vectors:
        distance += math.pow(fts1[vec] - fts2[vec], 2)
    return math.sqrt(distance)

def getIndexImage(fts, index, vectors):
    minDistance = sys.maxint
    bestImages = deque([])
    for item in index:
        distance = calcDistance(fts, item, vectors)
        if distance < minDistance:
            minDistance = distance
            bestImages.append(item["file"])
            if len(bestImages) > IMAGES_TO_USE_PER_IMAGE:
                bestImages.popleft();

    return random.choice(bestImages)

def processLine(i, w, index, inputImage, tileSize, channels, mosaic_tiles):
    mosaic_tiles.append([])
    for j in range(0, w / tileSize):
        roi = inputImage[i * tileSize:(i + 1) * tileSize, j * tileSize:(j + 1) * tileSize]
        fts = features.extractFeature(roi)
        index_image = getIndexImage(fts, index, channels)
        mosaic_tiles[-1].append(index_image)
        patch = preparePatch(index_image, tileSize)
        inputImage[i * tileSize:(i + 1) * tileSize, j * tileSize:(j + 1) * tileSize] = patch
        cv2.imshow("Progress", inputImage)
        cv2.waitKey(1)


def main():
    mosaic_tiles = []

    if len(sys.argv) < 5:
        print "Error, invalid arguments!"
        print "Call with " + sys.argv[0] + " input.jpg [tile-size] [rgb|hsv] output.jpg"
        sys.exit(1)

    #parse commandline arguments
    inputImagePath = str(sys.argv[1])
    tileSize = int(sys.argv[2])
    channels = list(str(sys.argv[3]))

    #read index + input image
    index = readIndex()
    inputImage = preparInputImage(inputImagePath, tileSize)

    (h, w, _) = inputImage.shape

    inputImage = cv2.resize(inputImage, (w / tileSize * tileSize, h / tileSize * tileSize))

    print inputImage.shape

    for i in range(0, h / tileSize):
        processLine(i, w, index, inputImage, tileSize, channels, mosaic_tiles)

    print "Finished processing of image"

    construct_level(mosaic_tiles)

    cv2.imwrite(str(sys.argv[4]), inputImage)


if __name__ == "__main__":
    main()
