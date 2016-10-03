'''
This is just practice stuff.

Alarm clock that plays either the top trending YouTube video or a random video 
from a local file named videolist.txt.  The decision as to which to play is based 
on user input when script is run.
The alarm clock does not terminate once the alarm triggers.  Instead, it starts 
over so it will play a video daily until the user manually kills the script.

Requirement:  
-Chrome or Firefox
-A file named videolist.txt in same directory of script that looks something like this: 
https://www.youtube.com/watch?v=6NhzaWuG2wg
https://www.youtube.com/watch?v=yW_oZR9a714
https://www.youtube.com/watch?v=PKehlbkbO3Q

This has been tested in Python 2.7 and 3.4
'''
import argparse
import time
import datetime
import random
import requests
import json
import sys
from selenium import webdriver


parser = argparse.ArgumentParser(description='Alarm Clock')

parser.add_argument('-time', action="store", dest="wake_time", default="7:00 AM", required=True,
                    help="The time you want to wake up.  Available formats are 7:00PM, '7:00 PM', 19:00 or 1900.  If you use a space, you must put time in quotes - '7:00 PM' ")

parser.add_argument('-type', action="store", dest="video_type", default="top", required=False,
                    help="Available inputs are top or random.  Top will pull top trending video.  Random will pull from a local videolist.txt file.")

parser.add_argument('-browser', action="store", dest="video_browser", default="Chrome", required=False,
                    help="Specify the browser you have on your machine. Options are Firefox or Chrome.  The default is chrome.")

results = parser.parse_args() 

# Turns users input into a workable time format
def process_time_from_user(wake_time):
    try: 
        return time.strftime("%H%M", time.strptime(wake_time, "%I%M%p")) # Looks for 12 hour format - e.g. 700PM
    except:
        pass
    try: 
        return time.strftime("%H%M", time.strptime(wake_time, "%H%M")) # Looks for 24 hour format - e.g. 1900
    except:
        print ("\nI did not understand the time you entered. \nPlease enter in these formats: \n\n\t 7:00AM \n\t '7:00 AM' \n\t 2100 \n\t 21:00\n\n")
        raise # Added this to exit out of the script.  https://docs.python.org/2/tutorial/errors.html#user-defined-exceptions


# Selects random video from file videolist.txt. Re-opens file every time in the event that you want to change videos in videolist.txt without exiting the script 
def play_local_video():
    video_list = list()
    with open('videolist.txt', 'r') as f:
        for lines in f:
            video_list.append(lines)
    
    play_video(random.choice(video_list), 60) # Sets the video to play for 60 seconds


# Gets yesterdays top YouTube trending YouTube video.  
# We could use this to dump all the videos to a file for later use  
def play_top_video():
    # Sets date to two days ago since I'm not sure how soon the previous days videos are available
    dates = (datetime.date.today() - datetime.timedelta(2)).strftime("%Y%m%d")

    # Used http://curl.trillworks.com to convert curl command pulled from chrome's dev tools
    headers = {
        'Origin': 'http://www.google.com',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'Accept': '*/*',
        'Referer': 'http://www.google.com/trends/hotvideos',
        'Proxy-Connection': 'keep-alive'
       }

    data = "hvd="+dates+"&geo=US&mob=0&hvsm=0"

    req = requests.post('https://www.google.com/trends/hotvideos/hotItems', headers=headers, data=data)

    mydic = json.loads(req.text)
    top_video = mydic['videoList'][0]['url'] # Maybe make this random rather than the top
    video_length = mydic['videoList'][0]['length']
    video_play_time = convert_video_duration(video_length)
    
    play_video(top_video, video_play_time)


# Converts video duration from YouTube to seconds so we can control how long the video plays
# Was going to use time, but this seemed simpler for what was needed
def convert_video_duration(video_length):
    if len(video_length) <= 2:
        return video_length
    elif len(video_length) == 4: # Stop at 9 minutes 
        return (int(video_length[0]) * 60 + int(video_length[2:]))
    else:
        return 60 # Defaults to 60 seconds if duration is greater than 9:59


# Plays video for specified amount of time
def play_video(url, duration):
    video_browser = results.video_browser.title()
    
    if video_browser == 'Firefox':
        browser = webdriver.Firefox()
    else: 
        browser = webdriver.Chrome() #Default back to chrome in case someone enters something other than firefox or chrome

    browser.get(url)
    time.sleep(8) # changed this to 8 seconds to account for video start time
    # Skip ad after 5 seconds if option is available
    try:
        browser.find_element_by_class_name('videoAdUiSkipButton').click()
    except:
        pass
    time.sleep(duration)
    browser.quit()


alarm = process_time_from_user(results.wake_time.replace(":", "").replace(" ", "")) # Clean up input so it is easier to work with
video_type = results.video_type.lower()


while True:
    current_time = time.strftime("%H%M")
    if alarm != current_time:
        #print(current_time)
        sys.stdout.write("\rIt is now " + current_time + ".  Your alarm is set to go off at " + alarm) # http://stackoverflow.com/a/5291323/4393950
        time.sleep(15) # Only sleep for 15 seconds in the event that your pc goes to sleep at any time during the day
    elif alarm == current_time:
        sys.stdout.write("\rIt is now " + current_time + ".  Alarm is going off now!!!                 ") # http://stackoverflow.com/a/5291323/4393950
		
        # In the event that one fails, try the other
        if video_type == "top":
            try: 
                play_top_video()
            except:
                play_local_video()
        elif video_type != "top":
            try:
                play_local_video()
            except:
                play_top_video()
        time.sleep(60)