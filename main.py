import os, json, datetime
from openpyxl import Workbook

#? Install colorful comments extention in VSC to see colored comments

#TODO uncomment for windows and not multimc
#minecraft_dir = os.path.join(os.environ['APPDATA'], '.minecraft', 'logs')
#latest_log = os.path.join(minecraft_dir, 'latest.log')

#! local path bc I'm to lazy to code linux support correctly
latest_log = "./parsefiles/latest.log"

#^ Create a new workbook and select the active worksheet
wb = Workbook()
ws = wb.active

#^ Set the column headers
ws.append(['Item', 'Owner', 'Buy:', 'Sell:'])

#^ Get the characters used as decimal and thousands separators on the user's machine
decimal_separator = '.'
thousands_separator = ','

#^ create vars for later
#* shop info var for loop
shop_info = []

#* Dictionary used to translate for humans
dict_pages = ['enchanted_books.json','potions.json','heads.json'] # dictionary pages (you can add more in the future)
index_dictionary = {}

for file_name in dict_pages:
    with open(f"./dictionary/{file_name}", 'r') as file:
        data = json.load(file)
        index_dictionary.update(data)

#^ Read the chat log from the file
try:
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
            item = line.split('Item: ')[1].split('\n')[0]

            #~ Look if the item name starts with Enchanted Book, if yes make it an enchantment, if yes but no, then unknown, if no; then just pass by.
            #~ (For potions, enchanted books, and music discs.)
            if item.startswith('Enchanted Book#'):
                try:
                    item = index_dictionary[item]
                except KeyError:
                    item = 'ERROR Unknown Enchanted Book: ' + item
            
            if item.startswith('Potion#'):
                try:
                    item = index_dictionary[item]
                except KeyError:
                    item = 'ERROR Unknown Potion: ' + item
            
            if item.startswith('Player Head#'):
                try:
                    item = index_dictionary[item]
                except KeyError:
                    item = 'ERROR Unknown Head: ' + item

            #* get buy price
            if (i + 1 < len(lines) and '[CHAT] Buy' in lines[i + 1] and 'for' in lines[i + 1]) or (i + 2 < len(lines) and '[CHAT] Buy' in lines[i + 2] and 'for' in lines[i + 2]):
                if '[CHAT] Buy' in lines[i + 1]:
                    buy_line = lines[i + 1]
                else:
                    buy_line = lines[i + 2]
                
                # Remove the thousands separator from the strings
                amount_buy_string = buy_line.split('Buy ')[1].split(' for')[0]
                amount_buy_string = amount_buy_string.replace(thousands_separator, '').replace('\n', '')
                amount_buy = float(amount_buy_string)

                price_buy_string = buy_line.split('for ')[1]
                price_buy_string = price_buy_string.replace(thousands_separator, '').replace('\n', '')
                price_buy = float(price_buy_string)
                buy = price_buy / amount_buy

            #* get sell price
            if (i + 1 < len(lines) and '[CHAT] Sell' in lines[i + 1] and 'for' in lines[i + 1]) or (i + 2 < len(lines) and '[CHAT] Sell' in lines[i + 2] and 'for' in lines[i + 2]):
                if '[CHAT] Sell' in lines[i + 1]:
                    sell_line = lines[i + 1]
                else:
                    sell_line = lines[i + 2]

                # Remove the thousands separator from the strings
                amount_sell_string = sell_line.split('Sell ')[1].split(' for')[0]
                amount_sell_string = amount_sell_string.replace(thousands_separator, '').replace('\n', '')
                amount_sell = float(amount_sell_string)

                price_sell_string = sell_line.split('for ')[1]
                price_sell_string = price_sell_string.replace(thousands_separator, '').replace('\n', '')
                price_sell = float(price_sell_string)
                sell = price_sell / amount_sell

            #* add row to excel workbook if all data is present
            if not any(info['item'] == item and info['owner'] == owner and info['buy'] == buy and info['sell'] == sell for info in shop_info):
                ws.append([item, owner, buy, sell])
                shop_info.append({'item': item, 'owner': owner, 'buy': buy, 'sell': sell})

    #^ Save the workbook to a file
    time = datetime.datetime.now().time().strftime('%H-%M-%S')
    date = datetime.datetime.now().date()
    wb.save(f'./exports/{date}-at-{time}-shopdata.xlsx')
    wb.save('./exports/latest-shopdata.xlsx')

except FileNotFoundError:
    print(f"{latest_log} could not be found.")
