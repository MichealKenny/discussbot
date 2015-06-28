#!/usr/bin/python3
from praw.errors import AlreadySubmitted
from sys import argv, exit, stdout
from bs4 import BeautifulSoup
from time import time, sleep
from requests import get
from praw import Reddit
from json import loads
import logging

#Logging configuration.
logging.basicConfig(filename='errors.log', format='%(asctime)s: %(message)s')

#Load configuration file.
try:
    config_file = open('config.json', 'r')
    config = loads(config_file.read())
    config_file.close()

except FileNotFoundError:
    print('[Error]: config.json not found, make sure to edit and rename sample_config.json')
    exit()

#Get json root titles.
show = config['shows'][argv[1]]
settings = config['settings']
templates = config['templates']

#Get settings.
version = '1.5'
user_agent = settings['user_agent'].format(version=version)
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

print('discussbot-cli v{0} - Episode Discussion Bot.\n---------------------------------------------'.format(version))
print('Logging into Reddit..', end='\t'); stdout.flush()

bs4_attrs = {'class': 'yt-uix-sessionlink yt-uix-tile-link  spf-link  yt-ui-ellipsis yt-ui-ellipsis-2'}

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
        html = get('https://www.youtube.com/channel/{channel_id}/videos'.format(channel_id=channel), headers=headers).text
        soup = BeautifulSoup(html)
        latest = soup.find_all('a', attrs=bs4_attrs)[0]

        video_title = latest.string
        video_id = latest.get('href').replace('/watch?v=', '')

    except:
        logging.warning('Error with Youtube API.')
        sleep(loop_int); continue

    #If the given episode number is in the latest video title.
    if episode in video_title.lower():
        #Record time found.
        time_found = time()
        #Discussion thread information.
        submission_title = templates['title'].format(show_code=argv[1].upper(), episode=episode)
        text_body = templates['thread'].format(full_name=podcast, episode=episode,
                                               video_title=video_title, video_id=video_id)

        try:
            #Try to post the discussion thread to Reddit.
            print('Available.')
            print('Posting to Reddit..', end='\t'); stdout.flush()
            dthread_permalink = reddit.submit(subreddit, submission_title, text=text_body).permalink

            time_discussion = str(round(time() - time_found, 1))
            print('Submitted.')

        except:
            authenticated = False
            while not authenticated:
                try:
                    reddit.refresh_access_information(reddit_oauth)
                    refresh_time = time()
                    authenticated = True

                except:
                    sleep(5); pass

            continue

        #Load comment for video thread.
        reddit_comment = templates['comment'].format(link=dthread_permalink)

        try:
            #If the video has not been linked to, add a link to the video.
            print('Adding link..', end='\t\t'); stdout.flush()
            vthread_permalink = reddit.submit(subreddit, video_title, url='https://youtube.com/watch?v=' + video_id).permalink
            time_link = str(round(time() - time_found, 1))
            print('Submitted.')

            #Then add a comment to our own video link.
            link = reddit.get_submission(vthread_permalink)
            link_added = True

        except AlreadySubmitted:
            print('Already Submitted.')
            #Get the latest 5 submissions on the shows subreddit.
            subreddit_new = reddit.get_subreddit(subreddit).get_new(limit=5)
            reddit_comment = templates['alt_comment'].format(link=dthread_permalink)

            #For each thread, check if the video has already been linked too.
            for thread in subreddit_new:
                #If it has, add the comment and break the loop.
                if video_id in thread.url:
                    link = thread
                    link_added = False
                    break

        print('Adding comment..', end='\t'); stdout.flush()
        link.add_comment(reddit_comment)
        time_comment = str(round(time() - time_found, 1))
        print('Submitted.')

        #Print time statistics to stdout.
        print('\nTime Statistics:\n----------------')
        print('Discussion:\t' + time_discussion + ' seconds.')
        if link_added:
            print('Link:\t\t' + time_link + ' seconds.')
        print('Comment:\t' + time_comment + ' seconds.')

        #End the program.
        exit()

    #Refresh reddit token every 30 minutes.
    if time() - refresh_time > refresh_int:
        authenticated = False
        while not authenticated:
            try:
                reddit.refresh_access_information(reddit_oauth)
                refresh_time = time()
                authenticated = True

            except:
                sleep(5); pass

    #Wait given period.
    sleep(loop_int)
