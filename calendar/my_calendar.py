from icalendar import Calendar
import datetime
import pytz
from dateutil import tz
import subprocess
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import argparse
from dotenv import load_dotenv
import logging
import logging.config
import html

def sanitize_text(text):
    """Sanitize user input or ICS text for safe HTML rendering."""
    if not text:
        return ""

    # Escape special HTML characters
    safe_text = html.escape(text)

    # Replace newlines with <br> for HTML emails
    safe_text = safe_text.replace("\n", "<br>")

    return safe_text

# We have two versions of the logging configuration.  The default only
# writes to the log, while the verbose version will echo to the console.
# Initial configuration
config = {
    'version': 1,
    'formatters': {
        'simple': {'format': '%(asctime)s - %(levelname)s - %(message)s'}
    },
    'handlers': {
        'console': {
            'class': 'logging.FileHandler',
            'formatter': 'simple',
            'filename': 'calendar.log',
            'level': logging.DEBUG
        }
    },
    'root': {'handlers': ['console'], 'level': logging.DEBUG}
}
logging.config.dictConfig(config)

# Runtime reconfiguration
verbose_config = {
    'version': 1,
    'formatters': {
        'simple': {'format': '%(asctime)s - %(levelname)s - %(message)s'},
        'default': {'format': '%(levelname)s: %(message)s'}  # Added missing formatter
    },
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'runtime.log',
            'formatter': 'simple',
            'level': 'INFO'
        },
        'stdout': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
    },
    'root': {'handlers': ['file', 'stdout'], 'level': 'DEBUG'}  # Include both handlers
}

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='calendar.log',
    filemode='a'
)

def send_email(distro_file, subject, html_file):
    '''
    Compose and send email to the distrobution list.

    Parameters:
    distro_file: File path to text file containing the distribution list
    subject: Subject for the email
    html_file: File path to html file to be included in the body of the email
    '''
    SMTP_SERVER = "smtp.mail.yahoo.com"
    SMTP_PORT = 587
    EMAIL_FROM = "rlynch3456@yahoo.com"

    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    if SMTP_PASSWORD == None:
        logging.error("Error accessing nonexistent variable directly: SMTP_PASSWORD")
        return False

    SMTP_USERNAME = os.getenv("SMTP_USERNAME")
    if SMTP_PASSWORD == None:
        logging.error("Error accessing nonexistent variable directly: SMTP_USERNAME")
        return False

    distro = []
    # get the distro list
    try:
        with open(distro_file, "r") as file:
            for line in file:
                # Check for a commented line
                if line.find('#') == -1:
                    distro.append(line.strip())
    except FileNotFoundError:
        logging.error(f'{distro_file} not found')
        return False

    try:
        with open(html_file, "r") as f:
            html_content = f.read()
    except FileNotFoundError:
        logging.error(f'{html_file} not found')
        return False

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_FROM
    msg['Bcc'] = ", ".join(distro)
    html_part = MIMEText(html_content, 'html')
    msg.attach(html_part)
    debuglevel = True
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.set_debuglevel(debuglevel)
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(EMAIL_FROM, distro, msg.as_string())
            server.quit()
            logging.info(f"Email sent to {msg['To']}")
            logging.info(f"Email sent bcc to {msg['Bcc']}")

    except smtplib.SMTPException as e:
        logging.error(f"SMTP error occurred: {e}")

    return True

