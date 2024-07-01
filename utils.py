from datetime import timedelta


def get_most_recent_business_day(date):
    if date.weekday() < 5:  # Monday=0, Sunday=6
        return date
    
    offset = max(1, (date.weekday() + 1) % 5)
    most_recent_business_day = date - timedelta(days=offset)
    
    return most_recent_business_day