import datetime
import telebot as tb
import random
import re
import requests
import urllib3
import socket
import time


from lxml import etree
from DataSearch import utility as ut
from ChatBot import dictionary as cc
from chatterbot import ChatBot
from DataSearch.utility import write_user_cache
from DataSearch.utility import get_user_cache


import csv


token = '730406855:AAGBHg4Vokf8N4tJoqhUOZG7Xf8y41uo7Ww'
pathOfPhoto = 'D:\Workspace\Staedel\Abbildung/'
pathOfDataset = 'D:\Workspace\Staedel/Objekte.xml'
pathOfGene = 'generatedDataSet.xml'
path_of_log = 'D:\Workspace\Staedel/'
xmlparse = etree.XMLParser(encoding="utf-8")
tree = etree.parse(pathOfDataset, parser=xmlparse)
root = tree.getroot()
treeGene = etree.parse(pathOfGene)
rootGene = treeGene.getroot()
__dict__ = cc.dict
bot = tb.TeleBot(token)
logger = ut.initlog(path_of_log)

logPath = 'userCache.csv'
fieldnames = ut.fieldnames
processDict = ['yes', 'no', 'artist', 'style', 'time', 'periode',
               'related', 'relate', 'comment', 'hi', 'hello', 'hallo', 'good day', 'hi!', 'hello!', 'hallo!', 'good day!']
command_list = ['chat', 'endChat', 'search', 'start', 'help', 'restart', 'museum', 'visit']

