import datetime
import telebot as tb
import random
import re
import requests
import urllib3
import socket

from lxml import etree
from DataSearch import utility as ut
from ChatBot import dictionary as cc
from chatterbot import ChatBot

import csv

token = '703120726:AAHrVpXPG-z0omcSTqSC0Q8Ze5tGBIFXM-o'#'706415631:AAG1Y6sfLmvxU_TENOaVwGA3hzXdaGJiaWo'
pathOfPhoto = 'C:/Users\linuk\Desktop\Staedel\Abbildung/compressed/'
pathOfDataset = 'C:/Users\linuk\Desktop\Staedel/Objekte.xml'
pathOfGene = 'generatedDataSet.xml'
papapa = etree.XMLParser(encoding="utf-8")
tree = etree.parse(pathOfDataset, parser=papapa)
root = tree.getroot()
treeGene = etree.parse(pathOfGene)
rootGene = treeGene.getroot()
__dict__ = cc.dict
bot = tb.TeleBot(token)

logPath = 'userCache.csv'
fieldnames = ['userID', 'knowInfo', 'artist', 'refnumber', 'style', 'period', 'chatting']
processDict = ['yes', 'no', 'artist', 'style', 'time', 'periode', 'related','hi', 'hello', 'hallo', 'good day','hi!', 'hello!', 'hallo!', 'good day!']

chattingBot = ChatBot("Training Example",
                      read_only=True,
                      storage_adapter="chatterbot.storage.SQLStorageAdapter",
                      logic_adapters=[
                          # {'import_path': 'chatterbot.logic.MathematicalEvaluation'
                          #  },
                          # {'import_path': 'chatterbot.logic.BestMatch'
                          #  },
                          {'import_path': 'chatterbot.logic.SpecificResponseAdapter',
                           'input_text': 'Who are you',
                           'output_text': 'I am Dr. Jo, a chat bot of Städel Museum :-)'},
                          {'import_path': 'chatterbot.logic.LowConfidenceAdapter',
                            'threshold': 0.65,
                            'default_response': 'I am sorry, but I do not understand.'},
                          {
                            "import_path": "chatterbot.logic.BestMatch",
                            "statement_comparison_function": "chatterbot.comparisons.levenshtein_distance",
                            "response_selection_method": "chatterbot.response_selection.get_first_response"
                          }
                      ],
                      database="../database.db"
                      )


def init(userid):
    write_user_cache(userid, 'knowInfo', '0')
    write_user_cache(userid, 'artist', '')
    write_user_cache(userid, 'style', '')
    write_user_cache(userid, 'period', '')
    write_user_cache(userid, 'refnumber', '')
    write_user_cache(userid, 'chatting', 'False')
    return


def get_semantic(text, dict):
    for dd in dict:
        if text in dict[dd]:
            return dd


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False


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
        bot.reply_to(message, 'We ended our chat :( See ya!')
        return
    write_user_cache(userid, 'chatting', 'True')
    write_user_cache(userid, 'knowInfo', '0')

    bot.reply_to(message,
                 'Okay, now let\'s chat!\nTo end the chat and go back to the museum guide, please use \'/endChat\'!')
    return


@bot.message_handler(commands=['artist'])
def send_welcome(message):
    userid = str(message.from_user.id)
    bot.send_message(message.chat.id, 'Step:%s\nArtist:%s\nStyle:%s' % (get_user_cache(userid, 'knowInfo'),
                                                                        get_user_cache(userid, 'artist'),
                                                                        get_user_cache(userid, 'style')))


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
    bot.send_message(message.chat.id, 'Welcome to the chatbot Hey Dr.Jo!\nTo start the museum guide please enter'
                                  ' /museum\n To just talk to me please enter /chat.'
                                  '\nTo restart the chatbot please use /restart.')


@bot.message_handler(commands=['museum'])
def greating(message):
    userid = str(message.from_user.id)
    bot.send_message(message.chat.id, "Hey there, I am Dr. Jo!\n"
                                      "Today I will be your museum guide and provide you with "
                                      "interesting information about our art objects!\n\n"
                                      "Which object are you currently looking at?\n\n"

                                      "[Type in the <b>Ref. number</b> or <b>Title</b> of any object]", parse_mode='HTML')
    write_user_cache(userid, 'knowInfo', '1')
    write_user_cache(userid, 'chatting', 'False')


