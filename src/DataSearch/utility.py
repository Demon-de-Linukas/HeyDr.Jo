# -*- coding: utf-8 -*-
from lxml import etree
import time
import requests
import re
import json
import csv
import datetime
from xml.dom.minidom import Document
from json.decoder import JSONDecodeError
import os
import logging

logPath = 'userCache.csv'
fieldnames = ['userID', 'knowInfo', 'artist', 'refnumber', 'style', 'period', 'chatting', 'search']
commentPath = 'Comment-Database.xml'


def initlog(logadress):
    today = str(datetime.date.today())
    try:
        os.mkdir(logadress+today)
    except (FileExistsError,FileNotFoundError) as e:
        print(e)
    # create logger with 'spam_application'
    logger = logging.getLogger('chatBot')
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler('%s/chatBot.log'%(logadress+today))
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


def search_related(current,root):
    relatedlist =[]
    ref = current.replace('_', ' ')
    refnumberlist = root.getiterator('object_number')
    for refnumber in refnumberlist:
        if refnumber.text.upper() == ref.upper():
            record = refnumber.getparent()
            if record.tag != 'record':
                continue
            break
    assolist = record.getiterator('Association_object')
    for asso in assolist:
        try:
            refn = asso.find('./association.object.object_number').find('./object_number')
            if refn.text == current or refn.text in relatedlist:
               continue
            if refn.text is not None:
                relatedlist.append(refn.text)
        except (AttributeError, EOFError, IndexError) as e:
            print(e)
    rellist = record.getiterator('Related_object')
    for rel in rellist:
        try:
            num = rel.find('./related_object_reference')
            if num.text == current or num.text in relatedlist:
                continue
            if num.text is not None:
                relatedlist.append(num.text)
        except (AttributeError, EOFError, IndexError) as e:
            print(e)
    return relatedlist


def search_pic_of_artist(artiName,current,root):
    relatedlist =[]
    creatorList=root.getiterator('Creator')
    for creator in creatorList:
        if creator.find('./name').text == artiName:
            recordcache = creator.getparent().getparent()
            number = recordcache.find('./object_number')
            if number.text == current:
                continue
            if number.text is not None:
                relatedlist.append(number.text)
            if len(relatedlist) >4:
                return relatedlist
    return relatedlist


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
    ref = ref.replace('_',' ')
    refnumberlist = root.getiterator('object_number')
    for refnumber in refnumberlist:
        if refnumber.text.upper() == ref.upper():
            record = refnumber.getparent()
            if record.tag != 'record':
                continue
            break
    if record == None:
        titleList = root.getiterator('Title')
        pattern = '(%s).*'%(ref)
        for bigtitle in titleList:
            title = bigtitle.find('.//title')
            if re.match(pattern,title.text):
                record = title.getparent().getparent()
                break
    ###refNum#####
    ref = record.find('object_number')
    refnumber = ref.text.replace(' ','_')
    ###Title######
    title = record.find('Title')
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
    if style =='Nothing':
        detail_Info = 'The \'%s\' is a %s %s created by %s.%s' % (
        titlestr, technik, art,  artist, dimension)
        dict['style'] = ''
        return detail_Info, dict
    detail_Info = 'The \'%s\' is a %s %s in style %s created by %s.%s'%(titlestr, technik, art, style, artist,dimension)
    return detail_Info,dict


