"""
## Shop-Log-Parser

Copyright (c) [Vox314](https://github.com/Vox314) and [32294](https://github.com/32294) \\
[MIT](https://choosealicense.com/licenses/mit/), see [LICENSE](https://github.com/Price-Index/Shop-Log-Parser/blob/master/LICENSE) for more details.
"""

# import neccessary libraries
# please install openpyxl using "pip3.10 install openpyxl"
import os, json, datetime, argparse, time, requests
from openpyxl import Workbook
from resources.metadata import version, OWNER, REPO

# set a var to compare to later to find how long the script took
start_time = time.time()

def get_latest_release(owner, repo):
    headers = {
        'Accept': 'application/vnd.github+json'
    }
    url = f'https://api.github.com/repos/{owner}/{repo}/releases/latest'
    try:
        response = requests.get(url, headers=headers)
    except requests.exceptions.RequestException:
        print('\033[31mWarning: Could not connect to the GitHub API. vUnknown.\033[0m')
        return 'vUnknown'

    if response.status_code == 200:
        return response.json()['tag_name']
    else:
        print(f'\033[31mAn error occurred: {response.text}\033[0m')
        return 'vUnknown'

latest_version = get_latest_release(OWNER, REPO)

if latest_version == version or latest_version == 'vUnknown':
    new_version = ''
else:
    new_version = f'\033[32m{latest_version} is now available!\033[0m\n\n'

# Determine the Minecraft directory based on the user's operating system
def file_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise FileNotFoundError(f"{string}\nThis Error may appear if you are using an unofficial minecraft launcher.\nPlease run the file using the --h arg.")

# Arguments for the command
parser = argparse.ArgumentParser(
    formatter_class=argparse.RawTextHelpFormatter,
    description=f'{new_version}\033[38;2;170;0;170m{REPO} {version}\033[0m\n\033[38;2;0;170;170mCopyright (c) 2023-present Vox313 and 32294\033[0m'
    )

# args for resource pack path
parser.add_argument('-p', '--path', type=file_path, help='Path to the .minecraft folder (this path will be cached).')
parser.add_argument('-tp', '--temppath', type=file_path, help='Temporarily set the path for one run.')
parser.add_argument('-rp', '--releasepath', action='store_true', help='Releases cached path.')

# get the arguments given to the command
args = parser.parse_args()

# prevents NameError
path2 = None
temppath2 = None

# Create cache directory if it doesn't exist
cache_dir = os.path.join(os.path.dirname(__file__), 'cache', 'shop_log_parser')
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)

# Create exports directory if it doesn't exist
exports_dir = os.path.join(os.path.dirname(__file__), 'exports', 'shop_log_parser')
if not os.path.exists(exports_dir):
    os.makedirs(exports_dir)

# Check if --path is set
if args.path:
    # Save path to cache file
    with open(os.path.join(cache_dir, 'path_cache.json'), 'w') as f:
        json.dump({'path': args.path}, f)

    print(f'Path saved to cache: {args.path}')
elif args.temppath:
    # Save temporary path to cache file
    with open(os.path.join(cache_dir, 'temppath_cache.json'), 'w') as f:
        json.dump({'path': args.temppath}, f)

    print(f'Temporary path saved to cache: {args.temppath}')
elif args.releasepath:
    # Delete saved path from cache file
    cache_file = os.path.join(cache_dir, 'path_cache.json')
    if os.path.exists(cache_file):
        os.remove(cache_file)

    print(f'Saved path released!')
    
    # compare time var to earlier to find how long it took
    end_time = time.time()
    elapsed_time = (end_time - start_time)*1000
    print(f"Done! {elapsed_time:.2f}ms")
    exit()
else:
    # Load temporary path from cache file if it exists
    temp_cache_file = os.path.join(cache_dir, 'temp_path_cache.json')
    if os.path.exists(temp_cache_file):
        with open(temp_cache_file, 'r') as f:
            cache_data = json.load(f)
            temppath2 = cache_data['path']

        # Delete temporary cache file
        os.remove(temp_cache_file)

        print(f'Temporary path loaded from cache: {temppath2}')
    else:
        # Load permanent path from cache file if it exists
        perm_cache_file = os.path.join(cache_dir, 'path_cache.json')
        if os.path.exists(perm_cache_file):
            with open(perm_cache_file, 'r') as f:
                cache_data = json.load(f)
                path2 = cache_data['path']

            print(f'Permanent path loaded from cache: {path2}')

# test if path was given, if not use the default path based on what OS it's being ran on.
if args.path:
    minecraft_dir = args.path
elif temppath2:
    minecraft_dir = temppath2
elif path2:
    minecraft_dir = path2
else:
    if os.name == 'nt':  # Windows
        minecraft_dir = os.path.join(os.environ['APPDATA'], '.minecraft')
    elif os.name == 'posix':  # macOS and Linux
        home_dir = os.path.expanduser('~')
        if os.uname()[0] == 'Darwin':  # macOS
            minecraft_dir = os.path.join(home_dir, 'Library', 'Application Support', 'minecraft')
        else:  # Linux
            minecraft_dir = os.path.join(home_dir, '.minecraft')

# Create a new workbook and select the active worksheet
wb = Workbook()
ws = wb.active

wb_sql = Workbook()
ws_sql = wb_sql.active

# Set the column headers
ws.append(['Item', 'Owner', 'Buy:', 'Sell:'])

# Get the characters used as decimal and thousands separators on the user's machine
decimal_separator = '.'
thousands_separator = ','

