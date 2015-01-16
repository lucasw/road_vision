#!/usr/bin/env python

# load images of driving down a road, find different features -
# the road, lane dividers, other cars, the sky, and unknown other stuff.

# load images in data dir, 'j' and 'k' iterate forward or backward through them
# road_vision$ ./scripts/road.py data

import cv2
import matplotlib.pyplot as plt
import numpy as np
import os
import sys

def get_mouse(event, x, y, flags, param):
    param.mx = x
    param.my = y
    do_print = True
    if event == cv2.EVENT_MOUSEMOVE:
        do_print = False
    elif event == cv2.EVENT_LBUTTONDOWN:
        if not param.l_button_down:
            print 'left button down'
        param.l_button_down = True
    elif event == cv2.EVENT_LBUTTONUP:
        if param.l_button_down:
            print 'left button up'
        param.l_button_down = False
    
    if do_print:
        print event, x, y


class RoadVision():
    
    def __init__(self, dir_name):
        self.ox = None
        self.oy = None
        self.mx = None
        self.my = None
        self.l_button_down = False
        
        self.images = {}
        #for subdir, dirs, files in os.walk(name):
        #    for fl in sorted(files):
        for fl in sorted(os.listdir(dir_name)):
                name = os.path.join(dir_name, fl)
                im = cv2.imread(name)
                if im is not None:
                    print name
                    self.images[name] = im

                if len(self.images.keys()) > 10:
                    break
            #self.im = cv2.imread(name)
        
        self.ind = 0
        self.cy = 500
        #self.overlay = np.zeros(self.im.shape, np.uint8) 

        cv2.namedWindow("image")
        cv2.setMouseCallback('image', get_mouse, self)

        plt.ion()
        plt.show()

    def spin(self):
        if False:
        #while True:
            if self.l_button_down:
                col = (255,0,0)
                sz = 30
                if (self.ox is not None and self.mx is not None):
                    cv2.line(self.overlay, (self.ox, self.oy),
                            (self.mx, self.my), col, sz)
                self.ox = self.mx
                self.oy = self.my
                #print self.mx, self.my
                #cv2.circle(self.overlay, (self.mx, self.my), sz, col, -1) 
            
            # unmarked parts of overlay
            black = self.overlay[:,:] == [0, 0, 0]
            used = self.overlay[:,:] != [0, 0, 0]
            comp = self.im
            comp[used] = self.overlay[used]

            cv2.imshow("image", comp)

        while True:
            cur = self.images[sorted(self.images.keys())[self.ind]] #.copy()
            
            if (self.cy >= cur.shape[0]):
                self.cy = self.cy % cur.shape[0]

            plt.axis([0, cur.shape[1], 0, 255])
            plt.clf()
            plt.plot(cur[self.cy,:,0])
            plt.draw()
            plt.pause(0.01)

            cur2 = cur.copy()
            cur2[self.cy,:,0] = 255 # [255,0,100]
            cv2.imshow("image", cur2)
        
            key = cv2.waitKey(0)
            #if key != -1:
            #    print key
            num_keys = len(self.images.keys())
            if key == ord('d'):
                self.cy += 1
                self.cy = self.cy % cur.shape[0]
            elif key == ord('f'):
                self.cy -= 1
                self.cy = (self.cy + cur.shape[0]) % cur.shape[0]
            elif key == ord('j'):
                self.ind += 1
                self.ind = self.ind % num_keys
                #print self.ind, self.images.keys()[self.ind]
            elif key == ord('k'):
                self.ind -= 1
                self.ind = (self.ind + num_keys) % num_keys
                #print self.ind, self.images.keys()[self.ind]
            elif key == ord('q'):
                break

comment = '''
>>> import cv2
>>> events = [i for i in dir(cv2) if 'EVENT' in i]
>>> print events
['EVENT_FLAG_ALTKEY', 
'EVENT_FLAG_CTRLKEY', 
'EVENT_FLAG_LBUTTON', 
'EVENT_FLAG_MBUTTON', 
'EVENT_FLAG_RBUTTON', 
'EVENT_FLAG_SHIFTKEY',
'EVENT_LBUTTONDBLCLK', 
'EVENT_LBUTTONDOWN', 
'EVENT_LBUTTONUP', 
'EVENT_MBUTTONDBLCLK', 
'EVENT_MBUTTONDOWN', 
'EVENT_MBUTTONUP', 
'EVENT_MOUSEMOVE', 
'EVENT_RBUTTONDBLCLK', 
'EVENT_RBUTTONDOWN',
'EVENT_RBUTTONUP']
'''

if __name__ == '__main__':
    road_vision = RoadVision(sys.argv[1])
    road_vision.spin()
