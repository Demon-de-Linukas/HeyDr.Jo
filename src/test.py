# _*_ coding:utf-8 _*_


import xml.etree.ElementTree as et
from lxml import etree
from src.DataSearch import utility as ut

#Give the path of the dataset
pathOfDataset = 'C:/Users\linuk\Desktop\Staedel_Teilset/Objekte.xml'
tree = etree.parse(pathOfDataset)
root = tree.getroot()
title, name, time = ut.get_start_info('464', root)
print('\nTitle is: ' +title +'\n')
print('Artist is: ' +name +'\n')
print('Created time is: ' +time +'\n')
print(ut.search_artist(name))