# -*- coding: utf-8 -*-
"""
Created on Wed May 30 11:44:43 2018

@author: Yaroslav Vergun
"""


# Obtaining price data from quandl


import quandl
import pandas as pd
import time
import pickle

# change the actual api key 
quandl.ApiConfig.api_key = "your_key_here"



# a dictionary of dataframes(timestamps,prices) accessed by ticker string key
price_data = {}

tickers = list(set(data[i][0][0] for i in range(len(data))))
 
for j in tickers:
    if j == 'GOOG':
        price_data[j] = quandl.get('WIKI/' + j +'L' + '.11', start_date="2011-1-1", end_date="2018-6-20")
    else:
        price_data[j] = quandl.get('WIKI/' + j + '.11', start_date="2011-1-1", end_date="2018-6-20")
        
    time.sleep(4)

# GOOG was missing price data, so I used GOOGL
# MMM was missing price data too, so I'm using data from yahoo finance


# note that the start_date and the end_date should be adjusted depending on when you want to
# calculate volatility
    
        

# MMM data from yahoo finance, then added to my price_data dictionary
mmm = pd.read_csv('some_directory\\prices_yahoo\\MMM.csv')
mmm = mmm.drop(columns=['Open', 'High', 'Low', 'Close', 'Volume'])
mmm['Date'] = pd.to_datetime(mmm['Date'])
mmm = mmm.set_index('Date')
mmm = mmm.rename(columns = {'Adj Close': 'Adj. Close'})

price_data['MMM'] = mmm




# saving price_data
with open('some_directory\\price_data.pickle', 'wb') as f:
    pickle.dump(price_data, f)
    
# loading
with open('some_directory\\price_data.pickle', 'rb') as f:
    price_data = pickle.load(f)




