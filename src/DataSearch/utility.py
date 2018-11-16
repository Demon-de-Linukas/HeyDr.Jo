from lxml import etree


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


tree = etree.parse('C:/Users\linuk\Desktop\Staedel_Teilset/Objekte.xml')
root = tree.getroot()
title, name, time = get_start_info('13', root)
print('\nTitle is: ' +title +'\n')
print('Artist is: ' +name +'\n')
print('Created time is: ' +time +'\n')
