"""
A simple but handy utility to generate an iCalendar event
file, which can be emailed out to attendees of the event by
the organizer.

The name and email address of the organizer, the default
timezone, as well as the number of minutes before the event
when a default alarm will be displayed, can be read from a
configuration file in YAML format. The default location for
this configuration file is `ical.yml` in the same directory.
"""
import os
import sys
import uuid
from datetime import datetime, timedelta
import yaml

import pytz
from icalendar import Calendar, Event, Alarm, vCalAddress, vDatetime, vText


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


def main() -> int:
    """ Generates an iCalendar event based on user input at the console. """

    # Reading from a configuration file
    if 'config_file' in os.environ:
        config_filename = os.environ['config_file']
    else:
        config_filename = './ical.yml'

    if os.path.isfile(config_filename):
        with open(config_filename, 'r', encoding='utf8') as config_file:
            config = yaml.load(config_file, Loader=yaml.SafeLoader)

        print(config)
    else:
        print('Unable to locate the configuration file.')
        return 0

    cal = Calendar()
    event = Event()
    event['uid'] = uuid.uuid1()

    print('Welcome to the iCalendar event generator.')

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
    while True:
        attendee_email = nonempty_input(
            "Please enter an email address (enter return to end): ", confirm_on_empty=False)
        if attendee_email == '':
            break

        attendee = vCalAddress('MAILTO:' + attendee_email)
        attendee.params['cn'] = vText(nonempty_input('Please enter a name: '))
        attendee.params['ROLE'] = vText('REQ-PARTICIPANT')
        event.add('attendee', attendee, encode=0)

    # Highest priority assigned to this event
    event.add('priority', 1)

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

    cal.add_component(event)

    with open(os.path.join('.', 'event.ics'), 'wb') as ics_file:
        ics_file.write(cal.to_ical())

    print("This event has been saved to the file 'event.ics'.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
