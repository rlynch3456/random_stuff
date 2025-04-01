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
    msg['To'] = ", ".join(distro)
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

    except smtplib.SMTPException as e:
        logging.error(f"SMTP error occurred: {e}")

    return True

def download_ics(isc_download):
    '''
    Download ICS file from Synology Calendar.'
    
    Parameters:
    isc_download: Filename for the download.

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

    command_string = f"curl -u {CALENDAR_USERNAME}:{CALENDAR_PASSWORD} {ICS_URL} -o {isc_download} -k"

    subprocess.call(command_string, shell=True)
 
    if os.path.exists(isc_download):
        logging.info('ics downloaded')
        return True
    else:
        logging.error('ics not downloaded')
        return False

def convert_ics_to_html(ics_file, days_out, html_file, extra):
    '''
    Convert ICS file content to an HTML file with events sorted by date.
    
    Parameters:
    ics_file: Path to ics calendar file
    days_out: Integer number of days that HTML file will show
    html_file: Output path to html file created

    '''
    
    try:
        with open(ics_file, 'r') as f:
            cal = Calendar.from_ical(f.read())
    except FileNotFoundError:
        logging.error(f'{ics_file} not found')
        return False
    
    events = []
    my_tz = pytz.timezone('America/New_York')
    now = my_tz.localize(datetime.datetime.now())
    
    for event in cal.walk("vevent"):
        summary = event.get("summary", "No Title")
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

    html = "<html><head><title>Lodge Calendar</title></head><body>\n"
    html += f"<h1>Good Samaritan Calendar Events - {days_out} Days Out</h1><br>\n"
    if extra != None:
        html += f'{extra}\n'
    html += f'<h2 style="color:red">Rental Events in Red</h2>\n'
    html += f'<h2 style="color:blue">Order of Eastern Star Events in Blue</h2>\n'

    html += "<h2>The next 7 days</h2>\n"
    new_heading = False
    for dtstart, dtend, summary in events:
        if dtstart >= now + datetime.timedelta(days=7) and new_heading == False:
            html += "<br><br><h2>In the future</h2>\n"
            new_heading = True
        dtstart_str = dtstart.strftime("%Y-%m-%d %I:%M %p")
        dtend_str = dtend.strftime("%Y-%m-%d %I:%M %p")
        #if summary.lower().find("rental") == -1 :
        #    color = "black"
        if summary.lower().find("rental") >= 0 :
            color = "red"
        elif summary.lower().find("oes") >= 0 :
            color = "blue"
        else:
            color = "black"
        html += f'<p style="color:{color}">{dtstart_str} - {dtend_str}: {summary}</p>\n'
    html += "</body></html>"

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
    parser.add_argument('-v', '--verbose', help='Send all logg messages to console', default=False, action='store_true')
    parser.add_argument('-e', '--extra', help='Extra text for mailing html')
    mail_group = parser.add_mutually_exclusive_group(required=True)
    mail_group.add_argument('--mail', dest='mail', help='Send email to distro list', action='store_true')
    mail_group.add_argument('--no-mail', dest='mail', help='No email will be sent', action='store_false')
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

    do_mail = getattr(args, 'mail')
    distro = getattr(args, 'distro')

    if do_mail == True and distro == None:
        logging.error('Mail was requested, but no distro list provided.')
        return

    isc_download = "download.ics"
    ics_data = download_ics(isc_download)
    window = int(getattr(args, "window"))
    extra = getattr(args, 'extra')
    html_file = "my_calendar.html"
    
    if ics_data:
        if convert_ics_to_html(isc_download, window, html_file, extra) == False:
            return
    
    do_mail = getattr(args, 'mail')

    if do_mail:
        distro = getattr(args, "distro")
        subject = getattr(args, "subject")
        send_email(distro, subject, html_file)

if __name__ == "__main__":
    main()
