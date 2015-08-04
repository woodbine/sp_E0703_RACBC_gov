# -*- coding: utf-8 -*-
import sys
reload(sys) # Reload does the trick!
sys.setdefaultencoding('UTF8')
import os
import re
import requests
import scraperwiki
import urllib2
from datetime import datetime
from bs4 import BeautifulSoup


# Set up variables
entity_id = "E0703_RACBC_gov"
url = "http://www.redcar-cleveland.gov.uk/rcbcweb.nsf/Web+Full+List/BDA34873F225499880257A0600543F90?OpenDocument"
errors = 0
# Set up functions
def validateFilename(filename):
    filenameregex = '^[a-zA-Z0-9]+_[a-zA-Z0-9]+_[a-zA-Z0-9]+_[0-9][0-9][0-9][0-9]_[0-9][0-9]$'
    dateregex = '[0-9][0-9][0-9][0-9]_[0-9][0-9]'
    validName = (re.search(filenameregex, filename) != None)
    found = re.search(dateregex, filename)
    if not found:
        return False
    date = found.group(0)
    year, month = int(date[:4]), int(date[5:7])
    now = datetime.now()
    validYear = (2000 <= year <= now.year)
    validMonth = (1 <= month <= 12)
    if all([validName, validYear, validMonth]):
        return True
def validateURL(url):
    try:
        r = requests.get(url, allow_redirects=True, timeout=20)
        count = 1
        while r.status_code == 500 and count < 4:
            print ("Attempt {0} - Status code: {1}. Retrying.".format(count, r.status_code))
            count += 1
            r = requests.get(url, allow_redirects=True, timeout=20)
        sourceFilename = r.headers.get('Content-Disposition')

        if sourceFilename:
            ext = os.path.splitext(sourceFilename)[1].replace('"', '').replace(';', '').replace(' ', '')
        else:
            ext = os.path.splitext(url)[1]
        validURL = r.status_code == 200
        validFiletype = ext in ['.csv', '.xls', '.xlsx']
        return validURL, validFiletype
    except:
        raise
def convert_mth_strings ( mth_string ):

    month_numbers = {'JAN': '01', 'FEB': '02', 'MAR':'03', 'APR':'04', 'MAY':'05', 'JUN':'06', 'JUL':'07', 'AUG':'08', 'SEP':'09','OCT':'10','NOV':'11','DEC':'12' }
    #loop through the months in our dictionary
    for k, v in month_numbers.items():
#then replace the word with the number

        mth_string = mth_string.replace(k, v)
    return mth_string
# pull down the content from the webpage

html = urllib2.urlopen(url)
soup = BeautifulSoup(html)
# find all entries with the required class
#block = soup.find('div', attrs = {'class':'main'})
block = soup.find( text = re.compile('Documents available to download on this page are: ')).find_next('ul').find_next('ul')
links = block.find_all('a')
for link in links:
    url = 'http://www.redcar-cleveland.gov.uk' + link['href']
   # print url
    html_csv = urllib2.urlopen(url)
    soup_csv = BeautifulSoup(html_csv)
    block_scv = soup_csv.find('div', 'column2')
    url_csvs = block_scv.find_all('a','set1')
    for url_csv in url_csvs:
        if '$FILE' in url_csv['href']:
            if not 'Credit' in  url_csv.text:
                url = 'http://www.redcar-cleveland.gov.uk'+url_csv['href']
                csvfile = url_csv.text.strip()
                csvfiles = csvfile.replace('10Invoices over 500 pounds -', ' ').replace('11Invoices over £ 500 -', ' ').replace('12Invoices over£500-', ' ').replace('12Invoices over £500', ' ').replace('02Invoices over 500', ' ').replace('03Invoices over 500', ' ').replace('04Invoices over 500', ' ').replace('05Invoices over 500', ' ').replace('06Invoices over 500', ' ').replace('07Invoices over 500', ' ').replace('08Invoices over 500', ' ').replace('09Invoices over 500', ' ').replace('01Invoices Over £500 ', ' ').replace('02Invoices Over £500 ', ' ').replace('03Invoices Over £500 ', ' ').replace('04Invoices Over £500 ', ' ').replace('05Invoices Over £500 ', ' ').replace('06Invoices Over £500 ', ' ').replace('07Invoices Over £500 ', ' ').replace('08Invoices Over £500 ', ' ').replace('09Invoices Over £500 ', ' ').replace('10Invoices Over £500 ', ' ').replace('11Invoices Over £500 ', ' ').replace('12Invoices Over £500 ', ' ').replace('Invoices Over £500 ', ' ').replace('Over £500 Invoices', ' ').replace('Credit Notes', ' ').replace('Invoices over£500-', ' ').replace('Invoices over 500 ', ' ').replace('Invoices over 500 pounds', ' ').replace('Over 500 Credit', ' ').replace('Over 500 Spend ', ' ').replace('£500 spend ', ' ').replace('Over 500 Credit Notes ', ' ').replace('Over 500 Spend -', ' ').replace('Over 500 Credits - ', ' ').replace('Invoices over £500 ', ' ').replace('Invoices over £ 500 - ', ' ').replace('Invoices over £500 - ', ' ').replace('pounds - ', ' ').replace('-', ' ').replace('Invoices over £500 ', ' ').replace('£500 Credit Notes ', ' ').replace('Credit',' ').replace('.csv', ' ').replace('csv', ' ').replace('Over', ' ').replace(u'\xa3500', ' ').replace('500', ' ').replace(' ', '').split(' ')[0].split('(')[0]
                csvMth = csvfiles[:3]
                if 'sAp' in csvMth:
                    csvMth = 'Apr'
                if 'Not' in csvMth:
                    csvMth = 'Mar'
                if 'sJu' in csvMth:
                    csvMth = 'Jun'
                csvYr = csvfiles[-2:]
                if 'il' in csvYr:
                    csvYr = '15'
                if 'ly' in csvYr:
                    csvYr = '14'
                if 'ch' in csvYr:
                    csvYr = '15'
                csvYr = '20' + csvYr
                csvMth = convert_mth_strings(csvMth.upper())
                filename = entity_id + "_" + csvYr + "_" + csvMth
                todays_date = str(datetime.now())
                file_url = url.strip()
                validFilename = validateFilename(filename)
                validURL, validFiletype = validateURL(file_url)
                if not validFilename:
                    print filename, "*Error: Invalid filename*"
                    print file_url
                    errors += 1
                    continue
                if not validURL:
                    print filename, "*Error: Invalid URL*"
                    print file_url
                    errors += 1
                    continue
                if not validFiletype:
                    print filename, "*Error: Invalid filetype*"
                    print file_url
                    errors += 1
                    continue
                scraperwiki.sqlite.save(unique_keys=['l'], data={"l": file_url, "f": filename, "d": todays_date })
                print filename
if errors > 0:
    raise Exception("%d errors occurred during scrape." % errors)
