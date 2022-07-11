import os
import fnmatch
import subprocess
import sys
import time
import pickledb
import json
from tkinter.filedialog import askdirectory
from alive_progress import alive_bar, alive_it, config_handler
# Sample manifest file:
# {
#     "title": "Long Gone Days",
#     "target": "/home/deck/Games/Itch/Long Gone Days/Long Gone Days.exe",
#     "startIn": "/home/deck/Games/Itch/Long Gone Days",
#     "launch_options": ""
# },
# Load config file
config_db = pickledb.load('config.db', True)
# Load local cache of game targets
targets_db = pickledb.load('targets.db', True)
config_handler.set_global(spinner='crab')
skip_games_dir = False

if not config_db.get('itch_games_dir'):
    itch_games_dir = askdirectory(initialdir='/home/deck/.config/itch/apps', title='Select itch apps folder')
    # Save games_dir to config file
    config_db.set('itch_games_dir', itch_games_dir)

# Ask user to select games directory if not in config file
if not config_db.get('games_dir') and not config_db.get('skip_games_dir'):
    games_dir = askdirectory(initialdir='~', title='Select folder containing all Windows games')
    # If user cancelled prompt then skip games_dir
    if games_dir == '':
        skip_games_dir = True
    # Save games_dir to config file
    config_db.set('games_dir', games_dir)
    config_db.set('skip_games_dir', True)

itch_games_dir = config_db.get('itch_games_dir')
games_dir = config_db.get('games_dir')
manifest_path = os.path.join('manifests', 'manifest.json')
manifests = []

print('Parsing each Itch game in ' + itch_games_dir)

# Get all directories in itch_games_dir
itch_directories = [d for d in os.listdir(itch_games_dir)
if os.path.isdir(os.path.join(itch_games_dir, d))]
# For each itch game directory, extract and parse the json file within .itch/receipt.json.gz
# Use alive-progress to show progress bar as we parse each game
with alive_bar(len(itch_directories)) as bar:
    for itch_dir in itch_directories:
        # Get the receipt.json.gz file
        receipt_file = os.path.join(itch_games_dir, itch_dir, '.itch', 'receipt.json.gz')
        # If the receipt file exists, parse it
        if os.path.isfile(receipt_file):
            # Extract the receipt.json.gz file
            os.system('gunzip -c ' + receipt_file + ' > ' + receipt_file + '.json')
            with open(receipt_file + '.json', 'r') as f:
                receipt = json.load(f)
                title = receipt.get('game').get('title')
                platforms = receipt.get('game').get('platforms')
                # If receipt.json.gz.json does not contain Linux but does contain Windows, add it to the manifest
                if 'linux' not in platforms and 'windows' in platforms:
                    # Find the games executable
                    first_file_entry = receipt.get('files')[0]
                    first_file_entry_path = os.path.join(itch_games_dir, itch_dir, first_file_entry)
                    base_path = os.path.join(itch_games_dir, itch_dir)
                    # If first entry of receipt.files is a directory, then the executable is within that directory
                    if os.path.isdir(first_file_entry_path):
                        targets = fnmatch.filter(os.listdir(first_file_entry_path), '*.exe')
                        fullPath = os.path.abspath(first_file_entry_path)
                    else:
                        targets = fnmatch.filter(os.listdir(base_path), '*.exe')
                        fullPath = os.path.abspath(base_path)
                    # If more than one target, ask the user to select one otherwise use the first one
                    if len(targets) > 1:
                        cached_target = targets_db.get(title)
                        if cached_target:
                            target = cached_target
                        else:
                            print()
                            print('Multiple potential game exes found for ' + title)
                            for i in range(len(targets)):
                                print(str(i) + ': ' + targets[i])
                            target = targets[int(input('Select the game exe: '))]
                            targets_db.set(title, target)
                    else:
                        target = targets[0]
                    target = os.path.join(fullPath, target)

                    # Get the game's startIn
                    startIn = os.path.join(fullPath)
                    # Set the game's launch_options
                    launch_options = ''
                    # Create the manifest entry
                    manifest_entry = '{{"title": "{}", "target": "{}", "startIn": "{}", "launch_options": "{}"}},'.format(
                        title, target, startIn, launch_options)
                    # Add manifest entry to list
                    manifests.append(manifest_entry)
                    f.close()
            # Delete receipt.json.gz.json
            os.remove(receipt_file + '.json')
        bar()

if not config_db.get('skip_games_dir'):
    print('Parsing each Windows game in ' + games_dir)

    # Get all directories in games_dir
    game_directories = [d for d in os.listdir(games_dir) if os.path.isdir(os.path.join(games_dir, d))]

    # Create a manifest entry for each Windows game
    with alive_bar(len(game_directories)) as bar:
        for directory in game_directories:
            # Get full path of directory
            fullPath = os.path.abspath(os.path.join(games_dir, directory))
            # Get the game's title
            title = directory
            # Get the game's target which is the full path to the game's executable
            targets = fnmatch.filter(os.listdir(os.path.join(games_dir, directory)), '*.exe')
            # If more than one target, ask the user to select one otherwise use the first one
            if len(targets) > 1:
                cached_target = targets_db.get(title)
                if cached_target:
                    target = cached_target
                else:
                    print()
                    print('Multiple potential game exes found for ' + title)
                    for i in range(len(targets)):
                        print(str(i) + ': ' + targets[i])
                    target = targets[int(input('Select the game exe: '))]
                    targets_db.set(title, target)
            else:
                target = targets[0]
            target = os.path.join(fullPath, target)

            # Get the game's startIn
            startIn = os.path.join(fullPath)
            # Set the game's launch_options
            launch_options = ''
            # Create the manifest entry
            manifest_entry = '{{"title": "{}", "target": "{}", "startIn": "{}", "launch_options": "{}"}},'.format(
                title, target, startIn, launch_options)
            # Add manifest entry to list
            manifests.append(manifest_entry)
            bar()

# For each manifest entry, write it to the manifest file
with open(manifest_path, 'w') as manifestFile:
    manifestFile.write("[\n")
    for manifest_entry in manifests:
        # If the last entry
        if manifest_entry == manifests[-1]:
            # Remove the comma from the end of the entry
            manifest_entry = manifest_entry[:-1]
        manifestFile.write(manifest_entry + "\n")
    manifestFile.write("]\n")

    # Close the manifest file
    manifestFile.close()

# Print the number of games processed
print()
print('Processed ' + str(len(manifests)) + ' games and saved manifest to ' + os.path.abspath(manifest_path))
# Print each game's title from json manifest_entry
for manifest_entry in manifests:
    # trim manifest_entry of comma if exists
    if manifest_entry[-1] == ',':
        manifest_entry = manifest_entry[:-1]
    # Load json from manifest_entry
    manifest_dict = json.loads(manifest_entry)
    print('* ' + manifest_dict['title'])
