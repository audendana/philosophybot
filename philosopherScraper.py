import time
import re
import requests
from bs4 import BeautifulSoup as bs
import sqlite3

#after _ (A-C)
philoBaseUrl = 'https://en.wikipedia.org/wiki/List_of_philosophers_'
bioBaseUrl = 'https://en.wikipedia.org/wiki/'

letterList = ['(A-C)', '(D-H)', '(I-Q)', '(R-Z)']


philosopherNameList = []
underScoreNameList = []

nameBioDict = {}

conn = sqlite3.connect('philosophybot.db')
c = conn.cursor()

def main():

  for element in letterList:
    html_text = requests.get(philoBaseUrl+element).text
    soup = bs(html_text, 'html.parser')
    contentDiv = soup.select('#mw-content-text ul li a')

    for a in contentDiv:
      name = a.getText()
      if(len(name) > 1):
        modName = name.replace(" ", "_")
        underScoreNameList.append(modName)
        philosopherNameList.append(name) 

  nameList = [] 
  underNameList = []
  for i in philosopherNameList:
    if(i != 'Article' and  i != 'Category' and i !='Glossary' and i !='Outline' and i !='Portal'):
      nameList.append(i)
 
  for i in philosopherNameList:
    if(i != 'Article' and i != 'Category' and i !='Glossary' and i !='Outline' and i !='Portal'):
      underNameList.append(i)


  nameCount = 0
  for name in underNameList:
    tempUrl = 'https://en.wikipedia.org/wiki/'+name
    print(tempUrl)
    tempList = []
    bioPage = requests.get(tempUrl).text
    soup2 = bs(bioPage, 'html.parser')

    nameConvert = name.split('_')[0]
    bio = soup2.select('#mw-content-text .mw-parser-output > p')
    count = 0
    
    for p in bio:
      try:
        bioString = str(p)
        if(count> 0):
          break
        else:
          if(nameConvert in bioString):
            bioText = p.getText()
            bioTextNewLine = bioText.replace('\n', '')
            bioTextNewLine2 = bioTextNewLine.replace('\xa0', ' ')
            finishedText = re.sub(r'[[0-9]*]', '', bioTextNewLine2)
            dataToAdd = [(nameList[nameCount], finishedText)]
            print(dataToAdd)
            print()
            print()
            c.executemany("INSERT INTO philosophers VALUES (?,?)", dataToAdd)
            count+=1
      except:
         print("no bio " + name)
    nameCount+=1
    time.sleep(0.5)
  conn.commit()
if __name__ == '__main__':
  main()
