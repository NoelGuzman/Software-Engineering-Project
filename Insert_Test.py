from iexfinance.stocks import Stock
from iexfinance.refdata import get_iex_symbols
from iexfinance.utils import exceptions # Not used here
from os import environ
from datetime import datetime, time
from more_itertools import grouper #this one is use to chunk the symbol list into blocks of 100, not used here
import mysql.connector as sql
######### OS Environment Settings ################
environ['IEX_TOKEN'] = 'Tsk_234462620ac5432ab25388f076e97782' # Setting Environment Token stops any need of inputing token in every function call
                                                              # This is Test Token only, must use regular token for actual data
environ['IEX_API_VERSION'] = 'iexcloud-sandbox' #required verisons accessible: [v1, iexcloud-sandbox, beta]
######### OS Environment Settings ################

######### Server Info #########
try:
    dbconnection = sql.connect(host = "dragon.websiteinc.com", user = "afadmin_ScrumD", passwd = "SpiceGirls!", database = "afadmin_SpicyStocks")
    cursor = dbconnection.cursor()
except sql.Error as err:
        print(err)
######### Server Info #########

Symbols = get_iex_symbols() #Only Pulls Symbols, not really used for anythin in this test file but to test
A = Stock("A") #Stock() can have multiple stock tickers, up to 100 in the form of a list of tickers Stock(["TSLA", "AAPL"]) for example
Price = A.get_price() #In a batch, gives symbol and price together
Name = A.get_company_name() #similar as get_price()
print(Price)
StockA = (Name, "A", Price)
stmt = "INSERT INTO stock_data (name, ticker, curr_price) VALUES (%s, %s, %s)"
cursor.execute(stmt, StockA)
dbconnection.commit()
dbconnection.close()