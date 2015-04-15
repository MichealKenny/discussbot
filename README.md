discussbot v1.2 - Youtube video discussion bot for Reddit.
===

If you're a podcaster or you moderate a subreddit for a podcast, discussbot can help you out. Everytime an episode of the podcast is uploaded to Youtube, discussbot will post an episode discussion thread to reddit, and if it hasn't been done already, submit a link to the episode as well.

discussbot is really fast, I feel confident in saying it is the fastest Youtube video bot on Reddit, it can post a video within 3 seconds of it being published to Youtube, that's 50x faster than even our closest competitor. Why is that, well it's because we don't use the Youtube Data API (anymore), v2 was deprecated and v3 is slow as hell, so we decided to move away from it and return to the days of no APIs, web scraping with BeautifulSoup4(bs4), until v3 gets faster or gets replaced, discussbot will keep using bs4.

Requirements
===

* Python Reddit API Wrapper (PRAW)
* BeautifulSoup4 (bs4)
* Project on Reddit for OAuth.
* At least one Reddit refresh token generated with the token_util or otherwise.
* At least one Youtube channel_id, legacy usernames won't work.
