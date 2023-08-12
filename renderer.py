"""
## MythicMC-Price-Index-Utils

Copyright (c) [Vox313](https://github.com/Vox314) and [32294](https://github.com/32294) \
MIT, see LICENSE for more details.
"""

# import neccessary libraries
import os, json, argparse, time, requests, zipfile

# set a var to compare to later to find how long the script took
start_time = time.time()

OWNER = 'Vox314'
REPO = 'MythicMC-Price-Index-Utils'
version = 'v0.1.3'

def get_latest_release(owner, repo):
    headers = {
        'Accept': 'application/vnd.github+json'
    }
    url = f'https://api.github.com/repos/{owner}/{repo}/releases/latest'
    try:
        response = requests.get(url, headers=headers)
    except requests.exceptions.RequestException:
        print('Warning: Could not connect to the GitHub API. vUnknown.')
        return 'vUnknown'

    if response.status_code == 200:
        return response.json()['tag_name']
    else:
        print(f'An error occurred: {response.text}')
        return 'vUnknown'

latest_version = get_latest_release(OWNER, REPO)

if latest_version == version or latest_version == 'vUnknown':
    new_version = ''
else:
    new_version = f'{latest_version} is now available!\n'

# Determine the Minecraft directory based on the user's operating system
def file_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise FileNotFoundError(f"{string}\nThis Error may appear if you are using an unofficial minecraft launcher.\nPlease run the file using the --h arg.")

# Arguments for the command
parser = argparse.ArgumentParser(
    formatter_class=argparse.RawTextHelpFormatter,
    description=f'{new_version}{REPO} {version}\nCopyright (c) Vox313 and 32294'
    )

# args for resource pack path
parser.add_argument('-p', '--path', type=file_path, help='Path to the .minecraft folder (this path will be cached).')
parser.add_argument('-tp', '--temppath', type=file_path, help='Temporarily set the path for one run.')
parser.add_argument('-rp', '--releasepath', action='store_true', help='Releases cached path.')

#! Vox finish these args, -s will be for renaming and moving to resourcepacks folder
#! -r will be for pulling the renders back
parser.add_argument('-s', '--sendrenders')
parser.add_argument('-r', '--retrieverenders')


# get the arguments given to the command
args = parser.parse_args()

# Create cache directory if it doesn't exist
cache_dir = os.path.join(os.path.dirname(__file__), 'cache/renderer')
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)

# Create exports directory if it doesn't exist
exports_dir = os.path.join(os.path.dirname(__file__), 'exports/renders')
if not os.path.exists(exports_dir):
    os.makedirs(exports_dir)

# Create the output directory if it doesn't exist
extracted_dir = os.path.join(os.path.dirname(__file__), 'cache/renderer/extracts')
if not os.path.exists(extracted_dir):
    os.makedirs(extracted_dir)

# Check if --path is set
if args.path:
    # Save path to cache file
    with open(os.path.join(cache_dir, 'path_cache.json'), 'w') as f:
        json.dump({'path': args.path}, f)

    print(f'Path saved to cache: {args.path}')
elif args.temppath:
    # Save temporary path to cache file
    with open(os.path.join(cache_dir, 'path_cache.json'), 'w') as f:
        json.dump({'path': args.temppath}, f)

    print(f'Temporary path saved to cache: {args.temppath}')
elif args.releasepath:
    # Delete saved path from cache file
    cache_file = os.path.join(cache_dir, 'path_cache.json')
    if os.path.exists(cache_file):
        os.remove(cache_file)
    
    print(f'Saved path released')
    
    # compare time var to earlier to find how long it took
    end_time = time.time()
    elapsed_time = (end_time - start_time)*1000
    print(f"Done! {elapsed_time:.2f}ms")
    exit()
else:
    # Load temporary path from cache file if it exists
    temp_cache_file = os.path.join(cache_dir, 'path_cache.json')
    if os.path.exists(temp_cache_file):
        with open(temp_cache_file, 'r') as f:
            cache_data = json.load(f)
            args.path = cache_data['path']

        # Delete temporary cache file
        os.remove(temp_cache_file)

        print(f'Temporary path loaded from cache: {args.path}')
    else:
        # Load permanent path from cache file if it exists
        perm_cache_file = os.path.join(cache_dir, 'path_cache.json')
        if os.path.exists(perm_cache_file):
            with open(perm_cache_file, 'r') as f:
                cache_data = json.load(f)
                args.path = cache_data['path']

            print(f'Permanent path loaded from cache: {args.path}')

# test if path was given, if not use the default path based on what OS it's being ran on.
if args.path:
    path = args.path
else:
    if os.name == 'nt':  # Windows
        minecraft_dir = os.path.join(os.environ['APPDATA'], '.minecraft', 'versions')
    elif os.name == 'posix':  # macOS and Linux
        home_dir = os.path.expanduser('~')
        if os.uname()[0] == 'Darwin':  # macOS
            minecraft_dir = os.path.join(home_dir, 'Library', 'Application Support', 'minecraft', 'versions')
        else:  # Linux
            minecraft_dir = os.path.join(home_dir, '.minecraft', 'versions')

    # Get a list of all installed Minecraft versions that start with 1.x
    versions = [d for d in os.listdir(minecraft_dir) if os.path.isdir(os.path.join(minecraft_dir, d)) and d.startswith('1.')]

    # Sort the versions in descending order
    versions.sort(key=lambda v: tuple(map(int, v.split('.'))), reverse=True)

    # Set the path to the latest Minecraft .jar file
    jar_file_path = os.path.join(minecraft_dir, versions[0], f'{versions[0]}.jar')

    # Open the .jar file
    with zipfile.ZipFile(jar_file_path, 'r') as jar_file:
        # Extract all files in the assets folder
        for file in jar_file.namelist():
            if file.startswith('assets/'):
                jar_file.extract(file, extracted_dir)

try:
    # compare time var to earlier to find how long it took
    end_time = time.time()
    elapsed_time = (end_time - start_time)*1000
    print(f"Done! {elapsed_time:.2f}ms")
except:
    raise