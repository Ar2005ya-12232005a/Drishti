import os
import sys
from urllib.parse import parse_qs

sys.stdout.reconfigure(encoding="utf-8")
# allow importing tracker.py and theme.py from the parent folder
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from theme import message_page, status_page
from tracker import FollowUpTracker

query = parse_qs(os.environ.get("QUERY_STRING", ""))
pid = query.get("pid", [""])[0].strip().upper()

print("Content-Type: text/html; charset=utf-8")
print()                                   # blank line ends the headers

try:
    t = FollowUpTracker()
    t.load()
    print(status_page(t.get_status(pid), back_link="/form.html"))
except KeyError:
    print(message_page(f"Patient {pid or '(blank)'} not found", back_link="/form.html"))
except Exception as ex:
    print(message_page(f"Error: {ex}", back_link="/form.html"))