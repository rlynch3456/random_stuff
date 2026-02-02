from flask import Flask, render_template, request
import calendar
import my_calendar
from datetime import datetime
import os

app = Flask(__name__)

class customHTMLCalendar(calendar.HTMLCalendar):
    def __init__(self,  bookings, firstweekday=calendar.MONDAY):
        super().__init__(firstweekday)
        self.bookings = bookings

    def formatday(self, day, weekday):
        if day == 0:
            return '<td class="noday">&nbsp;</td>'

        cls = "highlight" if self.bookings[day] == 1 else ""
        return f'<td class="{cls}">{day}</td>'


@app.route("/calendar", methods=["GET", "POST"])
def show_calendar():
    
    now = datetime.now()

    # Defauls
    year = now.year
    month = now.month

    # 1️⃣ URL query params (?month=5&year=2026)
    if request.method == "GET":
        if request.args.get("month"):
            month = int(request.args.get("month"))
        if request.args.get("year"):
            year = int(request.args.get("year"))

    # 2️⃣ Form POST
    if request.method == "POST":
        month = int(request.form["month"])
        year = int(request.form["year"])

    length = 32

    days = calendar.monthrange(year, month)[1]
    events = my_calendar.get_events("today.ics", days, "", year, month)

    bookings = [0]*(length + 1)

    for event in range(len(events)):
        day = events[event][0].timetuple().tm_mday
        bookings[day] = 1


    cal = customHTMLCalendar(
        bookings,
        firstweekday=calendar.SUNDAY,
    )


    calendar_html = cal.formatmonth(year, month)

    return render_template(
        "calendar.html",
        calendar_html=calendar_html,
        year=year,
        month=month,
        months=list(enumerate(calendar.month_name))[1:],
        years=range(now.year, now.year + 6)
    )

if __name__ == "__main__":
    myhost = "127.0.0.1"
    myport = 5001

    # Only print once, even in debug mode with reloader
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        print(f"Server starting at http://{myhost}:{myport}")

    app.run(debug=True, host=myhost, port=myport)

