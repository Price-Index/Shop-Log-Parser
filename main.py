import os
from openpyxl import Workbook

minecraft_dir = os.path.join(os.environ['APPDATA'], '.minecraft', 'logs')
latest_log = os.path.join(minecraft_dir, 'latest.log')

# Create a new workbook and select the active worksheet
wb = Workbook()
ws = wb.active

# Set the column headers
ws.append(['Item', 'Owner', 'Buy:', 'Sell:'])

shop_info = []

# Read the chat log from the file
with open(latest_log, "r") as file:
    lines = file.readlines()
    buy = sell = None
    
    for i, line in enumerate(lines):
        if '[CHAT] Shop Information:' in line:
            owner = line.split('Owner: ')[1].split('\\n')[0]
            # stock = line.split('Stock: ')[1].split('\\n')[0]
            item = line.split('Item: ')[1].split('\\n')[0]

            if (i + 1 < len(lines) and '[CHAT] Buy' in lines[i + 1] and 'for' in lines[i + 1]) or (i + 2 < len(lines) and '[CHAT] Buy' in lines[i + 2] and 'for' in lines[i + 2]):
                if '[CHAT] Buy' in lines[i + 1]:
                    buy_line = lines[i + 1]
                else:
                    buy_line = lines[i + 2]
                amount_buy = float(buy_line.split('Buy ')[1].split(' for')[0])
                price_buy = float(buy_line.split('for ')[1])
                buy = price_buy / amount_buy

            if (i + 1 < len(lines) and '[CHAT] Sell' in lines[i + 1] and 'for' in lines[i + 1]) or (i + 2 < len(lines) and '[CHAT] Sell' in lines[i + 2] and 'for' in lines[i + 2]):
                if '[CHAT] Sell' in lines[i + 1]:
                    sell_line = lines[i + 1]
                else:
                    sell_line = lines[i + 2]
                amount_sell = float(sell_line.split('Sell ')[1].split(' for')[0])
                price_sell = float(sell_line.split('for ')[1])
                sell = price_sell / amount_sell

            if not any(info['item'] == item and info['owner'] == owner and info['buy'] == buy and info['sell'] == sell for info in shop_info):
                ws.append([item, owner, buy, sell])
                shop_info.append({'item': item, 'owner': owner, 'buy': buy, 'sell': sell})

# Save the workbook to a file
wb.save('shopdata.xlsx')