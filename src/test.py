# _*_ coding:utf-8 _*_


import xml.etree.ElementTree as et
from lxml import etree
from src.DataSearch import utility as ut
import time


#Give the path of the dataset
pretime = time.time()
pathOfDataset = 'C:/Users\linuk\Desktop\Staedel_Teilset/Objekte.xml'
tree = etree.parse(pathOfDataset)
root = tree.getroot()
title, name, createtime = ut.get_start_info('464', root)
print('\nTitle is: ' +title +'\n')
print('Artist is: ' +name +'\n')
print('Created time is: ' +createtime +'\n')
print(ut.search_artist(name))
print('\nDuration of the test: %.3f seconds'%(time.time()-pretime))