def name_API(nameString):
    """
    Covert name string to an acceptable format for API
    :param nameString:
    :return:
    """
    if 'd. Ä.'in nameString:
        sasd = nameString.replace('d. Ä.', 'the_Elder')
    s1 = nameString.replace('d. Ä.', 'the_Elder')
    s2 = s1.replace('d. J.', 'der Jüngere')
    s3 = s2.replace('d. V.', 'the_Father')
    #s3 = sa.replace('.', '')
    # s4 = s3.replace(' ', '_')
    # s5 = s4.replace('-', '_')
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
        if 'http://dbpedia.org/ontology/wikiPageRedirects' in artist:
            APIname = artist['http://dbpedia.org/ontology/wikiPageRedirects'][0]['value'][28:]
            fi = search_wiki(APIname)
            return fi

        descriptionList = artist['http://dbpedia.org/ontology/abstract']
        for description in descriptionList:
            if description['lang'] == 'en':
                final = 'Englisch description: '+description['value']
                return final
        for description in descriptionList:
            if description['lang'] == 'de':
                final = 'German description: '+description['value']
                return final
    except (KeyError,JSONDecodeError) as e:
        print(e)
    try:
        add = 'https://en.wikipedia.org/w/api.php?action=query&titles= ' \
              '%s &prop=extracts&exintro&format=json&formatversion=2' % (
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
        aName = APIname.replace('the_Elder', 'der_Ältere')
        add = 'https://de.wikipedia.org/w/api.php?action=query&titles= ' \
              '%s &prop=extracts&exintro&format=json&formatversion=2' % (
            aName)
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
    if name == '':
        return 'Can\'t find any information....'
    artistList = root.getiterator('style')
    for artist in artistList:
        if artist.attrib['stylename'] == name :
            desc = artist.find('.//description')
            return desc.text
    return search_wiki(name)


def create_artist_datenSet(listSum, fpath):
    '''
    Exampel:
        listing = ut.getAllArtist(root)
        ut.create_artist_datenSet(listing, 'C:/Users\linuk\Desktop/listAll.xml')
        lstSum = ut.getAllStyle(root)
        ut.create_style_tree(lstSum, 'C:/Users\linuk\Desktop/listAll.xml','C:/Users\linuk\Desktop\lisss.xml')
    :param listSum:
    :param fpath:
    :return:
    '''
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
        if i == 63:
            print('Here!')
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


def search_img(namestr):
    """
    Get the description from Wikimedia
    Parameters
    ----------
    namestr ::
        str name string from xml data set
    Returns
    -------
    description ::str
    """
    APIname = name_API(namestr)
    nPos = namestr.index(',')
    nachname = namestr[0:nPos]
    S = requests.Session()
    URL = "https://de.wikipedia.org/w/api.php"
    mediaURL = 'https://de.wikipedia.org/wiki/%s#/media/'% (APIname)

    PARAMS = {
        'action': 'query',
        'format': 'json',
        'prop': 'images',
        'titles': APIname
    }

    saveAdres = 'D:\Workspace\HeyDr.Jo\src\DataSearch\d/%s.jpg'%(APIname)

    datas= S.get(url=URL, params=PARAMS)
    datas.encoding = ';utf-8'
    jData = json.loads(datas.text)
    print(jData)

    pages =jData['query']['pages']
    for ii in pages:
        id = pages[ii]
        images = id['images']
        for srcImg in images:
            src = srcImg['title']
            if '.jpg' not in src:
                continue
            if ('selbst' in src.lower()) or ('porträt' in src.lower()) or ('self' in src.lower()):
                res= mediaURL+src
                resUrl = res.replace(' ', '_')
                print(resUrl)
                resPage = requests.get(resUrl)
                downPage = re.findall(r'https://upload.*?jpg\"', resPage.text)
                downUrl = downPage[0][0:(len(downPage[0])-1)]
                tryimg = requests.get(downUrl)
                print(downPage[0])
                with open(saveAdres, 'a+') as f:
                    f.write(tryimg.content)
                    return f
        for srcImg in images:
            src = srcImg['title']
            if '.jpg' not in src:
                continue
            if nachname.lower() in src.lower():
                res = mediaURL + src
                resUrl = res.replace(' ', '_')
                print(resUrl)
                resPage = requests.get(resUrl)
                downPage = re.findall(r'https://upload.*?jpg\"', resPage.text)
                downUrl = downPage[0][0:(len(downPage[0]) - 1)]
                tryimg = requests.get(downUrl)
                print(downPage[0])
                with open(saveAdres, 'a+') as f:
                    f.write(tryimg.content)
                    return f


def get_user_cache(userid, key):
    global logPath
    with open(logPath, "rt", encoding='utf-8') as log:
        reader = csv.DictReader(log)
        for row in reader:
            if row['userID'] == userid:
                return row[key]


def write_user_cache(userid, key, value):
    global logPath,fieldnames
    csvdict = csv.DictReader(open(logPath, 'rt', encoding='utf-8', newline=''))
    dictrow = []
    for row in csvdict:
        if row['userID'] == userid:
            row[key] = value
        # rowcache.update(row)
        dictrow.append(row)

    with open(logPath, "w+", encoding='utf-8', newline='') as lloo:
        # lloo.write(new_a_buf.getvalue())
        wrier = csv.DictWriter(lloo, fieldnames)
        wrier.writeheader()
        for wowow in dictrow:
            wrier.writerow(wowow)


def init_comment():
    global commentPath
    doc = Document()  # create DOM object
    record = doc.createElement('records')
    doc.appendChild(record)
    f = open(commentPath, 'w', encoding='utf-8')
    doc.writexml(f, indent='\t', newl='\n', addindent='\t', encoding='utf-8')
    f.close()


def write_comment(userid,message):
    global commentPath
    ref = get_user_cache(userid, 'refnumber')
    username = message.chat.first_name
    comment = message.text
    tree = etree.parse(commentPath)
    root = tree.getroot()
    rec = etree.Element('rec')
    new_child(rec, comment, 'comment')
    new_child(rec, ref, 'refNumber')
    new_child(rec, username, 'userName')
    root.append(rec)
    tree.write(commentPath, encoding="utf-8",xml_declaration=True)

    # posts = db.posts
    #
    # pars={'refNumber': ref,
    #       'userName': username,
    #       'comment': comment,
    #       'like':like}
    # posts.insert_one(pars).inserted_id


def new_child(root,comment, key):
    com = etree.Element(key)
    com.text = comment
    root.append(com)


def read_comment(ref):
    global commentPath
    recordList = []
    tree = etree.parse(commentPath)
    root = tree.getroot()
    refnumberlist = root.getiterator('refNumber')
    for refnumber in refnumberlist:
        if refnumber.text.upper() == ref.upper():
            record = refnumber.getparent()
            if record.tag != 'rec':
                continue
            else:
                recordList.append(record)
    return recordList


    # posts = db.posts
    # try:
    #     comments = posts.find({'refNumber': refNumber})
    #     return comments
    # except pymongo.errors.CursorNotFound as e:
    #     print(e)