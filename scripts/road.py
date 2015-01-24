#!/usr/bin/env python

# load images of driving down a road, find different features -
# the road, lane dividers, other cars, the sky, and unknown other stuff.

# load images in data dir, 'j' and 'k' iterate forward or backward through them
# 'd' and 'f' to move test line around
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
        
        self.p1d = {}

        # currently in half height coords
        # x1, y2, x2, y2
        self.roi = {}
        self.roi["left"] = ((370, 360), (570, 390))
        self.roi["right"] = ((1200, 360), (1400, 390))

        for k in self.roi.keys():
            self.p1d[k] = None

        self.images = {}
        #for subdir, dirs, files in os.walk(name):
        #    for fl in sorted(files):
        for fl in sorted(os.listdir(dir_name)):
                name = os.path.join(dir_name, fl)
                im = cv2.imread(name)
                if im is not None:
                    print name
                    self.images[name] = im

                if len(self.images.keys()) > 20:
                    break
            #self.im = cv2.imread(name)
        
        print 'loaded ', len(self.images.keys()), 'images'
        self.ind = 0
        self.cy = None
        #self.overlay = np.zeros(self.im.shape, np.uint8) 

        cv2.namedWindow("image")
        cv2.setMouseCallback('image', get_mouse, self)

        plt.ion()
        plt.show()
    
    def findLanePts(self, im, vis):
            
            poss_pts = {}
            # look for lane markings
            for y in range(im.shape[0]-1, 0, -1):
                row = im[y,:].astype(int)
                diff = row[1:] - row[:-1]
                rises = diff >  10
                drops = diff < -5
                r2 = np.where(rises)[0]
                d2 = np.where(drops)[0]
                #print y, 'shape', rises.shape, r2, len(r2), np.sum(rises)
                for rise in r2:
                    dr = d2 - rise
                    matches = np.where( np.logical_and(dr >= 0, dr < 20) )[0]
                    if len(matches) > 0:
                        # start x and half width
                        half_pt_x = rise + dr[matches[0]]/2
                        #print rise, half_pt_x, matches[0], matches, dr
                        if not y in poss_pts.keys():
                            poss_pts[y] = []
                            
                        poss_pts[y].append( (rise, half_pt_x) ) 
                        vis[y,rise:half_pt_x,0] = 255
                        vis[y,rise:half_pt_x,1] = 155
                        vis[y,rise:half_pt_x,2] = 0
                        if rise - 5 >= 0:
                            vis[y,rise-5:rise,0] = 0
                            vis[y,rise-5:rise,1] = 0
                            vis[y,rise-5:rise,2] = 0
                #print 'h', y, r2
                #print 'l', y, d2
            return poss_pts
    
    def findLane(self, name, cur2, vis, init_roi, do_plot=True):
        roi = init_roi
        lane_x = []
        lane_y = []
        yend   = roi[1][1]
        
        step = 10
        count = 0
        p1d = None
        while True:

            roi_im1 = cur2[roi[0][1]:roi[1][1], roi[0][0]:roi[1][0]]
            roi_pts1 = self.findLanePts(roi_im1, 
                            vis[roi[0][1]:roi[1][1], roi[0][0]:roi[1][0]] )
            #print roi
            cv2.rectangle(vis, roi[0], roi[1], (255,0,0), 1)

            keys = sorted(roi_pts1.keys())
            x1 = [roi_pts1[y][0][0] + roi[0][0] for y in keys]
            y1 = [y + roi[0][1] for y in keys]
            
            lane_x.extend(x1)
            lane_y.extend(y1)
            #print lane_x
            #print lane_y

            ystart   = roi[0][1] - step
            yp = np.linspace(ystart, yend, yend - ystart)
            xp = None
            if len(lane_y) > 4:
                pf = np.polyfit(lane_y, lane_x, 1)
                p1d = np.poly1d(pf)
            else:
                
                p1d = self.p1d[name]
            
            if p1d is not None:
                #if do_plot:
                if True:
                    xp = p1d(yp)
                    p1 = ( int(xp[0]), int(yp[0]) )
                    p2 = ( int(xp[-1]), int(yp[-1]) )
                    cv2.line(vis, p1, p2, (count*5,50,255 - count * 2))

                    if False:
                        plt.plot(x1,y1, '.')
                        plt.plot(xp,yp)
                    if False: 
                        gi1 = np.logical_and(xp > 1, xp < vis.shape[1]) 
                        gi2 = np.logical_and(yp > 1, yp < vis.shape[0]) 
                        gi = np.logical_and(gi1, gi2)
                        vis[yp[gi].astype(int), xp[gi].astype(int)-1, :] = 0
                        vis[yp[gi].astype(int), xp[gi].astype(int), 0] = 250
                        vis[yp[gi].astype(int), xp[gi].astype(int), 1] = 50
            
            # new roi
            count +=1 
            if count > 24:
                break
            if ystart < 0: 
                break
            if xp is not None and len(xp) >= step:
                pad = step * 6 - count * 2
                roi = ((int(np.amin(xp[:step]) - pad), ystart), 
                       (int(np.amax(xp[:step]) + pad), ystart + step))
            else:
                roi = ((roi[0][0] - 2, ystart), 
                       (roi[1][0] + 2, ystart + step))
       
        print name, 'num_pts', len(lane_x)
        if len(lane_x) > len(xp)/3:
            if (self.p1d[name] is None):
                print name, 'locking on', p1d
            self.p1d[name] = p1d
            # don't save the current polyfit
        if False:
            plt.xlabel('x')
            plt.ylabel('y')
            plt.gca().invert_yaxis()
            plt.draw()
            plt.pause(0.01)

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
            
            if (self.cy == None):
                self.cy = cur.shape[0] * 3 / 4
            if (self.cy >= cur.shape[0]):
                self.cy = self.cy % cur.shape[0]

            plt.clf()
            r = cur[self.cy,:,2].astype(int)
            g = cur[self.cy,:,0].astype(int)
            b = cur[self.cy,:,1].astype(int)
            #plt.plot(b[1:] - b[:-1], '.', ms=2.0)
            #plt.plot(g[1:] - g[:-1], '.', ms=2.0)
            #plt.plot(r[1:] - r[:-1], '.', ms=2.0)
            #plt.axis([0, cur.shape[1], -40, 40])
            #plt.draw()
            #plt.pause(0.01)

            cur2 = cv2.cvtColor(cur[cur.shape[0]/2:,:], cv2.COLOR_BGR2GRAY)

            vis = cv2.cvtColor(cur2, cv2.COLOR_GRAY2BGR)
            
            for k in self.roi.keys():
                self.findLane(k, cur2, vis, self.roi[k])
           
            #cur2[self.cy,:,0] = 255 # [255,0,100]
            # hard coded masking out of sky, make algorithmic later TBD
            # should make this happen early to reduce resource usage
            #cv2.imshow("image", cur2[:,1:,:]-cur2[:,:-1,:])
            cv2.imshow("image", vis)
        
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
            elif key == ord('s'):
                cv2.imwrite("test.png", vis)
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
