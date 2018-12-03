import requests
from src.DataSearch import utility as ut


# name='Peter_Paul_Rubens'
# add = 'https://de.wikipedia.org/w/api.php?action=query&titles=Christian_Georg_Schütz_der_Ältere&prop=extracts&exintro&format=json&formatversion=2'
# # add = 'https://de.wikipedia.org/wiki/Christian_Georg_Schütz_der_Ältere'
# # jadd = 'http://dbpedia.org/data/'+name+'.json'
# data = requests.get(add).json
# what = data.query.pages[0].extract

# matteo is a dictionary with lots of keys
# that correspond to the player's properties.
# Each value is a list of dictionaries itself.

print(ut.search_wiki('China'))
# # 1.88  (float)
# birth_year = matteo['http://dbpedia.org/ontology/birthYear'][0]['value']
# # '1995'  (string)
# hand = matteo['http://dbpedia.org/ontology/plays'][0]['value']
# # 'Right-handed (two-handed backhand)'  (string)
# singles_rank = matteo['http://dbpedia.org/property/currentsinglesranking'][0]['value']
# # 'No. 171'  (string)