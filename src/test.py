# _*_ coding:utf-8 _*_


import xml.etree.ElementTree as et
from lxml import etree
from src.DataSearch import utility as ut
import time

#
# ut.search_wiki('art photography')
# #Give the path of the dataset
# pretime = time.time()
pathOfDataset = 'C:/Users\linuk\Desktop\Staedel/Objekte.xml'
# pathOfArtistSet = 'listAll.xml'
tree = etree.parse(pathOfDataset)
root = tree.getroot()


# treeArtist = etree.parse(pathOfArtistSet)
# rootArtist = treeArtist.getroot()

listing = ut.getAllArtist(root)
ut.create_artist_datenSet(listing,'C:/Users\linuk\Desktop/listAll.xml')
lstSum = ut.getAllStyle(root)
ut.create_style_tree(lstSum,'C:/Users\linuk\Desktop/listAll.xml','C:/Users\linuk\Desktop\lisss.xml')


# num = input('Please give the number of the painting:\n')
# title, name, createtime,record = ut.get_start_info(num, root)
# style = ut.get_style(record)
# print(ut.search_wiki(style))
# print(ut.search_artist_xml(name,rootArtist))

# print('\nTitle is: ' +title +'\n')
# print('Artist is: ' +name +'\n')
# print('Created time is: ' +createtime +'\n')
# print(ut.search_artist_wiki(name))
# print('\nDuration of the test: %.3f seconds'%(time.time()-pretime))