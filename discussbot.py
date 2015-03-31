#!/usr/bin/python3
from sys import argv, exit, stdout
from datetime import datetime
from time import time, sleep
from requests import get
from praw import Reddit
from json import loads

#Load configuration file.
config_file = open('config.json', 'r')
config = loads(config_file.read())
config_file.close()

#Get json root titles.
show = config['shows'][argv[1]]
settings = config['settings']
templates = config['templates']

#Get settings.
version = settings['version']
user_agent = settings['user_agent'].format(version=version)
google_oauth = settings['google_oauth']
loop_int = settings['loop_time']
refresh_int = settings['refresh_time']

#Get show information.
subreddit = show['subreddit']
podcast = show['full_name']
channel = show['youtube_id']
reddit_oauth = show['reddit_token']

#Other information.
episode = argv[2]
start_time = time()
headers = {'User-Agent': user_agent, 'Cache-Control': 'max-age=0, no-cache'}
google_api = 'http://gdata.youtube.com/feeds/api/users/{0}/uploads?v=2&alt=jsonc'.format(channel)

print('discussbot-cli v{0} - Episode Discussion Bot.\n---------------------------------------------'.format(version))
print('Logging into Reddit..', end='\t'); stdout.flush()

#Load instance of Reddit.
reddit = Reddit(user_agent=user_agent)
reddit.set_oauth_app_info(client_id=settings['client_id'], client_secret=settings['client_secret'],
                          redirect_uri=settings['redirect_uri'])

try:
    reddit.refresh_access_information(reddit_oauth)
    refresh_time = time()

except:
    print('Failed.')
    exit()

print('Success.')

#Infinite loop to check the Youtube API for the episode.
print('Checking Youtube API..', end='\t'); stdout.flush()
while True:
    try:
        #Get latest video from Youtube user.
        latest = get(google_api, headers=headers).json()['data']['items'][0]
        video_title = latest['title']
        upload_date = latest['uploaded']
        video_id = latest['id']

    except:
        sleep(1); continue

    #If the given episode number is in the latest video title.
    if episode in video_title:
        published = int((datetime.strptime(upload_date,
                    '%Y-%m-%dT%H:%M:%S.000Z') - datetime(1970, 1, 1)).total_seconds())

        #And if the program was started before it was uploaded.
        if start_time < published:
            pass  #Continue on with program.

        else:
            #Refresh reddit token every 30 minutes.
            if time() - refresh_time > refresh_int:
                reddit.refresh_access_information(reddit_oauth)
                refresh_time = time()

            #Wait given period and restart loop.
            sleep(loop_int); continue

        #Discussion thread information.
        submission_title = templates['title'].format(show_code=argv[1].upper(), episode=episode)
        text_body = templates['thread'].format(full_name=podcast, episode=episode,
                                               video_title=video_title, video_id=video_id)

        try:
            #Try to post the dicussion thread to Reddit.
            print('Available.')
            time_found = str(round(time() - published, 1))
            print('Posting to Reddit..', end='\t'); stdout.flush()
            dthread_permalink = reddit.submit(subreddit, submission_title, text=text_body)

            time_discussion = str(round(time() - published, 1))
            print('Submitted.')

        except:
            #If it failed, get another access token and wait 10 seconds.
            reddit.refresh_access_information(reddit_oauth)
            sleep(10)
            continue

        #Load comment for video thread.
        reddit_comment = templates['comment'].format(link=dthread_permalink)

        #Get the latest 5 submissions on the shows subreddit.
        subreddit_new = reddit.get_subreddit(subreddit).get_new(limit=5)

        #For each thread, check if the video has already been linked too.
        for thread in subreddit_new:
            #If it has, add the comment and break the loop.
            if video_id in thread.url:
                print('Adding comment..', end='\t'); stdout.flush()
                thread.add_comment(reddit_comment)
                print('Submitted.')
                time_comment = str(round(time() - published, 1))
                link_added = False
                break

        else:
            #If the video has not been linked to, add a link to the video.
            print('Adding link..', end='\t\t'); stdout.flush()
            vthread_permalink = reddit.submit(subreddit, video_title, url='https://youtube.com/watch?v=' + video_id)
            time_link = str(round(time() - published, 1))
            print('Submitted.')

            #Then add a comment to our own video link.
            print('Adding comment..', end='\t'); stdout.flush()
            link = reddit.get_submission(vthread_permalink[:4]+vthread_permalink[5:])
            link.add_comment(reddit_comment)
            print('Submitted.')
            time_comment = str(round(time() - published, 1))
            link_added = True

        #Print time statistics to stdout.
        print('\nTime Statistics:\n----------------')
        print('Found:\t\t' + time_found + ' seconds.')
        print('Discussion:\t' + time_discussion + ' seconds.')
        if link_added:
            print('Link:\t\t' + time_link + ' seconds.')
        print('Comment:\t' + time_comment + ' seconds.')

        #End the program.
        exit()

    #Refresh reddit token every 30 minutes.
    if time() - refresh_time > refresh_int:
        reddit.refresh_access_information(reddit_oauth)
        refresh_time = time()

    #Wait given period.
    sleep(loop_int)