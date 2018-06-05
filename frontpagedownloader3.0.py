import praw, requests, os, time, shutil, multiprocessing, re, downloaderconstants

mainbase = downloaderconstants.basepath
r = praw.Reddit(client_id=downloaderconstants.client_id, client_secret=downloaderconstants.client_secret,
                user_agent='collects information from the front page of u/PM_ME_U_IN_THE_POSE')


# class that takes in data form the post objects returned from the reddit api and standardizes the information
class superclass:

    def __init__(self, data, oldscore=False):
        self.url = str(data[0])
        self.title = self.modtitle(str(data[1]))
        self.ida = str(data[3])
        self.subreddit = str(data[4])
        self.author = str(data[5])
        self.is_self = data[6]

        if oldscore:
            self.score = oldscore
        else:
            self.score = data[2]

        if 'gfycat' in self.url:
            self.extension = '.mp4'
        else:
            self.extension = '.jpg'

        self.info = self.subreddit + " " + self.author + " " + str(self.score) + ' ' + self.title + ' ' + self.ida + \
            ' ' + self.url
        self.dirname = r'downloads_'

    def folderpath(self):
        return os.path.join(mainbase, self.dirname, self.subreddit, self.author)

    def storagepath(self, score=False):
        if score:
            # self.oldscore = self.score
            self.score = score

        return os.path.join(mainbase, self.dirname, self.subreddit, self.author, "[" + self.author + "]" +
                            "[" + str(self.score) + "]" + self.title + self.ida + self.extension)

    def allpath(self):
        return os.path.join(mainbase, self.dirname, self.subreddit)

    def allstoragepath(self, score=False):
        if score:
            # self.oldscore = self.score
            self.score = score

        return os.path.join(mainbase, self.dirname, self.subreddit, "[" + self.author + "]" + "[" + str(self.score)
                            + "]" + self.title + self.ida + self.extension)

    def totalpath(self):
        return os.path.join(mainbase, self.dirname, '_allsubreddits')

    def totalstoragepath(self, score=False):
        if score:
            # self.oldscore = self.score
            self.score = score

        return os.path.join(mainbase, self.dirname, '_allsubreddits', "[" + str(self.score) + "]" + "[" + self.author
                            + "]" + '[' + self.subreddit + ']' + self.title + self.ida + self.extension)

    def modurl(self):
        url = self.url
        if 'http:' in url[:5]:
            url = 'https:' + url[5:]

        if 'www' in url[:4]:
            url = 'https://' + url

        if 'm.imgur' in url:
            url = url[:5] + url[6:]

        if 'i.i' not in url and 'i.r' not in url and 'tumblr' not in url and 'v.redd' not in url and '.' \
                not in url[-5:] and 'gfycat' not in url:
            url = url[0:8] + 'i.' + url[8:] + '.jpg'

        if 'gfycat' in url:

            if 'giant' in url[:18]:
                # print ('giant url organizer')
                url = url[0:8] + url[14:]
                # print ('inital url after mutation', url)

                if '.mp4' in url:
                    url = url[:-4]
                    # print ('mp4 url', url)

                elif '.webm' in url:
                    # print('webm url', url)
                    url = url[:-5]

            elif 'pl/gifs/detail' in url:
                url = url.replace('/pl/gifs/detail/', '/')
                #  print ('replaced' , url)

            elif 'gifs/detail' in url:
                url = url[:19] + url[31:]
                #  print ('remove details url', url)

            jsonurl = url[:19] + "cajax/get/" + url[19:]
            info = requests.get(jsonurl)
            data = info.json()

            try:
                url = data['gfyItem']['mp4Url']
            except KeyError:
                # print ("KeyError in gfycat handler, url does not exist, ", e)
                addfulllog(self.ida, os.path.join(mainbase, r'downloadlog\fulllog.txt'))
                return False

            return url
        return url

    def modtitle(self, title):
        bannedchars = {
            "\\": " ",
            "/": " ",
            "?": '.',
            "!": '.',
            "\"": '..',
            "\'": "..",
            ">": "-",
            "<": "-",
            "*": "aesterisk",
            '|': 'pipechar',
            ':': 'COLON',
            ';': 'semicolon'}

        for character in bannedchars.keys():
            title = title.replace(character, bannedchars[character])

        return title[:172]


# generates a dictionary of IDs and objects of the submission and passes it to multiprocessing for handling
def getposts(multi, limit):
    postdict = {}
    length = len(multi)
    progression = 0

    for subreddit in multi:
        try:
            posts = r.subreddit(subreddit).hot(limit=limit)

            for item in posts:
                superobj = superclass([item.url, item.title, item.score, item.id, item.subreddit, item.author,
                                       item.is_self])
                postdict[item.id] = superobj
            time.sleep(.5)

        except Exception as e:
            msg = ('ERROR ' + str(e))
            print(msg)
            addfulllog(msg, os.path.join(mainbase, r'downloadlog\fulllog.txt'))

        progression += 1
        if progression % 10 == 0 and downloaderconstants.verbose:
            print(str(100 * progression / length)[:4] + '%')
    multiprocessposts(postdict)


