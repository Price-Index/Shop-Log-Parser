"""
## MythicMC-Price-Index-Utils

Copyright (c) [Vox313](https://github.com/Vox314) and [32294](https://github.com/32294) \
MIT, see LICENSE for more details.
"""

# import neccessary libraries
import os, json, argparse, time, requests, zipfile, shutil, sys
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
    description=f'{new_version}\033[38;2;170;0;170m{REPO} {version}\033[0m\n\033[38;2;0;170;170mCopyright (c) Vox313 and 32294\033[0m'
    )

# args for resource pack path
parser.add_argument('-p', '--path', type=file_path, help='Path to the .minecraft folder (this path will be cached).')
parser.add_argument('-tp', '--temppath', type=file_path, help='Temporarily set the path for one run.')
parser.add_argument('-rp', '--releasepath', action='store_true', help='Releases cached path.')

#! Vox finish these args, -s will be for renaming and moving to resourcepacks folder
#! -r will be for pulling the renders back
parser.add_argument('-s', '--sendrenders', action='store_true', help='Sends the specific batch to the pack in your minecraft directory.')
parser.add_argument('-r', '--retrieverenders', action='store_true', help='Outputs the first batch of the rendered files.')
parser.add_argument('-d', '--defaultbatch', action='store_true', help='Sets the default batch back to 0.')

# get the arguments given to the command
args = parser.parse_args()

# prevents NameError
path2 = None
temppath2 = None

# Create cache directory if it doesn't exist
cache_dir = os.path.join(os.path.dirname(__file__), 'cache/renderer')
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)

# Create exports directory if it doesn't exist
exports_dir = os.path.join(os.path.dirname(__file__), 'exports/renders')
if not os.path.exists(exports_dir):
    os.makedirs(exports_dir)

# Create uncompiled directory if it doesn't exist
uncompiled_dir = os.path.join(exports_dir, 'uncompiled')
if not os.path.exists(uncompiled_dir):
    os.makedirs(uncompiled_dir)

# Create compiled directory if it doesn't exist
compiled_dir = os.path.join(exports_dir, 'compiled')
if not os.path.exists(compiled_dir):
    os.makedirs(compiled_dir)

# Create the output directory if it doesn't exist
extracted_dir = os.path.join(cache_dir, 'extracts')
if not os.path.exists(extracted_dir):
    os.makedirs(extracted_dir)

# Create assets folder with subfolders if it doesn't exist
src_folder = 'resources/renderer/render_pack'
assets = os.path.join(src_folder, 'assets', 'minecraft', 'textures')
if not os.path.exists(assets):
    os.makedirs(assets)

block_dir = os.path.join(assets, 'block')
if not os.path.exists(block_dir):
    os.makedirs(block_dir)

item_dir = os.path.join(assets, 'item')
if not os.path.exists(item_dir):
    os.makedirs(item_dir)

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
    print(f"\nDone! {elapsed_time:.2f}ms")
    sys.exit()
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

# Prevents ValueError of unability to convert string example: '1.19-pre3'
def try_int_or_float(s):
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return None

# Get a list of all installed Minecraft versions that start with 1.x and are 1.17+
version_numbers = {}
versions = []

try:

    if args.sendrenders:
        
        ver_path = os.path.join(minecraft_dir, 'versions')

        for d in os.listdir(ver_path):
            if os.path.isdir(os.path.join(ver_path, d)) and d.startswith('1.'):
                version_number = try_int_or_float(d.split('.')[1])
                version_numbers[d] = version_number
                if version_number is not None and version_number > 16:
                    versions.append(d)
                    # print(f'Found directory: {d}') # Uncomment when debugging

        # Sort the versions in descending order
        versions.sort(key=lambda v: tuple(map(lambda x: version_numbers[v] if version_numbers[v]
            is not None else float('-inf'), v.split('.'))), reverse=True)

        # Set the path to the latest Minecraft .jar file
        jar_file_path = os.path.join(ver_path, versions[0], f'{versions[0]}.jar')

        print(f"\nSelecting latest version: {versions[0]}")
        print(f"Extracting items from: {jar_file_path}\n")

        # Open the .jar file
        with zipfile.ZipFile(jar_file_path, 'r') as jar_file:
            # Extract all files in the assets folder
            for file in jar_file.namelist():
                if file.startswith('assets/'):
                    jar_file.extract(file, extracted_dir)

    elif not any(vars(args).values()):
        parser.print_help()
        print("\nPlease run this script using your terminal!\n\nUsually like this: python3 renderer.py -h\nThis might be different for your system!\n")
        time.sleep(5)
        input("Press any key to exit...")
        sys.exit()

