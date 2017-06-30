# StubHub Ticket Search GUI

A browser-based GUI for downloading and searching through concert tickets from the StubHub online ticket marketplace.


This program does 3 things:

1. Given a StubHub URL that lists events, download each event page's HTML (which contains ticket data for that event).
2. Parse each event's HTML to obtain ticket data.
3. Present all the ticket data in a browser-based GUI. You use this GUI to search the ticket data to find good tickets.

![alt txt](Images/browsergui-ticket-search.png)

Notes:

- This project requires the excellent lightweight browser-based GUI framework `browsergui`. Install with 
    - `easy_install browsergui`
    - or
    - `pip3 install browsergui`

- Running `main.py` will show you the GUI running with some example ticket data.

