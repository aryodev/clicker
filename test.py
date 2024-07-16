from datetime import datetime, timedelta

n = datetime.now()
print(n)
t = timedelta(minutes=25)
print((n + t).strftime('%H:%M'))