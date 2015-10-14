 #-*- coding: utf-8 -*-

#### IMPORTS 1.0

import os
import re
import scraperwiki
import urllib2
from datetime import datetime
from bs4 import BeautifulSoup


#### FUNCTIONS 1.0


def validateFilename(filename):
    filenameregex = '^[a-zA-Z0-9]+_[a-zA-Z0-9]+_[a-zA-Z0-9]+_[0-9][0-9][0-9][0-9]_[0-9QY][0-9]$'
    dateregex = '[0-9][0-9][0-9][0-9]_[0-9QY][0-9]'
    validName = (re.search(filenameregex, filename) != None)
    found = re.search(dateregex, filename)
    if not found:
        return False
    date = found.group(0)
    now = datetime.now()
    year, month = date[:4], date[5:7]
    validYear = (2000 <= int(year) <= now.year)
    if 'Q' in date:
        validMonth = (month in ['Q0', 'Q1', 'Q2', 'Q3', 'Q4'])
    elif 'Y' in date:
        validMonth = (month in ['Y1'])
    else:
        try:
            validMonth = datetime.strptime(date, "%Y_%m") < now
        except:
            return False
    if all([validName, validYear, validMonth]):
        return True


def validateURL(url):
    try:
        r = urllib2.urlopen(url)
        count = 1
        while r.getcode() == 500 and count < 4:
            print ("Attempt {0} - Status code: {1}. Retrying.".format(count, r.status_code))
            count += 1
            r = urllib2.urlopen(url)
        sourceFilename = r.headers.get('Content-Disposition')

        if sourceFilename:
            ext = os.path.splitext(sourceFilename)[1].replace('"', '').replace(';', '').replace(' ', '')
        else:
            ext = os.path.splitext(url)[1]
        validURL = r.getcode() == 200
        validFiletype = ext.lower() in ['.csv', '.xls', '.xlsx']
        return validURL, validFiletype
    except:
        print ("Error validating URL.")
        return False, False


def validate(filename, file_url):
    validFilename = validateFilename(filename)
    validURL, validFiletype = validateURL(file_url)
    if not validFilename:
        print filename, "*Error: Invalid filename*"
        print file_url
        return False
    if not validURL:
        print filename, "*Error: Invalid URL*"
        print file_url
        return False
    if not validFiletype:
        print filename, "*Error: Invalid filetype*"
        print file_url
        return False
    return True


def convert_mth_strings ( mth_string ):
    month_numbers = {'JAN': '01', 'FEB': '02', 'MAR':'03', 'APR':'04', 'MAY':'05', 'JUN':'06', 'JUL':'07', 'AUG':'08', 'SEP':'09','OCT':'10','NOV':'11','DEC':'12' }
    for k, v in month_numbers.items():
        mth_string = mth_string.replace(k, v)
    return mth_string


#### VARIABLES 1.0

entity_id = "E0703_RACBC_gov"
url = "http://www.redcar-cleveland.gov.uk/rcbcweb.nsf/Web+Full+List/BDA34873F225499880257A0600543F90?OpenDocument"
errors = 0
data = []


#### READ HTML 1.0

html = urllib2.urlopen(url)
soup = BeautifulSoup(html, "lxml")


#### SCRAPE DATA
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

block = soup.find( text = re.compile('Documents available to download on this page are: ')).find_next('ul').find_next('ul')
links = block.find_all('a')
for link in links:
    url = 'http://www.redcar-cleveland.gov.uk' + link['href']
    html_csv = urllib2.urlopen(url)
    soup_csv = BeautifulSoup(html_csv, 'lxml')
    block_scv = soup_csv.find('div', 'column2')
    url_csvs = block_scv.find_all('a','set1')
    t = block_scv.find('span', 'the council-st').text.strip()
    for url_csv in url_csvs:
        if '$FILE' in url_csv['href']:
            if 'Financial Year 2015-16' in t:
                if 'Spend' in url_csv.text.strip():
                    if 'Credit' not in url_csv.text.strip():
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
                        data.append([csvYr, csvMth, url])

            else:
                url = 'http://www.redcar-cleveland.gov.uk'+url_csv['href']
                if 'Credit' not in url_csv.text.strip():
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
                    data.append([csvYr, csvMth, url])


#### STORE DATA 1.0

for row in data:
    csvYr, csvMth, url = row
    filename = entity_id + "_" + csvYr + "_" + csvMth
    todays_date = str(datetime.now())
    file_url = url.strip()

    valid = validate(filename, file_url)

    if valid == True:
        scraperwiki.sqlite.save(unique_keys=['l'], data={"l": file_url, "f": filename, "d": todays_date })
        print filename
    else:
        errors += 1

if errors > 0:
    raise Exception("%d errors occurred during scrape." % errors)


#### EOF

