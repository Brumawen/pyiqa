import cv2
import os
import json
import numpy as np
from iqaconfig import IQAConfig
import imagetools
from matplotlib import path
import rectpoints

class IQAScore:
    def __init__(self):
        # Load the config from the config file
        self.config = IQAConfig(None)

    def ComputeIqaScore(self, frontImage, backImage):
        result = np.zeros(16, dtype=int)

        # Load the front image
        front = imagetools.readImageFile(frontImage)
        if len(front) == 0:
            return result
        frontHist = imagetools.getHistogram(front)

        canny, ratio = imagetools.getCannyImage(front)
        rect, box = imagetools.getBoundingRectangles(canny)

        # TODO: Remove this
        imagetools.writeImageFile('/ZTemp/aaa.jpg',canny)

        # Load the back image, if required
        back = imagetools.readImageFile(backImage)

        # Run the tests
        (result[0], result[5]) = self.__checkImageSize(front)
        (result[1], result[2]) = self.__checkFoldsOrTears(rect,box)
        (result[3]) = self.__checkDocumentFraming(canny,rect)
        (result[4]) = self.__checkDocumentSkew(rect)
        (result[6]) = self.__checkPiggyBack(canny, rect)
        (result[7], result[8]) = self.__checkImageBrightness(frontHist)
        (result[9]) = self.__checkHorizontalStreaks(canny)
        (result[10], result[11]) = self.__checkCompressedFileSize(frontImage, frontHist)
        (result[12]) = self.__checkSpotNoise(frontImage, frontHist)
        if not back == None:
            result[13] = self.__checkFrontBackDimensions(front, back)
        (result[14]) = self.__checkCarbonStrip(canny)
        (result[15]) = self.__checkImageFocus(front,frontHist)

        print (result)
        return result

    # Test 1: Check for an undersized image
    # Test 6: Check for an oversized image
    def __checkImageSize(self, image):
        shape = image.shape
        undersized = 2
        oversized = 2
        # test width
        width = shape[1] / self.config.DPI * 10
        if (width < self.config.MinImageWidth):
            undersized = 1
        if (width > self.config.MaxImageWidth):
            oversized = 1
        # test height
        height = shape[0] / self.config.DPI * 10
        if (height < self.config.MinImageHeight):
            undersized = 1
        if (height > self.config.MaxImageHeight):
            oversized = 1
        return undersized, oversized

    # Test 2: Check for folded or torn document corners
    # Test 3: Check for folded or torn document edges
    def __checkFoldsOrTears(self, rect, poly):
        cornerFolds = 2
        edgeFolds = 2

        # Get the actual points associated with both shapes
        rectPoints = np.array(cv2.boxPoints(rect))
        rectPoints = rectPoints.astype(int)
        polyPoints = np.reshape(poly,(-1,2))
        # Get the difference in the shape areas
        rectArea = cv2.contourArea(rectPoints)
        polyArea = cv2.contourArea(poly)
        areaDiff = abs((rectArea - polyArea) / rectArea * 100)
        # Get the difference in the shape lengths
        rectLen = cv2.arcLength(rectPoints, True)
        polyLen = cv2.arcLength(poly, True)
        lenDiff = abs((rectLen - polyLen) / rectLen * 100)

        if areaDiff < 1.5 and lenDiff < 1.5:
            # No discernable difference => no folds or tears
            return cornerFolds, edgeFolds

        # Get the list of points that sits on the rectangle
        points = rectpoints.RectPoints(rectPoints, polyPoints)
        points.SortPoints()
        if not points.CheckCorners(self.config):
            cornerFolds = 1
        if not points.CheckEdges(self.config):
            edgeFolds = 1

        return cornerFolds, edgeFolds

    # Test 4: Check for Document Framing Errors
    def __checkDocumentFraming(self, image, rect):
        shape = image.shape
        # Get the actual points associated with the rectangle
        rectPoints = np.array(cv2.boxPoints(rect))
        p = rectPoints[0]
        minX = p[0]
        minY = p[1]
        maxX = p[0]
        maxY = p[1]

        for p in rectPoints:
            if p[0] < minX:
                minX = p[0]
            if p[0] > maxX:
                maxX = p[0]
            if p[1] < minY:
                minY = p[1]
            if p[1] > maxY:
                maxY = p[1]
        if self.__checkOverscan(minX, self.config.LeftEdgeOverscan):
            return 1
        elif self.__checkOverscan(shape[1] - maxX, self.config.RightEdgeOverscan):
            return 1
        elif self.__checkOverscan(minY, self.config.TopEdgeOverscan):
            return 1
        elif self.__checkOverscan(shape[0] - maxY, self.config.BottomEdgeOverscan):
            return 1
        else:
            return 2

    def __checkOverscan(self, a, b):
        # Convert to inches before testing
        c = int(a / self.config.DPI * 10)
        return c > b

    # Test 5: Check for excessive document skew
    def __checkDocumentSkew(self, rect):
        skewed = 2
        angle = imagetools.getRotationAngle(rect[2])
        if angle > 0 and angle > self.config.PositiveSkewAngle / 10:
            skewed = 1
        if angle < 0 and abs(angle) > self.config.NegativeSkewAngle / 10:
            skewed = 1 
        return skewed

    # Test 7: Check for piggy-back documents
    def __checkPiggyBack(self, image, rect):
        return 0

    # Test 8: Check if the image is too light
    # Test 9: Check if the image is too dark
    def __checkImageBrightness(self, hist):
        tooBright = 2
        tooDark = 2
        if imagetools.isBitonal(hist):
            # Bitonal Image
            blackCount = hist[0]
            totalCount = hist[0] + hist[255]
            percentBlack = blackCount/totalCount*100
            # Check if too light
            if percentBlack < self.config.BitonalMinBlack / 10:
                tooBright = 1
            # Check if too dark
            if percentBlack > self.config.BitonalMaxBlack / 10:
                tooDark = 1
        else:
            # Grayscale or Colour Image
            maxWhitest = -1
            minBlackest = -1
            for i in range(0, 256):
                if (hist[i] != 0):
                    minBlackest = i
                    break
            for i in range(255, -1, -1):
                if (hist[i] != 0):
                    maxWhitest = i
                    break
            middle = int((maxWhitest - minBlackest) /2)
            minWhitest = maxWhitest - int((maxWhitest - middle) * (self.config.GrayPercentWhitest / 1000))
            maxBlackest = int((middle - minBlackest) * (self.config.GrayPercentBlackest / 1000))
            totalBlack = 0
            blackCount = 0
            for i in range(minBlackest, maxBlackest + 1):
                blackCount += hist[i]
                totalBlack += (i * hist[i])
            avgBlack = totalBlack/ blackCount
            totalWhite = 0
            whiteCount = 0
            for i in range(minWhitest, maxWhitest + 1):
                whiteCount += hist[i]
                totalWhite += (i * hist[i])
            avgWhite = totalWhite/ whiteCount
            avgBrightness = avgWhite/maxWhitest * 100
            avgContrast = (avgWhite - avgBlack)/ maxWhitest * 100

            # Check if too light
            if avgBrightness > self.config.GrayMaxBrightness / 10:
                tooBright = 1
            if avgContrast < self.config.GrayMinContrast / 10:
                tooBright = 1
            # Check if too dark
            if avgBrightness < self.config.GrayMinBrightness / 10:
                tooDark = 1
            if avgContrast > self.config.GrayMaxContrast / 10:
                tooDark = 1

        return tooBright, tooDark

    # Test 10: Check for horizontal streaks
    def __checkHorizontalStreaks(self, image):
        return 0

    # Test 11: Check that the compressed image size is not too small
    # Test 12: Check that the compressed image size is not too big
    def __checkCompressedFileSize(self, frontImage, hist):
        tooSmall = 2
        tooBig = 2
        fileSize = os.path.getsize(frontImage)
        if imagetools.isBitonal(hist):
            # Bitonal Image
            if fileSize < self.config.BitonalMinCompressedSize:
                tooSmall = 1
            if fileSize > self.config.BitonalMaxCompressedSize:
                tooBig = 1
        else:
            # Grayscale or Color image
            if fileSize < self.config.GrayMinCompressedSize:
                tooSmall = 1
            if fileSize > self.config.GrayMaxCompressedSize:
                tooBig = 1
        return tooSmall, tooBig

    # Test 13: Check for excessive Spot noise
    def __checkSpotNoise(self, image, hist):
        if imagetools.isBitonal(hist):
            # This test is only applicable to bitonal images
            shape = image.shape
            maxY = shape[0]
            maxX = shape[1]
        return 2
    
    # Test 14: Check for a Front-Rear image dimmension mismatch
    def __checkFrontBackDimensions(self, front, back):
        frontShape = front.shape
        backShape = back.shape
        hDelta = abs(frontShape[0] - backShape[0])
        wDelta = abs(frontShape[1] - backShape[1])
        result = 2
        if hDelta > self.config.FrontRearHeightDifference:
            result = 1
        if wDelta > self.config.FrontRearWidthDifference:
            result = 1
        return result

    # Test 15: Check for a carbon strip
    def __checkCarbonStrip(self, image):
        return 0

    # Test 16: Check image is in focus
    def __checkImageFocus(self, image, hist):
        if not imagetools.isBitonal(hist):
            # This test is only applicable to grayscale and colour images
            if imagetools.BlurScore(image) <= self.config.BlurThreshold:
                return 1
        return 2

    
