import argparse
import numpy
from iqascore import IQAScore


parser = argparse.ArgumentParser(description='Compute Image Quality Assurance metrics for an image.')
parser.add_argument('images', metavar='Image', nargs='+', help='Path to the image file.')
args = vars(parser.parse_args())

images =args['images']
score = IQAScore()
if len(images) == 1:
    score.ComputeIqaScore(images[0], None)
else:
    score.ComputeIqaScore(images[0], images[1])

