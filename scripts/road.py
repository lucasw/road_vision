#!/usr/bin/env python

# load images of driving down a road, find different features -
# the road, lane dividers, other cars, the sky, and unknown other stuff.

import cv2
import sys

name = sys.argv[1]

im = cv2.imread(name)

cv2.imshow("image", im)
cv2.waitKey(0)


