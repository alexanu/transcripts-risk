# Earnings Call Transcripts and Risk

The task here is to forecast stock return volatility for the trading day immediately following an earnings call. The inputs are pieces of text, in particular earnings transcripts. The outputs are the labels +1 or -1 for volatility either going up or down after the call. The Machine Learning classifiers used here were Support Vector Machines, Neural Networks, Random Forests, and XGBoost. Each classifier's accuracy performance was backtested over a period of around 6 years. 

## Data

Earnings Call Transcripts for the top 50 holdings of the SP500 were obtained from [seekingalpha](https://seekingalpha.com/) from 2012-01-01 to 2018-07-01, totaling around 1250 transcripts. The code for this web scraping procedure can be found in [browser_automate.py](https://github.com/yaroverg/transcripts-risk/blob/master/browser_automate.py) where mainly the [selenium](https://pypi.org/project/selenium/) package was used. 

Stock price data was obtained mostly via the [Quandl Python Module](https://www.quandl.com/tools/python) and the code for that can be found in [quandl_price_data.py](https://github.com/yaroverg/transcripts-risk/blob/master/quandl_price_data.py) and some missing data was filled in from Yahoo Finance. 

## Volatility

Using historical price data, volatility was calculated as the standard deviation of the natural logarithm of the price relatives and then annualized. More details and the code for this calculation can be found in [vol_module.py](https://github.com/yaroverg/transcripts-risk/blob/master/vol_module.py). This has a function which can calculate volatilities for a given number of days around a date, and the historical window over which standard deviation is calculated can be adjusted as well. 

It is worthwhile to note that instead of historical volatility, we can use implied volatility. This was not done here but can be done in the future. A nice resource for getting implied volatility is [IVolatility](https://www.ivolatility.com/). 

## Transcript processing  

The first tool used to parse the transcript html files was [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) and the code with all the details can be found in [soup_module.py](https://github.com/yaroverg/transcripts-risk/blob/master/soup_module.py). Each transcript was split into two parts: the management discussion part and the question-and-answer part. The stock ticker was extracted from each transcript as well as the date of the call and whether it happened before the market opened or after the market closed. Lists of sentences and words were obtained from each part using [nltk](https://www.nltk.org/). 

## Features

The features were generated at the same stage as transcript processing and the code can be found in [soup_module.py](https://github.com/yaroverg/transcripts-risk/blob/master/soup_module.py). For both the management part and the Q&A part of a transcript we had the following features: 

* [Vader](https://github.com/cjhutto/vaderSentiment) Sentiment Analysis Python package
  * The Vader compound sentiment score was computed for each sentence and then the features used were the mean, standard deviation and skewness of those scores 
 

* [Textstat](https://github.com/shivam5992/textstat) Python package for calculating readability and complexity of a corpus 
  * The Coleman-Liau Index was found for both parts of the transcript which represented the reading grade level of the text
  * The fraction of difficult words present relative to the total number of words in each part was also used


* [Pysentiment](https://github.com/hanzhichao2000/pysentiment/) library for Sentiment Analysis using the [Loughran-McDonald](https://sraf.nd.edu/textual-analysis/resources/) financial dictionary
  * The Polarity of each part was calculated which gives a sense of spread between positive and negative words
  * The Subjectivity of each part was also used which gives the fraction of non-neutral words relative to the total number of words  


* Positive words from the [Loughran-McDonald](https://sraf.nd.edu/textual-analysis/resources/) financial dictionary
  * The fraction of positive words relative to the total number of words was used. Note that negative words were not used because the word "question" is classified as negative but appears frequently in earnings calls generally without a negative connotation. 


## Machine Learning

Code for the Machine Learning stage can be found in [ML_training_testing.py](https://github.com/yaroverg/transcripts-risk/blob/master/ML_training_testing.py) where mainly the [scikit-learn](http://scikit-learn.org/stable/)  library was used. The classifiers used and tested on this project were the following:

* [Support Vector Machines](http://scikit-learn.org/stable/modules/svm.html#svm-classification) using the default Radial Basis Function kernel as well as a linear kernel
* [Neural networks](http://scikit-learn.org/stable/modules/neural_networks_supervised.html)(Multi-layer Perceptron) using two hidden layers and the default "adam" solver
* [Random Forests](http://scikit-learn.org/stable/modules/ensemble.html#forest) using an increased number of estimators
* [XGBoost](https://xgboost.readthedocs.io/en/latest/python/python_api.html#module-xgboost.sklearn) with more estimators and subsampling during training

Note that SVM classifiers performed very well without parameter tuning while MLP, Random Forest and XGBoost classifiers required tuning. 

The split of the data into training and testing subsets was done with the idea of training on recent historical observations and testing the constructed classifier on the immediate following observations. Observations were grouped into which quarter of the year they occurred in. Quarters were defined as the first 3 months of the year, the next three and so on. For example, a classifier was trained on transcripts that occurred within the time range [2016-7-1, 2017-7-1) and was tested on transcripts that occurred in the range [2017-7-1, 2017-10-1). From 2012-1-1 to 2018-4-1 we had 21 such training/testing sets. For each training/testing set we calculated each classifier's accuracy score. Then the classifiers were evaluated according to the min, average, and max of their 21 accuracy scores. The best performing classifier was SVM with the rbf kernel for its high average score, high minimum score and great results with default parameters. The table below summarizes the results. 

|   | Min score  | Avg Score  | Max Score  |
|---|:---:|:---:|:---:|
| SVM_rbf  | 53.06%  | 70.31%  | 86.27%  |
| SVM_linear  | 51.02%  | 70.31%  | 88.00%  |
| MLP  | 51.02%  | 66.02%  | 82.00%  | 
| RF  | 51.02%  | 65.93%  | 82.00%   | 
| XGBoost  | 53.06%  | 64.72%  | 76.00%  | 




## Feature Importances

TODO: Write credits

## something

TODO: Write license
