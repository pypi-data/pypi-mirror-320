from binance.client import Client
from tabulate import tabulate 
import mysql.connector
import datetime
import keyboard
import json
import psycopg2
import re

def main():
    # print("hi")
    global con, cursor
    con=psycopg2.connect(
        user="postgres.nojyfntxgshnhpfpymin",
        password="Legion@150",
        host="aws-0-ap-south-1.pooler.supabase.com",
        port="6543",
        dbname="postgres"
    )
    cursor=con.cursor()
    
    
    while True:


        curbp()

        do =int(input("1. BUY\n2. SELL\n3. SHOW TRANSACTION\n4. ADD BALANCE\n5. LIVE MARKET\n6. PORTFOLIO\n7. EXIT\n"))

        if do==1:
            buy()
        elif do==2:
            sell()
        elif do ==3:
            trans()
        elif do==4:
            add()
        elif do==5:
            curr()
        elif do==6:
            port()
        elif do==7:
            exit()

def get_symbol(user_input):
    with open('intents.json') as file:
        data = json.load(file)
    for intent in data['intents']:
        for pattern in intent['patterns']:
            
            if re.search(pattern.lower(), user_input.lower()):
                return intent['symbol']
    return "Sorry, I didn't understand that."


def curr():
    inp=input("Which Crypto : ")
    
    symbol=get_symbol(inp)
    print(symbol)
    while True:
        
        if keyboard.is_pressed("space"):
            break
        client = Client()
        ticker = client.get_symbol_ticker(symbol=symbol)
        data=[ticker.values()]
        key = ticker.keys()
        print(tabulate(data, key , tablefmt="pretty"))
        
def buy():
    inp=input("Which Crypto : ")
    
    symbol=get_symbol(inp)
    print(symbol)
    curbp()
    bal=curb()
    
    quantity = float(input("How many : "))
    client = Client()
    ticker = client.get_symbol_ticker(symbol=symbol)
    price = float(ticker["price"])
    val = price * quantity
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if val < bal:
        
        print(f"Bought {quantity} units at rate of {price} \nTotal : {val}")
        f=bal-val
        cursor.execute(f"update balance set bal = {f}")
        con.commit()
        curbp()
        cb=curb()
        query = f"insert into orders VALUES ('{dt}','{symbol}', {price} , {quantity} , {val},'BUY',{bal})"
        cursor.execute(query)
        con.commit()
        cursor.execute(f"update portfolio set quantity = {quantity}, value = {val} where name = '{symbol}'")
        con.commit()


    else:
        print("JAA BE GARIB")


def sell():
    inp=input("Which Crypto : ")
    
    symbol=get_symbol(inp)
    print(symbol)
    
    cursor.execute(f"SELECT quantity from portfolio where name = '{symbol}'")
    res = cursor.fetchone()
    hold=res[0]
    bal=curb()
    quan = float(input("How many : "))
    cursor.execute(f"select quantity from portfolio where name ='{symbol}'")
    r=cursor.fetchone()
    s=r[0]
    if quan <= s:

        cursor.execute(f"select value from portfolio where name = '{symbol}'")
        temp=cursor.fetchone()
        client = Client()
        ticker = client.get_symbol_ticker(symbol=symbol)
        price = float(ticker["price"])
        val = price * quan
        mm=hold-quan
        dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        h=int(temp[0])
        gg=mm*price
        print(f"Sold {quan} units at rate of {price} \nTotal : {val}")
        f=bal+val
        cursor.execute(f"update balance set bal = {f}")
        con.commit()
        curbp()
        cb=curb()
        query = f"insert into orders VALUES ('{dt}','{symbol}', {price} , {quan} , {val},'SELL',{cb})"
        cursor.execute(query)
        con.commit()
        v=s-quan
        cursor.execute(f"update portfolio set quantity ={v} , value = {gg}  where name = '{symbol}'")
        con.commit()
        

    else:
        print("JAA BE GARIB")


def trans():
    
    query = "SELECT * FROM orders"
    cursor.execute(query)
    res = cursor.fetchall()
    heads = ["Date Time","Symbol", "Price", "Quantity", "Value","Type","Balance"]
    if res:

    ###################################################################
        GREEN = '\033[32m'  
        RED = '\033[31m'    
        RESET = '\033[0m'   
        for idx, row in enumerate(res):
            if row[5] == 'BUY':  
                res[idx] = tuple(GREEN + str(item) + RESET for item in row)  
            elif row[5] == 'SELL':
                res[idx] = tuple(RED + str(item) + RESET for item in row)   
    #####################################################################
    
        print(tabulate(res, headers=heads, tablefmt="pretty"))
    
        print(f" Trading Bal : {curb()}")

    else:
        print("JAA BE GARIB")

def curbp():
    cursor.execute("select * from balance")
    res = cursor.fetchone()
    print(f" Trading Bal : {res[0]}")

def curb():
    cursor.execute("select * from balance")
    res = cursor.fetchone()
    bal=res[0]
    return bal

def add():
    res=curb()
    curbp()
    amount = int(input("Amount : ")) # -ve for withdrawl
    f = res+amount
    cursor.execute(f"update balance set bal = {f}")
    con.commit()
    curbp()

def port():
    cursor.execute("select * from portfolio where quantity > 0")
    r=cursor.fetchall()
    if r:
            
        h=["Name","Quantity","Value"]
        print(tabulate(r,headers=h,tablefmt="grid"))
    else:
        print("JAA BE GARIB")






# if __name__=="__main__":
main()