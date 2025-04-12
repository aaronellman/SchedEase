import pandas as pd
import numpy as np
import math
import re
import calendar
from datetime import datetime, timezone, time, timedelta
from eventcreate import main as create_calendar_event

def format_datetime(date_str,start_hour):

    current_year = str(datetime.now().year)
    date_obj = datetime.strptime(str(date_str) + " " + current_year, "%a %d %b %Y")

    start_time_obj = time(start_hour,0)
    start_datetime = datetime.combine(date_obj, start_time_obj)
    end_datetime = start_datetime + timedelta(minutes=50)
    
    return start_datetime.isoformat(), end_datetime.isoformat()

class Event():
    summary = ""
    start_time = ""
    end_time = ""

    def __init__(self, summary, start_hour, start_date):
        self.summary = summary
        self.start_time = format_datetime(start_date, start_hour)[0] #TODO Pass in date fo
        self.end_time = format_datetime(start_date, start_hour)[1]
        

# Path to the Excel file
file_path = "timetable.xlsx"

# Load the Excel file
df = pd.read_excel(file_path, header=14)  # Set the correct row as headers
df = df.dropna(how="all")
df.rename(columns={df.columns[0]: "Time"}, inplace=True)
#print(df.head(10))  # Check the new format

cols = list(df.head(10))

#print(cols)
raw_dates = []
rows_list = []

for row in df.values:
    row_list = row.tolist()  # Convert the row to a list
    if re.search("H00",row_list[0]):
        rows_list.append(row_list)
        #print(row_list)
    else:
        raw_dates.append(row_list)
#print(rows_list[0][0])

day_pattern = "Mon|Tue|Wed|Thu|Fri|Sat"
refined_dates = []

for week in raw_dates:
    for day in week:
        if re.search(day_pattern,day):
            refined_dates.append(day)

#print(refined_dates)
 

dates_on_days = {
    "Mon" : [],
    "Tue" : [],
    "Wed" : [],
    "Thu" : [],
    "Fri" : [],
    "Sat" : []
}

#date_dict = {date: [] for date in refined_dates}
date_dict = {}
for date in refined_dates:
    if re.search("Mon",date):
        #print(date)
        pass
    date_dict[date] = []

days_list = []
subjects = []

for key in dates_on_days:  # Just iterate over keys (no enumerate)
    for date in refined_dates:  # Loop through each string in the list
        matches = re.findall(fr"{key} \d{{1,2}} \w{{3}}", date)  
        dates_on_days[key].extend(matches)  # Store matched results


for x in range(len(rows_list)):
    rows_list[x] = rows_list[x][1:]

col = 0 #column
row = 0
day_name = "" #represents integer version of day of the week
count = 0 #how many times we have iterated over a day
session = 0 #number of sessions iterated over
date = ""
n = len(rows_list)

while col < len(rows_list[0]):  # Loop through columns
    row = 0  # Reset row for each column
    while row < n:  # Loop through rows
        if (session * 6) == (n * 6):
            break
        subject = rows_list[row][col]
        subjects.append(subject)
        subject = ""
        day_name = calendar.day_abbr[col]
        
        if (len(subjects) == 10) and (session > 0):
            #print(subjects)
            #print(date)
            date_dict[date] = subjects.copy()
            subjects.clear()  
            count += 1 
        
        # Ensure count does not exceed the length of dates_on_days[day_name]
        if day_name in dates_on_days:
            if count >= len(dates_on_days[day_name]):
                count = 0
            date = dates_on_days[day_name][count]
        
        row += 1  # Increment row to avoid  infinite loop
        session += 1
    col += 1      



def create_events(date_dict, dates_on_days):
    events = []
    for i in range(len(dates_on_days["Mon"])):
        date = dates_on_days["Mon"][i]
        for j in range(len(date_dict)):
            if list(date_dict.keys())[j] == date:
                schedule = date_dict[date]
                for x in range(len(schedule)):
                    if str(schedule[x]) != "nan":
                        #print(type(schedule[x]) , schedule[x])
                        start_time = 8 + x
                        session = Event(schedule[x], start_time, date)

                        event = {"summary": session.summary,
                            "start":{
                                "dateTime": session.start_time,
                                "timeZone": "Africa/Johannesburg"} ,
                            "end":{
                                "dateTime" : session.end_time, 
                                "timeZone" : "Africa/Johannesburg"},
                            "reminders": {
                                "useDefault": False,  
                                "overrides": [] }
                            }
                    
                        events.append(event)
    return events

def add_events(events):
    for event in events:
        create_calendar_event(event)
print(create_events(date_dict, dates_on_days))
add_events(create_events(date_dict, dates_on_days))
