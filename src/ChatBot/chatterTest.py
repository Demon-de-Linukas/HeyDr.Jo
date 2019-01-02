from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from chatterbot.conversation import Statement
from chatterbot.trainers import ChatterBotCorpusTrainer

chatterbot = ChatBot("Training Example",
                     storage_adapter="chatterbot.storage.SQLStorageAdapter",
                     logic_adapters=[
                         "chatterbot.logic.MathematicalEvaluation",
                         # "chatterbot.logic.TimeLogicAdapter",
                         "chatterbot.logic.BestMatch"
                     ],
                     input_adapter="chatterbot.input.TerminalAdapter",
                     output_adapter="chatterbot.output.TerminalAdapter",
                     database="../database.db"
                     )
chatterbot.set_trainer(ListTrainer)
chatterbot.train([
    "Who are you",
    "I am Dr. Jo, a chat bot of Städel Museum :-)",
    "What can you do?",
    "Me as a guide in Städel Museum can provide you more information about the art works. "
    "It can help you know better about the art and the museum. "
    "You can tell me the reference number of pictures or title of pictures, and I will tell you "
    "more about the art work! "
    "\nTo start visiting meseum please enter /visit."
    "\nTo chat with me please use command /chat. "
    "\nTo restart the chat bot please use command /restart."
])
chatterbot.set_trainer(ChatterBotCorpusTrainer)

chatterbot.train(
    "chatterbot.corpus.english"
)

print("Type something to begin...")

# The following loop will execute each time the user enters input
while True:
    try:
        # We pass None to this method because the parameter
        # is not used by the TerminalAdapter
        bot_input = chatterbot.get_response(None)

    # Press ctrl-c or ctrl-d on the keyboard to exit
    except (KeyboardInterrupt, EOFError, SystemExit):
        break