import xml.etree.ElementTree as ET
import pickle
import os
import shutil
from os import listdir, getcwd
from os.path import join

sets=[('2012', 'train'), ('2012', 'val')]

classes = ["dog"]

wd = getcwd()

for year, image_set in sets:
    if not os.path.exists('VOCdevkit/VOC%s/imagesKept/'%(year)):
        os.makedirs('VOCdevkit/VOC%s/imagesKept/'%(year))
    image_ids = open('VOCdevkit/VOC%s/ImageSets/Main/%s.txt'%(year, image_set)).read().strip().split()
    for image_id in image_ids:
        in_file = open('VOCdevkit/VOC%s/Annotations/%s.xml'%(year, image_id))

        tree=ET.parse(in_file)
        root = tree.getroot()
        for obj in root.iter('object'):
            difficult = obj.find('difficult').text
            cls = obj.find('name').text
            if cls not in classes or int(difficult)==1:
                print 'no for',image_id
                continue
            print 'VOCdevkit/VOC%s/Annotations/%s.xml'%(year, image_id)
            #class is found then copy file into target dir
            shutil.copy2('VOCdevkit/VOC%s/JPEGImages/%s.jpg'%(year,image_id),'VOCdevkit/VOC%s/imagesKept'%(year))

