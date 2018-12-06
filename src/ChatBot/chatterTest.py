from chatterbot import ChatBot
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
chatterbot.set_trainer(ChatterBotCorpusTrainer)
#
# chatterbot.train(
#     "chatterbot.corpus.english"
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