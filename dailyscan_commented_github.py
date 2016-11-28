# -*- coding: utf-8 -*-
"""
This script will download daily price data from Yahoo for a given list of stock symbols.

It will then look for matching price highs or matching price lows given certain parameters
the user can specify.  The list of output can be e-mailed to a specified e-mail.

User must also specify a list of symbols to scan, an option filepath with
the format of one symbol per line.  An e-mail list of recipients.  And a sender
e-mail address with password to login to G-Mail's SMTP server to send.

If no e-mail specified, will output the results of scan to console.
"""
import pandas as pd
import pandas.io.data
import datetime
import sys
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP
import smtplib
import sys

SYMBOL_LIST = ['AAPL', 'AMZN', 'NFLX', 'FB', 'GOOG']
SYMBOL_FILEPATH = 'C:\\dailyscan\\symbols.txt'
EMAIL_LIST = [] #to receive the e-mail
EMAIL_SENDER = "" #sender function configured for gmail smtp
EMAIL_PASSWORD = "" #enter your password


'''#############################'''
'''### Custom Price Filters  ###'''
'''#############################'''
def get_matching_highs(data, n, filter):
    '''(pd.Panel, int, bool) -> dictionary(string:float)
	
	Takes data panel and n from user to check back looking for 
    two matching highs within range of the buffer, then returns them as
    dictionary sym:price. n should be same as data['SYM'].shape[0]
    '''
    match_dict = {}
    
    
    #for each symbol in panel
    for sym in data.items:
        #first set buffer for symbol based on most recent price
        buffer = set_price_buffer(data[sym].iloc[-1].High)      
        
        #first i loop starts with yesterday, j loop loops back to end of period
        #from inner j loop if match, add it and break, then check from i loop
        #if match break i loop too - stops searching once it finds a match
        #starts looking from last row in table(most recent day), counts backwards
        
        #i loop counts to index 1, j loop to index 0
        #day n-1 is the most recent trading day, day 0 is the oldest
        for i in range (n-1, 0, -1):
            for j in range (i-1, -1, -1):
                if abs(data[sym].iloc[i].High - data[sym].iloc[j].High) < buffer:
                    #High is close enough for a match
                    
                    #Filter - from the j element (oldest day of match) to most recent day
                    #has the matching high been broken? matching high = high[j] + buffer
                    if not filter:
                        match_dict[sym] = round(max(data[sym].iloc[i].High, data[sym].iloc[j].High), 2)
                        break
                    else:
                        #filter on
                        matching_high = data[sym].iloc[j].High + buffer
                        broken = False
                        for k in range (j, n):
                            if data[sym].iloc[k].High > matching_high:
                                broken = True
                                break
                        
                        if not broken:
                            match_dict[sym] = round(max(data[sym].iloc[i].High, data[sym].iloc[j].High), 2)
                            break
                        else:
                            break
            #break i loop, found signal                
            if abs(data[sym].iloc[i].High - data[sym].iloc[j].High) < buffer:
                break
            
    return match_dict

def get_matching_lows(data, n, filter):
    '''(pd.Panel, int, bool) -> dictionary(string:float)
	
	Takes data panel and n from user to check back looking for 
    two matching lows within range of the buffer, then returns them as
    dictionary sym:price. n should be same as data['SYM'].shape[0]
    '''
    match_dict = {}
    
    
    #for each symbol in panel
    for sym in data.items:
        #first set buffer for symbol based on most recent price
        buffer = set_price_buffer(data[sym].iloc[-1].High)      
        
        #first i loop starts with yesterday, j loop loops back to end of period
        #from inner j loop if match, add it and break, then check from i loop
        #if match break i loop too - stops searching once it finds a match
        #starts looking from last row in table(most recent day), counts backwards
        #i loop counts to index 1, j loop to index 0
        for i in range (n-1, 0, -1):
            for j in range (i-1, -1, -1):
                if abs(data[sym].iloc[i].Low - data[sym].iloc[j].Low) < buffer:
                    #Low close enough for match
                #Filter - from the j element (oldest day of match) to most recent day
                    #has the matching high been broken? matching high = high[j] + buffer
                    if not filter:
                        match_dict[sym] = round(min(data[sym].iloc[i].Low, data[sym].iloc[j].Low), 2)
                        break
                    else:
                        #filter on
                        matching_low = data[sym].iloc[j].Low - buffer
                        broken = False
                        for k in range (j, n):
                            if data[sym].iloc[k].Low < matching_low:
                                broken = True
                                break
                        
                        if not broken:
                            match_dict[sym] = round(min(data[sym].iloc[i].Low, data[sym].iloc[j].Low), 2)
                            break
                        else:
                            break
            if abs(data[sym].iloc[i].Low - data[sym].iloc[j].Low) < buffer:
                break
            
    return match_dict        
        
