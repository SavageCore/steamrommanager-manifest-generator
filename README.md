# steamrommanager-manifest-generator
Python script to generate [Steam Rom Manager](https://steamgriddb.github.io/steam-rom-manager/) manifest file from a directory of Windows games. Useful on Steam Deck to parse manually downloaded [itch.io](https://itch.io) games.

### How to

Firstly you'll want to create a folder to store all your Windows games
```
mkdir -p /home/deck/Games/Itch
```
Now download and extract all your games to this folder making sure to give each games folder a nice name [Steam Rom Manager](https://steamgriddb.github.io/steam-rom-manager/) can parse. E.g. if I was installing [NIGHT OF THE CONSUMERS](https://germfood.itch.io/nightoftheconsumers) I'd rename the extracted folder from `NIGHTOFTHECONSUMERS_1.04` to `NIGHT OF THE CONSUMERS`

Secondly we need to install pip

```
python -m ensurepip --upgrade
```

And finally clone, install and run the script.

```
cd /home/deck
git clone https://github.com/SavageCore/steamrommanager-manifest-generator.git
cd steamrommanager-manifest-generator
/home/deck/.local/bin/pip3 install -r requirements.txt
python parse.py

```

### To run again later

```
cd /home/deck/steamrommanager-manifest-generator
python parse.py
```
