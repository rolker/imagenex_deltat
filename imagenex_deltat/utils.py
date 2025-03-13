
import datetime

frequency_to_code = {
    120000: 58,
    260000: 86,
    675000: 169,
    1700000: 68
}

code_to_frequency = {v: k for k, v in frequency_to_code.items()}

# Maps valid range requests in meters to value to use in the
# Switch Data packet. byte 3 
range_to_code = {
    5:5,
    10:10,
    20:20,
    30:30,
    40:40,
    50:50,
    60:60,
    80:80,
    100:100,
    150:150,
    200:200,
    250:201,
    300:202
}

code_to_range = {v: k for k, v in range_to_code.items()}

def timestamp_from_strings(date: str, time: str, miliseconds: str) -> datetime.datetime:
    day = int(date[0:2])
    month = {"JAN":1, "FEB":2, "MAR":3, "APR":4, "MAY":5, "JUN":6, "JUL":7, "AUG":8, "SEP":9, "OCT":10, "NOV":11, "DEC":12}[date[3:6].decode()]
    year = int(date[7:11])
    hour = int(time[0:2])
    minute = int(time[3:5])
    seconds = int(time[6:8])

    ms = float(miliseconds)
    return datetime.datetime(year, month, day, hour, minute, seconds, int(ms*1000000), tzinfo=datetime.timezone.utc)
