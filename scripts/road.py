#!/usr/bin/env python

# load images of driving down a road, find different features -
# the road, lane dividers, other cars, the sky, and unknown other stuff.

# load images in data dir, 'j' and 'k' iterate forward or backward through them
# 'd' and 'f' to move test line around
# #road_vision$ ./scripts/road.py data
# road_vision$ ./scripts/road.py data/raw/video.mov

import cv
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

def visPoints(vis, xp, yp):
    gi1 = np.logical_and(xp > 1, xp < vis.shape[1]) 
    gi2 = np.logical_and(yp > 1, yp < vis.shape[0]) 
    gi = np.logical_and(gi1, gi2)
    vis[yp[gi].astype(int), xp[gi].astype(int)-1, :] = 0
    vis[yp[gi].astype(int), xp[gi].astype(int), 0] = 50
    vis[yp[gi].astype(int), xp[gi].astype(int), 1] = 250


# store persistent data for a single lane
# initial roi and rois from the best most recent lane match
class Lane():
    
    def __init__(self, name, roi):
            
        self.name = name
        self.init_roi = roi
        # all the rois continuing into distance, following the lane marker
        self.rois = {}
        self.lane_x = None
        self.lane_y = None
        self.xp = None
        self.yp = None
        # the polyfit class
        self.p1d = None
        self.lock_ind = -60 
        self.ind = 0

    def findLanePts(self, im, vis):
            # blur the image vertically some
            im[:-1,:] = im[:-1,:]/2 + im[1:,:]/2 

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
                new_pts = []
                for rise in r2:
                    dr = d2 - rise
                    matches = np.where( np.logical_and(dr >= 0, dr < 50) )[0]
                    for match in matches: #if len(matches) > 0:
                        # start x and half width
                        half_pt_x = rise + dr[match]/2
                        #if row[half_pt_x] < 70:
                        #    continue
                        #print rise, half_pt_x, matches[0], matches, dr
                        
                        #if not y in poss_pts.keys():
                        #    poss_pts[y] = []
                            
                        new_pts.append( (rise, half_pt_x, row[half_pt_x]) ) 
                       
                        #break
                #print 'h', y, r2
                #print 'l', y, d2

                # only take the best half of the points:
                if len(new_pts) > 5:
                    quality = sorted([a[2] for a in new_pts])
               
                    med_qual = quality[4*len(quality)/5]
                    #print 'med quality', med_qual 
                    for pt in new_pts:
                        if pt[2] > med_qual:
                            if not y in poss_pts.keys():
                                poss_pts[y] = []
                            poss_pts[y].append(pt)
                            
                            rise = pt[0]
                            half_pt_x = pt[1]
                            vis[y,rise:half_pt_x,0] = 255
                            vis[y,rise:half_pt_x,1] = 155
                            vis[y,rise:half_pt_x,2] = pt[2]
                            if rise - 5 >= 0:
                                vis[y,rise-5:rise,0] = 0
                                vis[y,rise-5:rise,1] = 0
                                vis[y,rise-5:rise,2] = 0
                         

            return poss_pts
    
    # TBD need to have a function to take an polyfit and find lane with it
    # without using any of the new data- this would allow comparing the old fit
    # to the new, and use the old if it is a lot better.
    def findLane(self, cur2, vis, do_plot=True):
        if 0 in self.rois.keys():
            roi = self.rois[0]
        else:
            roi = self.init_roi
        lane_x = []
        lane_y = []
        yend   = roi[1][1]
        
        rois = {}

        xp = None
        step = 10
        count = 0
        p1d = None
        lock_diff = (self.ind - self.lock_ind)
        #print self.name, self.ind, lock_diff 
        while True:
            rois[count] = roi 
            roi_im1 = cur2[roi[0][1]:roi[1][1], roi[0][0]:roi[1][0]]
            roi_pts1 = self.findLanePts(roi_im1, 
                            vis[roi[0][1]:roi[1][1], roi[0][0]:roi[1][0]] )
            #print roi
            cv2.rectangle(vis, roi[0], roi[1], (255 - lock_diff, 3 * lock_diff, 0), 1)

            keys = sorted(roi_pts1.keys())
            x1 = [roi_pts1[y][0][0] + roi[0][0] for y in keys]
            y1 = [y + roi[0][1] for y in keys]
            
            test_lane_x = lane_x[:]
            test_lane_y = lane_y[:]
            test_lane_x.extend(x1)
            test_lane_y.extend(y1)
            #print lane_x
            #print lane_y

            ystart   = roi[0][1] - step
            yp = np.linspace(ystart, yend, yend - ystart)
            xp = None
            order = 1
            error = None
            if count > 14:
                order = 2
            if len(test_lane_y) > 4:
                pf, residuals, rank, singular_values, rcond = \
                        np.polyfit(test_lane_y, test_lane_x, order, full=True)
                #print count, 'resid', residuals[0], len(lane_x)
                error = residuals[0]
                #print error, len(residuals)
                # not really understanding residuals, seem to be very high
                # sometimes and very low others
                if error < 500:
                    lane_x = test_lane_x
                    lane_y = test_lane_y
                #if (error > 500):
                #    break

            if len(lane_y) > 4:
                # TBD possible redundant polyfit
                pf = np.polyfit(lane_y, lane_x, order)
                p1d = np.poly1d(pf)
            else:
                p1d = self.p1d
            
            if p1d is not None:
                #if do_plot:
                if True:
                    
                    xp = p1d(yp)
                    if False:
                        p1 = ( int(xp[0]), int(yp[0]) )
                        p2 = ( int(xp[-1]), int(yp[-1]) )
                        cv2.line(vis, p1, p2, (count*5,50,255 - count * 2))

                    if False:
                        plt.plot(x1,y1, '.')
                        plt.plot(xp,yp)
                    #visPoints(vis, xp, yp)
            
            count += 1 
            if count > 26:
                break
            if ystart < 0: 
                break
            if self.rois is not None and count in self.rois.keys():
                roi = self.rois[count]
            elif xp is not None and len(xp) >= step:
                pad = step * 6 - count * 2
                roi = ((int(np.amin(xp[:step]) - pad), ystart), 
                       (int(np.amax(xp[:step]) + pad), ystart + step))
            else:
                roi = ((roi[0][0], ystart), 
                       (roi[1][0], ystart + step))
       
        if xp is not None:
            #print name, 'num_pts', len(lane_x)
            # save the current polyfit
            threshold = len(xp)/5
            if len(lane_x) > threshold:
                #if (self.p1d[name] is None):
                #print self.ind, self.name, 'locking on' #, p1d
                self.p1d  = p1d
                self.lane_x = lane_x
                self.lane_y = lane_y
                self.xp = xp
                self.yp = yp
                self.lock_ind = self.ind
                c2 = 0
                for y in np.arange(np.amax(yp) - 10, np.amin(yp), -10, np.int32):
                    xrng = xp[ np.logical_and(yp > y, yp < y + 10) ]
                    xmin = int(np.amin(xrng))
                    xmax = int(np.amax(xrng))
                    pad = int((step * 6 - c2 * 2) * 1.5)
                    new_roi = ((xmin - pad, y),  (xmax + pad, y + 10))
                    #print c2, self.name, new_roi
                    self.rois[c2] = new_roi 
                    c2 += 1
                #self.rois = rois
            elif lock_diff > 60:
                self.rois = {}
                self.p1d = None
        if False:
            plt.xlabel('x')
            plt.ylabel('y')
            plt.gca().invert_yaxis()
            plt.draw()
            plt.pause(0.01)
       

        if self.p1d:
            xp2 = self.p1d(yp)
            #plt.plot(xp2, yp, ms=2.0)
           
            visPoints(vis, xp2, yp)
        
        if False:
            plt.plot(lane_x, lane_y, '.', ms=4.0)
            plt.plot(xp, yp, ms=2.0)
            plt.gca().invert_yaxis()
            plt.title(str(len(lane_x)) + ' ' + str(len(xp)) + ' ' + 
                    str(threshold)  + ', p1d ' + str(p1d) + ', ' + str(self.p1d))
            plt.xlabel('lane_y')
            plt.ylabel('lane_x')
            plt.draw()
            plt.pause(0.01)

        self.ind += 1

