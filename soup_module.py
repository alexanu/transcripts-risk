# -*- coding: utf-8 -*-
"""
Created on Tue Jun 19 14:35:08 2018

@author: Yaroslav Vergun
"""


from bs4 import BeautifulSoup
import pandas as pd
import dateutil.parser as dparser
import datetime
from nltk.tokenize import sent_tokenize, word_tokenize
from textstat.textstat import textstat
import pysentiment as ps
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()
lm = ps.LM()

# Loughran McDonald dictionary, note that these words are all uppercase
LM_dict = pd.read_csv('some_directory\\LoughranMcDonald_MasterDictionary_2016.csv')

pos_words = list(LM_dict.loc[LM_dict['Positive'] != 0]['Word'])

# note that the word question appeared in the negative word list and this word
# appears many times in a transcript



#function that slurps soup

def process_soup(soup):
    '''
    note that the soup input is something from BeautifulSoup already
    bs4 gets imported elsewhere
    '''
    
    tags = soup.find_all('p')
    
    ending_phrases = ['Copyright policy:', 
                      'you may now disconnect', 
                      'you may disconnect',
                      'This does conclude today’s conference',
                      'This concludes today’s conference',
                      'This concludes today’s call',
                      "This concludes today's teleconference",
                      'That does conclude today’s conference',
                      'That concludes today’s conference',
                      'That concludes today’s call',
                      "That concludes today's teleconference"]
    
    ind_list_copyright = [i for i in range(len(tags)) if 
                          any(x.lower() in tags[i].text.lower() for x in ending_phrases) ]
    
    
    #truncated list of tags
    tags = tags[:ind_list_copyright[-1]] 
    
    #paragraphs
    paras = [tags[i].text for i in range(len(tags)) ]
    
    
    #turn into sentences
    sentences = []
    for i in range(len(paras)):
        sentences = sentences + sent_tokenize(paras[i])
    
    #split qna part and management part
    ind_list_qna = [i for i in range(len(sentences)) if 
                    ('question-and-answer session' in sentences[i].lower().strip() 
                    and len(sentences[i].lower().strip())<40 ) ]
    
    if len(ind_list_qna) == 0:
        ind_list_qna = [i for i in range(len(sentences)) if 
                        ('question and answer session' in sentences[i].lower().strip() 
                        and len(sentences[i].lower().strip())<40 ) ]
    
    if len(ind_list_qna) == 0:
        ind_list_qna = [i for i in range(len(sentences)) if 
                        ('now begin the question-and-answer session' in sentences[i].lower().strip() ) ]
    
    if len(ind_list_qna) == 0:
        ind_list_qna = [i for i in range(len(sentences)) if 
                        ('now begin the question and answer session' in sentences[i].lower().strip() ) ]
    
    if len(ind_list_qna) == 0:
        ind_list_qna = [i for i in range(len(sentences)) if 
                        ('first question comes from' in sentences[i].lower().strip() ) ]
    
    if len(ind_list_qna) == 0:
        ind_list_qna = [i for i in range(len(sentences)) if 
                        ('first question will come from' in sentences[i].lower().strip() ) ]
        
    if len(ind_list_qna) == 0:
        ind_list_qna = [i for i in range(len(sentences)) if 
                        ("we'll take our first question from" in sentences[i].lower().strip() ) ]
    
    if len(ind_list_qna) == 0:
        ind_list_qna = [i for i in range(len(sentences)) if 
                        ("will take our first question from" in sentences[i].lower().strip() ) ]
        
    if len(ind_list_qna) == 0:
        ind_list_qna = [i for i in range(len(sentences)) if 
                        ("first question today is coming from" in sentences[i].lower().strip() ) ]
     
    if len(ind_list_qna) == 0:
        ind_list_qna = [i for i in range(len(sentences)) if 
                        ("first question is from" in sentences[i].lower().strip() ) ]
     
    
    
    sentences_management = sentences[:ind_list_qna[0]]
    sentences_qna = sentences[ind_list_qna[0]:]
    
    part_management = ' '.join(sentences_management)
    part_qna = ' '.join(sentences_qna)
    
    
    #textstat features
    cl_grade_qna = textstat.coleman_liau_index(part_qna)
    frac_dif_words_qna = textstat.difficult_words(part_qna)/textstat.lexicon_count(part_qna)
    
    cl_grade_management = textstat.coleman_liau_index(part_management)
    frac_dif_words_management = textstat.difficult_words(part_management)/textstat.lexicon_count(part_management)
    
    
    #pysentiment features
    polarity_qna = lm.get_score(lm.tokenize(part_qna))['Polarity']
    subjectivity_qna = lm.get_score(lm.tokenize(part_qna))['Subjectivity']

    polarity_management = lm.get_score(lm.tokenize(part_management))['Polarity']
    subjectivity_management = lm.get_score(lm.tokenize(part_management))['Subjectivity']    
    
    
    #Loughran Mcdonald features
    frac_lm_pos_qna = len([x for x in word_tokenize(part_qna) if 
                           x.upper() in pos_words])/textstat.lexicon_count(part_qna)
    
    frac_lm_pos_management = len([x for x in word_tokenize(part_management) if 
                                  x.upper() in pos_words])/textstat.lexicon_count(part_management)
    
    
    #get Vader scores
    scores_management = [analyzer.polarity_scores(sentences_management[i])["compound"] for 
                         i in range(len(sentences_management))]
    
    scores_qna = [analyzer.polarity_scores(sentences_qna[i])["compound"] for 
                  i in range(len(sentences_qna))]
    
    
    
    #this if-else handles the issue of different formating on some transcripts when getting the date
    if soup.p.text.find("Call") == -1:
        try_ctr = 0
        
        while try_ctr <= 4:      # trying to get date from first few paragraphs
            
            try: 
                dparser.parse(paras[try_ctr])
            except ValueError:
                try_ctr = try_ctr + 1
            else:
                break
        
        datetime_string_from_text = paras[try_ctr]
        
        try:
           dparser.parse(paras[try_ctr])     # if we cant, just use published date
        except ValueError:
            datetime_string_from_text = soup.find("time", itemprop = "datePublished").text
                                                     
        
    else:
        datetime_string_from_text = soup.p.text[soup.p.text.find("Call"):]
    
    
    #before market open, after market close
    b4open_afterclose = "BMO"
    
    if (dparser.parse(datetime_string_from_text, fuzzy = True).time() > datetime.time(14,0)):
        b4open_afterclose = "AMC"
    
    
    event_date = dparser.parse(datetime_string_from_text, fuzzy = True).date()
    
    
    datetime_string_from_code = soup.find("time", itemprop = "datePublished").text
    
    # date in title vs publish date
    date_c = dparser.parse(datetime_string_from_code, fuzzy = True).date()
    date_t = dparser.parse(datetime_string_from_text, fuzzy = True).date()
    
    if ( (abs( date_c - date_t )).days > 5 ):
        event_date = date_c
        
    # gets the stock ticker and the date of earnings call and if it happened b4 open or after close
    ticker_n_date = [soup.find("a","ticker-link")["symbol"], event_date , b4open_afterclose ]
    
    
    
    return [ticker_n_date, 
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