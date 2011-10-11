import re, time, calendar, datetime, getpass
import gdata.calendar.service
import gdata.calendar
import atom.core
from BeautifulSoup import BeautifulSoup as bs
import icalendar
import urllib
import urllib2
from cookielib import CookieJar
import httpbot


"""Collect login data for unassisted data collection"""
warwickusername = raw_input("Enter Warwick Username: ")
warwickpassword = getpass.getpass("Enter Warwick Password: ")

googleusername = raw_input("Enter Google Username: ")
googlepassword = getpass.getpass("Enter Google Password: ")

calendarname = raw_input("Enter a new calendar name: ")

"""Parse warwick page"""
def warwick_ical():
    """Declare variables"""
    warwickurl = "http://www.eng.warwick.ac.uk/cgi-bin/timetable"

    bot = httpbot.HttpBot()
    bot.POST('https://websignon.warwick.ac.uk/origin/slogin?providerId=urn%3Awww.eng.warwick.ac.uk%3Ageneral%3Aservice&target=http://www.eng.warwick.ac.uk/cgi-bin/timetable', {'userName': warwickusername, 'password':warwickpassword})
    response = bot.GET(warwickurl)

    soup = bs(response)

    try:
        ical_url = soup.findAll('a')[0]['href'].replace('webcal','http')
    except KeyError:
        while 1:
            again = raw_input('Login Error! Try again? (y) ')
            if again == 'y':
                return warwick_ical()
                break
            elif again == 'n':
                exit(0)
            else:
                print 'Please enter y or n'
            
   
    return urllib2.urlopen(urllib2.Request(ical_url)).read()

#Load and login GCal
gcal_service = gdata.calendar.service.CalendarService()
gcal_service.ClientLogin(googleusername, googlepassword)


#Delete calendar if already exists. Need to extract to function to allow user to choose new calendar name if already exists.
feed = gcal_service.GetOwnCalendarsFeed()
for entry in feed.entry:   
    if entry.title.text == calendarname:
        delquestion = raw_input('%s Calendar already exists, delete? (y) ' % calendarname)
        if delquestion == 'y' or delquestion == '':
            print '%s Calendar deleted!' % calendarname
            gcal_service.Delete(entry.GetEditLink().href)
        elif delquestion == 'n':
            print 'Aborting...'
            exit(0)
        else:
            exit(0)
            
    
#Create new calendar
calendar = gdata.calendar.CalendarListEntry()
calendar.title = atom.Title(text=calendarname)
calendar.summary = atom.Summary(text='Warwick Engineering Timetable')
calendar.where = gdata.calendar.Where(value_string='University of Warwick')
calendar.color = gdata.calendar.Color(value='#2952A3')
calendar.timezone = gdata.calendar.Timezone(value='Europe/London')
calendar.hidden = gdata.calendar.Hidden(value='false')

new_calendar = gcal_service.InsertCalendar(new_calendar=calendar)

print '%s Calendar created!' % calendarname

def gcal_addevent(title, description, location, start, end):
    """Adds events to google calendar"""
    """Time variables expected as time object"""
    event = gdata.calendar.CalendarEventEntry()

    event.title = atom.Title(text=title)
    event.content = atom.Content(text=description)
    event.where.append(gdata.calendar.Where(value_string=location))

    #Convert time to string
    start = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", start)
    end = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", end)

    event.when.append(gdata.calendar.When(start_time=start, end_time=end))
    
    print '%s created' % (title)

    return gcal_service.InsertEvent(event, new_calendar.link[0].href)
	
ical_data = warwick_ical()
ical = icalendar.Calendar.from_string(ical_data)

for event in ical.walk('vevent'):
    #Rip data to most useful form
    title = event['description']
    category = event['categories']
    start = time.strptime(str(event['dtstart']), '%Y%m%dT%H%M%S')
    end = time.strptime(str(event['dtend']), '%Y%m%dT%H%M%S')
    modulecode = event['summary'][:5]
    staff = event['summary'][8:]
    
    #print event['sequence']
    
    if event.has_key('location'):
        location = event['location']
    else:
        location = ''
        
    #Reformat for readablity
    if category != 'Lecture':
        title = category.upper() + ' ' + title
        
    description = modulecode + '\n' + staff
    
    #print(title, description, location, start, end)
    try: gcal_addevent(title, description, location, start, end)
    except gdata.service.RequestError:
        print 'Google Calendar locking us out, waiting and trying again...'
        gcal_service.ClientLogin(googleusername, googlepassword)
        continue
    
    #Unused keys
    #dtstamp
    #last-modified
    #uid
