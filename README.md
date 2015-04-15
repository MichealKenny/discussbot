discussbot v1.2 - Youtube video discussion bot for Reddit.
===

If you're a podcaster or you moderate a subreddit for a podcast, discussbot can help you out. Everytime an episode of the podcast is uploaded to Youtube, discussbot will post an episode discussion thread to reddit, and if it hasn't been done already, submit a link to the episode as well.

discussbot is really fast, I feel confident in saying it is the fastest Youtube video bot on Reddit, it can post a video within 3 seconds of it being published to Youtube, that's 50x faster than even our closest competitor.

Requirements
===

* Python Reddit API Wrapper (PRAW)
* BeautifulSoup4 (bs4)
* Project on Reddit for OAuth.
* At least one Reddit refresh token generated with the token_util or otherwise.
* At least one Youtube channel_id, legacy usernames won't work.
