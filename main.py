"""
## MythicMC-Shoplogger

Copyright (c) [Vox313](https://github.com/Vox314) and [32294](https://github.com/32294) \
MIT, see LICENSE for more details.
"""

import os, json, datetime, argparse, time
from openpyxl import Workbook

start_time = time.time()

#? Install colorful comments extention in VSC to see colored comments

# Determine the Minecraft directory based on the user's operating system
def file_path(string):
    if os.path.isfile(string):
        return string
    else:
        raise FileNotFoundError(f"{string}\nThis Error may appear if you are using an unofficial minecraft launcher.\nPlease run the file using the --h arg.")

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawTextHelpFormatter,
    description=f'MythicMC shoplogger\nA logger for MythicMC shops to an excel file.'
    )
parser.add_argument('--path', type=file_path, help='Path to the latest.log file of the Minecraft directory')
args = parser.parse_args()

if args.path:
    latest_log = args.path
else:
    if os.name == 'nt':  # Windows
        minecraft_dir = os.path.join(os.environ['APPDATA'], '.minecraft', 'logs')
    elif os.name == 'posix':  # macOS and Linux
        home_dir = os.path.expanduser('~')
        if os.uname()[0] == 'Darwin':  # macOS
            minecraft_dir = os.path.join(home_dir, 'Library', 'Application Support', 'minecraft', 'logs')
        else:  # Linux
            minecraft_dir = os.path.join(home_dir, '.minecraft', 'logs')

    latest_log = os.path.join(minecraft_dir, 'latest.log')

# Create a new workbook and select the active worksheet
wb = Workbook()
ws = wb.active

# Set the column headers
ws.append(['Item', 'Owner', 'Buy:', 'Sell:'])

# Get the characters used as decimal and thousands separators on the user's machine
decimal_separator = '.'
thousands_separator = ','

# Create vars for later
# Shop info var for loop
shop_info = []

# Dictionary used to translate for humans
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
            buy_line = None
            for j in range(i + 1, min(i + 2001, len(lines))):
                if '[CHAT] Shop Information:' in lines[j]:
                    # We have reached the end of the current item, stop searching for buy price information
                    break
                if '[CHAT] Buy' in lines[j] and 'for' in lines[j]:
                    buy_line = lines[j]
                    break

            if buy_line:
                # Remove the thousands separator from the strings
                amount_buy_string = buy_line.split('Buy ')[1].split(' for')[0]
                amount_buy_string = amount_buy_string.replace(thousands_separator, '').replace('\n', '')
                amount_buy = float(amount_buy_string)

                price_buy_string = buy_line.split('for ')[1]
                price_buy_string = price_buy_string.replace(thousands_separator, '').replace('\n', '')
                price_buy = float(price_buy_string)
                buy = price_buy / amount_buy

            #* get sell price
            sell_line = None
            for j in range(i + 1, min(i + 2001, len(lines))):
                if '[CHAT] Shop Information:' in lines[j]:
                    # We have reached the end of the current item, stop searching for sell price information
                    break
                if '[CHAT] Sell' in lines[j] and 'for' in lines[j]:
                    sell_line = lines[j]
                    break

            if sell_line:
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
                
                # Uncomment when debugging
                #print(f"The item is: {item}")
                #print(f"The buy price is: ${buy}")
                #print(f"The sell price is: ${sell}")

                sell = None
                buy = None  

    #^ Save the workbook to a file
    customtime = datetime.datetime.now().time().strftime('%H-%M-%S')
    date = datetime.datetime.now().date()
    wb.save(f'./exports/{date}-at-{customtime}-shopdata.xlsx')
    wb.save('./exports/latest-shopdata.xlsx')

    end_time = time.time()
    elapsed_time = (end_time - start_time)*1000
    print(f"Done! {elapsed_time:.2f}ms")

except FileNotFoundError:
    print(f"{latest_log} could not be found.")
