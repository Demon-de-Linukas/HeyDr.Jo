import time
import telebot as tb
from lxml import etree
from DataSearch import utility as ut
from ChatBot import dictionary as cc


token = '706415631:AAG1Y6sfLmvxU_TENOaVwGA3hzXdaGJiaWo'
pathOfPhoto = 'C:/Users\linuk\Downloads\Staedel_Teilset\Abbildungen_Teilset/'
pathOfDataset = 'C:/Users\linuk\Downloads\Staedel_Teilset/Objekte.xml'
pathOfGene = 'C:/Users\linuk\Workspace\HeyDr.Jo\src/ChatBot/generatedDataSet.xml'
tree = etree.parse(pathOfDataset)
root = tree.getroot()
__currentrecord__ = None
__knowInfo__ = 0
__artistName__ =''
__style__ = ''

treeGene = etree.parse(pathOfGene)
rootGene = treeGene.getroot()
dictionary = cc.dict
bot = tb.TeleBot(token)


def get_semantic(text,dict):
    for dd in dict:
        if text in dict[dd]:
           return dd


def get_from_data(command,rootAll,rootGene):
    return ut.get_start_info(command,rootAll)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, u"Dear customer, I am Dr. Jo! "
                          u"\nToday I will be your museum guide "
                          u"and provide you some professional and interesting information about our art objects! "
                          u"\nWhich object are you currently looking at or interested in? ")


@bot.message_handler(content_types='text')
def get_input(message):#List):
    try:
        global __currentrecord__, __knowInfo__, __artistName__, __style__
        chatid = message.chat.id
        #if message.text.upper() == 'YES' and __knowInfo__ == 1:
          #  detail_Info, dict = ut.get_details(__currentrecord__)
           # __artistName__ = dict['artist']
           # __style__ = dict['style']
           # bot.reply_to(message, detail_Info)
            #chatid = message.chat.id
           # __knowInfo__=2
            #return
        if message.text.upper()=='YES' and __knowInfo__== 2:
            chatid = message.chat.id
            bot.send_message(chatid,u'What would you like to know, ' \
                ' introductions about the artist or style or some related objects of this object in our museum?' \
                '\n(artist,style,related objects)')
            __knowInfo__=3
            return
        elif message.text.upper()=="ARTIST" and __knowInfo__==3:
            chatid=message.chat.id
            bot.send_message(chatid, ut.search_artist_xml(__artistName__,rootGene) )
            __knowInfo__ = 2
            bot.send_message(chatid, u'\n\n\nWould you like to know about the style or '
                                     u'related objects of this object in our museum? ')
            return
        elif message.text.upper()=="STYLE" and __knowInfo__==3 :
            chatid = message.chat.id
            bot.send_message(chatid,ut.search_style_xml(__style__,rootGene))
            __knowInfo__ = 2
            bot.send_message(chatid, u'\n\n\nWould you like to know about the artist or '
                                     u'related objects of this object in our museum? ')
            return

        elif message.text.upper()=="RELATED OBJECTS" and __knowInfo__==3:
            chatid = message.chat.id
            bot.send_message(chatid, u'still working, Coming Soon...')
            __knowInfo__= 2
            bot.send_message(chatid, u'\n\n\nWould you like to know about the style or '
                                     u'artist of this object? ')
            return

        elif message.text.upper() == 'NO':
            bot.send_message(chatid,  u'Please give the number or the name of your interested object!')
            __knowInfo__ = 0
            return
        else:
            print(str(__knowInfo__))
            #for message in messageList:
            title, artist, period, refnum,record = get_from_data(message.text, root, rootGene)
            __artistName__ = artist
            __currentrecord__ = record
            detail_Info, dict = ut.get_details(__currentrecord__)
            __style__ = dict['style']
            bot.reply_to(message, 'Title: \n%s\n\nCreator: \n%s\n\nCreated period: \n%s\n\n\n%s'%(title,artist,period,detail_Info))
            bot.send_message(chatid,  u'Sending photo... Please wait')
            photo = open(pathOfPhoto+refnum+'.png','rb')
            bot.send_photo(chatid,photo)
            bot.send_message(chatid,  u'Should I introduce more information about the artist or style of this object?')
            __knowInfo__ =2
            return
    except (AttributeError):
        bot.send_message(chatid,'Sorry I don\'t understand!')


if __name__ == '__main__':
        #bot.set_update_listener(get_input)
        while True:
            bot.polling(none_stop=True)
            time.sleep(1)
