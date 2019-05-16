#!/usr/bin/env python

import sys; sys.path.insert(0, 'lib') # this line is necessary for the rest
import os                             # of the imports to work!

import web
import sqlitedb
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

###########################################################################################
##########################DO NOT CHANGE ANYTHING ABOVE THIS LINE!##########################
###########################################################################################

######################BEGIN HELPER METHODS######################

# helper method to convert times from database (which will return a string)
# into datetime objects. This will allow you to compare times correctly (using
# ==, !=, <, >, etc.) instead of lexicographically as strings.

# Sample use:
# current_time = string_to_time(sqlitedb.getTime())

def string_to_time(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

# helper method to render a template in the templates/ directory
#
# `template_name': name of template file to render
#
# `**context': a dictionary of variable names mapped to values
# that is passed to Jinja2's templating engine
#
# See curr_time's `GET' method for sample usage
#
# WARNING: DO NOT CHANGE THIS METHOD
def render_template(template_name, **context):
    extensions = context.pop('extensions', [])
    globals = context.pop('globals', {})

    jinja_env = Environment(autoescape=True,
            loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
            extensions=extensions,
            )
    jinja_env.globals.update(globals)

    web.header('Content-Type','text/html; charset=utf-8', unique=True)

    return jinja_env.get_template(template_name).render(context)

#####################END HELPER METHODS#####################

urls = ('/', 'AuctionBase_main',
        '/currtime', 'curr_time',
        '/selecttime', 'select_time',
        '/search', 'search_items',
        '/auctioninfo', 'auction_info',
        '/addbid','add_bid'
        )

class curr_time:
    # A simple GET request, to '/currtime'
    #
    # Notice that we pass in `current_time' to our `render_template' call
    # in order to have its value displayed on the web page
    def GET(self):
        current_time = sqlitedb.getTime()
        return render_template('curr_time.html', time = current_time)

class select_time:
    # Aanother GET request, this time to the URL '/selecttime'
    def GET(self):
        return render_template('select_time.html')

    # A POST request
    #
    # You can fetch the parameters passed to the URL
    # by calling `web.input()' for **both** POST requests
    # and GET requests
    def POST(self):
        post_params = web.input()
        MM = post_params['MM']
        dd = post_params['dd']
        yyyy = post_params['yyyy']
        HH = post_params['HH']
        mm = post_params['mm']
        ss = post_params['ss']
        enter_name = post_params['entername']


        selected_time = '%s-%s-%s %s:%s:%s' % (yyyy, MM, dd, HH, mm, ss)
        update_message = '(Hello, %s. Previously selected time was: %s.)' % (enter_name, selected_time)
        # TODO: save the selected time as the current time in the database
        cTime = sqlitedb.getTime()
        update_message = sqlitedb.setTime(selected_time, cTime, update_message)

        # Here, we assign `update_message' to `message', which means
        # we'll refer to it in our template as `message'
        return render_template('select_time.html', message = update_message)
    
class search_items:
    #Get request for the webpage to '/search'
    def GET(self):
        return render_template('search.html')

    def POST(self):
        #get params
        post_params = web.input()
        itemID = post_params['itemID']
        userID = post_params['userID']
        minPrice = post_params['minPrice']
        maxPrice = post_params['maxPrice']
        status = post_params['status']
        cat = post_params['cat']
        desc = post_params['desc']

        currTime = sqlitedb.getTime()

        #begin transaction
        t = sqlitedb.transaction()
        search_result = []
        err = ""
        try:
            search_result = sqlitedb.searchResults(itemID, userID, minPrice, maxPrice, status, cat, desc, currTime)
        except Exception as e:
            t.rollback()
            err = "Database Constraints Violated"
        else:
            t.commit()

        return render_template('search.html', err = err, search_result = search_result)

class auction_info:
    def GET(self):
        post_params = web.input()
        if bool(post_params):
            itemID = post_params['ItemID']

            t = sqlitedb.transaction()
            err = ""
            search_result1=[]
            search_result2=[]
            search_result3=[]
            #wait for kevins code:
            try:
                search_result1, search_result2, search_result3 = sqlitedb.auctionInfo(itemID)
            except:
                t.rollback()
                err = "error with getting auction information" 
            else:
                t.commit()
            
            return render_template('auction_info.html', sr1 = search_result1, sr2 = search_result2, sr3 = search_result3,
            cTime = sqlitedb.getTime())
        else:
            return render_template('auction_info.html')

            
    def POST(self):
        post_params = web.input()
        itemID = post_params['itemID']

        t = sqlitedb.transaction()
        err = ""
        search_result1=[]
        search_result2=[]
        search_result3=[]
         #wait for kevins code:
        try:
             search_result1, search_result2, search_result3 = sqlitedb.auctionInfo(itemID)
        except:
            t.rollback()
            err = "error with getting auction information" 
        else:
            t.commit()
        
        return render_template('auction_info.html', sr1 = search_result1, sr2 = search_result2, sr3 = search_result3,
        cTime = sqlitedb.getTime())

class add_bid:
    def GET(self):
        return render_template('add_bid.html')
    def POST(self):
        post_params = web.input()
        itemID = post_params['itemID']
        userID = post_params['userID']
        price = post_params['price']
        add_result = False

        t = sqlitedb.transaction()
        err = ""
    
        try:
            sqlitedb.placeBid(itemID, userID, price) 

        except Exception as e:
            t.rollback()
            err = unicode(e.message, "utf8")
        else:
            try:
                t.commit()
            except Exception as e:
                err = err = unicode(e.message, "utf8")
            else:
                add_result = True

        return render_template('add_bid.html', add_result = add_result, err1= err)


class AuctionBase_main:
    def GET(self):
        return render_template('main_page.html')
    
        

###########################################################################################
##########################DO NOT CHANGE ANYTHING BELOW THIS LINE!##########################
###########################################################################################

if __name__ == '__main__':
    web.internalerror = web.debugerror
    app = web.application(urls, globals())
    app.add_processor(web.loadhook(sqlitedb.enforceForeignKey))
    app.run()
