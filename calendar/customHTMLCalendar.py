import calendar

class customHTMLCalendar(calendar.HTMLCalendar):
    def __init__(self,  bookings, firstweekday=calendar.MONDAY, highlight_day=None):
        super().__init__(firstweekday)
        self.highlight_day = highlight_day
        self.bookings = bookings

    def formatday(self, day, weekday):
        if day == 0:
            return '<td class="noday">&nbsp;</td>'

        #cls = "highlight" if day == self.highlight_day else ""
        cls = "highlight" if self.bookings[day] == 1 else ""
        return f'<td class="{cls}">{day}</td>'