# throw and error if try fails
except FileNotFoundError:
    print(f"This Error may appear if you are using an unofficial minecraft launcher.\nPlease run the file using the --h arg.\n")

except IndexError:
    print(f"No Minecraft versions found in {minecraft_dir}\nWrong Directory?")

# Sending the renders and renaming em into the folder, then deleting

# Custom pack name (as we are not using a .zip)
new_name = '§5§lRender §3§lPack'

# Directories for the resourcepack
dst_folder = os.path.join(minecraft_dir, 'resourcepacks', new_name)

# Set the path to the .mcmeta file
mcmeta_path = os.path.join(src_folder, "pack.mcmeta")

pack_desc = (
    "\u00A78[\u00A75!\u00A78]\u00A77=\u00A78[\u00A75Rendering Pack\u00A78]\u00A77=\u00A78[\u00A75!\u00A78]\u00A7r\n"
    "\u00A78[\u00A73!\u00A78]\u00A77=\u00A78[\u00A73By Vox313 & 32294\u00A78]\u00A77=\u00A78[\u00A73!\u00A78]"
    )

pack_format = 6 # 1.16.2-rc1–1.16.5

json_folder = 'resources/renderer'
blocksjson = os.path.join(json_folder, 'blocks.json')
itemsjson = os.path.join(json_folder, 'items.json')

with open(blocksjson, 'r') as f:
    blocks_116 = json.load(f)

with open(itemsjson, 'r') as f:
    items_116 = json.load(f)

# Extract lists of blocks and items from dictionaries
blocks_116 = blocks_116['blocklist']
items_116 = items_116['itemlist']

png_items = os.path.join(extracted_dir, 'assets', 'minecraft', 'textures', 'item')
png_blocks = os.path.join(extracted_dir, 'assets', 'minecraft', 'textures', 'block')

# Separate processing of blocks and items without removing .png extension
blocks_ver_plus = [f for f in os.listdir(png_blocks) if f.endswith(".png")]
items_ver_plus = [f for f in os.listdir(png_items) if f.endswith(".png")]

# Find common elements for blocks and items
common_blocks = list(set(blocks_ver_plus) & set(blocks_116))
common_items = list(set(items_ver_plus) & set(items_116))

# Define source and destination directories for blocks and items
src_blocks_dir = png_blocks
dst_blocks_dir = os.path.join(src_folder, 'assets', 'minecraft', 'textures', 'block')
src_items_dir = png_items
dst_items_dir = os.path.join(src_folder, 'assets', 'minecraft', 'textures', 'item')

