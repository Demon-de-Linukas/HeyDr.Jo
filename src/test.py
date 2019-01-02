# _*_ coding:utf-8 _*_


import xml.etree.ElementTree as et
from lxml import etree
from src.DataSearch import utility as ut
import time

#
# print(ut.search_wiki('canvas'))
# #Give the path of the dataset
# pretime = time.time()
#pathOfDataset = 'C:/Users\linuk\Downloads\Staedel_Teilset/Objekte.xml'
pathOfDataset = 'generatedDataSet.xml'
tree = etree.parse(pathOfDataset)
root = tree.getroot()
artistList = root.getiterator('Artist')
for artist in artistList:
    try:
        sth = ut.search_img(artist.attrib['name'])
    except (KeyError,ValueError,IndexError) as e:
        print(e)


#

# # listing = ut.getAllArtist(root)
# # ut.create_artist_datenSet(listing,'C:/Users\linuk\Desktop/listAll.xml')
# # lstSum = ut.getAllStyle(root)
# # ut.create_style_tree(lstSum,'C:/Users\linuk\Desktop/listAll.xml','C:/Users\linuk\Desktop\lisss.xml')
#
# while True:
#     num = input('Please give the number of the painting:\n')
#     try:
#         title, name, createtime, refnum,record = ut.get_start_info(num, root)
#         info, dict_detail =ut.get_details(record)
#         print(refnum)
#         print(info)
#         print(dict_detail['artist'])
#         #print(ut.search_artist_xml(dict_detail['artist'],rootGene))
#        # print(ut.search_style_xml(dict_detail['style'],rootGene))
#     except AttributeError:
#         print('Can\'t find any thing' )
