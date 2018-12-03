# -*- coding: utf-8 -*-
from lxml import etree
import time
import requests
import re
from xml.dom.minidom import Document
from json.decoder import JSONDecodeError


def get_start_info(ref, root):
    """
    This method will search the title, name of artist and the created year from xml.

    Parameters
    ----------
    ref: :str
        Reference number or title of the object

    root: :str
        root of xml

    Returns
    -------
    tittle ::str

    name ::str

    year ::str
    """

    record = None
    if len(ref)<= 4:
        refnumberlist = root.getiterator('priref')
        for refnumber in refnumberlist:
            if refnumber.text == ref:
                record = refnumber.getparent()
                break
    else:
        titleList = root.getiterator('Title')
        pattern = '(%s).*'%(ref)
        for bigtitle in titleList:
            title = bigtitle.find('.//title')
            if re.match(pattern,title.text):
                record = title.getparent().getparent()
                break
    ###refNum#####
    ref = record.find('.//priref')
    refnumber = ref.text
    ###Title######
    title = record.find('.//Title')
    tt = title.find('.//title')
    titlestr = tt.text
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
        return titlestr, namestr, time,refnumber,record
    except (AttributeError,ValueError):
        end = 'oop'
    time = anfang
    return titlestr, namestr, time, refnumber, record



def get_details(record):
    dict = {}
    title = record.find('.//Title')
    tt = title.find('.//title')
    titlestr = tt.text
    dict['title'] = titlestr
    ##Diemension##
    height = ''
    width = ''
    dimens = record.getiterator('Dimension')
    for dim in dimens:
        if dim.find('.//term').get('occurrence') == '1':
            height = dim.find('.//dimension.value').text
            continue
        width = dim.find('.//dimension.value').text
        dimension = ' It is %s cm high, %s cm width.\n'%(height,width)
        dict['height'] = height
        dict['width'] = width
        break
    else:
        dimension = ''
    ##style##
    style = get_text_value(record,'.//school_style')
    ###technik##
    technik = get_text_value(record,'.//technique')
    ####Art
    art = get_text_value(record,'.//object_name')
    ####artist
    creator = record.find('.//Creator')
    name = creator.find('.//name')
    artist = name.text
    dict['style'] = style
    dict['technik'] = technik
    dict['art'] = art
    dict['artist'] = artist
    detail_Info = 'The \'%s\' is a %s %s in style %s created by %s.%s'%(titlestr, technik, art, style, artist,dimension)
    return detail_Info,dict


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


def search_wiki(namestr):
    """
    Get the description from DBpedia
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
        for description in descriptionList:
            if description['lang'] == 'de':
                final = 'German description: '+description['value']
                return final
    except (KeyError,JSONDecodeError):
        print('None english description!')
    try:
        add = 'https://en.wikipedia.org/w/api.php?action=query&titles= %s &prop=extracts&exintro&format=json&formatversion=2' % (
            APIname)
        datas = requests.get(add).json()
        querry = datas['query']
        page = querry['pages'][0]
        text = page['extract']
        if text != '':
            final += 'Englisch description: '
            final += re.sub(r'<.*?>', '', text)
            return final
    except KeyError:
        print('None english description!')
    try:
        add = 'https://de.wikipedia.org/w/api.php?action=query&titles= %s &prop=extracts&exintro&format=json&formatversion=2' % (
            APIname)
        datas = requests.get(add).json()
        querry = datas['query']
        page = querry['pages'][0]
        text = page['extract']
        if text == '':
            return 'No description'
        final += 'German description: '
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
        if artist.attrib['name'] == name :
            desc = artist.find('.//description')
            return desc.text
    return search_wiki(name)


def search_style_xml(name,root):
    """
        This method will search the description of style in the data set. If it is not in data set, then search it in internet.

        Parameters
        ----------
        name: :str
            name of style

        root: :str
            root of data set

        Returns
        -------
        description ::str

        """
    artistList = root.getiterator('style')
    for artist in artistList:
        if artist.attrib['stylename'] == name :
            desc = artist.find('.//description')
            return desc.text
    return search_wiki(name)


def create_artist_datenSet(listSum, fpath):
    doc = Document()  # create DOM object
    records = doc.createElement('records')
    AllPerson = doc.createElement('AllPerson')  # create root element
    doc.appendChild(records)
    records.appendChild(AllPerson)
    lenth = len(listSum[0])
    for i in range(lenth):
        artist = doc.createElement('Artist')
        artist.setAttribute('name', listSum[0][i])
        AllPerson.appendChild(artist)
        descrip = doc.createElement('description')
        artist.appendChild(descrip)
        text = doc.createTextNode((listSum[1][i]).encode('utf-8').decode('utf-8'))
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
        description = search_wiki(namestr)
        listDescrip.append(description)
        print('%d\n'%(i))
        print('Time: %.3f '%(time.time()-pre))
        i +=1
    print('\nDuration of the test: %.3f seconds' % (time.time() - pretime))
    sumList.append(listName)
    sumList.append(listDescrip)
    return sumList


def get_text_value(record,tagname):
    try:
        style = record.find(tagname)
        termList = style.getiterator('term')
        for term in termList:
            if term.get('lang')=='en-GB':
                return term.text
    except AttributeError:
        return 'Nothing'


def getAllStyle(root):
    listStyle = []
    listDescrip = []
    sumList = []
    recordList = root.getiterator('record')
    i=0
    pretime = time.time()
    for record in recordList:
        pre = time.time()
        style = get_text_value(record,'school_style')
        if (style in listStyle) or style == 'Nothing': continue
        listStyle.append(style)
        description = search_wiki(style)
        listDescrip.append(description)
        print('%d\n'%(i))
        print('Time: %.3f '%(time.time()-pre))
        i +=1
    print('\nDuration of the test: %.3f seconds' % (time.time() - pretime))
    sumList.append(listStyle)
    sumList.append(listDescrip)
    return sumList


def create_style_tree(listSum,fpath,outpath):
    tree = etree.parse(fpath)
    root = tree.getroot()
    all_style = etree.Element('Allstyle')  # create root element
    lenth = len(listSum[0])
    for i in range(lenth):
        styles = etree.Element('style')
        styles.set('stylename', listSum[0][i])
        all_style.append(styles)
        descrip = etree.Element('description')
        styles.append(descrip)
        # text = etree.Element((listSum[1][i]))
        descrip.text = listSum[1][i]
    root.append(all_style)
    tree.write(outpath, encoding="utf-8",xml_declaration=True)
