"""
## MythicMC-Price_Index-Utils

Copyright (c) [Vox313](https://github.com/Vox314) and [32294](https://github.com/32294) \
MIT, see LICENSE for more details.
"""

# import neccessary libraries
import os, json, datetime, argparse, time, requests

# set a var to compare to later to find how long the script took
start_time = time.time()

OWNER = 'Vox314'
REPO = 'MythicMC-shoplogger'
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
    if os.path.isfile(string):
        return string
    else:
        raise FileNotFoundError(f"{string}\nThis Error may appear if you are using an unofficial minecraft launcher.\nPlease run the file using the --h arg.")

# Arguments for the command
parser = argparse.ArgumentParser(
    formatter_class=argparse.RawTextHelpFormatter,
    description=f'{new_version}{REPO} {version}\nCopyright (c) Vox313 and 32294'
    )

# Set up argument parser
parser.add_argument('-pp', '--pathresourcepack', type=file_path, help='Path to the resource pack folder (this path will be cached).')
parser.add_argument('-tpp', '--temppathresourcepack', type=file_path, help='Temporarily set the path for one run.')
parser.add_argument('-rpp', '--releasepathresourcpack', action='store_true', help='Releases cached path.')

parser.add_argument('-pr', '--pathrenders', type=file_path, help='Path to the renders folder from the mod (this path will be cached).')
parser.add_argument('-tpr', '--temppathrenders', type=file_path, help='Temporarily set the path for one run.')
parser.add_argument('-rpr', '--releasepathrenders', action='store_true', help='Releases cached path.')


#! Vox finish these args, -s will be for renaming and moving to resourcepacks folder
#! -r will be for pulling the renders back
parser.add_argument('-s', '--sendrenders',
parser.add_argument('-r', '--retrieverenders',


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

# Check if --pathresourcepack is set
if args.pathresourcepack:
    # Save path to cache file
    with open(os.path.join(cache_dir, 'resourcepack_path_cache.json'), 'w') as f:
        json.dump({'path': args.pathresourcepack}, f)

    print(f'Path saved to cache: {args.pathresourcepack}')
elif args.temppathresourcepack:
    # Save temporary path to cache file
    with open(os.path.join(cache_dir, 'resourcepack_temp_path_cache.json'), 'w') as f:
        json.dump({'path': args.temppathresourcepack}, f)

    print(f'Temporary path saved to cache: {args.temppathresourcepack}')
elif args.releasepathresourcepack:
    # Delete saved path from cache file
    cache_file = os.path.join(cache_dir, 'resourcepack_path_cache.json')
    if os.path.exists(cache_file):
        os.remove(cache_file)

    print(f'Saved path released')
else:
    # Load temporary path from cache file if it exists
    temp_cache_file = os.path.join(cache_dir, 'resourcepack_temp_path_cache.json')
    if os.path.exists(temp_cache_file):
        with open(temp_cache_file, 'r') as f:
            cache_data = json.load(f)
            args.pathresourcepack = cache_data['path']

        # Delete temporary cache file
        os.remove(temp_cache_file)

        print(f'Temporary path loaded from cache: {args.pathresourcepack}')
    else:
        # Load permanent path from cache file if it exists
        perm_cache_file = os.path.join(cache_dir, 'resourcepack_path_cache.json')
        if os.path.exists(perm_cache_file):
            with open(perm_cache_file, 'r') as f:
                cache_data = json.load(f)
                args.pathresourcepack = cache_data['path']

            print(f'Permanent path loaded from cache: {args.pathresourcepack}')

# Check if --pathrenders is set
if args.pathrenders:
    # Save path to cache file
    with open(os.path.join(cache_dir, 'renders_path_cache.json'), 'w') as f:
        json.dump({'path': args.pathrenders}, f)

    print(f'Path saved to cache: {args.pathrenders}')
elif args.temppathrenders:
    # Save temporary path to cache file
    with open(os.path.join(cache_dir, 'renders_temp_path_cache.json'), 'w') as f:
        json.dump({'path': args.temppathrenders}, f)

    print(f'Temporary path saved to cache: {args.temppath}')
elif args.releasepathrenders:
    # Delete saved path from cache file
    cache_file = os.path.join(cache_dir, 'renders_path_cache.json')
    if os.path.exists(cache_file):
        os.remove(cache_file)

    print(f'Saved path released')
else:
    # Load temporary path from cache file if it exists
    temp_cache_file = os.path.join(cache_dir, 'renders_temp_path_cache.json')
    if os.path.exists(temp_cache_file):
        with open(temp_cache_file, 'r') as f:
            cache_data = json.load(f)
            args.pathrenders = cache_data['path']

        # Delete temporary cache file
        os.remove(temp_cache_file)

        print(f'Temporary path loaded from cache: {args.pathrenders}')
    else:
        # Load permanent path from cache file if it exists
        perm_cache_file = os.path.join(cache_dir, 'renders_path_cache.json')
        if os.path.exists(perm_cache_file):
            with open(perm_cache_file, 'r') as f:
                cache_data = json.load(f)
                args.pathrenders = cache_data['path']

            print(f'Permanent path loaded from cache: {args.path}')
