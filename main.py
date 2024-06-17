"""
## Shop-Log-Parser

Copyright (c) [Vox314](https://github.com/Vox314) and [32294](https://github.com/32294)
[MIT](https://choosealicense.com/licenses/mit/), see [LICENSE](https://github.com/Price-Index/Shop-Log-Parser/blob/master/LICENSE) for more details.
"""

import os
import json
import datetime
import argparse
import time
import requests
import sys
import zipfile
import shutil
import tempfile
from openpyxl import Workbook
from decimal import Decimal
from metadata import script_version, dict_version, OWNER, REPO, DICT_REPO

class ShopLogParser:
    def __init__(self, line_limit=2000, thousands_separator=','):
        self.OWNER = OWNER
        self.REPO = REPO
        self.DICT_REPO = DICT_REPO
        self.script_version = script_version
        self.dict_version = dict_version
        self.start_time = time.time()
        self.args = self.parse_arguments()
        self.line_limit = line_limit
        self.thousands_separator = thousands_separator
        self.shop_info = []
        self.cache_dir = os.path.join(os.path.dirname(__file__), 'cache')
        self.exports_dir = os.path.join(os.path.dirname(__file__), 'exports')
        self.dict_dest_dir = os.path.join(os.path.dirname(__file__), 'dictionaries')
        self.temppath2 = None # Initialize temppath2
        self.path2 = None     # Initialize path2
        self.ensure_directories()
        self.load_cache_paths() # Load cache paths before determining the Minecraft directory
        self.minecraft_dir = self.determine_minecraft_directory()
        self.setup_workbook()
        self.run()

    def get_latest_release(self, owner, repo):
        """
        Fetches the latest release tag from the GitHub API.
        """

        token = 'abcdefg'

        headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'token {token}'
        }
        url = f'https://api.github.com/repos/{owner}/{repo}/releases/latest'
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()['tag_name']
        except requests.RequestException as e:
            print(f'\033[31mWarning: Could not connect to the GitHub API. vUnknown. Error: {e}\033[0m')
            return 'vUnknown'

    def parse_arguments(self):
        parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
        
        script_latest_version = self.get_latest_release(self.OWNER, self.REPO)
        dict_latest_version = self.get_latest_release(self.OWNER, self.DICT_REPO)
        
        def format_version_msg(repo, latest_version, current_version):
            if latest_version != current_version and latest_version != 'vUnknown':
                return f'\033[32m{repo} {latest_version} is now available!\033[0m\n'
            return ''
        
        new_script_version_msg = format_version_msg(self.REPO, script_latest_version, self.script_version)
        new_dict_version_msg = format_version_msg(self.DICT_REPO, dict_latest_version, self.dict_version)
        
        version_messages = f'{new_script_version_msg}{new_dict_version_msg}'
        current_versions = f'\033[38;2;170;0;170m{self.REPO} {self.script_version} & {self.DICT_REPO} {self.dict_version}\033[0m'
        copyright_msg = '\033[38;2;0;170;170mCopyright (c) 2023-present Vox313 and 32294\033[0m'
        
        parser.description = f'{version_messages}\n{current_versions}\n{copyright_msg}'
        
        if new_script_version_msg or new_dict_version_msg:
            parser.add_argument('-u', '--update', 
                                choices=['all', 'dicts', 'script'], 
                                default='all', 
                                help='\033[32mUpdates to a newer version.\033[0m')

        parser.add_argument('-p', '--path', type=self.file_path, help='Path to the .minecraft folder (this path will be cached).')
        parser.add_argument('-tp', '--temppath', type=self.file_path, help='Temporarily set the path for one run.')
        parser.add_argument('-rp', '--releasepath', action='store_true', help='Releases cached path.')
        return parser.parse_args()

    def ensure_directories(self):
        os.makedirs(self.cache_dir, exist_ok=True)
        os.makedirs(self.exports_dir, exist_ok=True)

    def determine_minecraft_directory(self):
        if self.args.path:
            return self.args.path
        elif self.temppath2:
            return self.temppath2
        elif self.path2:
            return self.path2
        else:
            if os.name == 'nt':
                return os.path.join(os.environ['APPDATA'], '.minecraft')
            else:
                home_dir = os.path.expanduser('~')
                if os.uname()[0] == 'Darwin':
                    return os.path.join(home_dir, 'Library', 'Application Support', 'minecraft')
                else:
                    return os.path.join(home_dir, '.minecraft')

    def setup_workbook(self):
        self.wb = Workbook()
        self.ws = self.wb.active
        self.wb_sql = Workbook()
        self.ws_sql = self.wb_sql.active
        self.ws.append(['Item', 'Price', 'Price Type', 'Owner', 'Stock', 'Repair Cost'])

    def load_cache_paths(self): # TODO: some kind of issue with temppath not going away? Also why temppath2??!
        self.path2 = None
        self.temppath2 = None
        if self.args.path:
            self.save_cache_path(self.args.path, 'path_cache.json')
        elif self.args.temppath:
            self.save_cache_path(self.args.temppath, 'temppath_cache.json')
        elif self.args.releasepath:
            self.release_cache_path('path_cache.json')
        else:
            self.temppath2 = self.load_cache_path('temppath_cache.json')
            self.path2 = self.load_cache_path('path_cache.json')

    def save_cache_path(self, path, cache_file):
        with open(os.path.join(self.cache_dir, cache_file), 'w') as f:
            json.dump({'path': path}, f)
        print(f'Path saved to cache: {path}')

    def release_cache_path(self, cache_file):
        cache_file_path = os.path.join(self.cache_dir, cache_file)
        if os.path.exists(cache_file_path):
            os.remove(cache_file_path)
        print(f'Saved path released!')

    def load_cache_path(self, cache_file):
        cache_file_path = os.path.join(self.cache_dir, cache_file)
        if os.path.exists(cache_file_path):
            with open(cache_file_path, 'r') as f:
                cache_data = json.load(f)
                return cache_data['path']
        return None

    def file_path(self, string):
        if os.path.isdir(string):
            return string
        else:
            raise FileNotFoundError(f"{string}\nThis Error may appear if you are using an unofficial minecraft launcher.\nPlease run the file using the --help arg.")

    def update(self, option):
        print("Updating...")

        def download_and_extract(repo):
            try:
                response = requests.get(f'https://api.github.com/repos/{self.OWNER}/{repo}/releases/latest')
                response.raise_for_status()
                latest_release = response.json()
                zipball_url = latest_release['zipball_url']

                # Create a temporary directory
                with tempfile.TemporaryDirectory() as tmpdirname:
                    zip_path = os.path.join(tmpdirname, 'latest_release.zip')

                    # Download the zip file
                    with open(zip_path, 'wb') as f:
                        for chunk in requests.get(zipball_url, stream=True).iter_content(chunk_size=8192):
                            f.write(chunk)

                    # Extract the zip file
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(tmpdirname)

                    # Find the extracted directories
                    extracted_dirs = [d for d in os.listdir(tmpdirname) if os.path.isdir(os.path.join(tmpdirname, d))]
                    if not extracted_dirs:
                        raise RuntimeError("No extracted directory found")
                    
                    extracted_dir = os.path.join(tmpdirname, extracted_dirs[0])

                    if repo == self.DICT_REPO:
                        # Define paths to specific files to be copied
                        shop_log_parser_dir = os.path.join(extracted_dir, 'Shop-Log-Parser')
                        version_py = os.path.join(extracted_dir, 'version.py')

                        # Copy specific files to destination directories
                        if not os.path.exists(self.dict_dest_dir):
                            os.makedirs(self.dict_dest_dir)

                        # Copy Shop-Log-Parser directory
                        if os.path.exists(shop_log_parser_dir):
                            for item in os.listdir(shop_log_parser_dir):
                                s = os.path.join(shop_log_parser_dir, item)
                                d = os.path.join(self.dict_dest_dir, item)
                                if os.path.isdir(s):
                                    shutil.copytree(s, d, dirs_exist_ok=True)
                                else:
                                    shutil.copy2(s, d)

                        # Copy version.py
                        if os.path.exists(version_py):
                            shutil.copy2(version_py, self.dict_dest_dir)

                    if repo == self.REPO:
                        script_name = os.path.basename(__file__)
                        new_script_path = os.path.join(extracted_dir, script_name)

                        if os.path.exists(new_script_path):
                            shutil.copy2(new_script_path, script_name)
                        else:
                            print(f"Updated script not found in the release: {new_script_path}")
                            sys.exit(1)

                    return extracted_dir

            except Exception as e:
                print(f"An error occurred while updating {repo}: {e}")
                sys.exit(1)

        try:
            # It basically always runs this function
            if option in ['all', 'dicts', 'script']:
                download_and_extract(self.DICT_REPO)

            print("Update complete.")
            if option in ['all', 'script']:
                script_name = os.path.basename(__file__)
                print("Restarting the script...")
                sys.argv = [sys.argv[0], '--help']
                os.execv(sys.executable, ['python'] + [script_name] + sys.argv[1:])

        except Exception as e:
            print(f"An error occurred during update: {e}")
            sys.exit(1)

    def run(self):
        if self.args.update:
            self.update(option=self.args.update)
        else:
            self.parse_shop_logs()
            self.save_workbook()

    def parse_shop_logs(self):
        try:
            latest_log = os.path.join(self.minecraft_dir, 'logs', 'latest.log')
            with open(latest_log, 'r') as file:
                lines = file.readlines()
                self.process_log_lines(lines)
        except FileNotFoundError as e:
            print(f"An error occurred: {e}")

    def process_log_lines(self, lines):
        for i, line in enumerate(lines):
            if '[CHAT] Shop Information:' in line:
                owner = self.extract_owner(line)
                stock = self.extract_stock(line)
                item = self.extract_item(line)
                item = self.resolve_item_name(item)
                repair_cost = self.extract_repair_costs(lines, i)
                buy, sell = self.extract_prices(lines, i)

                if not any(info['item'] == item and info['owner'] == owner and info['buy'] == buy and info['sell'] == sell and info['stock'] == stock and info['repair_cost'] == repair_cost for info in self.shop_info):
                    if buy is not None:
                        self.ws.append([item, buy, "B", owner, stock, repair_cost])
                    if sell is not None:
                        self.ws.append([item, sell, "S", owner, stock, repair_cost])
                    # Append detailed dictionary to shop_info in order to prevent duplicates
                    self.shop_info.append({'item': item, 'owner': owner, 'buy': buy, 'sell': sell, 'stock': stock, 'repair_cost': repair_cost})
                    
                    # TODO: remove in future
                    # Uncomment when debugging
                    #print(f"The owner is: {owner}")
                    print(f"The item is: {item}")
                    #print(f"The buy price is: ${buy}")
                    #print(f"The sell price is: ${sell}")
                    #print(f"The stock is: {stock}")
                    #print(f"The repair cost is: {repair_cost}")
                    print("---")

    def extract_item(self, line):
        return line.split('Item: ')[1].split('\n')[0]

    def resolve_item_name(self, item):
        dict_pages = ['enchanted_books.json', 'potions.json', 'splash_potions.json', 'lingering_potions.json', 'tipped_arrows.json', 'heads.json', 'fireworks.json']
        index_dictionary = {}
        for file_name in dict_pages:
            with open(os.path.join('dictionaries', file_name), 'r') as file:
                data = json.load(file)
                index_dictionary.update(data)

        if item.startswith(('Enchanted Book#', 'Potion#', 'Splash Potion#', 'Lingering Potion#', 'Tipped Arrow#', 'Player Head#', 'Firework Rocket#')):
            return index_dictionary.get(item, f'ERROR Unknown {item.split("#")[0]}: {item}')
        return item

    def extract_owner(self, line):
        return line.split('Owner: ')[1].split('\\n')[0]
    
    def extract_stock(self, line):
        return line.split('Stock: ')[1].split('\\n')[0]
    
    def extract_repair_costs(self, lines, i):
        repair_cost = 0
        
        # Search for repair cost
        for j in range(i + 1, min(i + self.line_limit + 1, len(lines))):
            if '[CHAT] Shop Information:' in lines[j]:
                break
            if '[CHAT] Repair Cost:' in lines[j]:
                repair_cost_line = lines[j]
                repair_cost = Decimal(repair_cost_line.split(':')[-1].strip())
                break
        
        return repair_cost

    def extract_prices(self, lines, i):
        buy, sell = None, None
        
        # Search for buy price
        buy_line = None
        for j in range(i + 1, min(i + self.line_limit + 1, len(lines))):
            if '[CHAT] Shop Information:' in lines[j]:
                break
            if '[CHAT] Buy' in lines[j] and 'for' in lines[j]:
                buy_line = lines[j]
                break
        
        if buy_line:
            amount_buy_string = buy_line.split('Buy ')[1].split(' for')[0]
            amount_buy_string = amount_buy_string.replace(self.thousands_separator, '').replace('\n', '')

            price_buy_string = buy_line.split('for ')[1]
            price_buy_string = price_buy_string.replace(self.thousands_separator, '').replace('\n', '')

            buy = Decimal(price_buy_string) / Decimal(amount_buy_string)

        # Search for sell price
        sell_line = None
        for j in range(i + 1, min(i + self.line_limit + 1, len(lines))):
            if '[CHAT] Shop Information:' in lines[j]:
                break
            if '[CHAT] Sell' in lines[j] and 'for' in lines[j]:
                sell_line = lines[j]
                break

        if sell_line:
            amount_sell_string = sell_line.split('Sell ')[1].split(' for')[0]
            amount_sell_string = amount_sell_string.replace(self.thousands_separator, '').replace('\n', '')

            price_sell_string = sell_line.split('for ')[1]
            price_sell_string = price_sell_string.replace(self.thousands_separator, '').replace('\n', '')

            sell = Decimal(price_sell_string) / Decimal(amount_sell_string)

        return buy, sell

    def save_workbook(self):
        date = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        file_path = os.path.join(self.exports_dir, f'shop_information {date}.xlsx')
        self.wb.save(file_path)
        self.wb_sql.save(file_path.replace('shop_information', 'shop_information_sql'))
        print(f'Elapsed Time: {(time.time() - self.start_time)*1000:.2f}ms')

if __name__ == "__main__":
    ShopLogParser()