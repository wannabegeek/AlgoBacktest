import urllib.parse
import urllib.request

url = 'http://www.histdata.com/get.php'
values = {'tk' : 'c92691404446db5f82102a9cab029052',
        'date' : '2000',
        'datemonth' : '200011',
        'platform' : 'ASCII',
        'timeframe' : 'T',
        'fxpair' : 'EURUSD'
        }

data = urllib.parse.urlencode(values)
data = data.encode('utf-8') # data should be bytes
req = urllib.request.Request(url, data)
with urllib.request.urlopen(req) as response:
    the_page = response.read()
    print(the_page)