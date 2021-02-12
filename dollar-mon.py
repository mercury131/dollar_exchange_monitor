import asyncio
import aiohttp
import aiomoex
import pandas as pd
from datetime import datetime, timedelta
import requests 
from bs4 import BeautifulSoup
import time
import os
from os import environ

trigger=1
weektrigger=1
mounthtrigger=2
timeout=900
currency_previos=0



bot_chatID = ''
bot_token = ''

if environ.get('trigger') is not None:
    trigger = int(os.environ['trigger'])

if environ.get('weektrigger') is not None:
    weektrigger = int(os.environ['weektrigger'])

if environ.get('mounthtrigger') is not None:
    mounthtrigger = int(os.environ['mounthtrigger'])

if environ.get('timeout') is not None:
    timeout = int(os.environ['timeout'])

if environ.get('bot_chatID') is not None:
    bot_chatID = str(os.environ['bot_chatID'])

if environ.get('bot_token') is not None:
    bot_token = str(os.environ['bot_token'])

def get_currency_price_cbrf(today):

    from pycbrf.toolbox import ExchangeRates

    rates = ExchangeRates(today)
    rates.date_requested  
    rates.date_received  
    rates.dates_match  

    return rates['USD'].value 



def telegram_bot_sendtext(bot_message,bot_token,bot_chatID):
    
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message

    response = requests.get(send_text)

    return response.json()



def getdollar_history(start,finish):
    async def main():
        request_url = "https://iss.moex.com/iss/history/engines/currency/markets/selt/boards/cets/securities/USD000UTSTOM/securities.json?from=" + start + '&till=' + finish
        arguments = {"history.columns": ("SHORTNAME," "SECID," "CLOSE," "OPEN," "TRADEDATE",)}

        async with aiohttp.ClientSession() as session:
            iss = aiomoex.ISSClient(session, request_url, arguments)
            data = await iss.get()
            df = pd.DataFrame(data["history"])
            df.set_index("SECID", inplace=True)
            return df


    return asyncio.run(main())



DOLLAR_RUB = 'https://www.google.com/search?sxsrf=ALeKk01NWm6viYijAo3HXYOEQUyDEDtFEw%3A1584716087546&source=hp&ei=N9l0XtDXHs716QTcuaXoAg&q=%D0%B4%D0%BE%D0%BB%D0%BB%D0%B0%D1%80+%D0%BA+%D1%80%D1%83%D0%B1%D0%BB%D1%8E&oq=%D0%B4%D0%BE%D0%BB%D0%BB%D0%B0%D1%80+&gs_l=psy-ab.3.0.35i39i70i258j0i131l4j0j0i131l4.3044.4178..5294...1.0..0.83.544.7......0....1..gws-wiz.......35i39.5QL6Ev1Kfk4'

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'}



def get_currency_price(DOLLAR_RUB,headers):

    full_page = requests.get(DOLLAR_RUB, headers=headers)
    soup = BeautifulSoup(full_page.content, 'html.parser')
    convert = soup.findAll("span", {"class": "DFlfde", "class": "SwHCTb", "data-precision": 2})
    return convert[0].text

telegram_bot_sendtext("Dollar/RUB exchange bot started!",bot_token,bot_chatID)
while True:

    tod = datetime.today().strftime("%Y-%m-%d")
    yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    sevendays = (datetime.today() - timedelta(days=7)).strftime("%Y-%m-%d")
    mounth = (datetime.today() - timedelta(days=30)).strftime("%Y-%m-%d")

    dollarhistory=getdollar_history(sevendays,tod)
    dollarhistory_mounth=getdollar_history(mounth,tod)
    maxonweek=dollarhistory['CLOSE'].max()
    maxonmounth=dollarhistory_mounth['CLOSE'].max()
    try:
        currency = float(get_currency_price(DOLLAR_RUB,headers).replace(",", "."))
    except Exception:
        currency=float(get_currency_price_cbrf(datetime.today().strftime("%Y-%m-%d")))
    dollar_yesterday=dollarhistory.iloc[-2]['CLOSE']

    print("###############################################")
    print("Week history",dollarhistory)
    print("Current Dollar/RUB exchange rate",currency)
    print("Yesterday Dollar/RUB exchange rate",dollar_yesterday)
    print("Week MAX Dollar/RUB exchange rate",maxonweek)
    print("Mounth MAX Dollar/RUB exchange rate",maxonmounth)
    print("###############################################")


    diff=round(dollar_yesterday - currency)
    weekdiff=round(maxonweek - currency)
    mounthdiff=round(maxonmounth - currency)


    if currency_previos == currency:
        print("Dollar/RUB exchange rate has not changed")
        #telegram_bot_sendtext(("Dollar/RUB exchange rate has not changed"+ str(diff)),bot_token,bot_chatID)
    else:
        if diff >= trigger:
            print("Dollar/RUB exchange rate has decreased by ",diff,"(Yesterday MAX trigger)"," from " , str(dollar_yesterday) , ' to ' , str(currency))
            telegram_bot_sendtext(("Dollar/RUB exchange rate has decreased by " + str(diff) + " from " + str(dollar_yesterday) + ' to ' + str(currency) + "(Yesterday MAX trigger)" ),bot_token,bot_chatID)
        elif weekdiff >= weektrigger:
            print("Dollar/RUB exchange rate has decreased by ",weekdiff,"(Week MAX trigger)"," from " , str(maxonweek) , ' to ' , str(currency))
            telegram_bot_sendtext(("Dollar/RUB exchange rate has decreased by " + str(weekdiff)+ " from " + str(maxonweek) + ' to ' + str(currency) + "(Week MAX trigger)"),bot_token,bot_chatID)
        elif mounthdiff >= mounthtrigger:
            print("Dollar/RUB exchange rate has decreased by ",mounthdiff,"(Mounth MAX trigger)",  " from " , str(maxonmounth) , ' to ' , str(currency))
            telegram_bot_sendtext(("Dollar/RUB exchange rate has decreased by "+ str(mounthdiff) + " from " + str(maxonmounth) + ' to ' + str(currency) + "(Mounth MAX trigger)") ,bot_token,bot_chatID)


        diff=round(currency - dollar_yesterday)
        weekdiff=round(currency - maxonweek)
        mounthdiff=round(currency - maxonmounth)

        if diff >= trigger:
            print("Dollar/RUB exchange rate has increased by",diff,"(Yesterday MAX trigger)")
            telegram_bot_sendtext(("Dollar/RUB exchange rate has increased by " + str(diff)),bot_token,bot_chatID)
        elif weekdiff >= weektrigger:
            print("Dollar/RUB exchange rate has increased by",weekdiff,"(Week MAX trigger)")
            telegram_bot_sendtext(("Dollar/RUB exchange rate has increased by " + str(weekdiff)),bot_token,bot_chatID)
        elif mounthdiff >= mounthtrigger:
            print("Dollar/RUB exchange rate has increased by",mounthdiff,"(Mounth MAX trigger)")
            telegram_bot_sendtext(("Dollar/RUB exchange rate has increased by "+ str(mounthdiff)),bot_token,bot_chatID)



    currency_previos=currency
    print("Waiting",timeout,"minutes..")
    time.sleep(timeout)