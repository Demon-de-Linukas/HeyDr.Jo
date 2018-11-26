# _*_ coding:utf-8 _*_


import xml.etree.ElementTree as et
from lxml import etree
from src.DataSearch import utility as ut
import time


#Give the path of the dataset
pretime = time.time()
pathOfDataset = 'C:/Users\linuk\Desktop\Staedel/Objekte.xml'
pathOfArtistSet = 'listAll.xml'
tree = etree.parse(pathOfDataset)
root = tree.getroot()
treeArtist = etree.parse(pathOfArtistSet)
rootArtist = treeArtist.getroot()
# listing = ut.getAllArtist(root)
# ut.create_xml(listing,'C:/Users\linuk\Desktop/listAll.xml')

title, name, createtime = ut.get_start_info('464', root)
print(ut.search_artist_xml(name,rootArtist))

# print('\nTitle is: ' +title +'\n')
# print('Artist is: ' +name +'\n')
# print('Created time is: ' +createtime +'\n')
# print(ut.search_artist_wiki(name))
# print('\nDuration of the test: %.3f seconds'%(time.time()-pretime))