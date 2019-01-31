import datetime
import telebot as tb
import random
import re
import requests
import urllib3
import socket
import telebot
import logging


from lxml import etree
from DataSearch import utility as ut
from ChatBot import dictionary as cc
from chatterbot import ChatBot
from DataSearch.utility import write_user_cache
from DataSearch.utility import get_user_cache


import csv


token = '703120726:AAHrVpXPG-z0omcSTqSC0Q8Ze5tGBIFXM-o'
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
processDict = [ 'yes', 'no', 'artist', 'style', 'time', 'periode', 'related','hi', 'hello', 'hallo', 'good day','hi!', 'hello!', 'hallo!', 'good day!']

chattingBot = ChatBot("Training Example",
                      read_only=False,
                      storage_adapter="chatterbot.storage.SQLStorageAdapter",
                      logic_adapters=[
                          {'import_path': 'chatterbot.logic.SpecificResponseAdapter',
                           'input_text': 'Who are you',
                           'output_text': 'I am Dr. Jo, a chat bot of Städel Museum :-)'},
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
        init_cache(userid)
    if message.text.upper() == '/ENDCHAT':
        write_user_cache(userid, 'chatting', 'False')
        bot.reply_to(message, 'End chatting. See ya!')
        return
    write_user_cache(userid, 'chatting', 'True')
    write_user_cache(userid, 'knowInfo', '0')

    bot.reply_to(message,
                 'Okay, now let\'s chat!\nTo end the chatting and go back to Städel Museum, use command \'/endChat\'!')
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


@bot.message_handler(commands=['search'])
def send_welcome(message):
    userid = str(message.from_user.id)
    write_user_cache(userid, 'search', 'True')
    bot.send_message(message.chat.id, 'What do you want to search? Please tell me the key word!')


@bot.message_handler(commands=['start', 'help', 'restart'])
def send_welcome(message):
    userid = str(message.from_user.id)
    init(userid)
    bot.send_message(message.chat.id, 'Welcome to Hey Dr.Jo chat bot!\nTo start visiting meseum please enter'
                                  ' /visit\nTo chat with me please use command /chat.'
                                  '\nTo restart the chat bot please use command /restart.')


@bot.message_handler(commands=['visit'])
def greating(message):
    userid = str(message.from_user.id)
    bot.send_message(message.chat.id, "Dear customer, I am Dr. Jo!\n"
                                      "Today I will be your museum guide and provide you some "
                                      "professional and interesting information about our art objects!\n\n"
                                      "Which object are you currently looking at or interested in?\n\n"

                                      "[<b>Ref. number</b> or <b>Title</b> of object]\n\n"
                                      "If you have any question, use command /search. "
                                      "Then you can search it in Wikipedia!", parse_mode='HTML')
    write_user_cache(userid, 'knowInfo', '1')
    write_user_cache(userid, 'chatting', 'False')


@bot.message_handler(content_types='text')
def get_input(message):
    global logPath, processDict, db
    with open(logPath, "rt", encoding='utf-8') as log:
        reader = csv.DictReader(log)
        userList = [row['userID'] for row in reader]
    userid = str(message.from_user.id)
    name = str(message.chat.first_name)
    logger.info('---> Userid: %s, UserName, %s, Message: %s'%(userid, name, message.text))

    if userid not in userList:
        init_cache(userid)
    if get_user_cache(userid, 'search') == 'True':
        chatid = message.chat.id
        statment = ut.search_wiki(message.text)
        bot.send_message(chatid, 'From <b>Wikipedia</b>:\n<i>%s</i>' % statment, parse_mode='HTML')
        write_user_cache(userid, 'search', 'False')
        bot.send_message(chatid, '<b>Search ended</b>.\n\nNow you can continue your visit in museum :-)',
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

        elif get_semantic(message.text.lower(), 'yes') and get_user_cache(userid, 'knowInfo') == '3':
            artist = get_user_cache(userid, 'artist')
            curent = get_user_cache(userid, 'refnumber')
            piclist = ut.search_pic_of_artist(artist,curent,root)
            sent = 0
            if len(piclist)==0:
                bot.send_message(chatid,
                                 'Sorry, but i can\'t find any more in our Museum....\n\nWhat would you like to know, '
                                 'the <b>related object</b>, <b>time</b> or <b>style</b>.'
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
                        logger.warn('No photo')
                if sent == 1:
                    bot.send_message(chatid, 'Those are what I get. \n\nAre you intrested in any of them? '
                                             'Please give the reference number!\n\n'
                                             'Or I can also introduce you more about the'
                                             ' <b>artist</b>, <b>time</b> or <b>style</b>.'
                                             , parse_mode='HTML')
                elif sent == 0:
                    bot.send_message(chatid, 'Sorry, but i can\'t find any more in our Museum....'
                                             '\n\nWhat would you like to know, '
                                             'the <b>related object</b>, <b>time</b> or <b>style</b>.'
                                             '\n\nYou also can check <b>Comments</b> from others'
                                             ' or <b>write</b> a comment.'
                                                 ,parse_mode='HTML')

            write_user_cache(userid=userid,key='knowInfo',value='2')
            return
        elif ("COMMENT" in message.text.upper() and get_semantic(
                message.text, 'write')) or(get_semantic(message.text, 'yes') and get_user_cache(userid, 'knowInfo') == 'rc'):
            bot.send_message(chatid, 'Please text the comment now!')
            write_user_cache(userid=userid,key='knowInfo',value='wc')
            return
        elif (("COMMENT" in message.text.upper() and get_semantic(message.text.lower(), 'see'))
              or "COMMENT" in message.text.upper()) and get_user_cache(userid, 'knowInfo') == '2':
            ref = get_user_cache(userid=userid,key='refnumber')
            comments = ut.read_comment(ref)
            if len(comments) == 0:
                bot.send_message(chatid, 'Sorry, There is still no comments for this object!\n\n'
                                         'Do you want to write a comment?')
                write_user_cache(userid=userid, key='knowInfo', value='rc')
                return
            count = 0
            length = len(comments)
            bot.send_message(chatid, 'Here are some comments:')
            for i in range(length):
                comm = random.choice(comments)
                comments.remove(comm)
                bot.send_message(chatid, '[%s]. Comment from <b>[%s]</b>:\n\"%s\"\n\n'%(str(i+1), comm.find('userName').text,
                                                                      comm.find('comment').text),
                                 parse_mode='HTML')
                count += 1
                if count >= 3:
                    break
            bot.send_message(chatid, 'Do you want to write a comment?')
            write_user_cache(userid=userid,key='knowInfo',value='rc')
            return

        elif get_semantic(message.text, 'no') and get_user_cache(userid, 'knowInfo') == 'rc':
            write_user_cache(userid=userid, key='knowInfo', value='2')
            bot.send_message(chatid, 'Fine. Do you want to know more Information?',
                             parse_mode='HTML')
            return
        elif get_user_cache(userid, 'knowInfo') == 'wc':
            ut.write_comment(userid, message)
            bot.send_message(chatid, 'Comment success updated!')
            write_user_cache(userid=userid,key='knowInfo',value='2')
            bot.send_message(chatid, '\n\n\nDo you want to know more Information?',
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
                logger.warn('No photo')
            write_user_cache(userid=userid,key='knowInfo',value='3')
            bot.send_message(chatid, 'Do you want to see more works of this artist?',
                             parse_mode='HTML')
            return
        elif "STYLE" in message.text.upper() and get_user_cache(userid, 'knowInfo') == '2':
            bot.send_message(chatid, ut.search_style_xml(get_user_cache(userid, 'style'), rootGene))
            write_user_cache(userid=userid,key='knowInfo',value='2')
            bot.send_message(chatid, 'Do you want to know more Information?',
                             parse_mode='HTML')
            return

        elif "TIME" in message.text.upper() and get_user_cache(userid, 'knowInfo') == '2':
            chatid = message.chat.id
            bot.send_message(chatid, search_time(get_user_cache(userid, 'period')))
            write_user_cache(userid=userid,key='knowInfo',value='2')
            bot.send_message(chatid, 'Do you want to know more Information?',
                             parse_mode='HTML')
            return

        elif "RELATED" in message.text.upper() and get_user_cache(userid, 'knowInfo') == '2':
            curent = get_user_cache(userid, 'refnumber')
            relalist = ut.search_related(curent,root)
            artist = get_user_cache(userid, 'artist')
            piclist = ut.search_pic_of_artist(artist, curent, root)
            sent = 0
            i = 0
            if len(piclist) == 0 and len(relalist) == 0:
                bot.send_message(chatid,
                                 'Sorry, but i can\'t find any more in our Museum....\n\nWhat would you like to know, '
                                 'the <b>related object</b>, <b>time</b> or <b>style</b>.'
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
                        logger.warn('No photo')
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
                        logger.warn('No photo')
                    if i > 4:
                        break
                if sent == 0:
                    bot.send_message(chatid,
                                     'Sorry, but i can\'t find any more in our '
                                     'Museum....\n\nWhat would you like to know, '
                                     'the artist, time, '
                                     'style or some related objects of this picture?')
                else:
                    bot.send_message(chatid, 'Those are what I get. \n\nAre you intrested in any of them? '
                                             'Please give the reference number!\n\n'
                                             'Or I can also introduce you more about'
                                             ' the <b>artist</b>, <b>time</b> or <b>style</b>.'
                                             '\n\nYou also can check <b>Comments</b> from others'
                                             ' or <b>write</b> a comment.'
                                             , parse_mode='HTML')
            write_user_cache(userid=userid,key='knowInfo',value='2')
            return
        elif (get_semantic(message.text.lower(), 'yes') and get_user_cache(userid, 'knowInfo') == '2') \
                or (get_semantic(message.text.lower(), 'no') and get_user_cache(userid, 'knowInfo') == '3'):
            bot.send_message(chatid, u'What would you like to know, '
                                     'introductions about the artist, time, '
                                     'style or some related objects of this object in our museum?'
                                     '\n\n[<b>artist,time,style</b> or <b>related object</b>] '
                                     '\n\nYou also can check <b>Comments</b> from others'
                                             ' or <b>write</b> a comment.', parse_mode='HTML')
            write_user_cache(userid=userid, key='knowInfo',value='2')
            return
        elif get_semantic(message.text.lower(), 'no'):
            bot.send_message(chatid, u'Please give the number or the name of your interested object!')
            write_user_cache(userid=userid,key='knowInfo',value='1')
            return

        elif get_semantic(message.text.lower(), 'thanks'):
            n = random.choice(__dict__['you are welcome'])
            bot.send_message(chatid, n)
            return
        elif get_semantic(message.text.lower(), 'bye'):
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
            write_user_cache(userid,'search','False' )

            bot.reply_to(message, 'Title: \n%s\n\nCreator: \n%s\n\nCreated period: \n%s\n\n\n%s' % (
            title, artist, period, detail_Info))

            try:
                photo = open(pathOfPhoto + refnum + '.png', 'rb')
                bot.send_message(chatid, u'Sending photo... Please wait')
                bot.send_photo(chatid, photo)
            except FileNotFoundError as e5:
                logger.error('---> %s' % str(e5))
                logger.warn('No photo')
            bot.send_message(chatid,
                             u'Should I introduce more information about this object?',
                             parse_mode='HTML')
            write_user_cache(userid=userid,key='knowInfo',value='2')
            return
        else:
            bot.send_message(chatid,'Sorry I don\'t understand! '
                                 'Please follow the instruction'
                                    ' above or check the input!'
                                 '\n\nTo restart the chat bot please use command '
                                 '\'/restart\'.\nJust want to chat? Try command \'/chat\'!\n\n'
                                 'If you have any question, use command /search. '
                                 'Then you can search it in Wikipedia!')
            return
    except (AttributeError, EOFError, IndexError) as e6:
        logger.error('---> %s' % str(e6))
        bot.send_message(chatid, 'Sorry I don\'t understand! '
                                 'Please follow the instruction above or check the input!'
                                 '\n\nTo restart the chat bot please use command '
                                 '\'/restart\'.\nJust want to chat? Try command \'/chat\'! \n\n'
                                 'If you have any question, use command /search. '
                                 'Then you can search it in Wikipedia!')
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
time = datetime.datetime.now()
print("Bot started: " + str(time))
while True:
    try:
        bot.polling(none_stop=True)
        time.sleep(0.5)
    except (OSError, TimeoutError,requests.exceptions.ReadTimeout,urllib3.exceptions.ReadTimeoutError,socket.timeout) as e:
        logger.error('---> %s' % str(e))