class RoadVision():
    
    def __init__(self, dir_name):
        
        self.play = False
        if False:
            self.ox = None
            self.oy = None
            self.mx = None
            self.my = None
        self.l_button_down = False
        
        self.write_images = False

        # currently in half height coords
        # x1, y2, x2, y2
        self.lane = {}
        self.lane["left"]  = Lane("left", ((370, 360), (770, 390)))
        self.lane["right"] = Lane("right", ((1200, 360), (1600, 390)))

        #self.fourcc = cv2.VideoWriter_fourcc(*'XVID')

        self.out_vid = None
        self.cap = cv2.VideoCapture(dir_name)
        ret, self.cur = self.cap.read()

        cv2.namedWindow("image")
        self.cy = None
        self.ind = 0
        #cv2.setMouseCallback('image', get_mouse, self)

        plt.ion()
        plt.show()
    
        return
        
        # Using live video now and not dir of images
        ##############################################
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
        #self.overlay = np.zeros(self.im.shape, np.uint8) 
    
    def advance(self):
        ret, self.cur = self.cap.read()
        if self.write_images:
            name = "image" + str(100000 + self.ind) + ".jpg"
            cv2.imwrite(name, vis)
        self.ind += 1
    
    def spin(self):
        
        # old markup stuff, not using
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
            cur = self.cur #self.images[sorted(self.images.keys())[self.ind]] #.copy()
            if cur is None:
                continue


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

            # hard coded masking out of sky, make algorithmic later TBD
            # should make this happen early to reduce resource usage
            cur2 = cv2.cvtColor(cur[cur.shape[0]/2 - 100:-100,:], cv2.COLOR_BGR2GRAY)

            vis = cv2.cvtColor(cur2, cv2.COLOR_GRAY2BGR)
            # Tried writing video directly, didn't work and didn't bother
            # to try anything else, easier to save dir of images
            #if self.out_vid is None:
                #fourcc =  cv.CV_FOURCC(*'DIVX') #('P','I','M','1')
                #self.out_vid = cv2.VideoWriter('test.avi', fourcc, 30.0, (vis.shape[0],vis.shape[1]))
            
            if False: #for k in self.lane.keys():
                self.lane[k].findLane(cur2, vis)
         
            if self.out_vid:
                self.out_vid.write(vis)

            key = None
            cv2.imshow("image", vis)
           
            if self.play:
                key = cv2.waitKey(5)
                self.advance()
            else: 
                key = cv2.waitKey(0)
            
            if key == ord('q'):
                break
            #if key != -1:
            #    print key
            elif key == ord(' '):
                self.play = not self.play
            elif key == ord('j'):
                self.advance()
            elif key == ord('s'):
                name = "vis_save_" + str(100000 + self.ind) + ".jpg"
                cv2.imwrite(name, vis)
                print name
                name = "raw_save_" + str(100000 + self.ind) + ".jpg"
                cv2.imwrite(name, self.cur)

            # directory of images controls
            if False:
                num_keys = 1 #len(self.images.keys())
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
            
                if key == ord('d'):
                    for k in self.roi.keys():
                        for i in range(2):
                            self.roi[k][i][1] -= 4
                if key == ord('f'):
                    for k in self.roi.keys():
                        for i in range(2):
                            self.roi[k][i][1] += 4

                elif key == ord('s'):
                    cv2.imwrite("test.png", vis)
                    cv2.imwrite("raw.png", self.cur)
                elif key == ord('q'):
                    if self.out_vid:
                        self.out_vid.release();
                    break

                ret, self.cur = self.cap.read()
                ind += 1

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
