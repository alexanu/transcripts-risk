# -*- coding: utf-8 -*-
"""
Created on Fri Jun 22 11:44:41 2018

@author: Yaroslav Vergun
"""

import numpy as np
import pandas as pd


def ann_vol_func(date, numb_past_days, dataset):
    """
    annualized vol function
    volatility after the end of day of the date used
    date is like datetime.date(2017, 1, 31)
    numb_past_days, the historical sample window, is an integer
    dataset is a dataframe that has a column called 'Adj. Close'
    """
    
    # dataframe with an added column of returns 
    new_frame = dataset[['Adj. Close']]
    new_frame['returns'] = np.log(new_frame['Adj. Close']/(new_frame['Adj. Close'].shift(1)))
    
    # getting the index corresponding to the date given
    ind_list = list(new_frame.index)
    found = ind_list.index(pd.Timestamp(date))

    # series of length numb_past_days, and the last element is the return at date given, includes date given
    subset_hist_returns = new_frame['returns'][ind_list[found + 1 - numb_past_days : found + 1]]
    
    # sample standard deviation
    samp_std = np.std(  subset_hist_returns  , ddof=1)  
    
    # annualized volatility, multiplying by the square root of the number of trading days in a year
    ann_vol = np.sqrt(252) * (samp_std)      
    
    return ann_vol




    


def ann_vol_list_func(date, BMO_or_AMC, numb_past_days, plusminus_days, dataset):
    """
    this function produces a list of volatilities around the date given
    date is of the form datetime.date(2017, 1, 31)
    BMO_or_AMC is either the string 'AMC' or 'BMO'
    numb_past_days is an integer that determines the historical period over which we calculate standard dev
    plusminus_days is an integer that determines the window around the event date
    dataset is a dataframe that has a column called 'Adj. Close'
    """
    
    # list of timestamps of trading days, and the index at which the date occurs
    ind_list = list(dataset.index)
    found = ind_list.index(pd.Timestamp(date))
    
    # before or after market determines when the event occurs, we adjust the window according to this
    if BMO_or_AMC == 'AMC':
        ind_slice = ind_list[found - plusminus_days : found + plusminus_days + 1]
    elif BMO_or_AMC == 'BMO' :
        ind_slice = ind_list[found - plusminus_days - 1 : found + plusminus_days ]
    
    # this uses the above volatility function to get a list
    vols = [ann_vol_func(i.date(), numb_past_days, dataset ) for i in ind_slice ]
    
    return vols




