import cv2
import numpy as np
import os

def readImageFile(filePath):
    if filePath == None:
        return None
    if not os.path.isfile(filePath):
            return None
    return cv2.imread(filePath, cv2.IMREAD_GRAYSCALE)

def writeImageFile(filePath, image):
    cv2.imwrite(filePath,image)

def getHistogram(image):
    return np.array(cv2.calcHist([image],[0],None,[256],[0,256]))

def isBitonal(hist):
    for i in range(1,254):
        if hist[i] != 0:
            return False
    return True

def BlurScore(image):
    return cv2.Laplacian(image, cv2.CV_64F).var()

def getCannyImage(image):
    # Resize the image, if it's too big
    shape = image.shape
    if len(shape) == 3:
        canny = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        canny = image.copy()

    ratio = 1
    
    #if (shape[0] > 500):
    #    ratio = shape[0] / 500.0
    #    canny = resize(canny, height=500)
    
    # Add a black border
    shape = canny.shape
    h = shape[0]
    w = shape[1]
    base = np.zeros((h+20,w+20),np.uint8)
    base[10:h+10,10:w+10] = canny
    canny = base

    # Get the canny image
    canny = cv2.GaussianBlur(canny,(5,5),0)
    canny = cv2.Canny(canny, 50, 200)
    kernel = np.ones((2,2), np.uint8)
    canny = cv2.dilate(canny, kernel, iterations=3)
    
    return canny, ratio

def getBoundingRectangles(image):
    _, contours, _ = cv2.findContours(image.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) == 0:
        return None, None
    c = sorted(contours, key=cv2.contourArea, reverse=True)[:1][0]
    
    rect = cv2.minAreaRect(c)
    peri = 0.001 * cv2.arcLength(c, True)
    box = cv2.approxPolyDP(c, peri, True)
    
    return rect, box

def getRotationAngle(minAreaRectAngle):
    if minAreaRectAngle <= -90 or minAreaRectAngle >= 0:
        return 0
    if minAreaRectAngle <= -45:
        # Rotated clockwise
        return 90 + minAreaRectAngle
    else:
        return minAreaRectAngle

def isOnRectangle(rect, c):
    if isOnTheLine(rect[0],rect[1],c):
        return True
    if isOnTheLine(rect[1],rect[2],c):
        return True
    if isOnTheLine(rect[2],rect[3],c):
        return True
    return isOnTheLine(rect[3],rect[0],c)

# Returns whether or not the point c is between the points a and b
# and lies on the line defined by then points a and b
def isOnTheLine(a,b,c):
    for i in (0,-1,1):
        d = (c[0]+i,c[1])
        if __isBetween(a,b,d):
            return True
        if (i != 0):
            e = (c[0], c[1]+i)
            if __isBetween(a,b,e):
                return True
    return False

def __isBetween(a, b, c):
    crossproduct = (c[1] - a[1]) * (b[0] - a[0]) - (c[0] - a[0]) * (b[1] - a[1])
    if abs(crossproduct) != 0: return False   # (or != 0 if using integers)

    dotproduct = (c[0] - a[0]) * (b[0] - a[0]) + (c[1] - a[1])*(b[1] - a[1])
    if dotproduct < 0 : return False

    squaredlengthba = (b[0] - a[0])*(b[0] - a[0]) + (b[1] - a[1])*(b[1] - a[1])
    if dotproduct > squaredlengthba: return False

    return True

# Counts the number of spots in the image
def getSpotCount(image):
    return 0

spots =[[[-1,-1,3],[1,1,1],    [1,0,1],    [1,1,1]],
        [[-1,-1,4],[1,1,1,1],  [1,0,0,1],  [1,1,1,1]],
        [[-2,-1,4],[2,1,1,1],  [1,1,0,1],  [1,0,1,1],  [1,1,1,2]],
        [[-1,-1,4],[1,1,1,2],  [1,0,1,1],  [1,0,0,1],  [1,1,1,1]],
        [[-3,-1,5],[2,2,1,1,1],[2,1,1,0,1],[1,1,0,1,1],[1,0,1,1,2],[1,1,1,2,2]],
        [[-1,-1,4],[1,1,1,1],  [1,0,0,1],  [1,0,0,1],  [1,1,1,1]],
        [[-2,-1,5],[2,1,1,1,2],[1,1,0,1,1],[1,0,1,0,1],[1,1,0,1,1],[2,1,1,1,2]],
        [[-2,-1,4],[2,1,1,1],  [1,1,0,1],  [1,0,0,1],  [1,1,0,1],  [2,1,1,1]],
        [[-1,-1,4],[1,1,1,1],  [1,0,0,1],  [1,1,0,1],  [2,1,0,1],  [2,1,1,1]],
        [[-1,-1,5],[1,1,1,1,2],[1,0,0,1,1],[1,1,0,0,1],[2,1,0,1,1],[2,1,1,1,2]],
        [[-2,-1,5],[2,1,1,1,1],[1,1,0,0,1],[1,0,0,1,1],[1,0,1,1,2],[1,1,1,2,2]],
        [[-2,-1,5],[2,1,1,1,2],[1,1,0,1,1],[1,0,0,0,1],[1,1,0,1,1],[2,1,1,1,2]],
        [[-2,-1,5],[2,1,1,1,1],[1,1,0,0,1],[1,0,0,0,1],[1,0,1,1,1],[1,1,1,2,2]],
        [[-2,-1,5],[2,1,1,1,1],[1,1,0,0,1],[1,0,0,0,1],[1,0,1,0,1],[1,1,1,1,1]],
        [[-2,-1,5],[2,1,1,1,1],[1,1,0,0,1],[1,0,0,0,1],[1,0,0,1,1],[1,1,1,1,2]],
        [[-1,-1,5],[1,1,1,1,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,1,0,1],[1,1,1,1,1]]]

# There are
def __isSpot(image,y,x):
    for i in range(0,16):
        spot = spots[i]
        sc = len(spot)
        dx = spot[0][0]
        dy = spot[0][1]
        rc = spot[0][2]
        isSpot = True
        notSpot = False
        for r in range(1,sc):
            sr = spot[i][r]
            for c in (0,rc):
                y1 = y+dy+c
                x1 = x+dx
                if sr[c] == 0:
                    if y1 < 0 or x1 < 0:
                        notSpot = True
                        break
                    if image[y1,x1] != 0:
                        notSpot = True
                        break
                elif sr[c] == 1:
                    if y1 >= 0 and x1 >= 0:
                        if image[y+dy,x+dx] != 255:
                            notSpot = True
                            break
            if notSpot:
                break
        if isSpot:
            return True
    return False

