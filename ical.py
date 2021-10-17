"""
A simple but handy utility to generate an iCalendar event file, which can be emailed out to
attendees of the event by the organizer.

The name and email address of the organizer, the default timezone, as well as the number of
minutes before the event when a default alarm will be displayed, can be read from a
configuration file in YAML format. The default location for this configuration file is
`ical.yml` in the same directory.
"""
import os
import smtplib
import sys
import uuid
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart, MIMEBase

import pytz
import yaml
from icalendar import Alarm, Calendar, Event, vCalAddress, vDatetime, vText


def get_date(prompt: str, timezone: str) -> datetime:
    """ Obtains a date from user input. """
    date_str = input(f'Enter date of {prompt} (yy-mm-dd hh:mm): ')
    date = datetime.strptime(date_str, "%y-%m-%d %H:%M")

    print(f'The date you entered is: {date}')

    return date.replace(tzinfo=pytz.timezone(timezone))


def nonempty_input(prompt: str,
                   multi_line: bool = False,
                   confirm_on_empty: bool = True) -> str:
    """ Obtains a (usually) non-empty multi-line string from user input. """
    while True:
        if not multi_line:
            print(prompt)
        else:
            print(prompt + '(Ctrl-D (or Ctrl-Z on Windows) to end)')

        contents = ''
        line_count = 0
        while True:
            try:
                line = input()
            except EOFError:
                break

            if line_count != 0:
                contents += '\n'
            contents += line
            line_count += 1

            if not multi_line:
                break

        if contents == '' and confirm_on_empty:
            binary_response = input(
                'Your input is empty. Are you sure? (y/N): ')
            if binary_response == 'y':
                return contents
        else:
            return contents


def send_email(cal: Calendar,
               summary: str,
               config: dict,
               attendee_names: list,
               attendee_emails: list) -> None:
    """ Sending an email to each attendee, with 'invite.ics' as attachment. """
    # Build the email message and attach the event to it
    msg = MIMEMultipart()
    msg['Subject'] = summary
    msg['From'] = f"{config['organizer_name']} <{config['organizer_email']}>"
    attendees = []
    for name, email in zip(attendee_names, attendee_emails):
        attendees.append(f'{name} <{email}>')

    msg['To'] = ', '.join(attendees)
    print('Sending an email to: ' + msg['To'])

    msg_alternative = MIMEMultipart('alternative')
    msg.attach(msg_alternative)
    msg_alternative.attach(MIMEText(nonempty_input(
        'Please enter the body of your email message: ', multi_line=True) + '\n'))

    # Needed for Outlook to interpret the email correctly
    msg["Content-class"] = "urn:content-classes:calendarmessage"

    filename = 'invite.ics'

    if config['response_requested']:
        part = MIMEBase('text', "calendar", _charset='base64',
                        method="REQUEST", name=filename)
    else:
        part = MIMEBase('text', "calendar", _charset='base64',
                        method="PUBLISH", name=filename)
    part.set_payload(cal.to_ical())

    part.add_header('Content-Description', filename)
    part.add_header("Content-class", "urn:content-classes:calendarmessage")
    part.add_header("Filename", filename)
    part.add_header("Path", filename)
    msg.attach(part)

    # Sends the email out
    with smtplib.SMTP_SSL(config['mail_server'], port=465) as mailer:
        mailer.login(config['username'], config['password'])
        mailer.send_message(msg)
        print('Email message sent with the event invitation attached.')


