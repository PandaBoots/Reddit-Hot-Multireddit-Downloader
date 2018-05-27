# Reddit-Hot-Multireddit-Downloader
Downloads the first Nth amount of posts from a provided subreddit or multireddit

## Dependencies:

This project uses python 3.6 which can be downloaded at the bottom of the page [here](https://www.python.org/downloads/release/python-365/)

In order to use this script two additional modules muse be installed from ```dependencies.txt``` which as BeautifulSoup4 and Praw.

These can be installed by navigating to the python scripts folder located at 

```C:\Users\username\AppData\Local\Programs\Python\Python36\Scripts``` and the command prompt.

Only two commands must be run in the command prompt:

```pip3 install BeautifulSoup4```

```pip3 install praw```

After those are installed you are almost ready to run the script

## Reddit API Keys

Reddit API keys must be created to scrape the pages of each subreddit. This can very easily [here](https://old.reddit.com/prefs/apps)

[This is where the API details will be found](https://i.imgur.com/gR2cLyO.png)

fill out the documentation for a new app and copy and paste the areas in pink into downloaderconstants.py under client_id and client_secret

The client ID should be significantly shorter than the client secret:

```client_id = dSNykkqOpIcFjg```
```client_secret = woFyFjir5U07OSUPoCMOp1ATG80```


## Modifying variables in downloaderconstants.py:

#### basepath

is the directory where you want the files to be downloaded to and it is a raw string. For simplicity's sake, do not leave the trailing '\' character in the path because it will escape the following ' character used to close the string

Example:
```basepath = r'D:\redditdownloads'```


#### substodownload

is either a multireddit of subreddits separated by '+' or a singular subreddit. If you want to scrape all the pictures from your subscriptions a multireddit of your subscirptions can be made [here](https://old.reddit.com/subreddits) by clicking "multireddit of your subscriptions" on the right-hand sidebar

Eaxmple: 

```substodownload = 'pics'```
```substodownload = 'wallpapers+pics+funny'```

#### numposts

This is the number of posts that will be collected from the hot section of each subreddit. It will include any stickied posts (which will be ignored if they are a self post)

Example:

```numposts = 7```


#### verbose

This is a True of False value to determine the amount of output information that will be displayed

#### timebetweenupdates

This is the number of seconds that the program will wait before refreshing the data. When the data is refreshed, previously downloaded posts will have their data updated and new posts on the front page will be downloaded

The recommended value is 1800 seconds (30 minutes)

#### minscore

This is the lower bound of a score that will be downloaded. Anything below this score will not be downloaded. However, if a post is below this score and later is above the score and still on the front page, it will be downloaded. 

Example:

```minscore = 50```
