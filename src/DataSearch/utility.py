# -*- coding: utf-8 -*-
from lxml import etree
import time
import requests
import re
from xml.dom.minidom import Document
from json.decoder import JSONDecodeError


def get_start_info(number, root):
    """
    This method will search the title, name of artist and the created year from xml.

    Parameters
    ----------
    number: :str
        Reference number of the object

    root: :str
        root of xml

    Returns
    -------
    tittle ::str

    name ::str

    year ::str
    """
    record = None
    refnumberlist = root.getiterator('priref')
    for refnumber in refnumberlist:
        if refnumber.text == number:
            record = refnumber.getparent()
            break
    ###Title######
    title = record.find('.//title')
    titlestr = title.text
    ###artist#####
    creator = record.find('.//Creator')
    name = creator.find('.//name')
    namestr = name.text
    ###Time######
    product = record.find('.//Production_date')
    pre = ''
    end = ''

    anfang = product.find('.//production.date.start').text
    try:
        pre = product.find('.//production.date.start.prec').text
        end = product.find('.//production.date.end').text
        time = pre + ' ' + anfang + ' - ' + end
        return titlestr, namestr, time
    except AttributeError:
        end = 'oop'
    time = anfang


    return titlestr, namestr, time


def name_API(str):
    """
    Covert name string to an acceptable format for API
    :param str:
    :return:
    """
    s1 = str.replace('d. Ä.', 'der Ältere')
    s2 = s1.replace('d. J.', 'der Jüngere')
    s3 = s2.replace('d. V.', 'der Vetter')
    s4 = s3.replace(' ', '_')
    s5 = s4.replace('-', '_')
    try:
        nPos = s3.index(',')
        s4 = s3.replace(' ', '_')
        nachname = s4[0:nPos]
        afterCa = s4[(nPos + 2):]
        all = afterCa + '_' + nachname
        return all
    except ValueError:
        all = s3.replace(' ', '_')
        return all


def search_artist_wiki(namestr):
    """
    Get the description of artist from DBpedia
    Parameters
    ----------
    namestr ::
        str name string from xml data set
    Returns
    -------
    description ::str
    """
    APIname = name_API(namestr)
    final = ''
    try:
        jadd = 'http://dbpedia.org/data/' + APIname + '.json'
        add = 'http://dbpedia.org/resource/' + APIname
        data = requests.get(jadd).json()
        artist = data[add]
        # TODO: Language change?
        descriptionList = artist['http://dbpedia.org/ontology/abstract']
        for description in descriptionList:
            if description['lang'] == 'en':
                final = 'Englisch description: '+description['value']
                return final
            if description['lang'] == 'de':
                final = 'German description: '+description['value']
                return final
    except (KeyError,JSONDecodeError):
        print('None english description!')
    try:
        final += 'German description: '
        add = 'https://de.wikipedia.org/w/api.php?action=query&titles= %s &prop=extracts&exintro&format=json&formatversion=2' % (
            APIname)
        datas = requests.get(add).json()
        querry = datas['query']
        page = querry['pages'][0]
        text = page['extract']
        final += re.sub(r'<.*?>', '', text)
        return final
    except KeyError:
        return 'No description'


def search_artist_xml(name,root):
    """
        This method will search the description of artist in the data set. If it is not in data set, then search it in internet.

        Parameters
        ----------
        name: :str
            name of artist

        root: :str
            root of data set

        Returns
        -------
        description ::str

        """
    artistList = root.getiterator('Artist')
    for artist in artistList:
        if artist.attrib['name'] == name:
            desc = artist.find('.//descriprion')
            return desc.text
    return search_artist_wiki(name)

def create_xml(list, fpath):
    doc = Document()  # create DOM object
    AllPerson = doc.createElement('AllPerson')  # create root element
    doc.appendChild(AllPerson)
    lenth = len(list[0])
    for i in range(lenth):
        artist = doc.createElement('Artist')
        artist.setAttribute('name', list[0][i])
        AllPerson.appendChild(artist)
        descrip = doc.createElement('descriprion')
        artist.appendChild(descrip)
        text = doc.createTextNode((list[1][i]).encode('utf-8').decode('utf-8'))
        descrip.appendChild(text)
    f = open(fpath, 'w', encoding='utf-8')
    doc.writexml(f, indent='\t', newl='\n', addindent='\t', encoding='utf-8')
    f.close()


def getAllArtist(root):
    listName = []
    listDescrip = []
    sumList = []
    recordList = root.getiterator('record')
    i=0
    pretime = time.time()
    for record in recordList:
        pre = time.time()
        creator = record.find('.//Creator')
        name = creator.find('.//name')
        namestr = name.text
        if namestr in listName: continue
        listName.append(namestr)
        description = search_artist_wiki(namestr)
        listDescrip.append(description)
        print('%d\n'%(i))
        print('Time: %.3f '%(time.time()-pre))
        i +=1
    print('\nDuration of the test: %.3f seconds' % (time.time() - pretime))
    sumList.append(listName)
    sumList.append(listDescrip)
    return sumList
