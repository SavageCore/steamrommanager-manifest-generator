# steamrommanager-manifest-generator
Python script to generate a [Steam Rom Manager](https://steamgriddb.github.io/steam-rom-manager/) manifest file from Windows games installed with [itch.io](https://itch.io) and optionally a second directory of Windows games from anywhere!

# How to

Firstly you'll want to create a folder to store all your Windows games. This is optional if you are only parsing games installed from the [itch.io](https://itch.io) client. When the script asks for the Windows directory just click cancel.
```
mkdir -p /home/deck/Games/Windows
```
Now download and extract all your games to this folder making sure to give each games folder a nice name [Steam Rom Manager](https://steamgriddb.github.io/steam-rom-manager/) can parse.

Secondly, we need to install [pip](https://pypi.org/project/pip/)

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

You will be asked for the [itch.io](https://itch.io) apps directory which should auto-populate so just click enter, then either choose Windows directory or click close.

# Upgrading
```
cd /home/deck/steamrommanager-manifest-generator
git pull
/home/deck/.local/bin/pip3 install -r requirements.txt
```

# On Steam Deck

For this to work on Steam Deck we must trick the [itch.io](https://itch.io) client into thinking we have Wine and thus offering the choice to install Windows games. Run the following commands:

```
mkdir -p ~/.local/bin
```
```
cat <<EOF > ~/.local/bin/wine
#!/bin/sh
exec flatpak run org.winehq.Wine $*
EOF
```
```
chmod +x ~/.local/bin/wine
```
```
sed -i.bak ~/.local/share/applications/io.itch.itch.desktop -e 's!^Exec=\(/home/deck/.itch/itch.*\)!Exec=sh -c "PATH=/home/deck/.local/bin:$PATH \1"!'
```

Once that's done create a new parser within [SRM](https://steamgriddb.github.io/steam-rom-manager/) of type `Manual` and set the `Manifests Directory` to `/home/deck/steamrommanager-manifest-generator/manifests`