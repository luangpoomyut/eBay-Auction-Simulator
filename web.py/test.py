import sys; sys.path.insert(0, 'lib') # this line is necessary for the rest
import os                             # of the imports to work!

import web
import sqlitedb
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

# itemID, userID, minPrice, maxPrice, status, cat, desc, currTime
#a = sqlitedb.searchResults("1043749860", "", "", "", "", "", "", "")
#print(a)
#a = sqlitedb.query("select * from items where itemid = 1043374545")
#print(a)

# a = sqlitedb.auctionInfo(1043749860)
# print(a)

sqlitedb.placeBid(1046639674, 'Siyuan', 290)