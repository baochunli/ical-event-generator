# A handy command-line utility for generating and sending iCalendar events

This simple command-line utility is designed to generate an iCalendar event, and sending it out as an email to the attendees.

## Why Do We Need This?

It is written out of my frustration that very few applications allowed me to very quickly generate a simple and clean iCalendar event file (`.ics`), which I can attach and email out to the attendees.

For example, I can try to produce such an event file in the Calendar app in macOS, but once I need to add a few attendees, the app will force me to send invitations out before I am allowed to save the event file. To make the process even more cumbersome, the attendees are required to be in the *Contacts* app, and the only way to save the event file in *Calendar* is to mail the event and then save the attachment.

As another example, while Google Calendar is able to construct the event and send an email message to the attendees, the `From` address of the invitation email is not configurable and must be a `gmail.com` address, and the content of the message is also not configurable.

## What Does the Utility Do?

Instead of using calendar applications such as Calendar and Microsoft Outlook, this utility generates a single event as an iCalendar file (`.ics`). Most information, including a summary (title) of the event, its location (multiple lines are allowed), its date and time, the names and email addresses of its attendees, can be entered when running this utility.

The name and email address of the organizer, the default timezone, as well as the number of minutes before the event when a default alarm will be displayed, can be read from a configuration file in YAML format. The default location for this configuration file is `ical.yml` in the same directory.

Once the iCalendar event file has been generated, the utility will send it out as an attachment automatically to all the attendees if needed. The subject of the outgoing email message is the same as the summary (title) of the event, and the content of the email message can be composed on-the-fly when prompted. In order to send an email using an existing mail server, the domain name, username, and password of the mail server need to be added to the configuration file (`ical.yml`).

*Note:* If you are trying to use certain mail servers (such as `gmail.com`) to send emails from Python, you may need to generate an app-specific password. For `gmail.com`, you may also need to [allow less secure apps](https://support.google.com/accounts/answer/6010255) in your account.

## Installing and Running the Utility

To install the dependencies in your Python environment, run:

```shell
pip install -r requirements.txt --upgrade
```

To upgrade Python packages in an existing Python environment, run:

```shell
python upgrade_packages.py
```

To run the utility:

```shell
python ical.py
```

Enjoy!