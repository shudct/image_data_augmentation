# -*- coding: utf-8 -*-
"""
Created on Fri Aug 31 15:02:52 2018

@author: duchenting
"""

import cv2,os
import random
import codecs
import xml.dom.minidom

root_path = 'E:/back/dataset/add_data/gesture-20181011/aug/'
image_path = root_path + 'images/'
xml_path = root_path + 'xml/'
hsv_imgpath = root_path + 'hsv/images/'
hsv_xmlpath = root_path + 'hsv/xml/'

if not os.path.exists(hsv_imgpath):
    os.makedirs(hsv_imgpath)
if not os.path.exists(hsv_xmlpath):
    os.makedirs(hsv_xmlpath)

lines=[img for img in os.listdir(image_path)]
print len(lines)
random.seed(3)
random.shuffle(lines)
sub_count = 921
index = 0
for line in lines[:sub_count]:
    index = index + 1
    print index
    print line
    fname = image_path + line
    dom = xml.dom.minidom.parse(xml_path + line[:-4] +'.xml')
    img_hsv = cv2.cvtColor(cv2.imread(fname), cv2.COLOR_BGR2HSV)
    img_hsv[:, :, 2] = img_hsv[:, :, 2] * 0.5
    img_rgb = cv2.cvtColor(img_hsv, cv2.COLOR_HSV2BGR)
    cv2.imwrite(hsv_imgpath + line[:-4] + '_hsv.jpg', img_rgb)
    with open(os.path.join(hsv_xmlpath + line[:-4] + '_hsv.xml'),'w') as fh:          
        writer = codecs.lookup('utf-8')[3](fh)
        dom.writexml(writer)
         
print "done"
    
