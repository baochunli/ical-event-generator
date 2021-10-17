# A handy command-line utility for generating iCalendar events

This simple command-line utility is designed to generate an iCalendar event file, which can be emailed out to attendees of the event by the organizer.

It is written out of my frustration that very few applications allowed me to very quickly generate a simple and clean iCalendar event file (`.ics`), which I can attach and email out to the attendees. For example, I can try to produce such an event file in the Calendar app in macOS, but once I need to add a few attendees, the app will force me to send invitations out before I am allowed to save the event file. To make the process even more cumbersome, the only way to save the event file in *Calendar* is to mail the event and then save the attachment.

Instead of using calendar applications such as Calendar and Microsoft Outlook, this utility generates a single event as a iCalendar file (`.ics`). Most information, including a summary (title) of the event, its location (multiple lines are allowed), its date and time, the names and email addresses of its attendees, and its 

The name and email address of the organizer, the default timezone, as well as the number of minutes before the event when a default alarm will be displayed, can be read from a configuration file in YAML format. The default location for this configuration file is `ical.yml` in the same directory.

To install the dependencies in your Python environment, run:

```shell
pip install -r requirements.txt --upgrade
```

To run the utility:

```shell
python ical.py
```

Once the iCalendar event file has been generated, it can be emailed out to the attendees using any mail client.

Enjoy!