def download_ics(ics_download):
    '''
    Download ICS file from Synology Calendar.'

    Parameters:
    ics_download: Filename for the download.

    Return:
    True if file was downloaded, otherwise False.
    '''

    ICS_URL = os.getenv("ICS_URL")
    if ICS_URL == None:
        logging.error("Error accessing nonexistent variable directly: ICS_URL")
        return False

    CALENDAR_PASSWORD = os.getenv("CALENDAR_PASSWORD")
    if CALENDAR_PASSWORD == None:
        logging.error("Error accessing nonexistent variable directly: CALENDAR_PASSWORD")
        return False

    CALENDAR_USERNAME = os.getenv("CALENDAR_USERNAME")
    if CALENDAR_USERNAME == None:
        logging.error("Error accessing nonexistent variable directly: CALENDAR_USERNAME")
        return False

    command_string = f"curl -u {CALENDAR_USERNAME}:{CALENDAR_PASSWORD} {ICS_URL} -o {ics_download} -k"

    subprocess.call(command_string, shell=True)

    if os.path.exists(ics_download):
        logging.info('ics downloaded')
        return True
    else:
        logging.error('ics not downloaded')
        return False

def convert_ics_to_conflict_grouping(ics_file, days_out, html_file, extra, extra_file):
    '''
    Convert ICS file content to an HTML file with back to back events
    and possible conflicts.

    Parameters:
    ics_file: Path to ics calendar file
    html_file: Output path to html file created
    extra: some extra html that will be added to the email, typicaly a single line
    extra_file: path to a text file that contains additional html text to be added to the email.
    '''

    events = get_events(ics_file, days_out)

    # Get the calendar from 7 days ago.  This is assuming that this is being run from a script once a week

    previous_cal_name = f'{(datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")}.ics'
    previous_events = get_events(previous_cal_name, days_out)

    # Build pairs of contiguous events
    b2b_groups = []
    concurrent_groups = []

    for i in range(len(events) - 1):
        first = events[i]
        second = events[i + 1]
        if second[0].date() == first[0].date() + datetime.timedelta(days=1):
            b2b_groups.append([first, second])
        if second[0].date() == first[0].date():
            concurrent_groups.append([first, second])

    # Now let's create the html file
    # Grab the text from html_stub file and insert into our html
    try:
        with open('html_stub.txt', 'r') as f:
            stub = f.read()
    except FileNotFoundError:
        logging.error('html_stub.txt not found')
        return False

    html = f'<html><head><title>Lodge Calendar</title>\n'
    html += f'{stub}\n</style>\n</head>\n'
    html += f'<div class="container">\n'
    html += f"<h1>Good Samaritan Calendar</h1><br>\n"
    if previous_events:
        str_date = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%B %d, %Y")
        html += f'<h2>Rows in gray are new/modified since </br> {str_date}</h2>'

    # We can add extra content in two ways
    # --extra <string>
    # --extra-file <path to text file>
    if extra != None:
        html += f'{extra}\n'
    try:
        if extra_file != None:
            with open(extra_file, "r") as file:
                file_content = file.read()
            html+= f'{file_content}\n'
    except FileNotFoundError:
        # if this should abort or not is to be debated.
        logging.error(f'{extra_file} not found')
        return False

    html += f'<h2>Back to Back Events</h2><br>\n'
    html +=  f'<table class="event-table" style="width:100%">\n'
    html += f'\t<tr>\n<th style="width:50%">Date & Time</th>\n<th style="width:50%">Event</th>\n</tr>\n'

    for group in b2b_groups:
        for dtstart, dtend, summary in group:

            day = f'{dtstart:%A} {dtstart:%B} {dtstart.day}'
            start = dtstart.strftime("%-I:%M %p")
            end = dtend.strftime("%-I:%M %p")

            # Color some of the events so they are easier to see.
            if summary.lower().find("rental") >= 0 :
                modifier = 'class="rental"'
            elif summary.lower().find("oes") >= 0 :
                modifier = 'class="oes"'
            else:
                modifier = ''
            html += f'\n<tr {modifier}>\n'
            # Highlight any event that is new or modified
            if previous_events and not (dtstart, dtend, summary) in previous_events:
                background = 'style="background-color: lightgray;\"'
            else:
                background = ''
            html += f'\t<td {background}>{day}</br> {start} - {end}</td>\n'
            # Let's add some icons
            if summary.lower().find("blood") >= 0 :
                html += f'\t<td {background}>&#x1FA78 {summary}</td>\n</tr>\n'
            elif summary.lower().find("game") >= 0 :
                html += f'\t<td {background}>&#127922 {summary}</td>\n</tr>\n'
            else:
                html += f'\t<td {background}>{summary}</td>\n</tr>\n'

        html += f'\t<tr height="50px"></tr>\n'

    html += f'</table>\n'

    html += f'<h2>Possible Conflicts</h2><br>\n'
    html +=  f'<table class="event-table" style="width:100%">\n'
    html += f'\t<tr>\n<th style="width:50%">Date & Time</th>\n<th style="width:50%">Event</th>\n</tr>\n'

    for group in concurrent_groups:
        for dtstart, dtend, summary in group:

            day = f'{dtstart:%A} {dtstart:%B} {dtstart.day}'
            start = dtstart.strftime("%-I:%M %p")
            end = dtend.strftime("%-I:%M %p")

            # Color some of the events so they are easier to see.
            if summary.lower().find("rental") >= 0 :
                modifier = 'class="rental"'
            elif summary.lower().find("oes") >= 0 :
                modifier = 'class="oes"'
            else:
                modifier = ''
            html += f'\n<tr {modifier}>\n'
            # Highlight any event that is new or modified
            if previous_events and not (dtstart, dtend, summary) in previous_events:
                background = 'style="background-color: lightgray;\"'
            else:
                background = ''
            
            html += f'\t<td {background}>{day}</br> {start} - {end}</td>\n'
            # Let's add some icons
            if summary.lower().find("blood") >= 0 :
                html += f'\t<td {background}>&#x1FA78 {summary}</td>\n</tr>\n'
            elif summary.lower().find("game") >= 0 :
                html += f'\t<td {background}>&#127922 {summary}</td>\n</tr>\n'
            elif summary.lower().find('donut') >= 0:
                html += f'\t<td {background}>&#x1F369 {summary}</td>\n</tr>\n'
            else:
                html += f'\t<td {background}>{summary}</td>\n</tr>\n'

        html += f'\t<tr height="50px"></tr>\n'

    html += f'</table>\n'

    html += f"</div>\n"
    html += f'<p class="footer">\nWant to <a href="mailto:rlynch3456@yahoo.com?subject=Lodge Calendar Unsubscribe&body=Hello,%0D%0A%0D%0AI would like to unsubscribe from this calendar.">unsubscribe</a>?</br>\n'
    html += f'See full <a href="https://Rlynch3456.quickconnect.to/sharing/mIsvOeoew">calendar</a></p>\n'
    html += f"</body></html>\n"

    try:
        with open(html_file, "w") as f:
            f.write(html)
    except FileNotFoundError:
        logging.error(f'{html_file} could not be written.')
        return False

    return

