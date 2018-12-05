import datetime
import telebot as tb
import random
from lxml import etree
from src.DataSearch import utility as ut
from src.ChatBot import dictionary as cc


token = '706415631:AAG1Y6sfLmvxU_TENOaVwGA3hzXdaGJiaWo'
pathOfPhoto = 'C:/Users\linuk\Desktop\Staedel\Abbildungen/compressed/'
pathOfDataset = 'C:/Users\linuk\Desktop\Staedel/Objekte.xml'
pathOfGene = 'D:\Workspace_Pycharm\HeyDr.Jo\src\ChatBot\generatedDataSet.xml'
tree = etree.parse(pathOfDataset)
root = tree.getroot()
__currentrecord__ = None
__knowInfo__ = 0
__artistName__ =''
__style__ = ''

treeGene = etree.parse(pathOfGene)
rootGene = treeGene.getroot()
__dict__ = cc.dict
bot = tb.TeleBot(token)


def get_semantic(text,dict):
    for dd in dict:
        if text in dict[dd]:
           return dd


def get_from_data(command,rootAll,rootGene):
    return ut.get_start_info(command,rootAll)

@bot.message_handler(commands=['server'])
def send_welcome(message):
    global __knowInfo__,__currentrecord__,__artistName__,__style__
    bot.reply_to(message, 'Step:%s\nArtist:%s\nStyle:%s'%(__knowInfo__,__artistName__,__style__))


@bot.message_handler(commands=['start', 'help', 'restart'])
def send_welcome(message):
    global __knowInfo__,__currentrecord__
    if 'restart'in message.text:
        __knowInfo__ = 0
        __currentrecord__ = None
    bot.reply_to(message, u"Dear customer, I am Dr. Jo! "
                          u"\nToday I will be your museum guide "
                          u"and provide you some professional and interesting information about our art objects! "
                          u"\nWhich object are you currently looking at or interested in? ")




@bot.message_handler(content_types='text')
def get_input(message):
    print(message.text)
    try:
        global __currentrecord__, __knowInfo__, __artistName__, __style__, __dict__
        chatid = message.chat.id
        if message.text.lower() in __dict__['yes'] and __knowInfo__== 2:
            chatid = message.chat.id
            bot.send_message(chatid,u'What would you like to know, ' \
                ' introductions about the artist or style or some related objects of this object in our museum?' \
                '\n\n[artist,style,related objects]')
            __knowInfo__=3
            return
        elif message.text.upper()=="ARTIST" and __knowInfo__==3:
            chatid=message.chat.id
            bot.send_message(chatid, ut.search_artist_xml(__artistName__,rootGene) )
            __knowInfo__ = 2
            bot.send_message(chatid, u'\n\n\nDo you want to know more Information?\n\n[Yes or No]')
            return
        elif message.text.upper()=="STYLE" and __knowInfo__==3 :
            chatid = message.chat.id
            bot.send_message(chatid,ut.search_style_xml(__style__,rootGene))
            __knowInfo__ = 2
            bot.send_message(chatid, u'\n\n\nDo you want to know more information?\n\n[Yes or No]')
            return

        elif message.text.upper()=="RELATED OBJECTS" and __knowInfo__==3:
            chatid = message.chat.id
            bot.send_message(chatid, u'still working, Coming Soon...')
            __knowInfo__= 2
            bot.send_message(chatid, u'\n\n\nDo you want to know more Information?\n\n[Yes or No]')
            return

        elif message.text.upper() == 'NO':
            bot.send_message(chatid,  u'Please give the number or the name of your interested object!')
            __knowInfo__ = 0
            return
        elif message.text.lower() in __dict__['hello']:
           greating(message)
           return
        elif message.text.lower() in __dict__['thanks']:
            n=random.choice(__dict__['you are welcome'])
            bot.send_message(chatid,n)
            return
        elif message.text.lower() in __dict__['bye']:
            m = random.choice(__dict__['bye'])
            bot. send_message(chatid,m)

        elif __knowInfo__ == 0:
            print(str(__knowInfo__))
            #for message in messageList:
            title, artist, period, refnum,record = get_from_data(message.text, root, rootGene)
            __artistName__ = artist
            __currentrecord__ = record
            detail_Info, listing = ut.get_details(__currentrecord__)
            __style__ = listing['style']
            bot.reply_to(message, 'Title: \n%s\n\nCreator: \n%s\n\nCreated period: \n%s\n\n\n%s'%(title,artist,period,detail_Info))

            try:
                photo = open(pathOfPhoto+refnum+'.png','rb')
                bot.send_message(chatid, u'Sending photo... Please wait')
                bot.send_photo(chatid,photo)
            except (FileNotFoundError):
                print('no photo')
            bot.send_message(chatid,  u'Should I introduce more information about the artist or style of this object?')
            __knowInfo__ =2
            return
        elif (message.text.upper() !="ARTIST" and message.text.upper()!="STYLE" and message.text.upper()!="RELATED OBJECTS")\
                and __knowInfo__!=3 and len(message.text)>3:
            tt = ut.search_wiki(message.text)
            bot.reply_to(message,tt)
        else:
            bot.send_message(chatid, 'Sorry I don\'t understand! Please follow the instruction above!')
    except (AttributeError):
        bot.send_message(chatid,'Sorry I don\'t understand! Please follow the instruction above or check the input!')
        return


@bot.message_handler(content_types=['text'])
def greating(message):
    bot.reply_to(message, '%s!' % message.text)
    send_welcome(message)


if __name__ == '__main__':
    time = datetime.datetime.now()
    #    print Exception
    print("Bot started: " + str(time))
    #bot.set_update_listener(get_input)
    while True:
        bot.polling(none_stop=True)
        time.sleep(0.5)
