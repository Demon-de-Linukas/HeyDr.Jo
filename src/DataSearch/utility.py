from lxml import etree
import requests



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
    #Title######
    title = record.find('.//title')
    titlestr = title.text

    creator = record.find('.//Creator')
    name = creator.find('.//name')
    namestr = name.text

    product = record.find('.//Production_date')
    pre =''
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
    nPos = str.index(',')
    nachname = str[0:nPos]
    afterCa = str[(nPos+2):]
    after = afterCa.replace(' ', '_')
    all=after+'_'+nachname
    return all


def search_artist(namestr):
    """
    Get the description of artist from DBpedia
    :param namestr: name string from xml data set
    :return: Description
    """
    APIname=name_API(namestr)
    jadd = 'http://dbpedia.org/data/' + APIname + '.json'
    add = 'http://dbpedia.org/resource/' + APIname
    data = requests.get(jadd).json()
    artist = data[add]
    #TODO: Language change?
    description = artist['http://dbpedia.org/ontology/abstract'][2]['value']
    return description
