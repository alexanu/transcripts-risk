# -*- coding: utf-8 -*-
"""
Created on Thu Jun 14 09:44:22 2018

@author: Yaroslav Vergun
"""


import time
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys



browser = webdriver.Firefox(executable_path=r'some_directory\\geckodriver.exe')


#login

browser.get('https://seekingalpha.com/account/login')
time.sleep(3)

username = browser.find_element_by_id("login_user_email")
time.sleep(1)

password = browser.find_element_by_id("login_user_password")
time.sleep(1)

username.send_keys('username@domain.com')
time.sleep(1)

password.send_keys('FakePassword-123')
time.sleep(2)

password.send_keys(Keys.RETURN)
time.sleep(2)


#for one stock ticker

ticker = "AAPL"

# ["T", "V", "WFC", "UNH", "CVX", "HD", "PFE", "CSCO"]
# ["BA", "VZ", "PG", "MA", "C", "MRK", "KO", "NVDA", "NFLX"]
# ["DIS", "CMCSA", "ORCL", "PEP", "MCD", "IBM", "AMGN"]
# ["PM", "GE", "MMM", "TXN", "HON", "UNP", "ABT", "MO", "ACN", "NKE"]



list_of_tickers = ["SLB", "UTX", "CRM", "GILD", "CAT", "COST"]

for ticker in list_of_tickers:
    time.sleep(3)
    

    base_url = "https://seekingalpha.com/symbol/" + ticker + "/earnings/transcripts"
    
    browser.get(base_url)
    time.sleep(2)
    
    
    
    #scrolling
    
    for i in range(12):
        time.sleep(1)
        browser.execute_script("window.scrollTo(0, " + str(1080*i) + ")") 
        time.sleep(3)
    
    
    
    
    
    #finding the links I want, this needs to happen fast after scrolling
        
    links = browser.find_elements_by_partial_link_text('Earnings Call Transcript') 
    time.sleep(1)
    
    ticker_string = "(" + ticker + ")"
    
    if ticker_string in links[0].text :
        something =  links[0].text
        
    elif ticker_string in links[1].text :
        something =  links[1].text
        
    elif ticker_string in links[2].text :
        something =  links[2].text
        
    time.sleep(1)    
    
    pre_comp_name = something.split(" ")[0]
    
    if pre_comp_name.lower() == "the":
        pre_comp_name = something.split(" ")[1] 
    
    
    if pre_comp_name.find("'") != -1 :
        comp_name = pre_comp_name[:pre_comp_name.find("'")]
    else:
        comp_name = pre_comp_name    
        
    if comp_name.find(",") != -1 :
        comp_name = comp_name[:comp_name.find(",")]
    
    years_wanted = ["2018", "2017", "2016", "2015", "2014", "2013", 
                    "2012", "Q18", "Q17", "Q16", "Q15", "Q14", "Q13", "Q12"]
    
    filtered_links = [ a for a in links 
                      if ( ((ticker_string in a.text) or (comp_name.lower() in a.text.lower())) 
                      and (any(y in a.text for y in years_wanted)) ) ]
    
    filtered_urls = [ a.get_attribute("href") for a in filtered_links]
    
    time.sleep(2)
    
    
    
    
    
    # create folder with name of ticker to store all the calls
    
    if not os.path.exists('some_directory\\transcripts_from_selenium\\' + str(ticker)):
        os.makedirs('some_directory\\transcripts_from_selenium\\' + str(ticker))
    
    time.sleep(1)
    
    # going through the link urls and saving the source code, adding ?part=single
    
    for x in filtered_urls:
        time.sleep(2)
        browser.get(x + "?part=single")
        time.sleep(4)
        
        #single_page = browser.find_element_by_partial_link_text("Single page view")
        #single_page.click()
        #time.sleep(3)
        
        name_of_file_to_save = browser.find_element_by_tag_name('h1').text
        time.sleep(1)
        
        thing_to_save = browser.page_source
        time.sleep(2)
        
        with open('some_directory\\transcripts_from_selenium\\' 
                  + str(ticker) + '\\' + name_of_file_to_save + ".html", 
                  'w', encoding="utf-8") as f2:
            f2.writelines(thing_to_save)
            
        time.sleep(1)
    
    
    
    
    
    





