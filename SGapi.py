from iexfinance.stocks import Stock
from iexfinance.refdata import get_iex_symbols
from iexfinance.utils import exceptions
from os import environ
from datetime import datetime, time
from more_itertools import grouper
import mysql.connector as sql
######### OS Environment Settings ################
environ['IEX_TOKEN'] = '' # setting Environment Token stops any need of inputing token in every function call
environ['IEX_API_VERSION'] = 'iexcloud-sandbox' #required verisons accessable: [v1, iexcloud-sandbox, beta]
######### OS Environment Settings ################

######### Server Info #########
try:

    dbconnection = sql.connect(host = "", user = "", passwd = "!", database = "")#Server Info Removed
    cursor = dbconnection.cursor()
except sql.Error as err:
        print(err)
######### Server Info #########

def is_time_between(begin_time, end_time, check_time=None):
    # If check time is not given, default to current UTC time
    check_time = check_time or datetime.utcnow().time()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else: # crosses midnight
        return check_time >= begin_time or check_time <= end_time


def DataFromFile():
    '''
    Pulls data from a txt file of all the symbols used in the server

    Input: None
    Output: list of symbols
    '''
    Data = []
    with open('TickerList.txt', 'r') as filehandler:
        for line in filehandler:
            Ticker = line[:-1]
            Data.append(Ticker)
    filehandler.close()
    return Data

def StockList():
    '''
    API call for stock symbols

    Input: None
    Output: list of symbols
    '''
    ListT = get_iex_symbols() #get callable ticker symbols
    StockListSym = [] # Empty list to store ticker symbols
    for index in range(len(ListT)): #iterate through ListT and pull symbols
        itemsdict = ListT[index] #Pulls dictionary
        ticker = itemsdict['symbol']
        if '*' in ticker[-1]:
            ticker = ticker[0:(len(ticker)-1)]
        StockListSym.append(ticker) #Add to StockListSym
    return StockListSym

def ApiBatchCall(Tickers): #Api can only take 100 symbols at a time
    '''
    Main function to grab ticker current price at the time of call and their company name.

    Input: list of symbols
    Output: list of a list of symbols and their respective price and name
    '''
    Stocks100 = list(grouper(100,Tickers)) #group stocks in 100 sized chunks
    MergedB = []
    if None in Stocks100[-1]:
        for i in range(len(Stocks100)-1):
            Batch = Stock(list(Stocks100[i]))
            TempList = list(Stocks100[i])
            while True:
                try:
                    price = (Batch.get_price()) #Returns the price of all Stocks in the Batch(100 stocks in each Batch)
                    Sname = (Batch.get_company_name())
                    ListPrice = [[k,v] for k,v in price.items()]
                    NameList = [[k,v.encode("utf-8")] for k,v in Sname.items()]
                    ListPrice = (filter(lambda t: None not in t, ListPrice))
                    for i in range(len(NameList)):
                        if NameList[i][0] == ListPrice[i][0]:
                            ListPrice[i].insert(0,NameList[i][1])
                    break
                except exceptions.IEXSymbolError as E: #Symbol Not Found
                    print(E)
                    ErrorSymbol = str(E).split(' ')[1]
                    TempList.remove(ErrorSymbol)
                    Batch = Stock(list(TempList))
            MergedB.append(ListPrice)

        #For the Last chunk of 100
        Last100 = list(filter(None,list(Stocks100[-1]))) #Last Chunk will be filled with None until it fills to 100
        Batch = Stock(Last100)
        TempList = list(Last100)
        while True:
            try:
                price = (Batch.get_price()) #Returns the price of all Stocks in the Batch(100 stocks in each Batch)
                Sname = (Batch.get_company_name())
                ListPrice = [[k,v] for k,v in price.items()]
                NameList = [[k,v.encode("utf-8")] for k,v in Sname.items()]
                ListPrice = (filter(lambda t: None not in t, ListPrice))
                for i in range(len(NameList)):
                    if NameList[i][0] == ListPrice[i][0]:
                        ListPrice[i].insert(0,NameList[i][1])
                break
            except exceptions.IEXSymbolError as E: #Symbol Not Found
                print(E)
                ErrorSymbol = str(E).split(' ')[1]
                TempList.remove(ErrorSymbol)
                Batch = Stock(list(TempList))
        MergedB.append(ListPrice)
    else:                                       #No chunk is less than 100 symbols and no None items.
        for i in range(len(Stocks100)):
            Batch = Stock(list(Stocks100[i]))
            TempList = list(Stocks100[i])
            while True:
                try:
                    price = (Batch.get_price()) #Returns the price of all Stocks in the Batch(100 stocks in each Batch)
                    Sname = (Batch.get_company_name())
                    ListPrice = [[k,v] for k,v in price.items()]
                    NameList = [[k,v.encode("utf-8")] for k,v in Sname.items()]
                    ListPrice = (filter(lambda t: None not in t, ListPrice))
                    for i in range(len(NameList)):
                        if NameList[i][0] == ListPrice[i][0]:
                            ListPrice[i].insert(0,NameList[i][1])
                    break
                except exceptions.IEXSymbolError as E: #Symbol Not Found
                    print(E)
                    ErrorSymbol = str(E).split(' ')[1]
                    TempList.remove(ErrorSymbol)
                    Batch = Stock(list(TempList))
            MergedB.append(ListPrice)
    return MergedB

def SendDataToServer(Data):
    for i in range(8,0, -1):#Loop to send update past_hour prices starting with the oldest, working up to curr_price
        if i == 2:
            updateHours = "UPDATE stock_data SET past_hour_2 = past_hour"
            cursor.execute(updateHours)
            dbconnection.commit()
            print('Update Sent')
        elif i == 1:
            updateHours = "UPDATE stock_data SET past_hour = curr_price"
            cursor.execute(updateHours)
            dbconnection.commit()
            print('Update Sent')
        else:
            updateHours = "UPDATE stock_data SET past_hour_{} = past_hour_{}".format(i, i-1)
            cursor.execute(updateHours)
            dbconnection.commit()
            print("Update Sent")

    #Final Statement that 
    stmtP = "INSERT INTO stock_data (name, ticker, curr_price) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE curr_price = Values(curr_price)"
    for i in range(len(Data)):
        for j in range(len(Data[i])):
            #print("Data at I : {}".format(Data[i][j]))
            cursor.execute(stmtP, Data[i][j])
            dbconnection.commit()
            print('Sent')
    dbconnection.close()
def main():
    if is_time_between(time(3,59), time(4,0)) == True:
        Tickers = StockList()
    else:
        Tickers = DataFromFile()

    List_Ticker_and_Price = ApiBatchCall(Tickers)
    SendDataToServer(List_Ticker_and_Price)

main()
