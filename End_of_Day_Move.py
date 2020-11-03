import mysql.connector as sql

######### Server Info #########
try:

    dbconnection = sql.connect(host = "", user = "", passwd = "", database = "")#Server Info Removed
    cursorA = dbconnection.cursor(buffered = True)
    cursorB = dbconnection.cursor(buffered = True)
except sql.Error as err:
        print(err)
######### Server Info #########


def High_Low_Avg():
    '''
    End of Day update of high, low, and average for the day, as well as five day updates

    Input:None
    Output:None
    '''
    rowcountstmt = "SELECT id, past_hour_8, past_hour_7, past_hour_6, past_hour_5, past_hour_4, past_hour_3, past_hour_2, past_hour, curr_price FROM stock_data"
    cursorA.execute(rowcountstmt)
    row = cursorA.fetchone()
    while row is not None:
        listrow = list(row)
        id = listrow.pop(0)
        maxP = max(listrow)
        minP = min(listrow)
        avgP = round(sum(listrow)/len(listrow), 2)
        HLAstmt = "UPDATE stock_data SET today_low = %s,today_high = %s, today_avg = %s where id = %s"
        val = (minP, maxP, avgP, id)
        cursorB.execute(HLAstmt, val)
        dbconnection.commit()
        print("Sent")
        fivedaystmt = "SELECT five_day_high, five_day_low, five_day_avg FROM stock_data where id = {}".format(id)
        cursorB.execute(fivedaystmt)
        fiverow = list(cursorB.fetchone())
        if maxP > fiverow[0]:
            fiverow[0] = maxP
        if minP < fiverow[1] and fiverow[1] != 0:
            fiverow[1] = minP
        fivedayavg = avgP + fiverow[2]/ 2
        fivedayupdatestmt = "UPDATE stock_data SET five_day_high = %s, five_day_low = %s, five_day_avg = %s where id = %s"
        fiveval = (fiverow[0], fiverow[1], fivedayavg, id)
        cursorB.execute(fivedayupdatestmt, fiveval)
        dbconnection.commit()

        row = cursorA.fetchone()

def Daily_Move():
    '''
    Takes Data from table "stock_data" and transferring it to "past_data" table
    Input: None
    Output: None
    '''
    rowcountstmt = "SELECT id, past_hour_8, curr_price, today_avg  FROM stock_data"
    cursorA.execute(rowcountstmt)
    end_day_stmt = "INSERT INTO past_data (stock_id, open, close, average) VALUES (%s, %s, %s, %s)"
    row = cursorA.fetchone()
    while row is not None:
        cursorB.execute(end_day_stmt, row)
        dbconnection.commit()
        print("Sent Daily Move")
        row = cursorA.fetchone()

def main():
    High_Low_Avg()
    Daily_Move()
    dbconnection.close()
main()
