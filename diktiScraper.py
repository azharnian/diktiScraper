from bs4 import BeautifulSoup
from socket import error as SocketError
import urllib
import pandas
import MySQLdb
import os
import re
import time
import datetime

ts = time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
db = MySQLdb.connect(
    host = '127.0.0.1',
    user = 'root',
    passwd = '310116',
    db = 'diktiScraperdb'
)
class scrape(object): #membuat objek scrape

    def __init__(self, nameOfMachine): #inisiasi objek
        self.nameOfMachine = nameOfMachine #pemberian atribut objek pada inisiasi

    def getLink(self, addr): #membuat fungsi getLink
        dataLink = {  #membuat dictionary
        'addt' : [], #teks untuk penambahan
        'link' : [] #link yang ada di halaman
        }
        def scrapePage(addr):
            scrapeData = BeautifulSoup(urllib.urlopen(addr), "html.parser")
            return scrapeData
        data = scrapePage(addr)
        try :
            for recordRow in data.findAll('tr'):
                addtText = ""
                for recordLink in recordRow.findAll('a', href=True):
                    tempData = recordLink.text.split()
                    for listOfTempData in tempData:
                        addtText = addtText + listOfTempData + " "
                    dataLink['addt'].append(str(addtText))
                    dataLink['link'].append(str(recordLink['href']))
            print "Get DataLink Scrape HTML Object"        
            return dataLink
        except AttributeError :
            print "Not Found"
            return dataLink
    def getTextOnly(self,addr):
        dataText = {
            'addt' : []
        }
        listText = []
        def scrapePage(addr):
            scrapeData = BeautifulSoup(urllib.urlopen(addr), "html.parser")
            return scrapeData
        data = scrapePage(addr)
        try:
            for recordRow in data.findAll('tr'):
                for recordText in recordRow.findAll('td'):
                    listText.append(recordText.text)
            for item in listText[2::21]:
                addtText = ""
                tempData = item.split()
                for listOfTempData in tempData:
                    addtText = addtText + listOfTempData + " "
                dataText['addt'].append(str(addtText))
                #print addtText
            print "Get Text Faculty ScrapeHTML Object"
            return dataText
        except SocketError as e:
            if e.errno != errno.ECONNRESET:
                raise # Not error we are looking for
            pass # Handle error here.

urlServer = "/home/alien/diktiScraper" #server program host
urlTarget = "http://forlap.dikti.go.id/perguruantinggi/homerekap" #home rekap
dataGet = {
    'addt' : [],
    'link' : []
} #dictionary for data that got from scraper
scraperLayer0 = scrape('layer0_df')
dataGet = scraperLayer0.getLink(urlTarget)
layer0_df = pandas.DataFrame(dataGet, columns=['addt', 'link'])
cur = db.cursor()
query0 = 'USE diktiScraperdb;'
cur.execute(query0)
indexUniFac = "indexUniFac"
query7 = "DROP TABLE IF EXISTS  "+indexUniFac+";"
query8 = "CREATE TABLE "+indexUniFac+" (Id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,code VARCHAR(255), univ VARCHAR(255), fac VARCHAR(255));"
cur.execute(query7)
cur.execute(query8)
indexUniFac = {
    'code' : [],
    'univ' : [],
    'fac' : []
}
l = 0
i = 0
for link in layer0_df['link']:
    urlTarget0 = link
    if i/10 < 1:
        nameDb1 = 'list0' + str(i)
    else :
        nameDb1 = 'list' + str(i)
    nameDb1 = str(nameDb1)
    scraper1 = scrape('df1')
    dataGet1 = scraper1.getLink(urlTarget0)
    df1 = pandas.DataFrame(dataGet1, columns=['addt', 'link'])
    df1.index.name = 'institutionId'
    j = 0
    for link1 in  df1['link']:
        urlTarget1 = link1
        if j/10 < 1:
            nameDb2 = nameDb1 + "0" + str(j)
        else :
            nameDb2 = nameDb1 + str(j)
        nameDb2 = str(nameDb2)
        scraper2 = scrape('df2')
        dataGet2 = scraper2.getLink(urlTarget1)
        df2 = pandas.DataFrame(dataGet2, columns=['addt', 'link'])
        df2.index.name = 'institutionId'
        k = 0
        for link2 in  df2['link']:
            urlTarget2 = link2
            if k/10 < 1:
                nameDb3 = nameDb2 + "0" + str(k)
            else :
                nameDb3 = nameDb2 + str(k)
            nameDb3 = str(nameDb3)
            scraper3 = scrape('df3')
            dataGet3 = scraper3.getTextOnly(urlTarget2)
            df3 = pandas.DataFrame(dataGet3, columns=['addt'])
            df3.index.name = 'institutionId'
            m = 0
            print st
            for falcu in df3['addt']:
                if m/10 < 1:
                    code = nameDb3[4:] + "00000" + str(m)
                elif m/100 <1:
                    code = nameDb3[4:] + "0000" + str(m)
                elif m/1000 <1:
                    code = nameDb3[4:] + "000" + str(m)
                elif l/10000 <1:
                    code = nameDb3[4:] + "00" + str(m)
                elif m/100000 <1:
                    code = nameDb3[4:] + "0" + str(m)
                else :
                    code = nameDb3[4:] + str(m)
                indexUniFac['code'].append(code)
                indexUniFac['univ'].append(df2['addt'][k])
                indexUniFac['fac'].append(falcu)
                a = indexUniFac['code'][l]
                a = re.sub("[!@#$/']", '', a)
                b = indexUniFac['univ'][l]
                b = re.sub("[!@#$/']", '', b)
                c = indexUniFac['fac'][l]
                c = re.sub("[!@#$/']", '', c)
                print "adding Dict indexUniFac "+ a + " | " + b + " | " + c
                query11 = "INSERT INTO indexUniFac (code, univ, fac) VALUES ('"+a+"','"+b+"','"+c+"');" 
                cur.execute(query11)
                db.commit()
                print "insert to DB MySQL"
                m= m+1
                l = l+1
            k = k+1
        j = j+1
    i = i+1