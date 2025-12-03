from datetime import datetime, timedelta
import dateparser
import uuid

def parse_date(text):
    """Convert raw date text into a datetime object."""
    return dateparser.parse(text)

def create_ics_event(title, date):
    """Create a .ics calendar file for Google Calendar."""
    event_uid = str(uuid.uuid4())
    dt_start = date.strftime("%Y%m%dT%H%M%S")
    dt_end = (date + timedelta(hours=1)).strftime("%Y%m%dT%H%M%S")

    content = f"""BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
UID:{event_uid}
DTSTAMP:{dt_start}
DTSTART:{dt_start}
DTEND:{dt_end}
SUMMARY:{title}
END:VEVENT
END:VCALENDAR
"""

    filename = f"{title.replace(' ', '_')}.ics"
    with open(filename, "w") as f:
        f.write(content)

    print(f"Created event file: {filename}")

def process_events(event_list):
    for event in event_list:
        title = event["title"]
        raw_date = event["date"]
        parsed = parse_date(raw_date)
        if parsed:
            create_ics_event(title, parsed)
        else:
            print(f"Could not parse: {raw_date}")

# Example test data
events = [
    {"title": "DSA Test", "date": "25 Jan 2025 at 3 PM"},
    {"title": "Maths Assignment Deadline", "date": "30 Jan 2025"},
]

process_events(events)
