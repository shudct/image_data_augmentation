# -*- coding: utf-8 -*-
"""
Created on Thu May 31 14:46:12 2018

@author: duchenting
"""

import os
import math
import codecs
import cv2
import random
import xml.dom.minidom
from scipy import ndimage
import numpy as np
from multiprocessing import Pool

def PRotate(x, y, angle, w, h, W, H):
    anglePi = angle*math.pi/180.0
    cosA = math.cos(anglePi)
    sinA = math.sin(anglePi)
    dx = -1*w*cosA*0.5-h*sinA*0.5+0.5*W
    dy = w*sinA*0.5-h*cosA*0.5+0.5*H
    X = int(cosA*x+sinA*y+dx)
    Y = int(-sinA*x+cosA*y+dy)
    return X, Y

def aug_img(per_len_imgs,root_path):   
    img_path = root_path + 'images/'
    xml_path = root_path + 'xml/'
    img_aug_path = root_path + 'aug/images/'
    xml_aug_path = root_path + 'aug/xml/'
    index = 0
    angles = [0, 90, 180, 270]
    area_ratios = [0.007, 0.10, 0.20, 0.30, 0.45]
    wh_ratios = [3/4.0, 4/3.0, 3/4.0, 4/3.0]
    rez_inter = [cv2.INTER_NEAREST, cv2.INTER_LINEAR, cv2.INTER_AREA, cv2.INTER_CUBIC, cv2.INTER_LANCZOS4]
    for img in per_len_imgs:
        index = index+1
        print index
        print img
        image_origin = cv2.imread(img_path + img)
        height_origin, width_origin = image_origin.shape[:2]
    
        dom = xml.dom.minidom.parse(xml_path + img[:-4] +'.xml')
        root = dom.documentElement
    
        xmin_ori = int(root.getElementsByTagName('xmin')[0].firstChild.data)
        ymin_ori = int(root.getElementsByTagName('ymin')[0].firstChild.data)
        xmax_ori = int(root.getElementsByTagName('xmax')[0].firstChild.data)
        ymax_ori = int(root.getElementsByTagName('ymax')[0].firstChild.data)
        for angle in angles:
            image_rotated= ndimage.rotate(image_origin, angle)
            
            H=image_rotated.shape[0]
            W=image_rotated.shape[1]
            
            x1,y1 = PRotate(xmin_ori,ymin_ori,angle,width_origin,height_origin,W,H)
            x2,y2 = PRotate(xmax_ori,ymin_ori,angle,width_origin,height_origin,W,H)
            x3,y3 = PRotate(xmin_ori,ymax_ori,angle,width_origin,height_origin,W,H)
            x4,y4 = PRotate(xmax_ori,ymax_ori,angle,width_origin,height_origin,W,H)
            new_xmin = min(x1,x2,x3,x4)
            new_xmax = max(x1,x2,x3,x4)
            new_ymin = min(y1,y2,y3,y4)
            new_ymax = max(y1,y2,y3,y4)
        
            new_bbox_w = new_xmax - new_xmin + 1
            new_bbox_h = new_ymax - new_ymin + 1
        
            for idx, wh_ratio in enumerate(wh_ratios):
                rand_idx = random.randint(0,3)
                rand_ratio = random.uniform(area_ratios[rand_idx],area_ratios[rand_idx+1])
                
                new_area = new_bbox_h * new_bbox_w / rand_ratio
        
                if wh_ratio == 3/4.0:
                    new_height = 4*int(math.sqrt(new_area/12.0))
                    new_width = 3*int(math.sqrt(new_area/12.0))
                elif wh_ratio == 4/3.0:
                    new_height = 3*int(math.sqrt(new_area/12.0))
                    new_width = 4*int(math.sqrt(new_area/12.0))
                        
                try:
                    rand_x1 = random.randint(max(new_xmin-(new_width-new_bbox_w), 0), new_xmin)
                    rand_y1 = random.randint(max(new_ymin-(new_height-new_bbox_h), 0), new_ymin)
                    rand_x2 = min(rand_x1 + new_width, W)
                    rand_y2 = min(rand_y1 + new_height, H)
                except:
                    print "error"
                    continue
                else:
    
                    image_new = image_rotated[rand_y1:rand_y2+1, rand_x1:rand_x2+1]
                    if image_new.shape[1]>image_new.shape[0]:
                        aug_r = 640.0/image_new.shape[1]
                    else:
                        aug_r = 640.0/image_new.shape[0]
            
                    width_final = int(aug_r*image_new.shape[1])
                    height_final = int(aug_r*image_new.shape[0])
                    rand_rez_idx = random.randint(0,4)
                    image_final = cv2.resize(image_new,(width_final,height_final),interpolation=rez_inter[rand_rez_idx])
    
                    xmin_final = np.floor((new_xmin - rand_x1)*aug_r)
                    ymin_final = np.floor((new_ymin - rand_y1)*aug_r)
                    xmax_final = np.floor(xmin_final + new_bbox_w*aug_r)
                    ymax_final = np.floor(ymin_final + new_bbox_h*aug_r)
                    width_final = image_final.shape[1]
                    height_final = image_final.shape[0]
                    realwh_ratio = width_final*1.0/height_final
        
                    aug_dom = dom
                    root_new = aug_dom.documentElement
                    root_new.getElementsByTagName('xmin')[0].firstChild.data = int(xmin_final)
                    root_new.getElementsByTagName('ymin')[0].firstChild.data = int(ymin_final)
                    root_new.getElementsByTagName('xmax')[0].firstChild.data = int(xmax_final)
                    root_new.getElementsByTagName('ymax')[0].firstChild.data = int(ymax_final)
                    root_new.getElementsByTagName('width')[0].firstChild.data = width_final
                    root_new.getElementsByTagName('height')[0].firstChild.data = height_final
            
                    if realwh_ratio>=0.67 and realwh_ratio<=1.5 and width_final > 99 and height_final > 99:
                        cv2.imwrite(img_aug_path + img[:-4] + '_'+ str(idx) + '_' + str(angle) + '_aug' + '.jpg', image_final)
                        print img[:-4] + '_'+ str(idx) + '_' + str(angle) + '_aug' + '.jpg' + ' saved'
                        with open(os.path.join(xml_aug_path+img[:-4] + '_'+ str(idx) + '_' + str(angle) + '_aug' + '.xml'),'w') as fh:          
                            writer = codecs.lookup('utf-8')[3](fh)
                            aug_dom.writexml(writer)
        
if __name__ == "__main__":
    root_path = 'E:/back/dataset/net_rock/'
    img_path = root_path + 'images/'
    xml_path = root_path + 'xml/'
    img_aug_path = root_path + 'aug/images/'
    xml_aug_path = root_path + 'aug/xml/'
    allimgs=[img for img in os.listdir(img_path) if 'jpg' in img]
    num_kernel = 10
    all_len = len(allimgs)
    print all_len
    per_len = int(np.floor(all_len/num_kernel) + 1)

    if not os.path.exists(img_aug_path):
        os.makedirs(img_aug_path)
    
    if not os.path.exists(xml_aug_path):
        os.makedirs(xml_aug_path)

    pool = Pool(processes=num_kernel)
    for i in xrange(num_kernel):
        begin = per_len * i
        end = per_len * (i + 1)
        print begin,end
        if end > all_len:
            end = all_len
        per_len_imgs = allimgs[begin:end]
        pool.apply_async(aug_img, (per_len_imgs, root_path))
    pool.close()
    pool.join()