def get_events(ics_file, days_out, filter=None, year=None, month=None):

    try:
        with open(ics_file, 'r') as f:
            cal = Calendar.from_ical(f.read())
    except FileNotFoundError:
        logging.error(f'{ics_file} not found')
        return False
    
    events = []
    my_tz = pytz.timezone('America/New_York')
    if year == None and month == None:
        now = my_tz.localize(datetime.datetime.now())
    else:
        now = my_tz.localize(datetime.datetime(year, month, 1))

    for event in cal.walk("vevent"):
        summary = sanitize_text(event.get("summary", "No Title"))

        if not filter == None:
            if summary.lower().find(filter.lower()) == -1:
                continue

        dtstart = event.get("dtstart").dt
        dtend = event.get("dtend").dt

        if isinstance(dtstart, datetime.date) and not isinstance(dtstart, datetime.datetime):
            dtstart = datetime.datetime.combine(dtstart, datetime.time.min)
        if isinstance(dtend, datetime.date) and not isinstance(dtend, datetime.datetime):
            dtend = datetime.datetime.combine(dtend, datetime.time.min)

        # Ensure all datetimes are timezone-aware (convert naive to UTC)
        if dtstart.tzinfo is None:
            dtstart = dtstart.replace(tzinfo=tz.UTC)
        if dtend.tzinfo is None:
            dtend = dtend.replace(tzinfo=tz.UTC)

        if dtstart >= now and dtstart <= now + datetime.timedelta(days=days_out):
            events.append((dtstart, dtend, summary))

    # Sort events by start date
    events.sort(key=lambda x: x[0])
    return events

