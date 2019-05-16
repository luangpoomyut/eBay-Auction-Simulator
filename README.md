# eBay-Auction-Simulator

This web application simulates the auctioning system of the well-known eBay site in static time (snapshots).

## Design

*Front End*\
The front end is designed with HTML, CSS, Bootstrap, and the Jinja2 framework.

*Back End*\
The back end built on the web.py framework and SQLite.

## Setup

To set this up on your own local computer, first run the shell script, runParser.sh, followed by running createDatabase.sh.

Then move the AuctionBase.db binary file to the web.py directory. You then run auctionbase.py and it should be set up!

## Design Considerations

The constraints.txt file in the create_auctionbase directory details the triggers added to the database to protect integrity of the data added or altered.
