import urllib.parse
import urllib.request
import re
import time

FX_PAIR='EURUSD'
YEAR=2000
MONTH=12

def find_tk(fx_pair, year, month):
    url = 'http://www.histdata.com/download-free-forex-historical-data/?/ascii/tick-data-quotes/' + fx_pair.lower() + '/' + year + '/' + month
    headers = { 'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9',
                'Referer' : 'http://www.histdata.com/download-free-forex-historical-data/?/ascii/tick-data-quotes/' + fx_pair.lower() + '/' + year,
                'Connection' : 'keep-alive',
                'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language' : 'en-us',
                'Cache-Control' : 'max-age=0',
                #'Cookie' : 'complianceCookie=on; __cfduid=de55c641f7d6f852e1746e4660c2940c61460233664'
                }

    req = urllib.request.Request(url, headers = headers)

    p = re.compile(r"^.*id=\"tk\" value=\"(\S*)\".*$")
    found = False
    with urllib.request.urlopen(req) as response:
        r = response.read().decode("utf-8")
        for line in r.splitlines():
            m = p.match(line)
            if m is not None:
                print("found " + m.group(1))
                return m.group(1)

    print("Response Code: %s\nInfo: %s\n" % (response.getcode(), response.info()))
    print("Failed to find 'tk' in " + r)

def download(fx_pair, year, month):
    url = 'http://www.histdata.com/get.php'
    values = {'tk' : find_tk(fx_pair, year, month),
            'date' : year,
            'datemonth' : year + month,
            'platform' : 'ASCII',
            'timeframe' : 'T',
            'fxpair' : fx_pair
            }

    headers = { 'Content-Type' : 'application/x-www-form-urlencoded',
                'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9',
                'Referer' : 'http://www.histdata.com/download-free-forex-historical-data/?/ascii/tick-data-quotes/' + fx_pair.lower() + '/' + year + '/' + month,
                'Origin' : 'http://www.histdata.com'
                }

    data = urllib.parse.urlencode(values)
    data = data.encode('utf-8') # data should be bytes
    req = urllib.request.Request(url, data = data, headers = headers)
    with urllib.request.urlopen(req) as response:
        # print("Response Code: %s\nInfo: %s\n" % (response.getcode(), response.info()))
        return response.read()

def download_and_createfile(fx_pair, year, month):
    print("Processing [" + fx_pair + "] " + year + ':' + month)
    f = open(fx_pair + '_' + year + '_' + month + ".zip", 'wb')
    f.write(download(fx_pair, year, month))
    f.close()

y=2000
for m in range(5, 13):
    download_and_createfile('EURUSD', str(y), str(m).zfill(2));
    time.sleep(5)

for y in range(2000, 2015):
    for m in range(1, 13):
        download_and_createfile('EURUSD', str(y), str(m).zfill(2));
        time.sleep(5)

y = 2016
for m in range(1, 5):
    download_and_createfile('EURUSD', str(y), str(m).zfill(2));
    time.sleep(5)