@bot.message_handler(content_types='text')
def get_input(message):
    global logpath,processDict
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
        initCache(userid)

    try:
        chatid = message.chat.id
        for checkWrd in processDict:
            if checkWrd in message.text.lower() or bool(re.search(r'\d', message.text)) or get_user_cache(userid, 'knowInfo') in ['1','2']:
                write_user_cache(userid, 'chatting', 'False')
                break
        else:
            write_user_cache(userid, 'chatting', 'True')

        if 'ho are you' in message.text:
            statment = 'Who are you'
            response = chattingBot.get_response(statment)
            bot.send_message(chatid, response)
            return
        elif message.text.lower() in __dict__['hello']:
            greating(message)
            return
        elif get_user_cache(userid, 'chatting')=='True':
            statment = message.text
            response = chattingBot.get_response(statment)
            bot.send_message(chatid, response)
            return
        elif (message.text.lower() in __dict__['yes'] and get_user_cache(userid, 'knowInfo') == '2') \
                or (message.text.lower() in __dict__['no'] and get_user_cache(userid, 'knowInfo') == '3'):
            bot.send_message(chatid, u'Tell me, about what exactly you would like to know more, so I don\'t bore you!'
                                     '\n\n[<b>artist,time,style</b> or <b>related object</b>] ', parse_mode='HTML')
            write_user_cache(userid=userid,key='knowInfo',value='2')
            return
        elif message.text.lower() in __dict__['yes'] and get_user_cache(userid, 'knowInfo') == '3':
            artist = get_user_cache(userid, 'artist')
            curent = get_user_cache(userid, 'refnumber')
            piclist = ut.search_pic_of_artist(artist,curent,root)
            sent = 0
            if len(piclist)==0:
                bot.send_message(chatid,
                                 'Sorry, I can\'t help with this...\n\n But I can tell you more about: '
                                 'the <b>related objects</b>, <b>time</b> or <b>style</b>.'
                                 , parse_mode='HTML')
            else:
                try:
                    for pic in piclist:
                        photo = open(pathOfPhoto + pic + '.png', 'rb')
                        #bot.send_message(chatid, u'Sending photo... Please wait')
                        bot.send_photo(chatid, photo, caption='Reference number: %s'%(pic))
                        sent = 1

                except (FileNotFoundError):
                    print ('No photo')
                if sent == 1:
                    bot.send_message(chatid, 'These are the related objects. If you want to know more about one, '
                         'please enter the reference number!'
                         'Otherwise I can tell you more about the <b>artist</b>, <b>time</b> '
                         'or <b>style</b> of your current object.''
                                             , parse_mode='HTML')
                elif sent == 0:
                    bot.send_message(chatid, 'Sorry, I can\'t help with this...\n\n But I can tell you more about: '
                                                 'the <b>related objects</b>, <b>time</b> or <b>style</b>.'
                                                 , parse_mode='HTML')

            write_user_cache(userid=userid,key='knowInfo',value='2')
            return
        elif "ARTIST" in message.text.upper() and get_user_cache(userid, 'knowInfo') == '2':
            chatid = message.chat.id
            artName = get_user_cache(userid, 'artist')
            bot.send_message(chatid, ut.search_artist_xml(artName, rootGene))
            try:
                picname = ut.name_API(artName)
                photo = open(pathOfPhoto + picname + '.jpg', 'rb')
                #bot.send_message(chatid, u'Sending photo... Please wait')
                bot.send_photo(chatid, photo, caption=artName)
            except (FileNotFoundError):
                print('no photo')
            write_user_cache(userid=userid,key='knowInfo',value='3')
            bot.send_message(chatid, '\n\n\nDo you want to see more work from this artist?',
                             parse_mode='HTML')
            return
        elif "STYLE" in message.text.upper() and get_user_cache(userid, 'knowInfo') == '2':
            chatid = message.chat.id
            bot.send_message(chatid, ut.search_style_xml(get_user_cache(userid, 'style'), rootGene))
            write_user_cache(userid=userid,key='knowInfo',value='2')
            bot.send_message(chatid, '\n\n\nDo you want more information?',
                             parse_mode='HTML')
            return

        elif "TIME" in message.text.upper() and get_user_cache(userid, 'knowInfo') == '2':
            chatid = message.chat.id
            bot.send_message(chatid, search_Time(get_user_cache(userid, 'period')))
            write_user_cache(userid=userid,key='knowInfo',value='2')
            bot.send_message(chatid, '\n\n\nDo you want more information?',
                             parse_mode='HTML')
            return

        elif "RELATED" in message.text.upper() and get_user_cache(userid, 'knowInfo') == '2':
            curent = get_user_cache(userid, 'refnumber')
            relalist = ut.search_related(curent,root)
            i = 0
            sent = 0
            if len(relalist) == 0:
                bot.send_message(chatid,
                                 'Sorry, I can\'t help with this...\n\n But I can tell you more about: '
                             'the <b>artist</b>, <b>time</b>, '
                           '<b>style</b> or <b>related objects</b> of this object?'
                                                 , parse_mode='HTML')
            else:
                for ll in range(len(relalist)):
                    try:
                        pic = random.choice(relalist)
                        relalist.remove(pic)
                        photo = open(pathOfPhoto + pic + '.png', 'rb')
                       # bot.send_message(chatid, u'Sending photo... Please wait')
                        bot.send_photo(chatid, photo, caption='Reference number: %s' % (pic))
                        sent +=1
                        i += 1
                    except (FileNotFoundError):
                        print('not found')
                    if i>3:
                        break
                if sent == 0:
                    bot.send_message(chatid,
                                     'Sorry, I can\'t help with this...\n\n But I can tell you more about: '
                                      'the <b>artist</b>, <b>time</b>, '
                                           '<b>style</b> or <b>related objects</b> of this object?')
                else:
                    bot.send_message(chatid, 'These are the related objects. If you want to know more about one, '
                         'please enter the reference number!'
                         'Otherwise I can tell you more about the <b>artist</b>, <b>time</b> '
                         'or <b>style</b> of your current object.'
                                             , parse_mode='HTML')
            write_user_cache(userid=userid,key='knowInfo',value='2')
            return

        elif message.text.lower() in __dict__['no']:
            bot.send_message(chatid, u'Please type in the number or name of your object of interest!')
            write_user_cache(userid=userid,key='knowInfo',value='1')
            return

        elif message.text.lower() in __dict__['thanks']:
            n = random.choice(__dict__['you are welcome'])
            bot.send_message(chatid, n)
            return
        elif message.text.lower() in __dict__['bye']:
            m = random.choice(__dict__['bye'])
            bot.send_message(chatid, m)

        elif bool(re.search(r'\d', message.text)) and get_user_cache(userid, 'knowInfo') in ['0','1','2']:
            print(get_user_cache(userid, 'knowInfo'))
            # for message in messageList:
            title, artist, period, refnum, record = ut.get_start_info(message.text, root)
            detail_Info, listing = ut.get_details(record)

            write_user_cache(userid,'knowInfo','0' )
            write_user_cache(userid,'artist',artist )
            write_user_cache(userid,'refnumber',refnum )
            write_user_cache(userid,'style',listing['style'] )
            write_user_cache(userid,'period',period )
            write_user_cache(userid,'chatting','False' )

            bot.reply_to(message, 'Title: \n%s\n\nArtist: \n%s\n\nTime period: \n%s\n\n\n%s' % (
            title, artist, period, detail_Info))

            try:
                photo = open(pathOfPhoto + refnum + '.png', 'rb')
                #bot.send_message(chatid, u'Sending photo... Please wait')
                bot.send_photo(chatid, photo)
            except (FileNotFoundError):
                print('no photo')
            bot.send_message(chatid,
                             u'Would you like more information about this object?',
                             parse_mode='HTML')
            write_user_cache(userid=userid,key='knowInfo',value='2')
            return
        else:
            bot.send_message(chatid,'Sorry I don\'t understand! '
                                 'Please follow the instructions above and check your input!'
                                 '\n\nTo restart the chatbot please use '
                                 '\'/restart\'.\nIf you just want to chat try \'/chat\'! ')
            return
    except (AttributeError, EOFError, IndexError) as e:
        print(e)
        bot.send_message(chatid, 'Sorry I don\'t understand! '
                                 'Please follow the instructions above and check your input!'
                                 '\n\nTo restart the chatbot please use '
                                 '\'/restart\'.\nIf you just want to chat try \'/chat\'! ')
        return


def search_Time(text):
    period = text[len(text) - 4:len(text) - 2]
    tt = str(int(period) + 1)
    periodSearch = '%sth century' % (tt)
    return ut.search_wiki(periodSearch)


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
    except (OSError, TimeoutError,requests.exceptions.ReadTimeout,urllib3.exceptions.ReadTimeoutError,socket.timeout) as e:
        print(e)
