import requests
from bs4 import BeautifulSoup as bs
import sqlite3 
import re
import time


def getPhilosopherNamesFromDB():
  conn = sqlite3.connect('philosophybot.db')
  c = conn.cursor()
  names = []
  for i in c.execute("SELECT DISTINCT name FROM philosophers"):
    names.append(i[0])

  return names

def addQuoteToDB(dataToAdd):
  try:
    conn = sqlite3.connect('philosophybot.db')
    c = conn.cursor()
    print(dataToAdd)
    c.executemany("INSERT INTO quotes VALUES (?,?,?,?)", dataToAdd)
    conn.commit()
    conn.close()
  except Exception as e:
    print(e)
      
def accentCheck(name):
  tempNameArray = []
  for char in name:
    if(len(char) != len(char.encode())):
     tempNameArray.append('_')
    else:
      tempNameArray.append(char)

  retVal = ''.join(tempNameArray)
  temp = retVal.replace('.', '')
  temp2 = temp.replace('-', ' ')
  name = temp2.split(' ')
  firstName = name[0]
  lastName = name[-1]
  return (firstName, lastName)




def main():
  philosopherNames = getPhilosopherNamesFromDB()
  qid = 0
  f = open("goodreadauthor.txt", "w")  
  for name in philosopherNames:
    googleSearchUrl = 'https://www.google.com/search?rlz=1C5CHFA_enUS896US896&sxsrf=ALeKk03z7YuMh6qBDC-6vy5b_vyIDDdwyQ%3A1596495759262&ei=j5coX9LND_uDytMP0dqbqAw&q='
    googleSearchUrlEnd = '+quotes+goodreads'
    googleFormatName = name.replace(' ', '+')
    googleFinishedUrl = googleSearchUrl+googleFormatName+googleSearchUrlEnd

    google_request_text = requests.get(googleFinishedUrl).text
    googleSoup = bs(google_request_text, 'html.parser')
    pageLinks = googleSoup.find_all('a', href=True)

    #check for goodreads link existence
    noGoogleSearchMatch = "It looks like there aren't any great matches for your search"

    baseGoodReadsUrlCheck = '/url?q=https://www.goodreads.com/author/quotes/'
    nameTuple = accentCheck(name)
    print(nameTuple)
    print(len(nameTuple))
    firstName = nameTuple[0].lower()
    lastName = nameTuple[-1].lower()


    goodReadsUrlTemp =  ""
    for a in pageLinks:
      if(baseGoodReadsUrlCheck in a['href']):
        print(a['href'])
        if(firstName in a['href'].lower() and lastName in a['href'].lower()):
          goodReadsUrlTemp = a['href'].split('/')
          break

    
    if(not goodReadsUrlTemp):
      print(name + "had no link to goodreads")
      print()
      f.write(name + "\n")
      continue
   
    baseGoodReadsUrl = 'https://www.goodreads.com/author/quotes/'
    goodReadsUrlEnd = goodReadsUrlTemp[-1].split('&')[0]
    goodReadsUrlFinal = baseGoodReadsUrl+goodReadsUrlEnd
    goodReadRequest = requests.get(goodReadsUrlFinal).text
    goodReadSoup = bs(goodReadRequest, 'html.parser')
    nextPageCheck = goodReadSoup.select('.leftContainer div div .next_page')
    nextPageText = 'next'
    if(nextPageText not in str(nextPageCheck)):
          # ONLY 1 PAGE

          # GET QUOTES
          soup4 = bs(goodReadRequest, 'html.parser')
          quoteList = soup4.select('.leftContainer .quote .quoteDetails')
          quoteListLength = len(quoteList)
          for i in range(0, quoteListLength):
            # make sure its the correct author 
            quote = quoteList[i].getText().split('\n    ―\n  \n')
            quoteClean1 = quote[0].replace('\n      ', '')
            quoteClean2 = quoteClean1[0:-1]
            quoteClean3 = quoteClean2[2:]
            tags = quote[1].replace('\n', '')
            tagArray = []
            tagsSplit= tags.split("tags:")
            authorNameDash = name.replace(' ', '-')
            try:
              bigSplit= tagsSplit[1].split('       ')
              tagsWithOutFirstSpace= bigSplit[1:]
              finalTagArray = tagsWithOutFirstSpace[0:-1]
              lastTagWithNum = tagsWithOutFirstSpace[-1].split(' ')
              finishedText = re.sub(r'\d', '', lastTagWithNum[0])
              finalTagArray.append(finishedText)
              noCommaTagArray = []
              for tag in finalTagArray:
                tempTag = tag.replace(',', '')
                tagArray.append(tempTag)
              tagArray.append(authorNameDash)
            except:
              #add author name
              tagArray.append(authorNameDash)
            
            tagString = ','.join(tagArray)
            dataToAdd = [(qid, name, quoteClean3, tagString)]
            addQuoteToDB(dataToAdd)
            qid+=1
            print()
            print()

    else:
      # multiple pages
      #grab the last number so we can loop pages
      soup3 = bs(goodReadRequest, 'html.parser')
      pageList = soup3.select('.leftContainer div div a')
      lastPageNum = int(pageList[-2:][0].getText())
      multiPageUrl =  goodReadsUrlFinal+"?page="

      for i in range(1,lastPageNum+1):
        print(multiPageUrl+str(i))
        print("-----------------------------------------------")
        print()
        print()
        html_text3 = requests.get(multiPageUrl+str(i)).text
        soup = bs(html_text3, 'html.parser')
        quoteList = soup.select('.leftContainer .quote .quoteDetails')
        quoteListLength = len(quoteList)
        for i in range(0, quoteListLength):
          # make sure its the correct author 
          quote = quoteList[i].getText().split('\n    ―\n  \n')
          quoteClean1 = quote[0].replace('\n      ', '')
          quoteClean2 = quoteClean1[0:-1]
          quoteClean3 = quoteClean2[2:]
          tags = quote[1].replace('\n', '')
          tagArray = []
          tagsSplit= tags.split("tags:")
          authorNameDash = name.replace(' ', '-')
          try:
            bigSplit= tagsSplit[1].split('       ')
            tagsWithOutFirstSpace= bigSplit[1:]
            finalTagArray = tagsWithOutFirstSpace[0:-1]
            lastTagWithNum = tagsWithOutFirstSpace[-1].split(' ')
            finishedText = re.sub(r'\d', '', lastTagWithNum[0])
            finalTagArray.append(finishedText)
            noCommaTagArray = []
            for tag in finalTagArray:
              tempTag = tag.replace(',', '')
              tagArray.append(tempTag)
            tagArray.append(authorNameDash)
          except:
            #add author name
            tagArray.append(authorNameDash)
          
          tagString = ','.join(tagArray)
          dataToAdd = [(qid, name, quoteClean3, tagString)]
          addQuoteToDB(dataToAdd)
          qid+=1
          print()
          print()

  f.close()
if __name__ == '__main__':
  main()
