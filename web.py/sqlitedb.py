import web

db = web.database(dbn='sqlite',
        db='AuctionBase' #TODO: add your SQLite database filename
    )

######################BEGIN HELPER METHODS######################

# Enforce foreign key constraints
# WARNING: DO NOT REMOVE THIS!
def enforceForeignKey():
    db.query('PRAGMA foreign_keys = ON')

# initiates a transaction on the database
def transaction():
    return db.transaction()
# Sample usage (in auctionbase.py):
#
# t = sqlitedb.transaction()
# try:
#     sqlitedb.query('[FIRST QUERY STATEMENT]')
#     sqlitedb.query('[SECOND QUERY STATEMENT]')
# except Exception as e:
#     t.rollback()
#     print str(e)
# else:
#     t.commit()
#
# check out http://webpy.org/cookbook/transactions for examples

# returns the current time from your database
def getTime():
    # TODO: update the query string to match
    # the correct column and table name in your database
    query_string = 'select * from CurrentTime'
    results = query(query_string)
    # alternatively: return results[0]['currenttime']
    return results[0].Time # TODO: update this as well to match the
                                  # column name

# returns a single item specified by the Item's ID in the database
# Note: if the `result' list is empty (i.e. there are no items for a
# a given ID), this will throw an Exception!
def getItemById(item_id):
    # TODO: rewrite this method to catch the Exception in case `result' is empty
    query_string = 'select * from Items where item_ID = $itemID'
    result = query(query_string, {'itemID': item_id})
    return result[0]

# wrapper method around web.py's db.query method
# check out http://webpy.org/cookbook/query for more info
def query(query_string, vars = {}):
    return list(db.query(query_string, vars))

#####################END HELPER METHODS#####################

#TODO: additional methods to interact with your database,
# e.g. to update the current time

def setTime(selected_time, cTime, update_message):
    t = transaction()
    try:
        query_string = "UPDATE CurrentTime SET time = $selected_time"
        db.query(query_string, {'selected_time': selected_time})
    except Exception as e:
        t.rollback()
        print str(e)
        return "Cannot go back in time. Please pick a future time."
    else:
        t.commit()
    return update_message


# Returns a list of dictionary of the results of the search
def searchResults(itemID, userID, minPrice, maxPrice, status, cat, desc, currTime):
    query_string = '''SELECT * FROM (SELECT Items.itemid, name, currently, first_bid, buy_price, number_of_bids, started, ends, seller_userid, 
    description, group_concat(category) as Category FROM ITEMS INNER JOIN CATEGORIES ON ITEMS.itemid = CATEGORIES.itemid GROUP BY Items.itemid) as t1 WHERE '''
    counter = 1     # counter is used to make sure the first string appended does not include an extra AND
    if itemID:
        if counter == 1:
            query_string = query_string + 'itemid = ' + str(itemID)
        else:
            query_string = query_string + ' AND itemid = ' + str(itemID)
        counter += 1
    if userID:
        if counter == 1:
            query_string = query_string + 'seller_userid = "' + str(userID.strip()) + '"'
        else:
            query_string = query_string + ' AND seller_userid = "' + str(userID.strip()) + '"'
        counter += 1
    # Checks that the current price of an auction or the buy-now price of an item is higher than the min price stated
    if minPrice:
        if counter == 1:
            query_string = query_string + 'first_bid >= ' + str(minPrice)
        else:
            query_string = query_string + ' AND first_bid >= ' + str(minPrice)
        counter += 1
    # Opposite of min price
    if maxPrice:
        if counter == 1:
            query_string = query_string + 'buy_price <= ' + str(maxPrice)
        else:
            query_string = query_string + ' AND buy_price <= ' + str(maxPrice)
        counter += 1
    # Status is guaranteed to be open, close, notStarted, or all with all being the radio button defaulted on the form
    if status:
        if counter == 1:
            # Checks that current time is between the starting and end time of an auction
            if status == 'open':
                query_string = query_string + '("' + str(currTime) + '" >= started AND "' + str(currTime) + '" < ends AND currently < buy_price)'
                counter += 1
            # Checks that current time is after end time of an auction
            elif status == 'close':
                query_string = query_string + '("' + str(currTime) + '" >= ends OR currently >= buy_price)'
                counter += 1
            # Checks that current time is before starting time of an auction
            elif status == 'notStarted':
                query_string = query_string + '"' + str(currTime) + '" < started'
                counter += 1
        else:
            if status == 'open':
                query_string = query_string + ' AND ("' + str(currTime) + '" >= started AND "' + str(currTime) + '" < ends AND currently < buy_price)'
                counter += 1
            elif status == 'close':
                query_string = query_string + ' AND ("' + str(currTime) + '" >= ends OR currently >= buy_price)'
                counter += 1
            elif status == 'notStarted':
                query_string = query_string + ' AND "' + str(currTime) + '" < started'
                counter += 1 
    if cat:
        if counter == 1:
            query_string = query_string + 'category like "%' + str(cat) + '%"'
        else:
            query_string = query_string + ' AND category like "%' + str(cat) + '%"'
        counter += 1
    if desc:
        if counter == 1:
            query_string = query_string + 'description like "%' + str(desc) + '%"'
        else:
            query_string = query_string + ' AND description like "%' + str(desc) + '%"'
        counter += 1
    # If all arguments are empty strings or null, then we do not want to include the word 'where' in the query string from earlier in
    # the method
    if counter == 1:
        query_string = '''SELECT * FROM (SELECT Items.itemid, name, currently, first_bid, buy_price, number_of_bids, started, ends, seller_userid, 
        description, group_concat(category) as Category FROM ITEMS INNER JOIN CATEGORIES ON ITEMS.itemid = CATEGORIES.itemid GROUP BY Items.itemid) as t1'''
    return query(query_string)

def auctionInfo(itemID):
    query_string1 = "select * from items where itemid = " + str(itemID)
    query_string2 = "select category from categories where itemid = " + str(itemID)
    query_string3 = "select * from bids where itemid = "  + str(itemID) + " order by time"

    return query(query_string1), query(query_string2), query(query_string3)

def placeBid(itemID, userID, price):
    query_string = "insert into bids (itemid, userid, amount, time) values (" + str(itemID) + ", '" + str(userID.strip()) + "', " + str(price) + ", '" + getTime() + "') "
    db.query(query_string)