def get_newest_matching_highs(data, n, filter):
    '''(pd.Panel, int, bool) -> dictionary(string:float)
	
	Takes data panel and n from user to check back looking for 
    two matching highs within range of the buffer, then returns them as
    dictionary sym:price. n should be same as data['SYM'].shape[0]
    ONLY compares yesterday with rest of period
    '''
    match_dict = {}
    
    
    #for each symbol in panel
    for sym in data.items:
        #first set buffer for symbol based on most recent price
        buffer = set_price_buffer(data[sym].iloc[-1].High)      
        
        for i in [n-1]:
            #i loop is one day, yesterday (most recent closed bar)
            for j in range (i-1, -1, -1):
                if abs(data[sym].iloc[i].High - data[sym].iloc[j].High) < buffer:
                    #High is close enough for a match
                    
                    #Filter - from the j element (oldest day of match) to most recent day
                    #has the matching high been broken? matching high = high[j] + buffer
                    if not filter:
                        match_dict[sym] = round(max(data[sym].iloc[i].High, data[sym].iloc[j].High), 2)
                        break
                    else:
                        #filter on
                        matching_high = data[sym].iloc[j].High + buffer
                        broken = False
                        for k in range (j, n):
                            if data[sym].iloc[k].High > matching_high:
                                broken = True
                                break
                        
                        if not broken:
                            match_dict[sym] = round(max(data[sym].iloc[i].High, data[sym].iloc[j].High), 2)
                            break
                        else:
                            break
            #break i loop, found signal                
            if abs(data[sym].iloc[i].High - data[sym].iloc[j].High) < buffer:
                break
            
    return match_dict

def get_newest_matching_lows(data, n, filter):
    '''(pd.Panel, int, bool) -> dictionary(string:float)
	
	Takes data panel and n from user to check back looking for 
    two matching lows within range of the buffer, then returns them as
    dictionary sym:price. n should be same as data['SYM'].shape[0]
    Only comparing yesterdays bar, most recent closed candle for signals
    '''
    match_dict = {}
    
    
    #for each symbol in panel
    for sym in data.items:
        #first set buffer for symbol based on most recent price
        buffer = set_price_buffer(data[sym].iloc[-1].High)      
        
        for i in [n-1]:
            #only looking at yesterdays bar
            for j in range (i-1, -1, -1):
                if abs(data[sym].iloc[i].Low - data[sym].iloc[j].Low) < buffer:
                    #Low close enough for match
                #Filter - from the j element (oldest day of match) to most recent day
                    #has the matching high been broken? matching high = high[j] + buffer
                    if not filter:
                        match_dict[sym] = round(min(data[sym].iloc[i].Low, data[sym].iloc[j].Low), 2)
                        break
                    else:
                        #filter on
                        matching_low = data[sym].iloc[j].Low - buffer
                        broken = False
                        for k in range (j, n):
                            if data[sym].iloc[k].Low < matching_low:
                                broken = True
                                break
                        
                        if not broken:
                            match_dict[sym] = round(min(data[sym].iloc[i].Low, data[sym].iloc[j].Low), 2)
                            break
                        else:
                            break
            if abs(data[sym].iloc[i].Low - data[sym].iloc[j].Low) < buffer:
                break
            
    return match_dict    
    
def close_to_whole(signal):
    '''(dictionary string:float) -> dictionary string:float
	
	Takes dictionary of symbol : price and returns dictionary of only those
    pairs where the price is within buffer range of a whole # .00
    '''
    close_dict = {}
    
    for sym, price in signal.iteritems():
        buffer = min(set_price_buffer(price), 0.35)
        #want the minimum buffer to be .10
        buffer = max(buffer, 0.10)
        decimal = price - int(price)
        if abs(1 - decimal) <= buffer or decimal <= buffer:
            #close to whole
            close_dict[sym] = price

    return close_dict
    
'''#############################'''
'''###    HELPER FUNCTIONS   ###'''
'''#############################'''
def set_price_buffer(price):
    '''(float) -> float
	
	Given a stocks price, determine how wide the buffer
    should be for that stock.  Minimum is 5 cents, then its .001 * price, rounded up.
	The buffer is the margin of error past a high or low to not be counted as different.
    '''
    buffer = 0.05
    
    if price > 55:
        buffer = round(0.001 * price, 2)
    
    return buffer
    

