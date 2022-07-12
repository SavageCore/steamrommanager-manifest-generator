import os
import fnmatch
import sys
from time import sleep
import pickledb
import json
from tkinter.filedialog import askdirectory
from alive_progress import alive_bar, config_handler
import pyfiglet

first_run = False
# If the config file doesn't exist set first run to True
if not os.path.isfile('config.db'):
    first_run = True

config_db = pickledb.load('config.db', True)
targets_db = pickledb.load('targets.db', True)

config_handler.set_global(spinner='crab')
skip_games_dir = False
itch_path = os.path.join(os.path.expanduser('~'), '.config/itch/apps')
desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(os.path.abspath(__file__))

def menu():
    print('\n')
    print(pyfiglet.figlet_format('SRM-MG',font='doom'))
    print('1. Run')
    print('2. Update')
    print('3. Create desktop shortcut')
    print('4. Quit')
    print('\n')
    choice = input('Enter your choice: ')
    if choice == '1':
        os.system('clear')
        run()
    elif choice == '2':
        os.system('clear')
        update()
    elif choice == '3':
        os.system('clear')
        create_desktop_shortcut()
        sleep(3)
        os.system('clear')
        menu()
    elif choice == '4':
        sys.exit()
    else:
        os.system('clear')
        menu()

def run():
    if not config_db.get('itch_games_dir'):
        itch_games_dir = askdirectory(initialdir=itch_path, title='Select itch apps folder')
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
                                print('\n')
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
                        print('\n')
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
    print('\n')
    print('Processed ' + str(len(manifests)) + ' games and saved manifest to ' + os.path.abspath(manifest_path))
    # Print each game's title from json manifest_entry
    for manifest_entry in manifests:
        # trim manifest_entry of comma if exists
        if manifest_entry[-1] == ',':
            manifest_entry = manifest_entry[:-1]
        # Load json from manifest_entry
        manifest_dict = json.loads(manifest_entry)
        print('* ' + manifest_dict['title'])

def create_desktop_shortcut():
        # Create the .desktop file
        desktop_file_path = os.path.join(desktop_path, 'steamrommanager-manifest-generator.desktop')
        desktop_file = open(desktop_file_path, 'w')
        desktop_file.write('[Desktop Entry]\n')
        desktop_file.write('Name=SRM-MG\n')
        desktop_file.write('Comment=Parse games with steamrommanager-manifest-generator\n')
        desktop_file.write('Exec=python ' + script_path + '\n')
        desktop_file.write('Path=' + script_dir + '\n')
        desktop_file.write('Icon=steamdeck-gaming-return\n')
        desktop_file.write('Terminal=true\n')
        desktop_file.write('Type=Application\n')
        desktop_file.write('Categories=Game;Utility\n')
        desktop_file.close()
        # Print the .desktop file path
        print('\n')
        print('Created .desktop file at ' + os.path.abspath(desktop_file_path))

# Define update function to update the script by git pull and relaunch
def update():
    # Pull the latest version of the script from git
    os.system('git pull')
    os.system('clear')
    # Relaunch the script
    os.system('python ' + script_path)

# If first run of this script, ask the user if they want to create a desktop shortcut to launch this script
if first_run:
    print('\n')
    print('This is the first time you have run this script. Would you like to create a desktop shortcut to launch this script? (Y/n)')
    create_desktop_file = input()
    if create_desktop_file != 'n':
        create_desktop_shortcut()

menu()

print('\n')
print('Press any key to exit')
input()
sys.exit()