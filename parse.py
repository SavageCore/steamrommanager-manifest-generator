import os
import fnmatch
import pickledb
import json
from tkinter.filedialog import askdirectory
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

# Ask user to select games directory if not in config file
if not config_db.get('games_dir'):
    games_dir = askdirectory(title='Select folder containing all itch games')
    # Save games_dir to config file
    config_db.set('games_dir', games_dir)

# Get all directories in games_dir
directories = [d for d in os.listdir(config_db.get('games_dir')) if os.path.isdir(os.path.join(config_db.get('games_dir'), d))]
manifests = []

# Create a manifest entry for each game
for directory in directories:
    # Get full path of directory
    fullPath = os.path.abspath(directory)
    # Get the game's title
    title = directory
    # Get the game's target which is the full path to the game's executable
    targets = fnmatch.filter(os.listdir(directory), '*.exe')
    # If more than one target, ask the user to select one otherwise use the first one
    if len(targets) > 1:
        cached_target = targets_db.get(title)
        if cached_target:
            target = cached_target
        else:
            print('Multiple potential game exes found:')
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

# For each manifest entry, write it to the manifest file
with open('manifest.json', 'w') as manifestFile:
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

# Clear console
os.system('cls' if os.name == 'nt' else "printf '\033c'")
# Print the number of games processed
print('Processed ' + str(len(manifests)) + ' games:\n')
# Print each game's title from json manifest_entry
for manifest_entry in manifests:
    # trim manifest_entry of comma if exists
    if manifest_entry[-1] == ',':
        manifest_entry = manifest_entry[:-1]
    # Load json from manifest_entry
    manifest_dict = json.loads(manifest_entry)
    print(manifest_dict['title'])
