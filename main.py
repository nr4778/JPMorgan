

__author__ = 'Neil Watson'

import pandas as pd
import datetime
import random
import threading

#####################################################################################
#
#  Written in Python 3.4.3
#
#  The spec was (intentionally?) vague, and I could have done all sorts of fancy
#  things, but I kept it very basic, and as close to the spec as I could
#
#
#
####################################################################################



########################################################################################
#
# set up the base data
#
########################################################################################

sampleData = {}
sampleData["TEA"] = {"Type":"Common","Last Div":0,"Fixed Div":0,"Par":100,"Price":20}
sampleData["POP"] = {"Type":"Common","Last Div":8,"Fixed Div":0,"Par":100,"Price":30}
sampleData["ALE"] = {"Type":"Common","Last Div":23,"Fixed Div":0,"Par":60,"Price":40}
sampleData["GIN"] = {"Type":"Preferred","Last Div":8,"Fixed Div":2,"Par":100,"Price":50}
sampleData["JOE"] = {"Type":"Common","Last Div":13,"Fixed Div":0,"Par":250,"Price":60}
trades = pd.DataFrame(columns = ["Time","Stock","Quantity","B/S","Price"])
trades.set_index("Time",inplace=True)
trades.index = pd.to_datetime(trades.index)
running = True
t = None


########################################################################################
#
# calculation functions
#
########################################################################################

def calculate_dividend_yield(stock):
    if not stock in sampleData:
        return None
    if sampleData[stock]["Price"] == 0:
            return 0
    if sampleData[stock]["Type"] == "Common":
        return sampleData[stock]["Last Div"]/sampleData[stock]["Price"]
    else:
        return sampleData[stock]["Fixed Div"]*sampleData[stock]["Par"]/sampleData[stock]["Price"]

def calculate_PE_ratio(stock):
    if not stock in sampleData:
        return None
    if sampleData[stock]["Last Div"] == 0:
            return 0
    return sampleData[stock]["Price"]/sampleData[stock]["Last Div"]

def calculate_stock_price(stock):
    if len(trades) != 0:
        print(trades)
    print()
    if not stock in trades["Stock"].values:
        return None
    now = datetime.datetime.now()
    t = trades[now-datetime.timedelta(minutes=15):now].groupby("Stock").get_group(stock)
    if len(t) == 0:
        return 0
    return (t["Price"] * t["Quantity"]).sum()/(t["Quantity"].sum())


def calculate_gbce():
    if len(sampleData) == 0:
        return 0
    product = 1
    for k,v in sampleData.items():
        product*=v["Price"]
    return product**(1/len(sampleData))


def record_trade(stock,quantity,bs):
    if not stock in sampleData:
        return
    price = sampleData[stock]["Price"]
    now = datetime.datetime.now()
    trades.loc[now] = [stock,quantity,bs,price]
    if bs == "b":
        print("Bought",quantity,"of",stock,"at",price)
    else:
        print("Sold",quantity,"of",stock,"at",price)

########################################################################################
#
# various other functions for display or interaction purposes
#
########################################################################################

def change_prices():
    global t
    for name,data in sampleData.items():
        val = round(random.randint(-1,1)*random.random()*data["Price"]/100,2)
        sampleData[name]["Price"] += val
    t = threading.Timer(10,change_prices)
    t.start()

def parse_input(s):
    global running
    if s == "":
        return
    s = s.split()
    print("*" * 70)
    if s[0].lower() == "div" and len(s) > 1:
        result = calculate_dividend_yield(s[1])
        print("Dividend for",s[1],result)
    if s[0].lower() == "p/e" and len(s) > 1:
        result = calculate_PE_ratio(s[1])
        print("P/E Ratio for",s[1],result)
    if s[0].lower() == "buy" and len(s) > 1:
        try:
            quantity = int(s[1])
            record_trade(s[2],quantity,"b")
        except ValueError as e:
            print("Quantity entered wasnt an integer")
    if s[0].lower() == "sell" and len(s) > 1:
        try:
            quantity = int(s[1])
            record_trade(s[2],quantity,"s")
        except ValueError as e:
            print("Quantity entered wasnt an integer")
    if s[0].lower() == "price" and len(s) > 1:
        result = calculate_stock_price(s[1])
        print("Calculated price of",s[1],result)
    if s[0].lower() == "gbce":
        result = calculate_gbce()
        print("Calculated GBCE",result)
    if s[0].lower() == "q":
        running = False
        t.cancel()
    print("*" * 70)

def print_menu():
    print("-" * 70)
    print("Stock prices")
    print("-" * 10)
    print(" ".join([k + ":" + str(v["Price"]) for k,v in sampleData.items()]))
    print("-" * 70)
    print("Menu")
    print("-" * 10)
    print("div stock - displays the dividend yield for stock")
    print("p/e stock - displays the p/e ratio for stock")
    print("buy num stock - records a trade of a buy of num stock")
    print("sell num stock - records a trade of a sell of num stock")
    print("price stock - displays the calculated stock price for stock")
    print("gbce - displays the GBCE Index over all stocks")
    print("q - quits the program")

change_prices()


if __name__ == "__main__":
    while running:
        print_menu()
        userInput = input()
        parse_input(userInput)
