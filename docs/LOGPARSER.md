
# Log Parser

This is the documentation of the [Log parser](/docs/LOGPARSER.md)

> [!WARNING]
> This tool may contain bugs, if you do find some, please notify [@thevoxy](https://discordapp.com/users/967391331553013811) on discord.

- [Main](/README.md) _<-- Click here to get back!_

## How to use 
- Make sure you've joined [MythicMC](https://mythicmc.org)
- Go to any shop and right click the **chest** of a chestshop\
  *(Only the chests you click will be logged!)*
- [Run](#how-to-run) the [main.py](https://github.com/Vox314/MythicMC-Log-Parser/blob/master/main.py) file
- Open the new ``./exports/latest-shopdata.xlsx`` file which contains the data. 

## How to run
Open the projects root folder in your terminal and execute the following;

```py
python3 main.py -h
```

This will show you additional info of how to use the script.\
> [!NOTE]
> *Depending on your OS it might be ``py`` ``python``, ``python3`` or other.*

> [!IMPORTANT]
> The [dictionary](/resources/log_parser) list may be incomplete causing unknown items (enchanted items for example) to appear.

> [!IMPORTANT]
> The [dictionary](/resources/log_parser) was only made for Non-anvilled items as those are the only items actually worth something.

## How it works
Everytime you boot Minecraft, the game makes a ``latest.log`` file under ``C:\Users\%USERPROFILE%\AppData\Roaming\.minecraft\logs``.\
This ``latest.log`` file stores all game data booting information, even chat data.\
The [main.py](https://github.com/Vox314/MythicMC-Log-Parser/blob/master/main.py) file will
read trough all of the ``latest.log`` file and search for lines containing:\
``[CHAT] Shop Information:`` as a key-string
to identify where relevant ShopInformation is shown.\
It then takes the Data it finds under that key-string, recalculates prices per item and stores it in an
excel file,\
which is made under ``./exports/``.
