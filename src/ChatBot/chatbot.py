import datetime
import telebot as tb
import random
import pandas as pd

from lxml import etree
from DataSearch import utility as ut
from ChatBot import dictionary as cc
from chatterbot import ChatBot

import csv

token = '703120726:AAHrVpXPG-z0omcSTqSC0Q8Ze5tGBIFXM-o'#'706415631:AAG1Y6sfLmvxU_TENOaVwGA3hzXdaGJiaWo'
pathOfPhoto = 'D:\Workspace\Staedel\Abbildung/'
pathOfDataset = 'D:\Workspace\Staedel/Objekte.xml'
pathOfGene = 'generatedDataSet.xml'
tree = etree.parse(pathOfDataset)
root = tree.getroot()
treeGene = etree.parse(pathOfGene)
rootGene = treeGene.getroot()
__dict__ = cc.dict
bot = tb.TeleBot(token)

logPath = 'userCache.csv'
fieldnames = ['userID', 'knowInfo', 'artist', 'style', 'period', 'chatting']

chattingBot = ChatBot("Training Example",
                      read_only=False,
                      storage_adapter="chatterbot.storage.SQLStorageAdapter",
                      logic_adapters=[
                          {'import_path': 'chatterbot.logic.MathematicalEvaluation'
                           },
                          {'import_path': 'chatterbot.logic.BestMatch'
                           },
                          {'import_path': 'chatterbot.logic.SpecificResponseAdapter',
                           'input_text': 'Who are you',
                           'output_text': 'I am Dr. Jo, a chat bot of Städel Museum :-)'}
                      ],
                      database="../database.db"
                      )


def init(userid):
    write_user_cache(userid, 'knowInfo', '0')
    write_user_cache(userid, 'artist', '')
    write_user_cache(userid, 'style', '')
    write_user_cache(userid, 'period', '')
    write_user_cache(userid, 'chatting', 'False')
    return


def get_semantic(text, dict):
    for dd in dict:
        if text in dict[dd]:
            return dd


def get_from_data(command, rootAll, rootGene):
    return ut.get_start_info(command, rootAll)


@bot.message_handler(commands=['chat', 'endChat'])
def chatter_command(message):
    userid = str(message.from_user.id)
    with open(logPath, "rt", encoding='utf-8') as log:
        reader = csv.DictReader(log)
        userList = [row['userID'] for row in reader]
    userid = str(message.from_user.id)
    if userid not in userList:
        initCache(userid)
    if message.text.upper() == '/ENDCHAT':
        write_user_cache(userid, 'chatting', 'False')
        bot.reply_to(message, 'End chatting. See ya!')
        return
    write_user_cache(userid, 'chatting', 'True')
    bot.reply_to(message,
                 'Okay, now let\'s chat!\nTo end the chatting and go back to Städel Museum, use command \'/endChat\'!')
    return


@bot.message_handler(commands=['server'])
def send_welcome(message):
    userid = str(message.from_user.id)
    bot.send_message(message.chat.id, 'Step:%s\nArtist:%s\nStyle:%s' % (get_user_cache(userid, 'knowInfo'),
                                                                        get_user_cache(userid, 'artist'),
                                                                        get_user_cache(userid, 'style')))

@bot.message_handler(commands=['start', 'help', 'restart'])
def send_welcome(message):
    userid = str(message.from_user.id)
    init(userid)
    bot.send_message(message.chat.id, 'Welcome to Hey Dr.Jo chat bot!\nTo start visiting meseum please enter'
                                  ' /visit\nTo chat with me please use command /chat.'
                                  '\nTo restart the chat bot please use command /restart.')


@bot.message_handler(commands=['visit'])
def greating(message):
    bot.send_message(message.chat.id, "Dear customer, I am Dr. Jo!\n"
                                      "Today I will be your museum guide and provide you some "
                                      "professional and interesting information about our art objects!\n\n"
                                      "Which object are you currently looking at or interested in?\n\n"

                                      "[<b>Ref. number</b> or <b>Title</b> of object]", parse_mode='HTML')


