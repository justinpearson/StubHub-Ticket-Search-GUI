#!/usr/bin/env python3

# StubHub Powersearch: A browser-based GUI for searching concert tickets from the StubHub online ticket marketplace.

# This program does 3 things:
#
# 1. Given a StubHub URL that lists events, download each event page's HTML (which contains ticket data for that event).
# 2. Parse each event's HTML to obtain ticket data.
# 3. Present all the ticket data in a browser-based GUI. You use this GUI to search the ticket data to find good tickets.


########################################
# USER-DEFINED VARIABLES: FILL THESE IN

# StubHub URL that lists events:
# For example, here is a StubHub page that lists the 16 showings 
# for the 'Book Of Mormon' musical in San Jose, CA in July 2017:
all_events_url = 'https://www.stubhub.com/the-book-of-mormon-san-jose-tickets/performer/1496118/'
#
# Here is a listing of showings in Los Angeles, CA:
# all_events_url = 'https://www.stubhub.com/the-book-of-mormon-los-angeles-tickets/performer/711295/'
#
# There is a sample index file saved in  
# Example-Data/Book-of-Mormon-San-Jose-2017/index-file/


# Existing directory each event page's HTML will be saved
html_dir = 'Example-Data/Book-of-Mormon-San-Jose-2017/HTML-events/'
# html_dir = 'you-try'  

# Save ticket data here
ticket_data_file = 'Example-Data/Book-of-Mormon-San-Jose-2017/tickets.pickle'
# ticket_data_file = 'you-try/tickets.pickle'  

# Pic of theater to show in GUI
theater_pic = 'Example-Data/Book-of-Mormon-San-Jose-2017/san-jose-theater.png'

# END USER-DEFINED VARIABLES
########################################





import os

have_tix_data       = os.path.exists(ticket_data_file)
have_event_htmls    = len([f for f in os.listdir(html_dir) if f.lower().endswith('html')]) > 0

import sys

assert sys.version_info >= (3,6), "Python version <3.6 detected; I dev'd this on my python 3.6 distro, so you may need to eg replace strings like f'Value: \{i\}' ."

try:
    import browsergui
    del browsergui
except ImportError:
    print('''
        This program uses the 'browsergui' lightweight browser-based GUI framework.
        Please install browsergui: 'pip install browsergui' or 'easy_install browsergui'
        More info: https://github.com/speezepearson/browsergui
        ''')
    sys.exit(1)






if have_event_htmls:
    print("Don't need to download each events' HTML, good.")
else:

    print('''
    ##################################################################
    # PART 1/3: Download the 'index' page that lists all event pages.
    ##################################################################
    ''')

    import time, os, sys
    from selenium import webdriver
    from selenium.common.exceptions import WebDriverException
    from bs4 import BeautifulSoup


    print('Firing up Firefox...')
    driver = webdriver.Firefox()
    driver.implicitly_wait(30)
    driver.set_page_load_timeout(30)
    # driver.manage().timeouts().pageLoadTimeout(10, TimeUnit.SECONDS); # only java selenium has this?

    def get_src(url): 
        ## retrieve page with selenium
        print('getting page...')
        driver.get(url)
        print('allegedly done.')

        # Hm: StubHub page isn't actually fully loaded yet. Wait.
        print('sleeping for 10s anyway...')
        time.sleep(10)
        print('done.')

        src = driver.page_source
        return src


    print('''
    # --------------------------------------------------------
    # Download the 'index' page that lists all event pages...
    # --------------------------------------------------------
    ''')


    if all_events_url is not None:
        src = get_src(all_events_url)
    else:
        fn = os.path.join(  'Example-Data',
                            'Book-of-Mormon-San-Jose-2017',
                            'index-file',
                            'The Book of Mormon San Jose Tickets - The Book of Mormon San Jose Tickets - StubHub.html')
        print(f"Index URL variable 'all_events_url' not defined, using {fn}")
        src = open(fn,"r",encoding="utf-8").read()

    soup = BeautifulSoup(src,"html.parser")


    print('''
    # --------------------------------------------------------
    # Search index page for links to all event pages...
    # --------------------------------------------------------
    ''')


    [x.decompose() for x in soup.find_all('div',{'id':'component-recommended-events'})]
    event_div = soup.find_all('div',{'class':'events'})
    assert not(len(event_div) < 1), "Um, couldn't find any divs with class 'event', perhaps webdriver isn't allowing JS?"
    assert not(len(event_div) > 1), "Um, found more than one div with 'events' class, will create ambiguity. Use e['class'] to find classes with which to differentiate."
    events = event_div[0].find_all('div',{'class': 'event'})

    urls = []
    for e in events:
        mylink = e.find('a',{'class':'event-link'})
        url = mylink['href']
        if not url.startswith('http'):
            if url.startswith('//'):
                # simple fix:
                url = 'https:' + url
            else:
                assert False, "Hey, url doesn't start right: " + url
        urls.append(url)

    print('Found {} event URLs:'.format(len(urls)))
    print(urls)

    print('''
    # --------------------------------------------------------
    # Retrieve event pages with Selenium and save HTML...
    # --------------------------------------------------------
    ''')

    for i,url in enumerate(urls):
        src = get_src(url)
        fn = os.path.join(html_dir, str(i)+'.html')
        open(fn,'w').write(src)

    print('Done. Closing Selenium / Firefox...')
    driver.quit()



