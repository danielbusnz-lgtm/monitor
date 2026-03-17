import time
import threading
import db
import alerts


def _check():
    for service in db.get_all_services():
        name     = service["name"]
        interval = service["interval_seconds"]
        last     = service["last_ping"]
        alerted  = service["alerted"]

        if last is None:
            continue

        elapsed = time.time() - last
        grace   = interval * 1.5

        if elapsed > grace and alerted == 0:
            alerts.send_alert(name)
            db.set_alerted(name)

        elif elapsed <= grace and alerted == 1:
            alerts.send_recovery(name)
            db.clear_alerted(name)


def _loop():
    while True:
        time.sleep(60)
        _check()


def start_checker():
    t = threading.Thread(target=_loop, daemon=True)
    t.start()
