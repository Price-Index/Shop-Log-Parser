import os, json
from openpyxl import Workbook

#? Install colorful comments extention in VSC to see colored comments

#TODO uncomment for windows and not multimc
# minecraft_dir = os.path.join(os.environ['APPDATA'], '.minecraft', 'logs')
# latest_log = os.path.join(minecraft_dir, 'latest.log')

#! local path bc i'm to lazy to code linux support corrently
latest_log = "./latest.log"

#^ Create a new workbook and select the active worksheet
wb = Workbook()
ws = wb.active

#^ Set the column headers
ws.append(['Item', 'Owner', 'Buy:', 'Sell:'])

#^ create vars for later
#* shop info var for loop
shop_info = []

# Dictionary used to translate for humans
dict_pages = ['enchanted_books.json'] # dictionary pages (you can add more in the future)
index_dictionary = {}

for file_name in dict_pages:
    with open(file_name, 'r') as file:
        data = json.load(file)
        index_dictionary.update(data)

#^ Read the chat log from the file
with open(latest_log, 'r') as file:
    lines = file.readlines()
    buy = sell = None
    
    #^ runs when fines the correct shop info header
    for i, line in enumerate(lines):
        if '[CHAT] Shop Information:' in line:
            
            #* get owner of the shop
            owner = line.split('Owner: ')[1].split('\\n')[0]

            #* get stock of shop
            # stock = line.split('Stock: ')[1].split('\\n')[0]

            #* get item name
            item = line.split('Item: ')[1].split('\\n')[0]

            #~ Compare item name against dictionary to see if item name should be changed to something more readable
            #~ (For potions, enchanted books, and music discs.)
            if item in index_dictionary.keys:
                item = index_dictionary[item]
            
            #* get buy price
            if (i + 1 < len(lines) and '[CHAT] Buy' in lines[i + 1] and 'for' in lines[i + 1]) or (i + 2 < len(lines) and '[CHAT] Buy' in lines[i + 2] and 'for' in lines[i + 2]):
                if '[CHAT] Buy' in lines[i + 1]:
                    buy_line = lines[i + 1]
                else:
                    buy_line = lines[i + 2]
                amount_buy = float(buy_line.split('Buy ')[1].split(' for')[0])
                price_buy = float(buy_line.split('for ')[1])
                buy = price_buy / amount_buy

            #* get sell price
            if (i + 1 < len(lines) and '[CHAT] Sell' in lines[i + 1] and 'for' in lines[i + 1]) or (i + 2 < len(lines) and '[CHAT] Sell' in lines[i + 2] and 'for' in lines[i + 2]):
                if '[CHAT] Sell' in lines[i + 1]:
                    sell_line = lines[i + 1]
                else:
                    sell_line = lines[i + 2]
                amount_sell = float(sell_line.split('Sell ')[1].split(' for')[0])
                price_sell = float(sell_line.split('for ')[1])
                sell = price_sell / amount_sell

            #* add row to excel workbook if all data is present
            if not any(info['item'] == item and info['owner'] == owner and info['buy'] == buy and info['sell'] == sell for info in shop_info):
                ws.append([item, owner, buy, sell])
                shop_info.append({'item': item, 'owner': owner, 'buy': buy, 'sell': sell})

#^ Save the workbook to a file
wb.save('shopdata.xlsx')