@bot.message_handler(content_types='text')
def get_input(message):
    global logpath
    print(message.text)
    with open(logPath, "rt", encoding='utf-8') as log:
        reader = csv.DictReader(log)
        userList = [row['userID'] for row in reader]
    userid = str(message.from_user.id)
    if userid not in userList:
        initCache(userid)

    try:
        chatting = get_user_cache(userid, 'chatting')
        knowInfo = get_user_cache(userid, 'knowInfo')
        artist = get_user_cache(userid, 'artist')
        style = get_user_cache(userid, 'style')
        period = get_user_cache(userid, 'period')
    except (AttributeError):
        print('Creating new user cache...')

    try:
        chatid = message.chat.id
        if 'ho are you' in message.text:
            statment = 'Who are you'
            response = chattingBot.get_response(statment)
            bot.send_message(chatid, response)
            return
        elif get_user_cache(userid, 'chatting')=='True':
            statment = message.text
            response = chattingBot.get_response(statment)
            bot.send_message(chatid, response)
            return
        elif message.text.lower() in __dict__['yes'] and get_user_cache(userid, 'knowInfo') == '2':
            chatid = message.chat.id
            bot.send_message(chatid, u'What would you like to know, ' \
                                     'introductions about the artist, time, style or some related objects of this object in our museum?' \
                                     '\n\n[<b>artist,time,style</b>]', parse_mode='HTML')
            write_user_cache(userid=userid,key='knowInfo',value='2')
            return
        elif "ARTIST" in message.text.upper() and get_user_cache(userid, 'knowInfo') == '2':
            chatid = message.chat.id
            artName = get_user_cache(userid, 'artist')
            bot.send_message(chatid, ut.search_artist_xml(artName, rootGene))
            try:
                picname = ut.name_API(artName)
                photo = open(pathOfPhoto + picname + '.jpg', 'rb')
                bot.send_message(chatid, u'Sending photo... Please wait')
                bot.send_photo(chatid, photo,caption=artName)
            except (FileNotFoundError):
                print('no photo')
            write_user_cache(userid=userid,key='knowInfo',value='2')
            bot.send_message(chatid, '\n\n\nDo you want to know more Information?\n\n[<b>Yes</b> or <b>No</b>]',
                             parse_mode='HTML')
            return
        elif "STYLE" in message.text.upper() and get_user_cache(userid, 'knowInfo') == '2':
            chatid = message.chat.id
            bot.send_message(chatid, ut.search_style_xml(get_user_cache(userid, 'style'), rootGene))
            write_user_cache(userid=userid,key='knowInfo',value='2')
            bot.send_message(chatid, '\n\n\nDo you want to know more Information?\n\n[<b>Yes</b> or <b>No</b>]',
                             parse_mode='HTML')
            return

        elif "TIME" in message.text.upper() and get_user_cache(userid, 'knowInfo') == '2':
            chatid = message.chat.id
            bot.send_message(chatid, search_Time(get_user_cache(userid, 'period')))
            write_user_cache(userid=userid,key='knowInfo',value='2')
            bot.send_message(chatid, '\n\n\nDo you want to know more Information?\n\n[<b>Yes</b> or <b>No</b>]',
                             parse_mode='HTML')
            return

        elif message.text.upper() == "RELATED OBJECTS" and get_user_cache(userid, 'knowInfo') == '2':
            chatid = message.chat.id
            bot.send_message(chatid, u'still working, Coming Soon...')
            write_user_cache(userid=userid,key='knowInfo',value='2')
            bot.send_message(chatid, '\n\n\nDo you want to know more Information?\n\n[<b>Yes</b> or <b>No</b>]',
                             parse_mode='HTML')
            return

        elif message.text.upper() == 'NO':
            bot.send_message(chatid, u'Please give the number or the name of your interested object!')
            write_user_cache(userid=userid,key='knowInfo',value='0')
            return
        elif message.text.lower() in __dict__['hello'] and get_user_cache(userid, 'knowInfo') == '0':
            greating(message)
            return
        elif message.text.lower() in __dict__['hello'] and get_user_cache(userid, 'knowInfo') != '0':
            statment = message.text
            response = chattingBot.get_response(statment)
            bot.send_message(chatid, response)
            return
        elif message.text.lower() in __dict__['thanks']:
            n = random.choice(__dict__['you are welcome'])
            bot.send_message(chatid, n)
            return
        elif message.text.lower() in __dict__['bye']:
            m = random.choice(__dict__['bye'])
            bot.send_message(chatid, m)

        elif get_user_cache(userid, 'knowInfo') == '0':
            print(get_user_cache(userid, 'knowInfo'))
            # for message in messageList:
            title, artist, period, refnum, record = ut.get_start_info(message.text, root)
            detail_Info, listing = ut.get_details(record)

            write_user_cache(userid,'knowInfo','0' )
            write_user_cache(userid,'artist',artist )
            write_user_cache(userid,'style',listing['style'] )
            write_user_cache(userid,'period',period )
            write_user_cache(userid,'chatting','False' )

            bot.reply_to(message, 'Title: \n%s\n\nCreator: \n%s\n\nCreated period: \n%s\n\n\n%s' % (
            title, artist, period, detail_Info))

            try:
                photo = open(pathOfPhoto + refnum + '.png', 'rb')
                bot.send_message(chatid, u'Sending photo... Please wait')
                bot.send_photo(chatid, photo)
            except (FileNotFoundError):
                print('no photo')
            bot.send_message(chatid,
                             u'Should I introduce more information about the artist or style of this object?\n\n[<b>Yes</b> or <b>No</b>]',
                             parse_mode='HTML')
            write_user_cache(userid=userid,key='knowInfo',value='2')
            return
        elif (
                message.text.upper() != "ARTIST" and message.text.upper() != "STYLE" and message.text.upper() != "RELATED OBJECTS") \
                and get_user_cache(userid, 'knowInfo') != '3' and len(message.text) > 4:
            bot.send_message(chatid,
                             'Sorry I don\'t understand! '
                                 'Please follow the instruction above or check the input!'
                                 '\n\nTo restart the chat bot please use command '
                                 '\'/restart\'.\nJust want to chat? Try command \'/chat\'! ')
            return
        else:
            bot.send_message(chatid,'Sorry I don\'t understand! '
                                 'Please follow the instruction above or check the input!'
                                 '\n\nTo restart the chat bot please use command '
                                 '\'/restart\'.\nJust want to chat? Try command \'/chat\'! ')
            return
    except (AttributeError, EOFError, IndexError) as e:
        print(e)
        bot.send_message(chatid, 'Sorry I don\'t understand! '
                                 'Please follow the instruction above or check the input!'
                                 '\n\nTo restart the chat bot please use command '
                                 '\'/restart\'.\nJust want to chat? Try command \'/chat\'! ')
        return


def search_Time(text):
    period = text[len(text) - 4:len(text) - 2]
    tt = str(int(period) + 1)
    periodSearch = '%sth century' % (tt)
    return ut.search_wiki(periodSearch)


def search_related(ref):
    ut.s
    return False


def get_user_cache(userid, key):
    global logPath
    with open(logPath, "rt", encoding='utf-8') as log:
        reader = csv.DictReader(log)
        for row in reader:
            if row['userID'] == userid:
                return row[key]


def write_user_cache(userid, key, value):
    global logPath,fieldnames
    csvdict = csv.DictReader(open(logPath))
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


def initCache(userid):
    global logPath
    with open(logPath, "a+", encoding='utf-8') as log:
        writer = csv.writer(log)
        writer.writerow([userid, '0', '', '', '', 'False'])



with open(logPath, 'w', newline='',encoding='utf-8') as csvfile:
    spamwriter = csv.writer(csvfile)
    spamwriter.writerow(fieldnames )
time = datetime.datetime.now()
print("Bot started: " + str(time))
while True:
    try:
        bot.polling(none_stop=True)
        time.sleep(0.5)
    except (OSError ) as e:
        print(e)