# Shop info var for loop
shop_info = []

# Dictionary #?? ids into human readable names
dict_pages = ['enchanted_books.json','potions.json','splash_potions.json','lingering_potions.json','tipped_arrows.json','heads.json'] # dictionary pages (you can add more in the future)
index_dictionary = {}

for file_name in dict_pages:
    with open(os.path.join('resources', 'shop_log_parser', file_name), 'r') as file:
        data = json.load(file)
        index_dictionary.update(data)

#^ Read the chat log from the file
try:
    latest_log = os.path.join(minecraft_dir, 'logs', 'latest.log')

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

            if item.startswith('Splash Potion#'):
                try:
                    item = index_dictionary[item]
                except KeyError:
                    item = 'ERROR Unknown Splash Potion: ' + item

            if item.startswith('Lingering Potion#'):
                try:
                    item = index_dictionary[item]
                except KeyError:
                    item = 'ERROR Unknown Lingering Potion: ' + item

            if item.startswith('Tipped Arrow#'):
                try:
                    item = index_dictionary[item]
                except KeyError:
                    item = 'ERROR Unknown Tipped Arrow: ' + item

            if item.startswith('Player Head#'):
                try:
                    item = index_dictionary[item]
                except KeyError:
                    item = 'ERROR Unknown Head: ' + item

            #* get buy price, loops until it finds the line it's on 
            buy_line = None
            for j in range(i + 1, min(i + 2001, len(lines))):
                if '[CHAT] Shop Information:' in lines[j]:
                    # We have reached the end of the current item, stop searching for buy price information
                    break
                if '[CHAT] Buy' in lines[j] and 'for' in lines[j]:
                    buy_line = lines[j]
                    break

            # if the line was found, process it
            if buy_line:

                # Split and remove the thousands separator from the strings
                amount_buy_string = buy_line.split('Buy ')[1].split(' for')[0]
                amount_buy_string = amount_buy_string.replace(thousands_separator, '').replace('\n', '')

                # set the item count of the shop
                amount_buy = float(amount_buy_string)

                # Split and remove the thousands separator from the strings
                price_buy_string = buy_line.split('for ')[1]
                price_buy_string = price_buy_string.replace(thousands_separator, '').replace('\n', '')

                # set the price of the shop
                price_buy = float(price_buy_string)

                # caclulate the per item price
                buy = price_buy / amount_buy

            #* get sell price, loops until it finds the line it's on 
            sell_line = None
            for j in range(i + 1, min(i + 2001, len(lines))):
                if '[CHAT] Shop Information:' in lines[j]:
                    # We have reached the end of the current item, stop searching for sell price information
                    break
                if '[CHAT] Sell' in lines[j] and 'for' in lines[j]:
                    sell_line = lines[j]
                    break

            # if the line was found, process it
            if sell_line:
                
                # Split and remove the thousands separator from the strings
                amount_sell_string = sell_line.split('Sell ')[1].split(' for')[0]
                amount_sell_string = amount_sell_string.replace(thousands_separator, '').replace('\n', '')

                # set the item count of the shop
                amount_sell = float(amount_sell_string)

                # Split and remove the thousands separator from the strings
                price_sell_string = sell_line.split('for ')[1]
                price_sell_string = price_sell_string.replace(thousands_separator, '').replace('\n', '')

                # set the price of the shop
                price_sell = float(price_sell_string)

                # caclulate the per item price
                sell = price_sell / amount_sell

            #* add row to excel workbook if all data is present
            if not any(info['item'] == item and info['owner'] == owner and info['buy'] == buy and info['sell'] == sell for info in shop_info):
                
                # add sql and append
                if buy != None:

                    output = "INSERT INTO Prices VALUES ((SELECT ItemID FROM Items WHERE ItemName = '" + item + "'"
                    output += "), <SHOPID>, " + str(buy) + ", 'B');"
                    ws_sql.append([output])

                if sell != None:

                    output = "INSERT INTO Prices VALUES ((SELECT ItemID FROM Items WHERE ItemName = '" + item + "'"
                    output += "), <SHOPID>, " + str(sell) + ", 'S');"
                    ws_sql.append([output])

                # append to data only
                ws.append([item, owner, buy, sell])
                shop_info.append({'item': item, 'owner': owner, 'buy': buy, 'sell': sell})
                
                # Uncomment when debugging
                #print(f"The item is: {item}")
                #print(f"The buy price is: ${buy}")
                #print(f"The sell price is: ${sell}")

                # unset prices so they don't accidentally get re-used
                sell = None
                buy = None  

    #^ Save the workbook to a file
    customtime = datetime.datetime.now().time().strftime('%H-%M-%S')
    date = datetime.datetime.now().date()
    wb.save(os.path.join('exports', 'shop_log_parser', f'{date}-at-{customtime}-shopdata.xlsx'))
    wb.save(os.path.join('exports', 'shop_log_parser', 'latest-shopdata.xlsx'))
    wb_sql.save(os.path.join('exports', 'shop_log_parser', f'{date}-at-{customtime}-shopdata-sql.xlsx'))
    wb_sql.save(os.path.join('exports', 'shop_log_parser', 'latest-shopdata-sql.xlsx'))

    # compare time var to earlier to find how long it took
    end_time = time.time()
    elapsed_time = (end_time - start_time)*1000
    print(f"Done! {elapsed_time:.2f}ms")

# throw and error if it doesn't find the log file
except FileNotFoundError:
    print(f"{latest_log} could not be found.")