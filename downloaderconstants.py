#example: basepath = r'D:\redditdownloads'
#make sure there is no trailing '\' in the path as it will escape the final ' that ends the string
basepath = r''

# example: substodownload = 'wallpapers+pics+funny'
substodownload = ""

#example: numposts = 7
numposts = 7

# reddit api credentials that are generated on reddit.com/prefs/apps
#Fake examples: 
#client_id = 'dSNykkqOpIcFjg'
#client_secret = 'woFyFjir5U07OSUPoCMOp1ATG80'
client_id = ''
client_secret = ''

#verbose True/ False
verbose = False

# time between each update of downloader (in seconds) recommended value is 1800 (30mins)
timebetweenupdates = 1800

#recommended lower bound of score is 50 (depends on the size of subreddits you are downloading from)
minscore = 50
