# -*- coding: utf-8 -*-
"""
Created on Wed Sep 05 11:05:44 2018

@author: duchenting
"""
import os
import cv2
import numpy as np
import random
import codecs
import xml.dom.minidom
from multiprocessing import Pool

def motion_blur(image, degree=12, angle=45):
    image = np.array(image)
 
    # 这里生成任意角度的运动模糊kernel的矩阵， degree越大，模糊程度越高
    M = cv2.getRotationMatrix2D((degree / 2, degree / 2), angle, 1)
    motion_blur_kernel = np.diag(np.ones(degree))
    motion_blur_kernel = cv2.warpAffine(motion_blur_kernel, M, (degree, degree))
 
    motion_blur_kernel = motion_blur_kernel / degree
    blurred = cv2.filter2D(image, -1, motion_blur_kernel)
 
    # convert to uint8
    cv2.normalize(blurred, blurred, 0, 255, cv2.NORM_MINMAX)
    blurred = np.array(blurred, dtype=np.uint8)
    return blurred

def img_motionblur(per_len_imgs,root_path):
    img_path = root_path + 'images/'
    xml_path = root_path + 'xml/'
    save_path_img = root_path + 'blur/images/'
    save_path_xml = root_path + 'blur/xml/'

    degree = [10,20,30]
    angle = [30,60,120,150,210,240,300,330]

    count = 0
    for img in per_len_imgs:
        count = count + 1
        print count
        print img
        image = cv2.imread(img_path + img[:-4] + '.jpg')
        height,width = image.shape[:2]
        dom = xml.dom.minidom.parse(xml_path + img[:-4] +'.xml')
        idx1 = random.randint(0,2)
        idx2 = random.randint(0,7)
        img_blur = motion_blur(image, degree[idx1], angle[idx2])
        cv2.imwrite(save_path_img + img[:-4] + "_"+str(degree[idx1])+"_"+str(angle[idx2])+".jpg", img_blur)
        with open(os.path.join(save_path_xml + img[:-4] + "_"+str(degree[idx1])+"_"+str(angle[idx2])+".xml"),'w') as fh:          
            writer = codecs.lookup('utf-8')[3](fh)
            dom.writexml(writer)

if __name__ == "__main__":
    root_path = 'E:/back/dataset/add_data/gesture-20181011/aug/' 
    img_path = root_path + 'images/'
    xml_path = root_path + 'xml/'
    save_path_img = root_path + 'blur/images/'
    save_path_xml = root_path + 'blur/xml/'
    #allimgs=open("../20180828/ImageSets/val.txt").readlines()
    allimgs=[img for img in os.listdir(img_path)]
    #print len(allimgs)
    random.seed(2)
    random.shuffle(allimgs)
    num_kernel = 10
    all_len = 700
    print all_len
    per_len = int(np.floor(all_len/num_kernel) + 1)
        
    if not os.path.exists(save_path_img):
        os.makedirs(save_path_img)
    if not os.path.exists(save_path_xml):
        os.makedirs(save_path_xml)
    pool = Pool(processes=num_kernel)
    for i in xrange(num_kernel):
        begin = per_len * i
        end = per_len * (i + 1)
        print begin,end
        if end > all_len:
            end = all_len
        per_len_imgs = allimgs[begin:end]
        pool.apply_async(img_motionblur, (per_len_imgs, root_path))
    pool.close()
    pool.join()
    print "finished"