# function to create processes and target the filter funciton checkdownload 
def multiprocessposts(postdict):
    with open(os.path.join(mainbase, r'downloadlog\previouslydownloaded.txt'), 'r') as oldfile:
        oldposts = oldfile.readlines()
        oldposts = ''.join(oldposts)
    for key in postdict.keys():
        p = multiprocessing.Process(target=checkdownload, args=(key, postdict[key], oldposts))
        p.start()


# function to request data from the url generated in the superclass and download the information and copy it to dirs
def downloadimage(postobject):

    if downloaderconstants.verbose:
        print('download', postobject.info)

    url = postobject.modurl()
    if url:
        response = requests.get(url)

        for path in [postobject.folderpath(), postobject.allpath(), postobject.totalpath()]:
            try:
                os.makedirs(path)
            except FileExistsError:
                pass

        # download the actual content
        try:
            with open(str(postobject.storagepath()), 'wb') as fo:
                for chunk in response.iter_content(4096):
                    fo.write(chunk)

            # copy the content to other dirs
            shutil.copy(postobject.storagepath(), postobject.allstoragepath())
            shutil.copy(postobject.storagepath(), postobject.totalstoragepath())

            # log that shit
        except Exception as e:
            if downloaderconstants.verbose:
                print('-->: ', postobject.info)
                print(e)

        finally:
            addfulllog(postobject.info, os.path.join(mainbase, r'downloadlog\fulllog.txt'))
            addfulllog(postobject.ida, os.path.join(mainbase, r'downloadlog\previouslydownloaded.txt'))


# renames all the files and updates the scores 
def updateinformation(postobject):
    base = os.path.join(mainbase, r'downloads_', str(postobject.subreddit), str(postobject.author))
    oldscore = 0
    newscore = str(postobject.score)

    try:
        path = os.listdir(base)
    except FileNotFoundError:
        # print ('renamed ERROR: ', base, ' was downloaded somewhere else!')
        return 0

    for item in path:
        if postobject.ida in item:
            dirtofile, file_extension = os.path.splitext(item)
            regexsearch = re.compile(r'\d*\d')
            f = regexsearch.search(str(dirtofile)[(len(str(postobject.author))+2):])
            oldscore = int(f.group())
            break
    if oldscore == 0:
        print('return-- early file not found :(')
        return 0

    if postobject.score > oldscore:
        try:
            os.rename(postobject.storagepath(oldscore), postobject.storagepath(newscore))
            os.rename(postobject.allstoragepath(oldscore), postobject.allstoragepath(newscore))
            os.rename(postobject.totalstoragepath(oldscore), postobject.totalstoragepath(newscore))
        except Exception as e:
            addfulllog(str(e), os.path.join(mainbase, r'downloadlog\fileexistserror.txt'))

        if downloaderconstants.verbose:
            print('renaming scores:', oldscore, newscore, postobject.info)


# filter function to determine how the post should be processed (download, update, ignore)
def checkdownload(item, postobject, oldposts):
    # low upvote post save for later

    if int(postobject.score) < 50:
        # print ('passing post', postobject.url, 'because of the score ', postobject.score)
        return 0

    # already downloaded
    elif item in oldposts:
        updateinformation(postobject)
    # disregard if its not tumblr, imgur, gfycat, or reddit

    elif "tumblr" not in postobject.url and 'imgur' not in postobject.url and 'gfycat' not in postobject.url and 'redd'\
            not in postobject.url:
        return 0

    # disregard if its an imgur .gif or .gifv
    elif '.gif' in postobject.url or '.gifv' in postobject.url or 'v.redd' in postobject.url:
        return 0

    # dont download if its an imgur album or comments section
    elif '/a/' in postobject.url or '/r/' in postobject.url:
        return 0

    elif postobject.is_self:
        return 0

    else:
        downloadimage(postobject)


# writes the data to various logs
def addfulllog(data, path):
    path = os.path.join(mainbase, path)

    with open(path, 'a') as newfile:
        try:
            newfile.write(data)
        except Exception as e:
            newfile.write('there was an encode error with this file' + str(e))
        newfile.write("\n")


# starter function
if __name__ == "__main__":

    multi = downloaderconstants.substodownload.split('+')
    limit = downloaderconstants.numposts
    
    try:
        logpath = os.path.join(mainbase, r'downloadlog')
        os.makedirs(logpath)
        for filename in ('fileexistserror.txt', 'fulllog.txt', 'previouslydownloaded.txt'):
            with open(os.path.join(logpath, filename), 'w') as file:
                pass

    except FileExistsError:
        if downloaderconstants.verbose:
            print('dirs exist')

    print('number of subreddits to download: ', len(multi))

    while True:
        # split the string from downloader constants and pass it along with the number of posts required
        getposts(multi, limit)
        print('Waiting for next update')
        time.sleep(downloaderconstants.timebetweenupdates)
