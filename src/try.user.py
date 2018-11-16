# _*_ coding:utf-8 _*_


import xml.etree.ElementTree as et
from lxml import etree


tree = etree.parse('C:/Users\linuk\Desktop\Staedel_Teilset/Objekte.xml')
root = tree.getroot()
record = None
refnumberlist = root.getiterator('priref')
for refnumber in refnumberlist:
    if refnumber.text == '13':
        record = refnumber.getparent()




root = etree.Element("13")