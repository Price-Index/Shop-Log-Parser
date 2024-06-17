
# <p align="center"> Shop Log Parser </p>

---

This is the documentation of the [Shop Log parser](/docs/SHOPLOGPARSER.md).

> [!CAUTION]
> This tool may contain bugs, if you do find some, please notify [@thevoxy](https://discordapp.com/users/967391331553013811) on discord.

- [Main](/README.md) _<-- Click here to get back!_

### Content
- [ Shop Log Parser ](#-shop-log-parser-)
    - [Content](#content)
  - [How to use](#how-to-use)
  - [How to run](#how-to-run)
  - [Updating](#updating)
  - [How it works](#how-it-works)

---

## How to use 
- Make sure you've joined [MythicMC](https://mythicmc.org)
- Go to any shop and right click the **chest** of a chestshop\
  *(Only the chests you click will be logged!)*
- [Run](#how-to-run) the [main.py](https://github.com/Price-Index/Shop-Log-Parser/blob/master/main.py) file
- Open the new ``./exports/latest-shopdata.xlsx`` file which contains the data. 

## How to run
Open the projects root folder in your terminal and execute the following;

```py
python3 main.py -h
```

This will show you additional info of how to use the script.
> [!NOTE]
> *Depending on your OS it might be ``py`` ``python``, ``python3`` or other.*

> [!TIP]
> Running ``python3 main.py`` without the ``-h`` arg runs the script in normal mode, so it parses logs. 

> [!IMPORTANT]
> The [dictionary](https://github.com/Price-Index/Dictionary) lists may be incomplete causing unknown items (enchanted items for example) to appear.

> [!IMPORTANT]
> The [dictionary](https://github.com/Price-Index/Dictionary) were only made for Non-anvilled items as those are the only items actually worth something.

## Updating
There's built in ways to update both the Dictionary and the script itself.
```py
# Updating everything if theres updates for it
python3 main.py --update all

# Updating only the script
python3 main.py --update script

# Updating only the Dictionary
python3 main.py --update dicts
```
You should usually get notified if your local copy can get updated when running the script using the ``-h`` arg.

> [!TIP]
> If you do not get notified, it could be that you do not have a working internet connection.

## How it works
Everytime you boot Minecraft, the game makes a ``latest.log`` file under ``C:\Users\%USERPROFILE%\AppData\Roaming\.minecraft\logs``.\
This ``latest.log`` file stores all game data booting information, even chat data.\
The [main.py](https://github.com/Price-Index/Shop-Log-Parser/blob/master/main.py) file will
read trough all of the ``latest.log`` file and search for lines containing:\
``[CHAT] Shop Information:`` as a key-string
to identify where relevant ShopInformation is shown.\
It then takes the Data it finds under that key-string, recalculates prices per item and stores it in an
excel file,\
which is made under ``./exports/``.
