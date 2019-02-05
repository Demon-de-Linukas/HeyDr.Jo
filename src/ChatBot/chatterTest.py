from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer, UbuntuCorpusTrainer
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
    'When will the museum close?',
    'On Tuesday, Wednesday, Saturday and Sunday it will close at 18:00. On Thursday and Friday it will close at 21:00.'
])
# chatterbot.set_trainer(ChatterBotCorpusTrainer)
#
# chatterbot.train(
#      "C:/Users\linuk\Desktop\chatterbot-corpus-master\chatterbot_corpus\data\english"
# )

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