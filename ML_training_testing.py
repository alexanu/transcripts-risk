# -*- coding: utf-8 -*-
"""
Created on Fri May 18 09:47:08 2018

@author: Yaroslav Vergun
"""


import os
import pickle
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta
import datetime
from nltk.tokenize import sent_tokenize
import numpy as np
from math import copysign
from scipy.stats import skew
import matplotlib.pyplot as plt

from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import RFECV
from sklearn import svm
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
from xgboost.sklearn import XGBClassifier

os.chdir('some_directory')
from soup_module import *
from vol_module import *



"""
data[j] will look like the following:
    
   [['GOOG',  datetime.date(2017,1,31), 'AMC'], 
    scores_management, 
    scores_qna, 
    cl_grade_management, 
    frac_dif_words_management, 
    polarity_management, 
    subjectivity_management, 
    frac_lm_pos_management, 
    cl_grade_qna, 
    frac_dif_words_qna, 
    polarity_qna, 
    subjectivity_qna, 
    frac_lm_pos_qna]
"""

# data[j][0] is a list containing ticker, date, and b4/after market close
# note that scores_management and scores_qna are lists of vader compound scores

# after market close (AMC) means event happens at date, volatility affected on date + 1 trading day
# b4 mkt open (BMO) means event happens at date - 1 trading day, volatility affected on date



data = []

# looping through folders and files
    
for folder in os.listdir('some_directory\\transcripts_from_selenium'):
    for filename in os.listdir('some_directory\\transcripts_from_selenium\\' + folder ):
        file = open('some_directory\\transcripts_from_selenium\\' 
                    + folder + '\\' + filename , "r", encoding="utf-8")
        soup = BeautifulSoup(file, 'html.parser')
        file.close()
        
        data.append(process_soup(soup))
        
        
# save the data for later use, it takes a while to create data list above
with open('some_directory\\data.pickle', 'wb') as f:
    pickle.dump(data, f)
    
# load the transcript data
with open('some_directory\\data.pickle', 'rb') as f:
    data = pickle.load(f)

# I deleted FB's transcript from 2012-7-26 as there is no previous price data to calculate volatility

# loading Price data
with open('some_directory\\price_data.pickle', 'rb') as f:
    price_data = pickle.load(f)



# after loading the necessary data, machine learning follows
    

# start at 2012-01-01
# end at 2018-07-01

gn_scores = []
lr_scores = []
lr_feature_weights = []    
#lsvc_scores = []                 # <--- not going to use this one
#lsvc_feature_weights = []
mlp_scores = []
rf_scores = []
rf_feature_importances = []
xgb_scores = []
xgb_feature_importances = []

rfecv_grid_scores = []


# stepping through the time periods 

delta_t = relativedelta(months= +3) 

begin_date = datetime.date(2012, 1, 1)