if have_tix_data:
    print("Don't need to parse events' HTML into ticket data, good.")
else:

    print('''
    ################################################
    # PART 2/3: Extract tickets from saved HTML
    ################################################
    ''')



    import time, os, sys, itertools, re, string
    from bs4 import BeautifulSoup
    import pickle


    files = [os.path.join(html_dir,x) for x in os.listdir(html_dir) if x.endswith('.html')]
    print('Gonna parse these saved HTML files:')
    print(files)

    def file_to_rough_ticket(fn):

        print("File:",fn)

        html = open(fn,"r",encoding="utf-8").read()
        soup = BeautifulSoup(html,"html.parser")

        # <title>The Book Of Mormon San Jose [07/19/2017] 07 PM Tickets on StubHub!</title>
        date = soup.title.text.split('Ticket')[0].split('[')[1].replace(']','').strip()  # '07/19/2017 07 PM'
        event = soup.title.text.split('[')[0].strip()  # 'The Book Of Mormon San Jose'

        # Debugging:
        # Remove script tags for printing html cleanly
        # [x.extract() for x in soup.findAll('script')]
        # print(soup.prettify())   # print html
        # print(soup.get_text(separator="\n"))  # print text

        ticket_html = soup.find_all("div",{"class": "ticket-item"})

        print('Found {} tickets'.format(len(ticket_html)))

        classes = [ 'sectioncell',
                    'dollar-value',
                    'rowcell',
                    'deliverymethod',
                    'seatNumbers',
                    'quantity',
                    'qtyText',
                    'ticketsText' ]

        for htm in ticket_html:
            # print(htm.prettify())  # debugging
            t = { c : [x.text for x in htm.select('.'+c)] for c in classes}
            t['file'] = fn
            t['date'] = date
            t['event'] = event

        return t


    tix_rough = [file_to_rough_ticket(f) for f in files]


    print('''
    #------------------------------------------
    # Clean up ticket data: "$100" => 100,  "1-3 tickets" => [1,2,3], etc
    #------------------------------------------
    ''')

    def qty2range(s):
        #  ['1 ticket']    => [1]
        #  ['1-3 tickets'] => [1,2,3]
        #  ['3 tickets']   => [3]
        #  []              => []
        q = [int(x) for x in re.findall(r'\d+',s)]
        if len(q)<=1:
            return q
        else:
            return list(range(q[0],q[1]+1))


    def col2num(col):
        # https://stackoverflow.com/questions/7261936/convert-an-excel-or-spreadsheet-column-letter-to-its-number-in-pythonic-fashion
        # col2num('A') = 1
        # col2num('Z') = 26
        # col2num('AA') = 27
        # col2num('AB') = 28
        # col2num('ZZ') = 702
        num = 0
        for c in col:
            if c in string.ascii_letters:
                num = num * 26 + (ord(c.upper()) - ord('A')) + 1
        return num

    def rough2dict(t):

        d = {   'event': t['event'],
                'date': t['date'],
                'section': t['sectioncell'][0], 
                'price': float(t['dollar-value'][0].replace('$','')),
                'delivery': t['deliverymethod'],
                'seats': list(map(int,re.findall(r'\d+',t['seatNumbers'][0]))) ,
                'quantity': qty2range(t['ticketsText'][0])
            }

        # Convert row num from 'A', 'AA', 'AB', to number.
        s = t['rowcell'][0]
        d['row'] = 9999
        if len(s) > 0 and s.isdigit():
            d['row'] = int(s)
        if len(s) > 0 and s.isalpha():
            d['row'] = col2num(s)

        return d


    tix = [ rough2dict(t) for t in tix_rough ]

    pickle.dump(tix,open(ticket_data_file,'wb'))

    print(f'Saved ticket data to {ticket_data_file}.')