def download_data(symbols, n=5):
    '''(list of strings) -> pd.Panel or pd.DataFrame
	
	Takes list of symbols as string, and number of days
    to look back and get data as n (n=5 means get last 5 days).
    Returns pandas panel if multiple symbols, otherwise pandas dataframe
    '''
    #Get the date, set Start and End
    today = datetime.date.today()
    start = get_start_date(n)
    end = today - datetime.timedelta(days=1)
    
    data = pd.io.data.get_data_yahoo(symbols, start=start, end=end)  
    
    return data

    
def get_start_date(n):
    '''(int) -> datetime
	
	Takes the n number of days user wants for data, keeps
    trying to find the proper start date so yahoo data returns
    the proper number of columns - allows user to get n bars of data
    instead of just n days back
    '''
    
    today = datetime.date.today()
    start = today - datetime.timedelta(days=n+1)
    end = today - datetime.timedelta(days=1)
    
    #Try current start
    data = pd.io.data.get_data_yahoo('SPY', start=start, end=end)

    if data.shape[0] == n:
        return start
    
    i = 1
    while data.shape[0] != n:
        i += 1
        start = today - datetime.timedelta(days=n+i)
        
        data = pd.io.data.get_data_yahoo('SPY', start=start, end=end)
        
        if data.shape[0] == n:
            return start
    
def load_symbols_from_file(filename):
    '''(string) -> list of strings
	
	Takes a string and looks for a file by that name.
    Then reads file line by line and removing whitespace to load
    symbol into symbol list.  This will run by default.
    '''
    try:
        symbols = [sym.rstrip() for sym in open(filename)]
        print "Loaded %s symbols from file." % len(symbols)
        return symbols
    except:
        print "Can't open file: ", filename
        symbols = []
        return symbols
        
def duplicate_sym(new, master):
    '''(list of strings, list of strings) -> bool
	
	Takes new list to see if any smybols are already in master
    if one is, we hit the endof the fin viz list so break
    '''
    for sym in new:
        if sym in master:
            return True
    return False

def output_signals(highs, lows, filter_name):
    """(dict, dict, string) -> string
    
    Converts dictionaries to pandas data frame then returns
    one long string of the output.
    """
    output = ""
    output += filter_name
    output += "\n"
    output += "\n"
    highs = pd.DataFrame(highs.items())
    output += "Highs:\n"
    output += highs.to_string(index=None, header=False, col_space=5)
    output += "\n"
    
    lows = pd.DataFrame(lows.items())
    output += "Lows:\n"
    output += lows.to_string(index=None, header=False, col_space=5)
    output += "\n"
    output += "\n"
    output += "Signal Total: %d   Highs: %d   Lows: %d" % ((len(highs)+len(lows)), len(highs), len(lows))
    output += "\n"
    output += "##########################################"
    output += "\n"
    output += "\n"
    output += "\n"
    
    return output

def send_email(message):
    '''(string) -> None
    
    Takes string, sends e-mail.
    '''
    recipients = EMAIL_LIST
    emaillist = [elem.strip().split(',') for elem in recipients]
    msg = MIMEMultipart()
    msg['Subject'] = 'Today\'s Alerts'
    msg['From'] = 'Daily Scan'
     
    part = MIMEText(message)
    msg.attach(part)  
    
    server = smtplib.SMTP("smtp.gmail.com:587")
    server.ehlo()
    server.starttls()
    server.login(EMAIL_SENDER, EMAIL_PASSWORD)
     
    server.sendmail(msg['From'], emaillist , msg.as_string())
    
'''#############################'''
'''###         MAIN          ###'''
'''#############################'''
def main():
    #Get Symbols
    symbols = SYMBOL_LIST
    symbols += load_symbols_from_file(SYMBOL_FILEPATH)
    symbols = list(set(symbols)) #Remove Duplicates
    symbols.sort()
    print "Downloading data for %d symbols.." % len(symbols)
    
    #Download the data
    n_days = 5 #days to scan back
    data = download_data(symbols, n_days).transpose(2, 1, 0)
    
    #Create String of Output
    output = ""
    #New
    matching_highs = get_newest_matching_highs(data, n_days, False)
    matching_lows = get_newest_matching_lows(data, n_days, False)
    output += output_signals(matching_highs, matching_lows, "New Signals")
    #Filtered
    matching_highs = get_matching_highs(data, n_days, True)
    matching_lows = get_matching_lows(data, n_days, True)
    output += output_signals(matching_highs, matching_lows, "Filtered Signals")
    #All
    matching_highs = get_matching_highs(data, n_days, False)
    matching_lows = get_matching_lows(data, n_days, False)
    output += output_signals(matching_highs, matching_lows, "All Signals")
    
    #Email the Results
    if len(EMAIL_LIST) == 0:
        print output
    else:
        send_email(output)
        print "Email Sent"

if __name__ == "__main__":
    main()

    