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
from resources.metadata import version, OWNER, REPO

def get_latest_release(owner, repo):
    """
    Fetches the latest release tag from the GitHub API.
    """
    headers = {
        'Accept': 'application/vnd.github+json'
    }
    url = f'https://api.github.com/repos/{owner}/{repo}/releases/latest'
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()['tag_name']
    except requests.RequestException as e:
        print(f'\033[31mWarning: Could not connect to the GitHub API. vUnknown. Error: {e}\033[0m')
        return 'vUnknown'

class ShopLogParser:
    def __init__(self):
        self.start_time = time.time()
        self.args = self.parse_arguments()
        self.shop_info = []
        self.cache_dir = os.path.join(os.path.dirname(__file__), 'cache')
        self.exports_dir = os.path.join(os.path.dirname(__file__), 'exports')
        self.temppath2 = None  # Initialize temppath2
        self.path2 = None      # Initialize path2
        self.ensure_directories()
        self.load_cache_paths()  # Load cache paths before determining the Minecraft directory
        self.minecraft_dir = self.determine_minecraft_directory()
        self.setup_workbook()
        self.run()

    def parse_arguments(self):
        parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
        latest_version = get_latest_release(OWNER, REPO)
        new_version_msg = f'\033[32m{latest_version} is now available!\033[0m\n\n' if latest_version != version else ''
        parser.description = f'{new_version_msg}\033[38;2;170;0;170m{REPO} {version}\033[0m\n\033[38;2;0;170;170mCopyright (c) 2023-present Vox313 and 32294\033[0m'
        
        if latest_version != version and latest_version != 'vUnknown':
            parser.add_argument('-u', '--update', nargs='?', const='latest', help='\033[32mUpdates to a newer version.\033[0m')

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
        self.ws.append(['Item', 'Price', 'Price Type', 'Owner'])

    def load_cache_paths(self):
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
            raise FileNotFoundError(f"{string}\nThis Error may appear if you are using an unofficial minecraft launcher.\nPlease run the file using the --h arg.")

    def update(self):
        print("Updating...")
        try:
            response = requests.get(f'https://api.github.com/repos/{OWNER}/{REPO}/releases/latest')
            response.raise_for_status()
            latest_release = response.json()
            zipball_url = latest_release['zipball_url']

            with tempfile.TemporaryDirectory() as tmpdirname:
                zip_path = os.path.join(tmpdirname, 'latest_release.zip')
                with open(zip_path, 'wb') as f:
                    for chunk in requests.get(zipball_url, stream=True).iter_content(chunk_size=8192):
                        f.write(chunk)

                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(tmpdirname)

                extracted_dir = next(os.path.join(tmpdirname, d) for d in os.listdir(tmpdirname) if os.path.isdir(os.path.join(tmpdirname, d)))
                script_name = os.path.basename(__file__)
                new_script_path = os.path.join(extracted_dir, script_name)

                if os.path.exists(new_script_path):
                    shutil.copy2(new_script_path, script_name)
                else:
                    print(f"Updated script not found in the release: {new_script_path}")
                    sys.exit(1)

            print("Update complete. Restarting the script...")
            sys.argv = [sys.argv[0], '--help']
            os.execv(sys.executable, ['python'] + [script_name] + sys.argv[1:])
        except Exception as e:
            print(f"An error occurred during update: {e}")
            sys.exit(1)

    def run(self):
        if self.args.update:
            self.update()
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
                item = self.extract_item(line)
                item = self.resolve_item_name(item)
                buy, sell = self.extract_prices(lines, i)

                if not any(info['item'] == item and info['owner'] == owner and info['buy'] == buy and info['sell'] == sell for info in self.shop_info):
                    if buy is not None:
                        self.ws.append([item, buy, "B", owner])
                    if sell is not None:
                        self.ws.append([item, sell, "S", owner])
                    self.shop_info.append({'item': item, 'owner': owner, 'buy': buy, 'sell': sell})

    def extract_owner(self, line):
        return line.split('Owner: ')[1].split('\\n')[0]

    def extract_item(self, line):
        return line.split('Item: ')[1].split('\n')[0]

    def resolve_item_name(self, item):
        dict_pages = ['enchanted_books.json', 'potions.json', 'splash_potions.json', 'lingering_potions.json', 'tipped_arrows.json', 'heads.json']
        index_dictionary = {}
        for file_name in dict_pages:
            with open(os.path.join('resources', 'dictionary', file_name), 'r') as file:
                data = json.load(file)
                index_dictionary.update(data)

        if item.startswith(('Enchanted Book#', 'Potion#', 'Splash Potion#', 'Lingering Potion#', 'Tipped Arrow#', 'Player Head#')):
            return index_dictionary.get(item, f'ERROR Unknown {item.split("#")[0]}: {item}')
        return item

    def extract_prices(self, lines, i):
        buy, sell = None, None
        if 'Buying at: ' in lines[i + 1]:
            buy = Decimal(lines[i + 1].split('Buying at: ')[1].split(' | ')[0])
        if 'Selling at: ' in lines[i + 2]:
            sell = Decimal(lines[i + 2].split('Selling at: ')[1].split(' | ')[0])
        return buy, sell

    def save_workbook(self):
        date = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        file_path = os.path.join(self.exports_dir, f'shop_information {date}.xlsx')
        self.wb.save(file_path)
        self.wb_sql.save(file_path.replace('shop_information', 'shop_information_sql'))
        print(f'Elapsed Time: {(time.time() - self.start_time)*1000:.2f}ms')

if __name__ == "__main__":
    ShopLogParser()