print('''
##################################################
# PART 3/3: Display ticket data in browser-based GUI
##################################################
''')

import sys, pickle, copy
from browsergui import *
from math import inf, floor, ceil
from MinMaxSliderBlock import MinMaxSliderBlock
from ToggleableButton import ToggleableButton





class TicketSearcher(object):
    def __init__(self, picklefile):
        self.picklefile = picklefile
        tix = pickle.load(open(picklefile,'rb'))
        # tix = tix[:20] # !!!!!!!!!!!!!!!!!!!!!!!!!!! limit initially
        # print(tix)
        self.tix = tix
        self.NUM_TIX = len(tix)
        print(f'Loaded {self.NUM_TIX} tickets from {picklefile}.')
        # Data-checking
        assert self.NUM_TIX > 0, "No tickets in pickle??"
        assert all( t.keys() == tix[0].keys() for t in tix ), 'Not all ticket dicts have same keys??'

        self.TICKET_PROPS = tix[0].keys()
        self.MIN_PRICE    = int(min(t['price'] for t in self.tix))
        self.MAX_PRICE    = int(max(t['price'] for t in self.tix))
        self.MIN_ROW      = int(min(t['row']   for t in self.tix))
        self.MAX_ROW      = int(max(t['row']   for t in self.tix))
        self.MIN_SEAT     = int(min(s for t in self.tix for s in t['seats']    if len(t)>0))
        self.MAX_SEAT     = int(max(s for t in self.tix for s in t['seats']    if len(t)>0))
        self.MIN_QTY      = int(min(q for t in self.tix for q in t['quantity'] if len(t)>0))
        self.MAX_QTY      = int(max(q for t in self.tix for q in t['quantity'] if len(t)>0))

        self.SECTIONS = set(t['section'] for t in self.tix)
        self.DELIVERY_METHODS = set(dm for t in self.tix for dm in t['delivery'])

    def search(self, min_price=0,   max_price=inf, 
                     min_row=0,     max_row=inf,
                     min_seat=0,    max_seat=inf,
                     min_qty=0,     max_qty=inf,
                     desired_sections=None,
                     desired_delivery_methods=None,
                     desire_known_seats=False
                     ):

        if desired_sections is None:
            desired_sections = self.SECTIONS

        if desired_delivery_methods is None:
            desired_delivery_methods = self.DELIVERY_METHODS

        results = [t for t in self.tix if 
            min_price <= t['price'] <= max_price
            and
            min_row <= t['row'] <= max_row
            and 
            all( min_seat <= seat <= max_seat for seat in t['seats'] )
            and
            all( qty in t['quantity'] for qty in range(floor(min_qty),ceil(max_qty)+1) )
            and
            t['section'] in desired_sections
            and
            any(dm in desired_delivery_methods for dm in t['delivery'])
            ]

        if desire_known_seats:
            results = [t for t in results if len(t['seats'])>0 ]

        return results
        