while (begin_date + 4*delta_t) <= datetime.date(2018, 1, 1):
    
    training_data = [data[i] for i in range(len(data)) if 
                     ( (begin_date <= data[i][0][1]) 
                     and (data[i][0][1] < (begin_date + 4*delta_t) ) ) ]
    
    testing_data = [data[i] for i in range(len(data)) if 
                    ( (begin_date + 4*delta_t <= data[i][0][1]) 
                    and (data[i][0][1] < (begin_date + 5*delta_t) ) ) ]
    
    
    # getting features and observations
    
    # what are my features? look above at how data[j] is described   
    obs_training = [ [np.mean(training_data[i][1]), 
                      np.std(training_data[i][1], ddof = 1), 
                      skew(training_data[i][1]), 
                      np.mean(training_data[i][2]), 
                      np.std(training_data[i][2], ddof = 1), 
                      skew(training_data[i][2]), 
                      training_data[i][3], 
                      training_data[i][4],
                      training_data[i][5],
                      training_data[i][6],
                      training_data[i][7],
                      training_data[i][8],
                      training_data[i][9],
                      training_data[i][10],
                      training_data[i][11],
                      training_data[i][12] ] for i in range(len(training_data)) ]
    
    
    obs_training_array = np.array(obs_training)
    
    scaler = StandardScaler() # for z-scoreing the columns, uses population standard deviation
    scaler.fit(obs_training_array) #scaler is changed
    scaled_obs_training = scaler.transform(obs_training_array)
    
    
    # now obs_testing
    obs_testing = [ [np.mean(testing_data[i][1]), 
                     np.std(testing_data[i][1], ddof = 1), 
                     skew(testing_data[i][1]), 
                     np.mean(testing_data[i][2]), 
                     np.std(testing_data[i][2], ddof = 1), 
                     skew(testing_data[i][2]), 
                     testing_data[i][3], 
                     testing_data[i][4], 
                     testing_data[i][5], 
                     testing_data[i][6], 
                     testing_data[i][7], 
                     testing_data[i][8], 
                     testing_data[i][9], 
                     testing_data[i][10], 
                     testing_data[i][11], 
                     testing_data[i][12] ] for i in range(len(testing_data)) ]
    
    
    
    obs_testing_array = np.array(obs_testing)
    
    scaled_obs_testing = scaler.transform(obs_testing_array)
    
    
    
    # Collection of volatilities, indexed the same way that the earnings calls are indexed in data
    list_of_vols_training = []
    
    for i in range(len(training_data)):
        #print(i, training_data[i][0][0], training_data[i][0][1] )
        list_of_vols_training.append(ann_vol_list_func(training_data[i][0][1], 
                                                       training_data[i][0][2], 
                                                       63, 
                                                       7, 
                                                       price_data[training_data[i][0][0]]))
                      # date, amc/bmo, hist window, window around event, data from ticker


    # label is +1 or -1, calculated as sign(vol(event date + 1td) - vol(event date)), sign(0) goes to +1
    # when plusminus_days = 7, the event is centered at index 7 
    labels_training = [ copysign(1,list_of_vols_training[i][8] - list_of_vols_training[i][7]) for 
                       i in range(len(training_data))]
    
    labels_training_array = np.array(labels_training)
    
    # collection of volatilities, testing set this time
    list_of_vols_testing = []
    
    for i in range(len(testing_data)):
        #print(i, testing_data[i][0][0], testing_data[i][0][1] )
        list_of_vols_testing.append(ann_vol_list_func(testing_data[i][0][1], 
                                                      testing_data[i][0][2], 
                                                      63, 
                                                      7, 
                                                      price_data[testing_data[i][0][0]]))
                      # date, amc/bmo, hist window, window around event, data from ticker
    
    labels_testing = [ copysign(1,list_of_vols_testing[i][8] - list_of_vols_testing[i][7]) for 
                      i in range(len(testing_data))]
    
    labels_testing_array = np.array(labels_testing)
    
    
    
    # classifiers 
    
    clf_gn = svm.SVC() #classifier, rbf default gaussian
    clf_lr = svm.SVC(kernel='linear') #linear classifier
    #clf_lsvc = svm.LinearSVC() #slightly different linear classifier, different hinge loss and multiclass reduction
    clf_mlp = MLPClassifier(hidden_layer_sizes=(10,4), solver='adam', max_iter=400) #multi layer perceptron neural network
    clf_rf = RandomForestClassifier(n_estimators=26) # 26 is the number of trees, default is 10
    clf_xgb = XGBClassifier(max_depth=3,  n_estimators=150, subsample=0.80)
    
    rfecv = RFECV(estimator=XGBClassifier(), scoring='accuracy') #recursive feat elim
    
    
    clf_gn.fit(scaled_obs_training, labels_training_array) #clf_xy is changed
    clf_lr.fit(scaled_obs_training, labels_training_array)
    #clf_lsvc.fit(scaled_obs_training, labels_training_array)
    clf_mlp.fit(scaled_obs_training, labels_training_array)
    clf_rf.fit(scaled_obs_training, labels_training_array)
    clf_xgb.fit(scaled_obs_training, labels_training_array)
    
    rfecv.fit(scaled_obs_training, labels_training_array)
    
    
    gn_scores.append(clf_gn.score(scaled_obs_testing, labels_testing_array))
    lr_scores.append(clf_lr.score(scaled_obs_testing, labels_testing_array))
    lr_feature_weights.append(np.abs(clf_lr.coef_)/np.sum(np.abs(clf_lr.coef_)))
    #lsvc_scores.append(clf_lsvc.score(scaled_obs_testing, labels_testing_array))
    #lsvc_feature_weights.append(np.abs(clf_lsvc.coef_)/np.sum(np.abs(clf_lsvc.coef_)))
    mlp_scores.append(clf_mlp.score(scaled_obs_testing, labels_testing_array))
    rf_scores.append(clf_rf.score(scaled_obs_testing, labels_testing_array))
    rf_feature_importances.append(clf_rf.feature_importances_)
    xgb_scores.append(clf_xgb.score(scaled_obs_testing, labels_testing_array))
    xgb_feature_importances.append(clf_xgb.feature_importances_)

    rfecv_grid_scores.append(rfecv.grid_scores_)
    
    
    print("trained on", begin_date, "-", begin_date + 4*delta_t, ",", 
          "tested on", begin_date + 4*delta_t, begin_date + 5*delta_t )
    
    print("gn:", clf_gn.score(scaled_obs_testing, labels_testing_array))
    print("lr:", clf_lr.score(scaled_obs_testing, labels_testing_array))
    #print("lsvc:", clf_lsvc.score(scaled_obs_testing, labels_testing_array))
    print("mlp:", clf_mlp.score(scaled_obs_testing, labels_testing_array))
    print("rf:", clf_rf.score(scaled_obs_testing, labels_testing_array))
    print("xgb:", clf_xgb.score(scaled_obs_testing, labels_testing_array))
    
    begin_date = begin_date + delta_t