chattingBot = ChatBot("Training Example",
                      read_only=False,
                      storage_adapter="chatterbot.storage.SQLStorageAdapter",
                      logic_adapters=[
                          {'import_path': 'chatterbot.logic.SpecificResponseAdapter',
                           'input_text': 'Who are you',
                           'output_text': 'I am LeoBot, your experience art museum guide :-)'},
                          # {'import_path': 'chatterbot.logic.LowConfidenceAdapter',
                          #   'threshold': 0.65,
                          #   'default_response': 'I am sorry, but I do not understand.'},
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
    write_user_cache(userid, 'search', 'False')
    return


def get_semantic(text, key):
    global __dict__
    for dd in __dict__[key]:
        if dd in text:
            return True
    return False


def is_process(text):
    global processDict
    for dd in processDict:
        if dd in text.lower():
            return True
    if bool(re.search(r'\d',text)):
        return True
    elif get_semantic(text.lower(), 'yes'):
        return True
    elif get_semantic(text.lower(), 'hello'):
        return True
    elif get_semantic(text.lower(), 'no'):
        return True
    elif get_semantic(text.lower(), 'write'):
        return True
    elif 'related' in text.lower():
        return True

    return False


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


@bot.message_handler(commands=['chat', 'endChat'])
def chatter_command(message):
    userid = str(message.from_user.id)
    with open(logPath, "rt", encoding='utf-8') as log:
        reader = csv.DictReader(log)
        userList = [row['userID'] for row in reader]
    userid = str(message.from_user.id)
    if userid not in userList:
        init_cache(userid)
    if message.text.upper() == '/ENDCHAT':
        write_user_cache(userid, 'chatting', 'False')
        bot.reply_to(message, 'We ended our chat :( See ya!')
        return
    write_user_cache(userid, 'chatting', 'True')
    write_user_cache(userid, 'knowInfo', '0')

    bot.reply_to(message,
                 'Okay, now let\'s chat!\nTo end the chat and go back to the museum guide, use command \'/endChat\'!')
    return


@bot.message_handler(commands=['artist'])
def send_welcome(message):
    userid = str(message.from_user.id)
    bot.send_message(message.chat.id, 'Step:%s\nArtist:%s\nStyle:%s' % (get_user_cache(userid, 'knowInfo'),
                                                                        get_user_cache(userid, 'artist'),
                                                                        get_user_cache(userid, 'style')))
    return


@bot.message_handler(commands=['server'])
def send_server(message):
    userid = str(message.from_user.id)
    bot.send_message(message.chat.id, 'Step:%s\nArtist:%s\nStyle:%s' % (get_user_cache(userid, 'knowInfo'),
                                                                        get_user_cache(userid, 'artist'),
                                                                        get_user_cache(userid, 'style')))
    return


@bot.message_handler(commands=['search'])
def search(message):
    userid = str(message.from_user.id)
    write_user_cache(userid, 'search', 'True')
    bot.send_message(message.chat.id, 'What do you want to search? Please tell me the key word!')
    return


@bot.message_handler(commands=['start', 'help', 'restart', 'Start', 'Restart'])
def sartInfo(message):
    userid = str(message.from_user.id)
    init(userid)
    bot.send_message(message.chat.id, 'Learning never exhausts the mind!\n'
                                      'That\'s why I am your personal museum guide for today!\n\n'
                                      'To start, just press /museum.\n\n'
                                      'One note: sometimes my old brain get\'s lost and needs a /restart.')
    return


@bot.message_handler(commands=['museum', 'visit'])
def greating(message):
    userid = str(message.from_user.id)
    bot.send_message(message.chat.id, "Hey there, I am LeoBot!\n"
                                      "Today I will be your museum guide and provide you with "
                                      "interesting information about our art objects!\n\n"
                                      "Which object are you currently looking at?\n\n"

                                      "[Type in the <b>Ref. number</b> or <b>Title</b> of any object]\n\n"
                                     , parse_mode='HTML')
    write_user_cache(userid, 'knowInfo', '1')
    write_user_cache(userid, 'chatting', 'False')
    return


def get_input(messages):
    global logPath, processDict, db, command_list
    for message in messages:
        with open(logPath, "rt", encoding='utf-8') as log:
            reader = csv.DictReader(log)
            userList = [row['userID'] for row in reader]
        userid = str(message.from_user.id)
        name = str(message.chat.first_name)
        logger.info('---> Userid: %s, UserName, %s, Message: %s'%(userid, name, message.text))
        for cmd in command_list:
            if message.text == '/%s' % cmd:
                return
        if userid not in userList:
            init_cache(userid)
        if get_user_cache(userid, 'search') == 'True':
            chatid = message.chat.id
            statment = ut.search_wiki(message.text)
            bot.send_message(chatid, 'From <b>Wikipedia</b>:\n<i>%s</i>' % statment, parse_mode='HTML')
            write_user_cache(userid, 'search', 'False')
            bot.send_message(chatid, '<b>Search ended</b>.\n\nNow you can continue your museum visit :-)',
                             parse_mode='HTML')
            return
        try:
            get_user_cache(userid, 'chatting')
            get_user_cache(userid, 'knowInfo')
            get_user_cache(userid, 'artist')
            get_user_cache(userid, 'style')
            get_user_cache(userid, 'period')
            get_user_cache(userid, 'search')
        except (AttributeError):
            logger.info('Creating new user cache...')
            init_cache(userid)

        try:
            chatid = message.chat.id
            if 'time' in message.text.lower() or 'hour' in message.text.lower():
                if 'open' in message.text.lower() or 'close' in message.text.lower():
                    bot.send_message(chatid, 'The opening hours of <i>Städel Museum</i> are:\n\n'
                                             'Tues. Wed. Sat. Sun. :\nfrom <b>10:00</b> to'
                                             ' <b>18:00</b>\n\n'
                                             'Thurs. Fri. :\nfrom <b>10:00</b> to'
                                             ' <b>21:00</b>\n\n'
                                             'Mon. :\n<b>Closed</b>', parse_mode='HTML')
                    return
            if get_user_cache(userid, 'knowInfo') not in ['1','wc', 'rc']:
                if is_process(message.text):
                    if get_user_cache(userid, 'chatting') != 'True':
                        write_user_cache(userid, 'chatting', 'False')
                    else:
                        statment = message.text
                        response = chattingBot.get_response(statment)
                        bot.send_message(chatid, response)
                        return
                else:
                    statment = message.text
                    response = chattingBot.get_response(statment)
                    bot.send_message(chatid, response)
                    return
            if 'ho are you' in message.text and get_user_cache(userid, 'knowInfo') not in ['wc', 'rc']:
                statment = 'Who are you'
                response = chattingBot.get_response(statment)
                bot.send_message(chatid, response)
                return
            elif get_user_cache(userid, 'chatting') == 'True':
                statment = message.text
                response = chattingBot.get_response(statment)
                bot.send_message(chatid, response)
                return
            elif get_semantic(message.text.lower(), 'hello') and get_user_cache(userid, 'knowInfo') not in ['wc', 'rc']:
                greating(message)
                return
            elif get_semantic(message.text.lower(), 'yes') and get_user_cache(userid, 'knowInfo') == '3':
                artist = get_user_cache(userid, 'artist')
                curent = get_user_cache(userid, 'refnumber')
                piclist = ut.search_pic_of_artist(artist,curent,root)
                sent = 0
                if len(piclist) == 0:
                    bot.send_message(chatid,
                                     'Sorry, there are no more related objects in our museum.'
                                     '\n\nBut I can tell you more about: '
                                     'the <b>related objects</b>, <b>time</b> or <b>style</b>.'
                                     , parse_mode='HTML')
                else:

                    for p in piclist:
                        try:
                            pic = p.replace(' ', '_')
                            photo = open(pathOfPhoto + pic + '.png', 'rb')
                            bot.send_message(chatid, u'Sending photo... Please wait')
                            bot.send_photo(chatid, photo, caption='Reference number: %s'%(pic))
                            sent = 1

                        except FileNotFoundError as e:
                            logger.error('---> %s' % str(e))
                            logger.warning('No photo')
                    if sent == 1:
                        bot.send_message(chatid, 'These are the related objects. If you want to know more about one, '
                                                 'please enter the reference number!\n'
                                                 'Otherwise I can tell you more about the <b>artist</b>, <b>time</b> '
                                                 'or <b>style</b> of your current object.'
                                                 '\n\nYou also can check <b>comments</b> from others'
                                                 ' or <b>write a comment</b>.'
                                                 , parse_mode='HTML')
                    elif sent == 0:
                        bot.send_message(chatid, 'Sorry, there are no more related objects in our museum.'
                                                 '\n\nBut I can tell you more about: '
                                                 'the <b>artist</b>, <b>time</b>, '
                                                 '<b>style</b> or <b>related objects</b> of this object.'
                                                 '\n\nYou also can <b>check comments</b> from others'
                                                 ' or <b>write a comment</b>.'
                                                 , parse_mode='HTML')

                write_user_cache(userid=userid,key='knowInfo',value='2')
                return
            elif ("COMMENT" in message.text.upper() and get_semantic(
                    message.text.lower(), 'write')) or(get_semantic(message.text.lower(), 'yes') and get_user_cache(userid, 'knowInfo') == 'rc'):
                bot.send_message(chatid, 'Please text the comment now!')
                write_user_cache(userid=userid,key='knowInfo',value='wc')
                return
            elif (("COMMENT" in message.text.upper() and get_semantic(message.text.lower(), 'see'))
                  or "COMMENT" in message.text.upper()) and get_user_cache(userid, 'knowInfo') == '2':
                ref = get_user_cache(userid=userid, key='refnumber')
                comments = ut.read_comment(ref)
                if len(comments) == 0:
                    bot.send_message(chatid, 'Sorry, there are no comments for this object!\n\n'
                                             'Do you want to write a comment? <b>yes</b> or <b>no</b>', parse_mode='HTML')
                    write_user_cache(userid=userid, key='knowInfo', value='rc')
                    return
                count = 0
                length = len(comments)
                bot.send_message(chatid, 'Here are the comments:')
                for i in range(length):
                    comm = random.choice(comments)
                    comments.remove(comm)
                    bot.send_message(chatid, '[%s]. Comment from <b>[%s]</b>:\n\"%s\"\n\n'%(str(i+1), comm.find('userName').text,
                                                                          comm.find('comment').text),parse_mode='HTML')
                    count += 1
                    if count >= 3:
                        break
                bot.send_message(chatid, 'Do you want to write a comment? <b>yes</b> or <b>no</b>',parse_mode='HTML')
                write_user_cache(userid=userid,key='knowInfo',value='rc')
                return

            elif get_semantic(message.text.lower(), 'no') and get_user_cache(userid, 'knowInfo') == 'rc':
                write_user_cache(userid=userid, key='knowInfo', value='2')
                bot.send_message(chatid, 'Fine. Do you want to know more Information?',
                                 parse_mode='HTML')
                return
            elif get_user_cache(userid, 'knowInfo') == 'wc':
                ut.write_comment(userid, message)
                bot.send_message(chatid, 'Comment successfully updated!')
                write_user_cache(userid=userid,key='knowInfo',value='2')
                bot.send_message(chatid, '\n\n\nDo you want to know more?',
                                 parse_mode='HTML')
                return
            elif "ARTIST" in message.text.upper() and get_user_cache(userid, 'knowInfo') == '2':
                artName = get_user_cache(userid, 'artist')
                bot.send_message(chatid, ut.search_artist_xml(artName, rootGene))
                try:
                    picname = ut.name_API(artName)
                    photo = open(pathOfPhoto + picname + '.jpg', 'rb')
                    bot.send_message(chatid, u'Sending photo... Please wait')
                    bot.send_photo(chatid, photo, caption=artName)
                except FileNotFoundError as e1:
                    logger.error('---> %s' % str(e1))
                    logger.warning('No photo')
                write_user_cache(userid=userid,key='knowInfo',value='3')
                bot.send_message(chatid, 'Do you want to see more works of this artist?',
                                 parse_mode='HTML')
                return
            elif "STYLE" in message.text.upper() and get_user_cache(userid, 'knowInfo') == '2':
                bot.send_message(chatid, ut.search_style_xml(get_user_cache(userid, 'style'), rootGene))
                write_user_cache(userid=userid,key='knowInfo',value='2')
                bot.send_message(chatid, 'Do you want to know more?',
                                 parse_mode='HTML')
                return

            elif "TIME" in message.text.upper() and get_user_cache(userid, 'knowInfo') == '2':
                chatid = message.chat.id
                bot.send_message(chatid, search_time(get_user_cache(userid, 'period')))
                write_user_cache(userid=userid,key='knowInfo',value='2')
                bot.send_message(chatid, 'Do you want to know more?',
                                 parse_mode='HTML')
                return

            elif "RELATED" in message.text.upper() and get_user_cache(userid, 'knowInfo') == '2':
                curent = get_user_cache(userid, 'refnumber')
                relalist = ut.search_related(curent,root)
                artist = get_user_cache(userid, 'artist')
                piclist = ut.search_pic_of_artist(artist, curent, root)
                for plp in piclist:
                    if plp in relalist:
                        piclist.remove(plp)
                sent = 0
                i = 0
                if len(piclist) == 0 and len(relalist) == 0:
                    bot.send_message(chatid, 'Sorry, there are no more related objects in our museum.'
                                             '\n\nBut I can tell you more about: '
                                             'the <b>artist</b>, <b>time</b>, '
                                             '<b>style</b> or <b>related objects</b> of this object.'
                                             '\n\nYou can also check <b>comments</b> from others'
                                             ' or <b>write a comment</b>.'
                                             , parse_mode='HTML')
                else:

                    for p in piclist:
                        try:
                            pic = p.replace(' ', '_')
                            photo = open(pathOfPhoto + pic + '.png', 'rb')
                            bot.send_message(chatid, u'Sending photo... Please wait')
                            bot.send_photo(chatid, photo, caption='Reference number: %s' % (pic))
                            sent += 1
                            i+=1

                        except FileNotFoundError as e2:
                            logger.error('---> %s' % str(e2))
                            logger.warning('No photo')
                    for ll in range(len(relalist)):
                        try:
                            p = random.choice(relalist)
                            relalist.remove(p)
                            pic = p.replace(' ', '_')
                            photo = open(pathOfPhoto + pic + '.png', 'rb')
                            bot.send_message(chatid, u'Sending photo... Please wait')
                            bot.send_photo(chatid, photo, caption='Reference number: %s' % (pic))
                            sent +=1
                            i += 1
                        except FileNotFoundError as e3:
                            logger.error('---> %s' % str(e3))
                            logger.warning('No photo')
                        if i > 4:
                            break
                    if sent == 0:
                        bot.send_message(chatid, 'Sorry, there are no more related objects in our museum.'
                                                 ' \n\nBut I can tell you more about: '
                                                 'the <b>artist</b>, <b>time</b>, '
                                                 '<b>style</b> or <b>related objects</b> of this object.'
                                                 '\n\nYou can also check <b>comments</b> from others'
                                                 ' or <b>write a comment</b>.'
                                                 , parse_mode='HTML')
                    else:
                        bot.send_message(chatid, 'These are the related objects. If you want to know more about one, '
                                                 'please enter the reference number!\n'
                                                 'Otherwise I can tell you more about the <b>artist</b>, <b>time</b> '
                                                 'or <b>style</b> of your current object.'
                                                 '\n\nYou can also check <b>comments</b> from others'
                                                 ' or <b>write a comment</b>.'
                                                 , parse_mode='HTML')
                write_user_cache(userid=userid,key='knowInfo',value='2')
                return
            elif (get_semantic(message.text.lower(), 'yes') and get_user_cache(userid, 'knowInfo') == '2') \
                    or (get_semantic(message.text.lower(), 'no') and get_user_cache(userid, 'knowInfo') == '3'):
                bot.send_message(chatid, u'Tell me, about what exactly you would like to know more, '
                                         u'so I don\'t bore you!'
                                         '\n\n[<b>artist,time,style</b> or <b>related object</b>] '
                                         '\n\nYou also can check <b>comments</b> from others'
                                         ' or <b>write a comment</b>.', parse_mode='HTML')
                write_user_cache(userid=userid, key='knowInfo', value='2')
                return
            elif get_semantic(message.text.lower(), 'no') and get_user_cache(userid, 'knowInfo') != 'rc':
                bot.send_message(chatid, u'Please type in the number or the name of your object of interest!')
                write_user_cache(userid=userid,key='knowInfo',value='1')
                return

            elif get_semantic(message.text.lower(), 'thanks') and get_user_cache(userid, 'knowInfo') not in ['wc', 'rc']:
                n = random.choice(__dict__['you are welcome'])
                bot.send_message(chatid, n)
                return
            elif get_semantic(message.text.lower(), 'bye') and get_user_cache(userid, 'knowInfo') not in ['wc', 'rc']:
                m = random.choice(__dict__['bye'])
                bot.send_message(chatid, m)

            elif bool(re.search(r'\d', message.text)) and get_user_cache(userid, 'knowInfo') in ['0','1','2']:
                print(get_user_cache(userid, 'knowInfo'))
                title, artist, period, refnum, record = ut.get_start_info(message.text, root)
                detail_Info, listing = ut.get_details(record)

                write_user_cache(userid, 'knowInfo', '0' )
                write_user_cache(userid, 'artist', artist)
                write_user_cache(userid, 'refnumber', refnum)
                write_user_cache(userid, 'style', listing['style'])
                write_user_cache(userid, 'period', period)
                write_user_cache(userid, 'chatting', 'False')
                write_user_cache(userid, 'search', 'False')

                bot.reply_to(message, 'Title: \n%s\n\nCreator: \n%s\n\nCreated period: \n%s\n\n\n%s' % (
                title, artist, period, detail_Info))

                try:
                    photo = open(pathOfPhoto + refnum + '.png', 'rb')
                    bot.send_message(chatid, u'Sending photo... Please wait')
                    bot.send_photo(chatid, photo)
                except FileNotFoundError as e5:
                    logger.error('---> %s' % str(e5))
                    logger.warning('No photo')
                bot.send_message(chatid,
                                 u'Would you like to know more about this object?',
                                 parse_mode='HTML')
                write_user_cache(userid=userid,key='knowInfo',value='2')
                return
            else:
                bot.send_message(chatid, 'Sorry I don\'t understand! '
                                         'Please check your input!'
                                         '\n\nTo restart the chatbot please use command '
                                         '\'/restart\'.\nJust want to chat? Try command \'/chat\'!\n\n'
                                         'If you have any other questions, try use command /search. '
                                         'to search in Wikipedia!')
                return
        except (AttributeError, EOFError, IndexError) as e6:
            logger.error('---> %s' % str(e6))
            bot.send_message(chatid, 'Sorry I don\'t understand! '
                                     'Please check your input!'
                                         '\n\nTo restart the chatbot please use command '
                                         '\'/restart\'.\nJust want to chat? Try command \'/chat\'!\n\n'
                                         'If you have any other questions, try use command /search. '
                                         'to search in Wikipedia!')
            return


def search_time(text):
    period = text[len(text) - 4:len(text) - 2]
    tt = str(int(period) + 1)
    periodSearch = '%sth century' % (tt)
    return ut.search_wiki(periodSearch)


def init_cache(userid):
    global logPath
    with open(logPath, "a+", encoding='utf-8') as log:
        writer = csv.writer(log)
        writer.writerow([userid, '0', '', '', '', 'False'])


with open(logPath, 'w', newline='',encoding='utf-8') as csvfile:
    spamwriter = csv.writer(csvfile)
    spamwriter.writerow(fieldnames )
ti = datetime.datetime.now()
print("Bot started: " + str(ti))
bot.set_update_listener(get_input)
try:
    bot.polling(none_stop=True, interval=0, timeout=3)
except (OSError, TimeoutError, ConnectionResetError, requests.exceptions.ReadTimeout, urllib3.exceptions.ReadTimeoutError,
        socket.timeout, RecursionError, urllib3.exceptions.ProtocolError,requests.exceptions.ConnectionError) as e:
    logger.error('---> %s' % str(e))
    time.sleep(0.5)

