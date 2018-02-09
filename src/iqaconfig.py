import json
import os

class IQAConfig(object):
    def __init__(self, configFile):
        if configFile == None:
            configFile = 'config.json'
        if os.path.isfile(configFile):
            # Parse the file to get the configuration
            file = open(configFile, 'r')
            config = file.read()
            file.close()
            self.__dict__ = json.loads(config)
        self.__setDefaults()
        # Save the changes back, if required
        if hasattr(self, 'mustSave'): 
            if self.mustSave:
                delattr(self,'mustSave')
                self.Save(configFile)

    def Save(self, filePath):
        file = open(filePath, 'w')
        file.write(json.dumps(self.__dict__))
        file.close()

    def __setDefaults(self):
        # Check that all the required attributes are defined
        self.__checkAttr('DPI', 200)

        self.__checkAttr('MinImageWidth', 65)
        self.__checkAttr('MaxImageWidth', 100)
        
        self.__checkAttr('MinImageHeight', 25)
        self.__checkAttr('MaxImageHeight', 50)

        self.__checkAttr('LeftEdgeOverscan', 10)
        self.__checkAttr('RightEdgeOverscan', 10)
        self.__checkAttr('TopEdgeOverscan', 10)
        self.__checkAttr('BottomEdgeOverscan', 10)

        self.__checkAttr('BitonalMinCompressedSize', 2000)
        self.__checkAttr('BitonalMaxCompressedSize', 100000)
        self.__checkAttr('BitonalMinBlack', 20)
        self.__checkAttr('BitonalMaxBlack', 800)

        self.__checkAttr('GrayMinCompressedSize', 2000)
        self.__checkAttr('GrayMaxCompressedSize', 200000)
        self.__checkAttr('GrayPercentWhitest', 780)
        self.__checkAttr('GrayPercentBlackest', 780)
        self.__checkAttr('GrayMaxBrightness', 900)
        self.__checkAttr('GrayMinBrightness', 600)
        self.__checkAttr('GrayMinContrast', 500)
        self.__checkAttr('GrayMaxContrast', 800)

        self.__checkAttr('NegativeSkewAngle', 10)
        self.__checkAttr('PositiveSkewAngle', 10)

        self.__checkAttr('TornCornerWidth', 10)
        self.__checkAttr('TornCornerHeigth', 5)
        self.__checkAttr('TornEdgeWidth', 10)
        self.__checkAttr('TornEdgeHeigth', 5)

        self.__checkAttr('FrontRearWidthDifference', 4)
        self.__checkAttr('FrontRearHeightDifference', 3)

        self.__checkAttr('BlurThreshold', 250)
        

    def __checkAttr(self, name, defValue):
        if not hasattr(self, name):
            self.__dict__[name] = defValue
            self.mustSave = True

    