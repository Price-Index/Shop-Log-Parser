# MythicMC shoplogger

A logger for MythicMC shops to an excel file.

## Requirements

- [Python 3.10](https://www.python.org/downloads/release/python-3100/)

```
  pip install openpyxl
```

## Compatibility
- [Microsoft Windows](https://www.microsoft.com/en-us/software-download/), [MacOS](https://www.apple.com/macos) & [Linux](https://www.linux.org/pages/download/)
### MacOS and Linux support have not been tested!
They should work _*in theory*_, but please provide Feedback.

## How to use
- Make sure you've joined [MythicMC](https://mythicmc.org)
- Go to any shop and right click the **chest** of a chestshop
- Run the [main.py](https://github.com/Vox314/MythicMC-shoplogger/blob/master/main.py) file
- Open the new ``./exports/latest-shopdata.xlsx`` file which contains the data. 

## Additional information
The dictionary list may be incomplete causing unknown items (enchanted items for example) to appear.
The dictionary was only made for Non-anvilled items as those are the only items actually worth something.

## How does it work (in a nutshell)?
So for those of you who would like to know how exactly this thing works; let me give you the grand tour-\
Everytime you boot Minecraft, the game makes a ``latest.log file`` under ``C:\Users\%USERPROFILE%\AppData\Roaming\.minecraft\logs``.\
This ``latest.log file`` file stores all game data booting information, even chat data.\
So once you execute the [main.py](https://github.com/Vox314/MythicMC-shoplogger/blob/master/main.py) file, it will basically
read trough all of the latest.log file lines and search for lines containing: ``[CHAT] Shop Information:`` as a key-string
to identify where relevant ShopInformation is shown. It then takes the Data it finds under that key-string and stores it in an
excel file, which is made under ``./exports/``.

So yeah nothing too complicated to be fair :P

## Authors

- [@Vox314](https://www.github.com/Vox314)
- [@32294](https://www.github.com/32294)

## License
This project is licensed under the terms of the [MIT](https://choosealicense.com/licenses/mit/) license.

```
MIT License

Copyright (c) [Vox313 https://github.com/Vox314 and 32294 https://github.com/32294]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```