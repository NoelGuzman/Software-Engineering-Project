from iexfinance.stocks import Stock
from iexfinance.refdata import get_iex_symbols
from os import environ

######### OS Environment Settings ################
environ['IEX_TOKEN'] = 'sk_9e30adf0ff3f4cf38db805ba73ec42e5' # setting Environment Token stops any need of inputing token in every function call
environ['IEX_API_VERSION'] = 'v1' #required verisons accessable: [v1, iexcloud-sandbox]
######### OS Environment Settings ################


def StockList():
    ListT = get_iex_symbols() #get callable ticker symbols
    StockListSym = [] # Empty list to store ticker symbols
    for index in range(len(ListT)): #iterate through ListT and pull symbols
        itemsdict = ListT[index] #Pulls dictionary
        ticker = itemsdict['symbol']
        if '*' in ticker[-1]:
            ticker = ticker[0:(len(ticker)-1)]
        StockListSym.append(ticker) #Add to StockListSym
    return StockListSym
def main():
    Tickers = StockList()
    with open('TickerList.txt', 'w') as filehandler:
        for i in Tickers:
            filehandler.write('%s\n' % i)
main()