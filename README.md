# Earnings Call Transcripts and Risk

The task here is to forecast stock return volatility for the trading day immediately following an earnings call. The inputs are pieces of text, in particular earnings transcripts. The outputs are the labels +1 or -1 for volatility either going up or down after the call. The Machine Learning classifiers used here were Support Vector Machines, Neural Networks, Random Forests, and XGBoost. Each classifier's accuracy performance was backtested over a period of around 6 years. 

## Data

Earnings Call Transcripts for the top 50 holdings of the SP500 were obtained from [seekingalpha](https://seekingalpha.com/) from 2012-01-01 to 2018-07-01, totaling around 1250 transcripts. The code for this web scraping can be found in [browser_automate.py](https://github.com/yaroverg/transcripts-risk/blob/master/browser_automate.py) where mainly the [selenium](https://pypi.org/project/selenium/) package was used. 

Stock price data was obtained mostly via the [Quandl Python Module](https://www.quandl.com/tools/python) and the code for that can be found in [quandl_price_data.py](https://github.com/yaroverg/transcripts-risk/blob/master/quandl_price_data.py) and some missing data was filled in from Yahoo Finance. 

## Volatility

Using historical price data, volatility was calculated as the standard deviation of the natural logarithm of the price relatives and then annualized. More details and the code for this calculation can be found in [vol_module.py](https://github.com/yaroverg/transcripts-risk/blob/master/vol_module.py). This has a function which can calculate volatilities for a given number of days around a date, and the historical window over which standard deviation is calculated can be adjusted as well. 

It is worthwhile to note that instead of historical volatility, we can use implied volatility. This was not done here but can be done in the future. A nice resource for getting implied volatility is [IVolatility](https://www.ivolatility.com/). 

## Transcript processing  

The first tool used to parse the transcript html files was [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) and the code with all the details can be found in [soup_module](https://github.com/yaroverg/transcripts-risk/blob/master/soup_module.py). Each transcript was split into two parts: the management discussion part and the question-and-answer part. The stock ticker was extracted from each transcript as well as the date of the call and whether it happened before the market opened or after the market closed. Lists of sentences and words were obtained from each part using [nltk](https://www.nltk.org/). 

## Machine Learning Classifiers

TODO: Write history

## Feature Importances

TODO: Write credits

## something

TODO: Write license
