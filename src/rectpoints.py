import numpy as np
import imagetools
import math

class RectPoints:
    def __init__(self, rectPoints, polyPoints):
        self.Rect = np.array(rectPoints).astype(int)
        self.Poly = np.array(polyPoints).astype(int)
        self.Left = PointGroup("Left",rectPoints[1],rectPoints[0])
        self.Top = PointGroup("Top",rectPoints[2], rectPoints[1])
        self.Right = PointGroup("Right",rectPoints[3], rectPoints[2])
        self.Bottom = PointGroup("Bottom",rectPoints[0], rectPoints[3])
        self.__loadPolyPoints()

    # Sort the points so that they are placed anti-clockwise
    def SortPoints(self):
        self.Left.SortPoints()
        self.Bottom.SortPoints()
        self.Right.SortPoints()
        self.Top.SortPoints()

    # Check the corners for folds or tears
    # Returns false if it finds at least 1 corner with a tear
    # Returns true if no corners have tears or folds
    def CheckCorners(self, config):
        # Top Left
        hp = self.Left.FirstPoint()
        wp = self.Top.LastPoint()
        if hp != None and wp != None:
            if not self.__checkForCornerTear(hp.DA, wp.DB, config):
                return False
        # Bottom Left
        hp = self.Left.LastPoint()
        wp = self.Bottom.FirstPoint()
        if hp != None and wp != None:
            if not self.__checkForCornerTear(hp.DB, wp.DA, config):
                return False
        # Bottom Right
        hp = self.Right.FirstPoint()
        wp = self.Bottom.LastPoint()
        if hp != None and wp != None:
            if not self.__checkForCornerTear(hp.DA, wp.DB, config):
                return False
        # Top Right
        hp = self.Right.LastPoint()
        wp = self.Top.FirstPoint()
        if hp != None and wp != None:
            if not self.__checkForCornerTear(hp.DB, wp.DA, config):
                return False
        # No folds or tears found
        return True

    # Check the edges for folds or tears
    # Returns false if it finds at least 1 edge with a fold or tear
    # Returns true if no edges have folds or tears 
    def CheckEdges(self, config):

        return True

    # Check if the width and height of the distances from the points to the corner
    # exceeds the configured value (in tenths of an inch)
    def __checkForCornerTear(self,h,w,config):
        # Get the area width and height in tenths of an inch
        hi = config.DPI * h * 10
        wi = config.DPI * w * 10
        if hi >= config.TornCornerHeigth and wi >= config.TornCornerWidth:
            return False
        return True

    # Loads the Poly Points into the associated line on the document rectangle
    def __loadPolyPoints(self):
        g = self.Left
        i = -1
        for p in self.Poly:
            i=i+1
            if imagetools.isOnTheLine(self.Left.A, self.Left.B, p):
                self.Left.AppendPoint(p,i)
                g = self.Left
                if imagetools.isOnTheLine(self.Bottom.A, self.Bottom.B, p):
                    self.Bottom.AppendPoint(p,i)
                    g = self.Bottom        
            elif imagetools.isOnTheLine(self.Bottom.A, self.Bottom.B, p):
                self.Bottom.AppendPoint(p,i)
                g = self.Bottom
                if imagetools.isOnTheLine(self.Right.A, self.Right.B, p):
                    self.Right.AppendPoint(p,i)
                    g = self.Right
            elif imagetools.isOnTheLine(self.Right.A, self.Right.B, p):
                self.Right.AppendPoint(p,i)
                g = self.Right
                if imagetools.isOnTheLine(self.Top.A, self.Top.B, p):
                    self.Top.AppendPoint(p,i)
                    g = self.Top
            elif imagetools.isOnTheLine(self.Top.A, self.Top.B, p):
                self.Top.AppendPoint(p,i)
                g = self.Top
                if imagetools.isOnTheLine(self.Left.A, self.Left.B, p):
                    self.Left.AppendPoint(p,i)
                    g = self.Left
            else:
                g.AppendOther(p,i)
        

class PointGroup:
    def __init__(self,name,a,b):
        self.Name = name
        self.A = a
        self.B = b
        self.Points = []
        self.Other = []

    def FirstPoint(self):
        if len(self.Points) == 0:
            return None
        return self.Points[0]

    def LastPoint(self):
        l = len(self.Points)
        if l == 0:
            return None
        return self.Points[l-1]

    def AppendPoint(self,p,i):
        self.Points.append(Point(self,p,i,True))
    
    def AppendOther(self,p,i):
        self.Other.append(Point(self,p,i,False))

    def SortPoints(self):
        self.Points.sort(key=getPointKey)

def getPointKey(item):
    return item.DA

class Point:
    def __init__(self,g,p,i,isOnRect):
        self.P = p
        self.I = i
        self.DA = self.__calcDistance(g.A,p)
        self.DB = self.__calcDistance(g.B,p)

    def __calcDistance(self,a,b):
        return int(np.linalg.norm(a-b))