class SearchGUI(GUI):

    def __init__(self, picklename, imgname=None):
        super(SearchGUI, self).__init__()
        self.searcher = TicketSearcher(picklename)
        self.header = list(map(EmphasizedText,self.searcher.TICKET_PROPS))

        self.desired_sections = copy.copy(self.searcher.SECTIONS)
        self.desired_delivery_methods = copy.copy(self.searcher.DELIVERY_METHODS)
        self.desire_known_seats = set(['req precise seats']) # sort of a hack w/ how we do our buttons

        # Make sliders & buttons
        self.price_slider = MinMaxSliderBlock(name='Price',  MIN=self.searcher.MIN_PRICE,  MAX=self.searcher.MAX_PRICE,  callback=self.redraw)
        self.row_slider   = MinMaxSliderBlock(name='Row',    MIN=self.searcher.MIN_ROW,    MAX=self.searcher.MAX_ROW,    callback=self.redraw)
        self.seat_slider  = MinMaxSliderBlock(name='Seat',   MIN=self.searcher.MIN_SEAT,   MAX=self.searcher.MAX_SEAT,   callback=self.redraw)
        self.qty_slider   = MinMaxSliderBlock(name='Qty',    MIN=self.searcher.MIN_QTY,    MAX=self.searcher.MAX_QTY,    callback=self.redraw, min_init_value=2,max_init_value=2 )

        self.section_buttons         = [ToggleableButton(name=prop,pressed=True,callback=self.redraw) for prop in self.searcher.SECTIONS]
        self.delivery_method_buttons = [ToggleableButton(name=prop,pressed=True,callback=self.redraw) for prop in self.searcher.DELIVERY_METHODS]
        self.known_seats_button      =  ToggleableButton(name='known seats?',pressed=False,callback=self.redraw)

        # Layout

        if imgname is not None:
            self.body.append(Image(imgname))

        self.body.append(Container(
                            self.price_slider.get_Element(),
                            self.row_slider.get_Element(),
                            self.seat_slider.get_Element(),
                            self.qty_slider.get_Element())
                        )
        self.body.append(Grid([
                            [b.get_Element() for b in self.section_buttons],
                            [b.get_Element() for b in self.delivery_method_buttons],
                            [self.known_seats_button.get_Element()]
                            ])
                        )
        # Note: Spence says an element e's parent is redrawn when e changes. 
        # So don't have 'body' be the parent of 'results' grid. Instead, wrap in Container.
        # That way, the entire body won't redraw every time new results are computed.
        # This avoids an annoying bug where sliders don't slide.
        self.body.append(Container(Grid([[]])))
        
        self.redraw()

    def redraw(self):
        query = {   'min_price': self.price_slider.get_min(),
                    'max_price': self.price_slider.get_max(), 
                    'min_row': self.row_slider.get_min(), 
                    'max_row': self.row_slider.get_max(),
                    'min_seat': self.seat_slider.get_min(), 
                    'max_seat': self.seat_slider.get_max(),
                    'min_qty': self.qty_slider.get_min(), 
                    'max_qty': self.qty_slider.get_max(),
                    'desired_sections': [b.name for b in self.section_buttons if b.pressed],
                    'desired_delivery_methods': [b.name for b in self.delivery_method_buttons if b.pressed],
                    'desire_known_seats': self.known_seats_button.pressed
                }
        results = self.searcher.search(**query)
        results.sort(key=lambda t: t['price'])
        text_results = [[Text(str(v)) for v in t.values()] for t in results]
        for row in text_results:
            for e in row:
                e.css['padding']='5px'

        g=Grid([
                [Text(f'Search results: {len(results)} tickets:')],
                [Grid([self.header,*text_results],
                    n_rows=len(results)+1, 
                    n_columns=len(self.header)
                    )]
            ])

        result_container = self.body[-1] 
        result_container.pop() 
        result_container.append(g)


SearchGUI(ticket_data_file, theater_pic).run()