def main() -> int:
    """ Generates an iCalendar event based on user input at the console. """

    print('Welcome to the iCalendar event generator.')

    # Reading from a configuration file
    if 'config_file' in os.environ:
        config_filename = os.environ['config_file']
    else:
        config_filename = './ical.yml'

    if os.path.isfile(config_filename):
        with open(config_filename, 'r', encoding='utf8') as config_file:
            config = yaml.load(config_file, Loader=yaml.SafeLoader)

        print('Current configuration: ')
        print(config)
    else:
        print('Unable to locate the configuration file.')
        return 0

    cal = Calendar()
    cal['prodid'] = '-//iCal-event-generator//github.com/baochunli//'
    cal['version'] = '2.0'

    # Are we requesting a response from the attendees?
    if config['response_requested']:
        cal['method'] = vText('REQUEST')
    else:
        cal['method'] = vText('PUBLISH')

    event = Event()
    event['uid'] = uuid.uuid1()

    # Summary of the event
    event['summary'] = vText(nonempty_input(
        'Please enter a summary for the event: '))

    # Start and end times of the event
    event['dtstart'] = vDatetime(get_date('event start', config['timezone']))
    event['dtend'] = vDatetime(get_date('event end', config['timezone']))

    # Location of the event
    event['location'] = vText(nonempty_input(
        'Please enter a location for the event: ', multi_line=True))

    # Organizer of the event
    organizer = vCalAddress('MAILTO:' + config['organizer_email'])
    organizer.params['cn'] = vText(config['organizer_name'])
    organizer.params['role'] = vText('CHAIR')
    event['organizer'] = organizer

    # Attendees of the event (optional)
    print("Now enter a list of attendees.")
    attendee_names = []
    attendee_emails = []

    while True:
        attendee_email = nonempty_input(
            "Please enter an email address (enter return to end): ", confirm_on_empty=False)
        if attendee_email == '':
            break

        attendee = vCalAddress('MAILTO:' + attendee_email)
        attendee_emails.append(attendee_email)
        attendee_name = nonempty_input('Please enter a name: ')
        attendee.params['cn'] = vText(attendee_name)
        attendee_names.append(attendee_name)
        print('Attendees so far:')
        print(attendee_names)
        print(attendee_emails)

        attendee.params['CUTYPE'] = vText('INDIVIDUAL')
        attendee.params['ROLE'] = vText('REQ-PARTICIPANT')

        if config['response_requested']:
            attendee.params['PARTSTAT'] = vText('NEEDS-ACTION')
            attendee.params['RSVP'] = vText('TRUE')
        else:
            attendee.params['PARTSTAT'] = vText('ACCEPTED')
            attendee.params['RSVP'] = vText('FALSE')

        event.add('attendee', attendee, encode=0)

    # Recurring event
    binary_response = input('Is the event recurring? (y/N): ')
    if binary_response == 'y':
        freq_terms = ['DAILY', 'WEEKLY', 'MONTHLY', 'YEARLY']
        frequency = int(input(
            'Frequency (daily = 0, weekly = 1, monthly = 2, yearly = 3): '))
        assert frequency >= 0 and frequency <= 3
        until = get_date('end of recurring event', config['timezone'])

        event.add('rrule', {'FREQ': freq_terms[frequency], 'UNTIL': until})

    description = input('Please enter a note (optional): ')
    if description != '':
        event.add('description', description)

    # adds an alarm minutes before the event
    alarm = Alarm()
    alarm.add('trigger', timedelta(
        minutes=-1 * config['alarm_before_event']))
    alarm.add('action', 'DISPLAY')
    desc = f"{event['summary']} starts in {config['alarm_before_event']} minutes"
    alarm.add('description', desc)
    event.add_component(alarm)

    # Highest priority assigned to this event
    event.add('priority', 1)

    # Adds a creation timestamp
    timezone = pytz.timezone(config['timezone'])
    event.add('created', timezone.localize(datetime.now()))

    cal.add_component(event)

    with open(os.path.join('.', 'invite.ics'), 'wb') as ics_file:
        ics_file.write(cal.to_ical())

    print("This event has been saved to the file 'event.ics'.")

    if attendee_emails:
        binary_response = input(
            'Would you like to send emails to the attendees? (y/N): ')
        if binary_response == 'y':
            # Sending an email to the attendees
            send_email(cal, event['summary'], config,
                       attendee_names, attendee_emails)

    return 0


if __name__ == '__main__':
    sys.exit(main())