print("gn_scores: ", 
      "Min", round(min(gn_scores),4), 
      " Max", round(max(gn_scores),4), 
      " Avg", round(np.mean(gn_scores),4))

print("lr_scores: ", 
      "Min", round(min(lr_scores),4), 
      " Max", round(max(lr_scores),4), 
      " Avg", round(np.mean(lr_scores),4))

#print("lsvc_scores: ", 
#      "Min", round(min(lsvc_scores),4), 
#      " Max", round(max(lsvc_scores),4), 
#      " Avg", round(np.mean(lsvc_scores),4))

print("mlp_scores: ", 
      "Min", round(min(mlp_scores),4), 
      " Max", round(max(mlp_scores),4), 
      " Avg", round(np.mean(mlp_scores),4))

print("rf_scores: ", 
      "Min", round(min(rf_scores),4), 
      " Max", round(max(rf_scores),4), 
      " Avg", round(np.mean(rf_scores),4))

print("xgb_scores: ", 
      "Min", round(min(xgb_scores),4), 
      " Max", round(max(xgb_scores),4), 
      " Avg", round(np.mean(xgb_scores),4))



# Recursive feature elimination with cross-validation tells me that all of the features should be used
# and feature importances from XGB and RF tell me that all of the features are relatively of the same importance


rf_feature_importances_array = np.array(rf_feature_importances)
print(np.mean(rf_feature_importances_array, axis = 0))
plt.plot(np.mean(rf_feature_importances_array, axis = 0))

xgb_feature_importances_array = np.array(xgb_feature_importances)
print(np.mean(xgb_feature_importances_array, axis = 0))
plt.plot(np.mean(xgb_feature_importances_array, axis = 0))

lr_feature_weights_array = np.array([np.reshape(x, max(x.shape)) for x in lr_feature_weights])
print(np.mean(lr_feature_weights_array, axis = 0))
plt.plot(np.mean(lr_feature_weights_array, axis = 0))

#lsvc_feature_weights_array = np.array([np.reshape(x, max(x.shape)) for x in lsvc_feature_weights])
#print(np.mean(lsvc_feature_weights_array, axis = 0))
#plt.plot(np.mean(lsvc_feature_weights_array, axis = 0))

rfecv_grid_scores_array = np.array(rfecv_grid_scores)
print(np.mean(rfecv_grid_scores_array, axis = 0))
plt.plot(np.mean(rfecv_grid_scores_array, axis = 0))





# some results

""" 
gn_scores:  Min 0.5306  Max 0.8627  Avg 0.7031
lr_scores:  Min 0.5102  Max 0.88  Avg 0.7031
mlp_scores:  Min 0.5102  Max 0.82  Avg 0.6602
rf_scores:  Min 0.5102  Max 0.82  Avg 0.6593
xgb_scores:  Min 0.5306  Max 0.76  Avg 0.6472
"""










    
    