def convert_ics_to_html(ics_file, days_out, html_file, extra, extra_file, filter):
    '''
    Convert ICS file content to an HTML file with events sorted by date.

    Parameters:
    ics_file: Path to ics calendar file
    days_out: Integer number of days that HTML file will show
    html_file: Output path to html file created
    extra: some extra html that will be added to the email, typicaly a single line
    extra_file: path to a text file that contains additional html text to be added to the email.
    '''

    events = get_events(ics_file, days_out, filter)

    # Get the calendar from 7 days ago.  This is assuming that this is being run from a script once a week

    previous_cal_name = f'{(datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")}.ics'
    previous_events = get_events(previous_cal_name, days_out, filter)

    # Grab the text from html_stub file and insert into our html
    try:
        with open('html_stub.txt', 'r') as f:
            stub = f.read()
    except FileNotFoundError:
        logging.error('html_stub.txt not found')
        return False

    html = f'<html><head><title>Lodge Calendar</title>\n'
    html += f'{stub}\n</style>\n</head>\n'
    html += f'<div class="container">\n'
    html += f"<h1>Good Samaritan Calendar Events - {days_out} Days Out</h1><br>\n"

    # We can add extra content in two ways
    # --extra <string>
    # --extra-file <path to text file>
    if extra != None:
        html += f'{extra}\n'
    try:
        if extra_file != None:
            with open(extra_file, "r") as file:
                file_content = file.read()
            html+= f'{file_content}\n'
    except FileNotFoundError:
        # if this should abort or not is to be debated.
        logging.error(f'{extra_file} not found')
        return False

    if not filter == None:
        html += f'<h2>Filter: {filter}</h2>\n'

    html += f'<h2 class="rental">Rental Events in Red</h2>\n'
    html += f'<h2 class="oes">Order of Eastern Star Events in Blue</h2>\n'
    if previous_events:
        str_date = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%B %d, %Y")
        html += f'<h2>Rows in gray are new/modified since </br> {str_date}</h2>'

    html += f"<h2>The next week</h2>\n"
    html +=  f'<table class="event-table" style="width:100%">\n'
    html += f'\t<tr>\n<th style="width:50%">Date & Time</th>\n<th style="width:50%">Event</th>\n</tr>\n'
    new_heading = False
    my_tz = pytz.timezone('America/New_York')
    now = my_tz.localize(datetime.datetime.now())
    for dtstart, dtend, summary in events:
        if dtstart >= now + datetime.timedelta(days=7) and new_heading == False:
            # end the previous table, and start a new one
            html += f'</table>\n'
            html += f"<h2>In the Future</h2>\n"
            html +=  f'<table class="event-table" style="width:100%">\n'
            html += f'\t<tr>\n<th style="width:50%">Date & Time</th>\n<th style="width:50%">Event</th>\n</tr>\n'
            new_heading = True
        day = f'{dtstart:%A} {dtstart:%B} {dtstart.day}'
        start = dtstart.strftime("%-I:%M %p")
        end = dtend.strftime("%-I:%M %p")

        # Color some of the events so they are easier to see.
        if summary.lower().find("rental") >= 0 :
            modifier = 'class="rental"'
        elif summary.lower().find("oes") >= 0 :
            modifier = 'class="oes"'
        else:
            modifier = ''

        html += f'\n<tr {modifier}>\n'

        # Highlight any event that is new or modified
        if previous_events and not (dtstart, dtend, summary) in previous_events:
            background = 'style="background-color: lightgray;\"'
        else:
            background = ''

        html += f'\t<td {background}>{day}</br> {start} - {end}</td>\n'

        # Let's add some icons
        if summary.lower().find("blood") >= 0 :
            html += f'\t<td {background}>&#x1FA78 {summary}</td>\n</tr>\n'
        elif summary.lower().find("game") >= 0 :
            html += f'\t<td {background}>&#127922 {summary}</td>\n</tr>\n'
        elif summary.lower().find('donut') >= 0:
            html += f'\t<td {background}>&#x1F369 {summary}</td>\n</tr>\n'
        else:
            html += f'\t<td {background}>{summary}</td>\n</tr>\n'

    html += f'</table>\n'

    html += f"</div>\n"
    html += f'<p class="footer">\nWant to <a href="mailto:rlynch3456@yahoo.com?subject=Lodge Calendar Unsubscribe&body=Hello,%0D%0A%0D%0AI would like to unsubscribe from this calendar.">unsubscribe</a>?</br>\n'
    html += f'See full <a href="https://Rlynch3456.quickconnect.to/sharing/mIsvOeoew">calendar</a></p>\n'
    html += f"</body></html>\n"

    try:
        with open(html_file, "w") as f:
            f.write(html)
    except FileNotFoundError:
        logging.error(f'{html_file} could not be written.')
        return False

    return True

