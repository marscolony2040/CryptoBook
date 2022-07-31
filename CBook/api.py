import websocket
import json
import threading
import numpy as np

class Order:

    bidprice = {}
    askprice = {}
    priceline = {}
    bidvol = {}
    askvol = {}

    def parsebid(self, book):
        sumx = 0
        i = 0
        x = []
        y = []
        for (price, vol) in book:
            x.append(i)
            sumx += vol
            y.append(sumx)
            i += 1
        return [-k for k in x[::-1]], y[::-1]

    def parseask(self, book):
        sumx = 0
        i = 0
        x = []
        y = []
        for (price, vol) in book:
            x.append(i)
            sumx += vol
            y.append(sumx)
            i += 1
        return x, y

    def parseprice(self, x, y):
        hold = []
        hold2 = []
        for i, j in zip(x, y):
            hold.append(i[0])
            hold2.append(j[0])
            
        yes = hold[::-1] + hold2
        n0, n1 = np.min(yes), np.max(yes)
        slabs = len(yes)
        dn = (n1 - n0)/(slabs - 1)
        hold3 = []
        for i in range(slabs):
            hold3.append(n0 + i*dn)
        return hold3
        

    def parsebook(self, n=50):
        for tickB, tickA in zip(self.bids, self.asks):
            bbook = sorted(self.bids[tickB].items(), reverse=True)[:n]
            abook = sorted(self.asks[tickA].items())[:n]
            self.bidprice[tickB], self.bidvol[tickB] = self.parsebid(bbook)
            self.askprice[tickA], self.askvol[tickA] = self.parseask(abook)
            self.priceline[tickB] = self.parseprice(bbook, abook)

class Parse(Order):

    bids = {}
    asks = {}
    sync = {}

    def parser(self, msg):
        if 'product_id' in msg.keys():
            ticker = msg['product_id']
            if msg['type'] == 'snapshot':
                self.bids[ticker] = {float(price):float(vol) for (price, vol) in msg['bids']}
                self.asks[ticker] = {float(price):float(vol) for (price, vol) in msg['asks']}
                self.sync[ticker] = True
                
            if msg['type'] == 'l2update':
                for (side, price, volume) in msg['changes']:
                    if side == 'buy':
                        if float(volume) == 0:
                            del self.bids[ticker][float(price)]
                        else:
                            self.bids[ticker][float(price)] = float(volume)
                    if side == 'sell':
                        if float(volume) == 0:
                            del self.asks[ticker][float(price)]
                        else:
                            self.asks[ticker][float(price)] = float(volume)
                




class CBPro(threading.Thread, Parse):

    def __init__(self, ticker=['BTC-USD'], depth=5):
        threading.Thread.__init__(self)
        self.ticker = ticker
        self.depth = depth
        self.url = 'wss://ws-feed.exchange.coinbase.com'

    def run(self):
        msg = {'type':'subscribe', 'product_ids': self.ticker,
               'channels':['level2']}
        conn = websocket.create_connection(self.url)
        conn.send(json.dumps(msg))
        while True:
            resp = json.loads(conn.recv())
            self.parser(resp)
            self.parsebook(n=self.depth)
