import time
import telebot as tb
from lxml import etree
from src.DataSearch import utility as ut

token = '706415631:AAG1Y6sfLmvxU_TENOaVwGA3hzXdaGJiaWo'
pathOfDataset = 'C:/Users\linuk\Desktop\Staedel/Objekte.xml'
pathOfGene = 'generatedDataSet.xml'
tree = etree.parse(pathOfDataset)
root = tree.getroot()
currentrecord = None
__knowInfo__ = 0

treeGene = etree.parse(pathOfGene)
rootGene = treeGene.getroot()

bot = tb.TeleBot(token)


def get_from_data(command,rootAll,rootGene):
    return ut.get_start_info(command,rootAll)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, u"Hello, welcome to this bot!")

def get_input(messageList):#List):
    global currentrecord, __knowInfo__
    for message in messageList:
        chatid = message.chat.id
        if message.text.upper() == 'YES' and __knowInfo__ >= 1:
            detail_Info, dict = ut.get_details(currentrecord)
            bot.reply_to(message, detail_Info)
            chatid = message.chat.id
            bot.send_message(chatid, u'Do you want to know more?')
            __knowInfo__ += 1
        elif message.text.upper() == 'NO' and __knowInfo__ >= 1:
            bot.send_message(chatid,  u'Please give the number or the name of the object!')
            __knowInfo__ = 0
        else:
            #for message in messageList:
            title, artist, period, record=get_from_data(message.text, root, rootGene)
            bot.reply_to(message, 'Title: \n%s\n\nCreator: \n%s\n\nCreated period: \n%s\n\n'%(title,artist,period))
            bot.send_message(chatid,  u'Do you want to know more?')
            currentrecord = record
            __knowInfo__ =1


@bot.message_handler(content_types=['text'])
def get_details(message):
    global __knowInfo__
    if message.text.upper() == 'YEasdS' and __knowInfo__>=1:
        detail_Info, dict=ut.get_details(currentrecord)
        bot.reply_to(message, detail_Info)
        chatid =message.chat.id
        bot.send_message(chatid,  u'Do you want to know more?')
        __knowInfo__ +=1

if __name__ == '__main__':
        bot.set_update_listener(get_input)

        bot.polling(none_stop=True)
        while True:
            time.sleep(1)