def initialize():

    '''
    Load envirnoment variables from .env file.

    Returns: args
    '''
    # This will hide usernames and passwords.

    load_dotenv()

    # Get the command line arguments
    parser = argparse.ArgumentParser(description='say something here')
    parser.add_argument('-w', '--window', help='time window', default="60")
    parser.add_argument('-d', '--distro', help='Distro file')
    parser.add_argument('-s', '--subject', help='Subject of email', default='Lodge Calendar')
    parser.add_argument('-v', '--verbose', help='Send all log messages to console', default=False, action='store_true')
    parser.add_argument('-e', '--extra', help='Extra text for mailing html', default=None)
    parser.add_argument('-f', '--filter', help='Text filer')
    parser.add_argument('-u', '--update', help='Look for calendar updates')
    parser.add_argument('--extra-file', help='Extra text for mailing html from text file', default=None)
    mail_group = parser.add_mutually_exclusive_group(required=True)
    mail_group.add_argument('-m', '--mail', help='Send email to distro list', action='store_true')
    mail_group.add_argument('-c', '--conflicts', help='No email will be sent', action='store_true')
    args = parser.parse_args()

    verbose = getattr(args, 'verbose')

    if verbose:
        # Clear existing handlers before reconfiguration
        root_logger = logging.getLogger()
        # Reset existing logging configuration
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        # Now apply the new verbose configuration
        logging.config.dictConfig(verbose_config)

    return args
def main():

    args = initialize()

    if hasattr(args, 'distro'):
        mail_distro = getattr(args, 'distro')

        # make a date string for calendar download with today's date
    today = datetime.datetime.now()
    today_string = f'{today.strftime("%Y-%m-%d")}.ics'
    ics_download = today_string
    ics_data = download_ics(today_string)

    window = int(getattr(args, "window"))
    extra = getattr(args, 'extra')
    extra_file = getattr(args, 'extra_file')
    filter = getattr(args, 'filter')
    html_file = "my_html.html"

    if ics_data:
        if getattr(args, 'mail'):
            if convert_ics_to_html(ics_download, window, html_file, extra, extra_file, filter) == False:
                return

        if getattr(args, 'conflicts'):
            if convert_ics_to_conflict_grouping(ics_download, window, html_file, extra, extra_file) == False:
                return

    if mail_distro:
        subject = getattr(args, "subject")
        send_email(mail_distro, subject, html_file)


if __name__ == "__main__":
    main()
