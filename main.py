"""
## Shop-Log-Parser

Copyright (c) [Vox314](https://github.com/Vox314) and [32294](https://github.com/32294) \\
[MIT](https://choosealicense.com/licenses/mit/), see [LICENSE](https://github.com/Price-Index/Shop-Log-Parser/blob/master/LICENSE) for more details.
"""

import os, json, datetime, argparse, time, requests
from openpyxl import Workbook
from resources.metadata import version, OWNER, REPO
from decimal import *

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

def file_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise FileNotFoundError(f"{string}\nThis Error may appear if you are using an unofficial minecraft launcher.\nPlease run the file using the --h arg.")

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawTextHelpFormatter,
    description=f'{new_version}\033[38;2;170;0;170m{REPO} {version}\033[0m\n\033[38;2;0;170;170mCopyright (c) 2023-present Vox313 and 32294\033[0m'
    )

parser.add_argument('-p', '--path', type=file_path, help='Path to the .minecraft folder (this path will be cached).')
parser.add_argument('-tp', '--temppath', type=file_path, help='Temporarily set the path for one run.')
parser.add_argument('-rp', '--releasepath', action='store_true', help='Releases cached path.')

args = parser.parse_args()

path2 = None
temppath2 = None

cache_dir = os.path.join(os.path.dirname(__file__), 'cache')
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)

exports_dir = os.path.join(os.path.dirname(__file__), 'exports')
if not os.path.exists(exports_dir):
    os.makedirs(exports_dir)

if args.path:
    with open(os.path.join(cache_dir, 'path_cache.json'), 'w') as f:
        json.dump({'path': args.path}, f)
    print(f'Path saved to cache: {args.path}')

elif args.temppath:
    with open(os.path.join(cache_dir, 'temppath_cache.json'), 'w') as f:
        json.dump({'path': args.temppath}, f)
    print(f'Temporary path saved to cache: {args.temppath}')

elif args.releasepath:
    cache_file = os.path.join(cache_dir, 'path_cache.json')
    if os.path.exists(cache_file):
        os.remove(cache_file)
    print(f'Saved path released!')
    end_time = time.time()
    elapsed_time = (end_time - start_time)*1000
    print(f"Done! {elapsed_time:.2f}ms")
    exit()

else:
    temp_cache_file = os.path.join(cache_dir, 'temp_path_cache.json')
    if os.path.exists(temp_cache_file):
        with open(temp_cache_file, 'r') as f:
            cache_data = json.load(f)
            temppath2 = cache_data['path']
        os.remove(temp_cache_file)
        print(f'Temporary path loaded from cache: {temppath2}')
    else:
        perm_cache_file = os.path.join(cache_dir, 'path_cache.json')
        if os.path.exists(perm_cache_file):
            with open(perm_cache_file, 'r') as f:
                cache_data = json.load(f)
                path2 = cache_data['path']
            print(f'Permanent path loaded from cache: {path2}')

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

wb = Workbook()
ws = wb.active

wb_sql = Workbook()
ws_sql = wb_sql.active

ws.append(['Item', 'Owner', 'Buy:', 'Sell:'])

decimal_separator = '.'
thousands_separator = ','

shop_info = []

dict_pages = ['enchanted_books.json','potions.json','splash_potions.json','lingering_potions.json','tipped_arrows.json','heads.json']
index_dictionary = {}

for file_name in dict_pages:
    with open(os.path.join('resources', 'dictionary', file_name), 'r') as file:
        data = json.load(file)
        index_dictionary.update(data)

try:
    latest_log = os.path.join(minecraft_dir, 'logs', 'latest.log')

    with open(latest_log, 'r') as file:
        lines = file.readlines()
        buy = sell = None

    for i, line in enumerate(lines):
        if '[CHAT] Shop Information:' in line:

            owner = line.split('Owner: ')[1].split('\\n')[0]
            item = line.split('Item: ')[1].split('\n')[0]

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

            buy_line = None
            for j in range(i + 1, min(i + 2001, len(lines))):
                if '[CHAT] Shop Information:' in lines[j]:
                    break
                if '[CHAT] Buy' in lines[j] and 'for' in lines[j]:
                    buy_line = lines[j]
                    break

            if buy_line:
                amount_buy_string = buy_line.split('Buy ')[1].split(' for')[0]
                amount_buy_string = amount_buy_string.replace(thousands_separator, '').replace('\n', '')

                price_buy_string = buy_line.split('for ')[1]
                price_buy_string = price_buy_string.replace(thousands_separator, '').replace('\n', '')

                buy = Decimal(price_buy_string) / Decimal(amount_buy_string)

            sell_line = None
            for j in range(i + 1, min(i + 2001, len(lines))):
                if '[CHAT] Shop Information:' in lines[j]:
                    break
                if '[CHAT] Sell' in lines[j] and 'for' in lines[j]:
                    sell_line = lines[j]
                    break

            if sell_line:
                amount_sell_string = sell_line.split('Sell ')[1].split(' for')[0]
                amount_sell_string = amount_sell_string.replace(thousands_separator, '').replace('\n', '')

                price_sell_string = sell_line.split('for ')[1]
                price_sell_string = price_sell_string.replace(thousands_separator, '').replace('\n', '')

                sell = Decimal(price_sell_string) / Decimal(amount_sell_string)

            if not any(info['item'] == item and info['owner'] == owner and info['buy'] == buy and info['sell'] == sell for info in shop_info):
                ws.append([item, owner, buy, sell])
                shop_info.append({'item': item, 'owner': owner, 'buy': buy, 'sell': sell})
                
                sell = None
                buy = None  

    customtime = datetime.datetime.now().time().strftime('%H-%M-%S')
    date = datetime.datetime.now().date()
    wb.save(os.path.join('exports', f'{date}-at-{customtime}-shopdata.xlsx'))
    wb.save(os.path.join('exports', 'latest-shopdata.xlsx'))

    end_time = time.time()
    elapsed_time = (end_time - start_time)*1000
    print(f"Done! {elapsed_time:.2f}ms")

except FileNotFoundError as e:
    print(f"An error occured: {e}")