import os
import urllib.error
import urllib.parse
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class DRISHTIClient:
    def __init__(self, host="localhost", port=8000):
        self.base = f"http://{host}:{port}"

    def ping(self):
        """Raises ConnectionError if the server cannot be reached."""
        try:
            urllib.request.urlopen(self.base + "/", timeout=3)
        except urllib.error.HTTPError:
            pass                          # server answered, so it is up
        except OSError:
            raise ConnectionError("Cannot reach the server. Is server.py running?")
        return True

    def fetch(self, patient_id):
        url = f"{self.base}/?{urllib.parse.urlencode({'pid': patient_id})}"
        try:
            with urllib.request.urlopen(url, timeout=5) as resp:
                return resp.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise LookupError(f"Patient {patient_id} not found on server")
            raise ConnectionError(f"Server returned error {e.code}")
        except OSError:
            raise ConnectionError("Cannot reach the server. Is server.py running?")

    def save_html(self, text, patient_id, folder=None):
        folder = folder or os.path.join(BASE_DIR, "downloads")
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, f"{patient_id}_status.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path