# _*_ coding:utf-8 _*_


import xml.etree.ElementTree as et
from lxml import etree
from src.DataSearch import utility as ut
import time

#
# print(ut.search_wiki('canvas'))
# #Give the path of the dataset
# pretime = time.time()
pathOfDataset = 'C:/Users\linuk\Desktop\Staedel/Objekte.xml'
pathOfGene = 'generatedDataSet.xml'
tree = etree.parse(pathOfDataset)
root = tree.getroot()



treeGene = etree.parse(pathOfGene)
rootGene = treeGene.getroot()

# listing = ut.getAllArtist(root)
# ut.create_artist_datenSet(listing,'C:/Users\linuk\Desktop/listAll.xml')
# lstSum = ut.getAllStyle(root)
# ut.create_style_tree(lstSum,'C:/Users\linuk\Desktop/listAll.xml','C:/Users\linuk\Desktop\lisss.xml')

while True:
    num = input('Please give the number of the painting:\n')
    try:
        title, name, createtime,record = ut.get_start_info(num, root)
        info, dict_detail =ut.get_details(record)
        print(info)
        print(dict_detail['artist'])
        print(ut.search_artist_xml(dict_detail['artist'],rootGene))
        print(ut.search_style_xml(dict_detail['style'],rootGene))
    except AttributeError:
        print('Can\'t find any thing' )
