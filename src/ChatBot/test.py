import csv
import pandas as pd

logPath='userCache.csv'
userid='781549524'
key='chatting'
value='True'
# with open(logPath, "rt", encoding='utf-8') as log:
csvdict = csv.DictReader(open(logPath))
dictrow =[]
for row in csvdict:
    if row['userID'] == userid:
        row[key] = value
    #rowcache.update(row)
    dictrow.append(row)

with open(logPath, "w+", encoding='utf-8',newline='') as lloo:
    # lloo.write(new_a_buf.getvalue())
    fieldnames = ['userID','knowInfo','artist','style','period','chatting']
    wrier = csv.DictWriter(lloo,fieldnames)
    wrier.writeheader()
    for wowow in dictrow:
        wrier.writerow(wowow)





inde = ['userID','knowInfo','artist','style','period','chatting']
df = pd.read_csv(logPath, header=None, names=inde, index_col="userID")
data = df.to_dict('index')
curColumn = data['781549524']
curColumn['chatting'] = 'True'
# row = {"foo": foo, "bar": bar, "baz":''}
data.pop('781549524')
data['781549524'] = curColumn

df = pd.DataFrame(data)
df.to_csv(logPath)

with open(logPath, "a+", encoding='utf-8') as log:
    writer = csv.writer(log)
    writer.writerow(['asdqsefq', '0', '', '', '', 'False'])

# logPath = 'userCache.csv'
# with open(logPath, "rt", encoding='utf-8') as log:
#     reader = csv.DictReader(log)
#     for row in reader:
#         if row['userID'] == '781549524':
#            print(row['knowInfo'])