if args.sendrenders:

    # Read the .mcmeta file
    try:
        with open(mcmeta_path, "r") as f:
            data = json.load(f)

        # Check for the release field
        if "release" in data:
            release_version = data["release"]
            print(f"The release version of the resource pack is: {release_version}")

        # Batch checker (updates if knowing we already had a previous batch)
        if "batch" in data:
            batch_version = data["batch"]
            
            batch = batch_version + 1

        # Error handler incase someone decides to edit the batch file
        else:
            print("Batch was not defined, defaulting back to 0")
            batch = 0

    except TypeError:
        print("Previous batch nto an int, defaulting back to 0.")
        batch = 0

    # Error handler if there was no previous pack.mcmeta file found
    except FileNotFoundError:
        print("No previous pack found, defaulting back to 0 and setting things up,\nplease run again after completion!")
        batch = 0

    print(f"Current batch: {batch}")

    # Copy common blocks from source to destination directory
    for block in common_blocks:
        src_file = os.path.join(src_blocks_dir, block)
        dst_file = os.path.join(dst_blocks_dir, block)
        shutil.copy(src_file, dst_file)

    # Copy common items from source to destination directory
    for item in common_items:
        src_file = os.path.join(src_items_dir, item)
        dst_file = os.path.join(dst_items_dir, item)
        shutil.copy(src_file, dst_file)

    # Create the data for the .mcmeta file

    data = {
        "pack": {
            "pack_format": pack_format,
            "description": pack_desc
        },
        "release": version,
        "batch": batch
    }

    # Write the data to the new .mcmeta file
    with open(mcmeta_path, "w") as f:
        json.dump(data, f, indent=4)

    # Copying the pack folder into minecraft directory
    shutil.copytree(src_folder, dst_folder, dirs_exist_ok=True)
    print("Successfully made the resourcepack,\nPlease go ingame and render using the https://github.com/AterAnimAvis/BlockRenderer/releases/ mod.")

    # Put code here to delete em from pack folder

    # compare time var to earlier to find how long it took
    end_time = time.time()
    elapsed_time = (end_time - start_time)*1000
    print(f"\nDone! {elapsed_time:.2f}ms")

    sys.exit()

if args.retrieverenders:

    try:
        with open(mcmeta_path, "r") as f:
            data = json.load(f)

        # Batch checker (updates if knowing we already had a previous batch)
        if "batch" in data:
            batch_version = data["batch"]

            if batch_version == 0:
                print("You cannot retrieve renders when there are none.\nUser -s first.")
                
                # compare time var to earlier to find how long it took
                end_time = time.time()
                elapsed_time = (end_time - start_time)*1000
                print(f"\nDone! {elapsed_time:.2f}ms")

                sys.exit()

            # Put code here to move first batch into cache or some folder
            mod_folder = os.path.join(minecraft_dir, 'renders')
            
            # Find the newest folder in the source directory
            newest_folder = max(
            (os.path.join(mod_folder, d) for d in os.listdir(mod_folder) if os.path.isdir(os.path.join(mod_folder, d))),
            key=os.path.getmtime
            )

            dst_path = os.path.join(uncompiled_dir, f"batch{batch_version}")

            # Copy the newest folder to the destination directory
            shutil.copytree(newest_folder, dst_path)
            print("Successfully copied mod folder to the uncompiled folder.")

    except FileNotFoundError:
        print("No previous render found, make sure to run -s first.\nDeleting the old pack happens automatically.")

        sys.exit()

    except FileExistsError:

        print(f"Overwritting previous 'batch{batch_version}'...")
        shutil.copytree(newest_folder, dst_path, dirs_exist_ok=True)
        print("Overwrite successful.")

    # Deletes the original pack folder from minecraft directory

    try:
        shutil.rmtree(dst_folder)
        print("Previous pack has successfully been removed!")

    except FileNotFoundError:
        print("Previous pack could not be removed as it does not exist!")

    # Put code here to output rendered images
    # IDFK2

    # compare time var to earlier to find how long it took
    end_time = time.time()
    elapsed_time = (end_time - start_time)*1000
    print(f"\nDone! {elapsed_time:.2f}ms")

    sys.exit()

# Sets back the batch int for pack.mcmeta in the render_pack folder
if args.defaultbatch:

    data = {
        "pack": {
            "pack_format": pack_format,
            "description": pack_desc
        },
        "release": version,
        "batch": 0
    }

    # Write the data to the new .mcmeta file
    with open(mcmeta_path, "w") as f:
        json.dump(data, f, indent=4)

    print("Successfully set the default batch to 0.")

    # compare time var to earlier to find how long it took
    end_time = time.time()
    elapsed_time = (end_time - start_time)*1000
    print(f"\nDone! {elapsed_time:.2f}ms")

    sys.exit()

# compare time var to earlier to find how long it took
end_time = time.time()
elapsed_time = (end_time - start_time)*1000
print(f"\nDone! {elapsed_time:.2f}ms")