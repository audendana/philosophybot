#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug  1 14:21:49 2020

@author: samc
"""

import sqlite3
import random
import requests

longLiveAccessToken = ""
page_id = "226635862037384"
fb_api_post_url_base = "https://graph.facebook.com/v8.0/"

def getRandomQuoteAndBio():
    conn = sqlite3.connect('philosophybot.db')
    c = conn.cursor()
    
    #selection of the last quote in the data base (first quote is index 0)
    totalQuotesQueryString = "SELECT COUNT(*) FROM quotes;"
    
    #getting the max count then generating a random int between 0 and last quote
    c.execute(totalQuotesQueryString)
    totalQuotes = c.fetchone()[0]
   
    i = random.randint(0,totalQuotes)
    j = str(i)
    
    #Selecting a random quote from the db using the new var, i
    randomQuoteQ = ("SELECT * FROM quotes WHERE qid = %s" % j)
    c.execute(randomQuoteQ)
    randomQuote = c.fetchall()

    bioQ = ("SELECT biography FROM philosophers WHERE name = (SELECT philosopher FROM quotes WHERE qid = %s);" % j)
    #using the same process we can grab the bio for the author that said the quote 
    c.execute(bioQ)
    getBio = c.fetchall()
    
    
    return (randomQuote, getBio)


def cleanUpRandomQuote(randomQuote, bioUnclean):
    qid = randomQuote[0][0]
    author = randomQuote[0][1]
    quote = randomQuote[0][2]
    tags = randomQuote[0][3]
    tagsSplit = tags.split(",")
    
    tagsFinal = []
    for a,element in enumerate(tagsSplit):
        tagsFinal.append(''.join(('#',tagsSplit[a])))
    
    print(quote)
    print("Final Tags:", tagsFinal)
    
    print("-" * 40)
    #selecting the biography for the specific quote must rewrite using specific variable
   
    authorBio = bioUnclean[0][0]
    tagFinalString =  " ".join(tagsFinal)
    print(authorBio)

    return (quote, authorBio, tagFinalString)

def postQuoteToFBApi(quote, authorBio, tagFinalString):
    messageData = "\""+quote+"\""+"\n\n"+authorBio+"\n"+tagFinalString
    jsonData = {
      "message": messageData,
      "access_token": longLiveAccessToken
    }
    response = requests.post(fb_api_post_url_base+page_id+"/feed", jsonData)

    if response.ok:
      print("Sucess posting")
    else:
      print(resposne)
      print("Failed to post to fb. Going to try and get another quote")
      runQuotePost()
    
def runQuotePost():
    randomQuote = getRandomQuoteAndBio()      
    cleanedQuoteTuple = cleanUpRandomQuote(randomQuote[0], randomQuote[1])
    postQuoteToFBApi(cleanedQuoteTuple[0], cleanedQuoteTuple[1], cleanedQuoteTuple[2])


def main():
  runQuotePost()
       
    
if __name__ == '__main__':
  main()
