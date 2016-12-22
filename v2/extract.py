"""
Extract a CSV file from the HTML of the RUSA perms table.

Basically the parsing part of the 'regen.py' script from
Oregon Randonneurs, leaving out the part that sucks the
HTML down (which can be done with the unix program 'curl' instead. 
"""

from html.parser import HTMLParser
import datetime
import logging
logging.basicConfig(level=logging.INFO)
import csv
import schemata   # Layout of our CSV files; note some of this is hard-wired in code

class Parser(HTMLParser):

    def __init__(self, csvwriter):
        self.row = [ ]
        self.in_row = False
        self.col_text = ""
        self.href = ""
        self.csvwriter = csvwriter
        HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        """
        Start tag --- the ones we care about are "tr"  (starting a table row),
        "td" (starting a column in the table), and "a"  (hyperlink).
        """
        logging.debug("Start tag {}".format(tag))
        if tag=="tr":          # Table row, but we don't know if it's the right table
            self.row = [ ]     # We'll gather up the columns in case, and test later
            self.in_row = True
            self.href = ""
            logging.debug("Entering table row")
        elif tag=="td":        # Within each column, we gather up text
            self.col_text = ""
            logging.debug("Entering column")
        elif tag=="a":         # Links could be to RUSA permanent records
            self.href = attrs[0][1]

    def handle_data(self, data):
        """
        If we are in a row, we gather up any text encountered to go in the
        columns.  col_data is initialized to "" at "tr" tag, start of column,
        and stored into the rows variable at matching "/tr" end-tag.
        """
        if self.in_row:
            self.col_text += data

    def handle_endtag(self, tag):
        """
        At end of column (/td), place gathered text into next element of row.
        At end of row, only if it looks like one of the permanent records we
        are snarfing, process the whole row and transform into the data we
        want.
        """
        logging.debug("End tag {}".format(tag))
        if tag=="td":
            self.row.append(self.col_text)
            self.col_text = ""
        if tag=="tr":
            logging.debug("Exiting row with values {}".format(self.row))
            if len(self.row) >= 8:
                states = self.row[7]
            else:
                states = ""
            if len(self.row) > 0 :
                logging.debug("Emitting")
                self.emit(self.row, self.href)
            else:
                logging.debug("Not emitting row: {}".format(self.row))
            self.in_row = False
            self.row = [ ]

    def emit(self, row, href):
        """
        Here is where we isolate knowledge of what we want the output
        to look like, as well as order of columns in the original.
        """
        if len(row) != 8:
            logging.warning("Encountered bad row: {}".format(row))
        assert(len(row) >= 8) ## Or else I've made a bad assumption about input
        perm_loc, perm_fr, perm_km, perm_climb, perm_super, perm_name, \
                  perm_owner, perm_states = row
        logging.debug(("Decoding columns as loc: " +
                      "{loc}, km: {km}, climb: {climb}, super: {super}, " +
                      "name: {name}, owner: {owner}, states: {states}," +
                      " free-route: {free}").format(
                          loc=perm_loc, free=perm_fr, km=perm_km,
                          climb=perm_climb,  super=perm_super,
                          name=perm_name, owner=perm_owner, states=perm_states))

        # We are seeing \xA0 in some empty fields, including climbing feet
        # and owner.  Repair those here: 
        if not perm_climb.isdecimal():
            perm_climb=" "
        if not perm_owner.isprintable():
            perm_owner="Unassigned"


        # A couple of less common options show up in 'Notes' to make the
        # table more readable
        perm_notes = ""
        if perm_fr == "yes":
            perm_notes += "Free-Route "
        if perm_super == "yes":
            perm_notes += "Super Randonn&eacute;e"


        href= "http://www.rusa.org" + href
        state, city = perm_loc.split(": ")
        row = [ state, city, perm_km, perm_climb, href, perm_name,
                perm_owner, perm_notes, perm_states ]
        
        # produce_line(row, file=self.destfile)
        self.csvwriter.writerow(row)


if __name__ == "__main__":
    import sys
    import argparse
    parser = argparse.ArgumentParser(description="Extract CSV from RUSA perms table.")
    parser.add_argument('infile', nargs='?',
                        type=argparse.FileType('r', encoding="utf-8", errors="replace"),
                        default=sys.stdin)
    parser.add_argument('outfile', nargs='?', help="CSV file output goes here",
                        type=argparse.FileType('w'), default=sys.stdout)
    args = parser.parse_args()
    writer = csv.writer(args.outfile)
    writer.writerow(schemata.rusa_snarf)
    raw = ""
    logging.info("Building raw input string")
    for line in args.infile:
        raw += line
    logging.info("Done building raw input, about to parse")
    html_parser = Parser(writer)
    logging.info("Built parser object; about to launch it")
    html_parser.feed(raw)
    html_parser.close()


                



