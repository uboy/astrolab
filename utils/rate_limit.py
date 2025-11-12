import time

def check_rate(user_data, per_min, per_hour):
    now = time.time()
    minute_times = [t for t in user_data["rate"]["minute"] if now - t < 60]
    hour_times = [t for t in user_data["rate"]["hour"] if now - t < 3600]
    user_data["rate"]["minute"] = minute_times
    user_data["rate"]["hour"] = hour_times
    if len(minute_times) >= per_min or len(hour_times) >= per_hour:
        return False
    minute_times.append(now)
    hour_times.append(now)
    return True
