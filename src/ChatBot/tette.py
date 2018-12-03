from ChatBot import dictionary as cc



def get_semantic(text,dict):
    for dd in dict:
        if text in dict[dd]:
            print('Key is \'%s\'' % (dd))
            return dd


get_semantic('ciao', cc.dict)