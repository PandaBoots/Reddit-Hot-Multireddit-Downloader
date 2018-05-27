import praw, requests, hashlib, os, time, shutil, multiprocessing, re
import downloaderconstants

# reddit api
r = praw.Reddit(client_id=downloaderconstants.client_id, client_secret=downloaderconstants.client_secret,
                user_agent='collects information from the front page of u/PM_ME_U_IN_THE_POSE')

multi = downloaderconstants.substodownload

# generates a list of all posts in all subreddits listed under multi
def getposts(multi, limit):

    postdict = {}
    length = len(multi)
    progression = 0

    for subreddit in multi:
        try:
            posts = r.subreddit(subreddit).hot(limit=limit)

            for item in posts:
                hashedurl = hashing(item.url)
                postdict[hashedurl] = item
            time.sleep(.5)

        except Exception as e:
            msg = ('ERROR ' + str(e))
            print(msg)
            addfulllog(msg,r'downloadlog\fulllog.txt')
        progression += 1
        if progression%10 ==0 and downloaderconstants.verbose:
            print (str(100* progression / length)[:4] + '%')
    multiprocessposts(postdict)


# sorts sends different elements of the postdict through the filter function "checkdownload" with multiprocessing
def multiprocessposts(postdict):
    with open(os.path.join(downloaderconstants.basepath, r'downloadlog\previouslydownloaded.txt'), 'r') as file:
        oldposts = file.readlines()
        oldposts = ''.join(oldposts)

    for key in postdict.keys():
        p = multiprocessing.Process(target=checkdownload, args=(key, postdict[key], oldposts))
        p.start()


# filters the each post into different categories
def checkdownload(item, postobject, oldposts):
    # low upvote post save for later

    if int(postobject.score) < 50:
        # print ('passing post', postobject.url, 'because of the score ', postobject.score)
        return 0

    # already downloaded
    elif item in oldposts:
        updateinformation(postobject)
    # disregard if its not tumblr, imgur, gfycat, or reddit

    elif "tumblr" not in postobject.url and 'imgur' not in postobject.url and 'gfycat' not in postobject.url and 'redd' \
            not in postobject.url:
        return 0

    # disregard if its an imgur .gif or .gifv
    elif '.gif' in postobject.url or '.gifv' in postobject.url or 'v.redd' in postobject.url:
        return 0

    # dont download if its an imgur album or comments section
    elif '/a/' in postobject.url or '/r/' in postobject.url:
        return 0

    elif postobject.is_self == True:
        return 0

    # download gfycat posts
    elif 'gfycat' in postobject.url:
        downloadImage(postobject, item, 2)

    # downlaod direct links to imgur and reddit
    elif 'i.i' not in postobject.url and 'i.r' not in postobject.url and 'tumblr' not in postobject.url and \
        'v.redd' not in postobject.url and '.' not in str(postobject.url)[-5:]:
        downloadImage(postobject, item, 1)

    # just catch all of downloads it probably works
    else:
        downloadImage(postobject, item, 0)

# md5 hashing function to hash the links no nothing is downloaded twice in a row
def hashing(input):
    name = bytes(input, 'utf-8')
    hash = hashlib.new('md5')
    hash.update(name)
    hash = hash.hexdigest()
    return hash


# downlad function for the files
def downloadImage(postobject, hashoflink, extension):
    # gets the data on the post
    retlist = metadata(postobject)
    title, subreddit, author, score, url =retlist
    # prints info for user to follow along
    info = subreddit + " " + author + " " + score + ' ' + title + ' ' + hashoflink + ' ' + url

    if downloaderconstants.verbose:
        print('download', info)

    # bunch of paths to store pictures in
    pathlist = pathhandler(retlist, str(hashoflink))
    folderpath, storagepath, allpath, allstoragepath, totalpath, totalstoragepath = pathlist

    if 'www' in url[:4]:
        url = 'https://' + url
    if 'm.imgur' in url:
        extension = 1
        url = url[:5] + url[6:]
        # print('HANDLING m.imgur: ', url)

    # adds the needed file extension to the path depending on what kind of link was found in the parent function
    if extension == 0:               # i.imgur or r.rddt
        storagepath += '.jpg'
        allstoragepath += '.jpg'
        totalstoragepath += '.jpg'

    elif extension == 1:            # imgur.com/AafaAsF type url
        storagepath += '.jpg'
        allstoragepath += '.jpg'
        totalstoragepath += '.jpg'

        if url[:5] == 'http:':
            url = 'https:' + url[5:]

        #make the url a direct link aka imgur.com/abcd -> i.imgur.com/abcd.jpg
        url = url[0:8] + 'i.' + url[8:] + '.jpg'

    # gfycat
    else:
        storagepath += '.mp4'
        allstoragepath += '.mp4'
        totalstoragepath += '.mp4'

        url = gfycathandler(url, hashoflink)

    response = requests.get(url)

    # make different dirs in case they are not there
    try:
        os.makedirs(folderpath)
    except Exception as e:
        pass
    try:
        os.makedirs(allpath)
    except Exception as e:
        pass
    try:
        os.makedirs(totalpath)
    except Exception as e:
        pass

    # download the actual content
    with open(storagepath, 'wb') as fo:
        for chunk in response.iter_content(4096):
            fo.write(chunk)

    # copy the content to other dirs
    shutil.copy(storagepath, allstoragepath)
    shutil.copy(storagepath, totalstoragepath)

    # log that shit
    addfulllog(info, r'downloadlog\fulllog.txt')
    addfulllog(str(hashoflink), r'downloadlog\previouslydownloaded.txt')


#  generate paths depending on what subreddit is being used
def pathhandler(retlist, hashoflink):
    if hashoflink == 0:
        hashoflink = ''
    title = retlist[0]
    subreddit = retlist[1]
    author = retlist[2]
    score = retlist[3]

    # url = retlist[4]

    # stores each photo in the /subreddit/author folder
    folderpath = os.path.join(downloaderconstants.basepath, r'downloads_', subreddit, author)
    storagepath = os.path.join(downloaderconstants.basepath, r'downloads_', subreddit, author,
                               "[" + author + "]" + "[" + score + "]" + title + hashoflink)

    # stores each photo in the subreddit folder
    allpath = os.path.join(downloaderconstants.basepath, r'\downloads_', subreddit)
    allstoragepath = os.path.join(downloaderconstants.basepath, r'downloads_', subreddit,
                                  "[" + author + "]" + "[" + score + "]" + title + hashoflink)
    # stores in all subreddits
    totalpath = os.path.join(downloaderconstants.basepath,r'downloads_', '_allsubreddits')
    totalstoragepath = os.path.join(downloaderconstants.basepath, r'downloads_', '_allsubreddits',
                                    "[" + score + "]" + "[" + author + "]" + '[' + subreddit + ']' + title + hashoflink)
    return [folderpath, storagepath, allpath, allstoragepath, totalpath, totalstoragepath]


#  gets the mp4 link for the gfycat post and returns the URL for download
def gfycathandler(url, hash):
    if url[:5] == 'http:':
        url = 'https:' + url[5:]

    elif 'www' in url[:5]:
        url = 'https://' + url

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
        mp4url = data['gfyItem']['mp4Url']
    except KeyError as e:
        # print ("KeyError in gfycat handler, url does not exist, ", e)
        addfulllog(hash, r'downloadlog\fulllog.txt')
        return 0

    return mp4url


#  just retrieves different data on the post and returns it in string format
def metadata(postobject):
    author = postobject.author
    score = postobject.score
    url = postobject.url
    subreddit = postobject.subreddit
    title = fileinputvalidation(str(postobject.title))

    returnlist = [str(title), str(subreddit), str(author), str(score), str(url)]
    return returnlist


#  filters characters that should not be used in windows naming conventions for files
def fileinputvalidation(inputstr):
    bannedchars ={
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
        inputstr = inputstr.replace(character, bannedchars[character])

    return inputstr


#  detailed log of all data including errors
def addfulllog(data, path):
    path = os.path.join(downloaderconstants.basepath, path)

    with open(path, 'a') as newfile:
        newfile.write("\n")
        try:
            newfile.write(data)
        except Exception as e:
            newfile.write('there was an encode error with this file' + str(e))


# updates old post scores and info stuff
def updateinformation(postobject):
    base = os.path.join(downloaderconstants.basepath, r'downloads_', str(postobject.subreddit), str(postobject.author))
    oldscore = 0

    try:
        path = os.listdir(base)
    except FileNotFoundError:
        # print ('renamed ERROR: ', base, ' was downloaded somewhere else!')
        return 0
    for item in path:
        if postobject.title in item:
            dirtofile, file_extension = os.path.splitext(item)
            regexsearch = re.compile(r'\d*\d')
            f = regexsearch.search(str(dirtofile)[(len(str(postobject.author))+2):])
            oldscore = int(f.group())
            break
    if oldscore == 0:
        return 0

    if str(hashing(postobject.url)) in dirtofile:
        hashvar = str(hashing(postobject.url))
    else:
        hashvar =0

    if postobject.score > oldscore:
        pathlistnew = pathhandler([str(postobject.title),str(postobject.subreddit),str(postobject.author),str(postobject.score),str(postobject.url)], hashvar)
        pathlistold = pathhandler([str(postobject.title),str(postobject.subreddit),str(postobject.author),str(oldscore),str(postobject.url)], str(hashing(postobject.url)))

        storagepath0 = pathlistnew[1] + file_extension
        allstoragepath0 = pathlistnew[3] + file_extension
        totalstoragepath0 = pathlistnew[5] + file_extension

        storagepath1 = pathlistold[1] + file_extension
        allstoragepath1 = pathlistold[3] + file_extension
        totalstoragepath1 = pathlistold[5] + file_extension

        try:
            os.rename(storagepath1, storagepath0)
            os.rename(allstoragepath1, allstoragepath0)
            os.rename(totalstoragepath1, totalstoragepath0)
        except Exception as e:
            addfulllog(str(e), os.path.join(downloaderconstants.basepath, r'downloadlog\fileexistserror.txt'))

        if downloaderconstants.verbose:
            print ('renaming scores:', oldscore, str(postobject.score), 'with paths: ', storagepath1, storagepath0)

if __name__ == "__main__":
    start = time.time()
    limit = downloaderconstants.numposts
    multi = multi.split('+')

    try:
        logpath = os.path.join(downloaderconstants.basepath, r'downloadlog')
        os.makedirs(logpath)

        with open (os.path.join(logpath,'fileexistserror.txt'), 'w') as file:
            pass
        with open(os.path.join(logpath, 'fulllog.txt'), 'w') as file:
            pass
        with open(os.path.join(logpath, 'previouslydownloaded.txt'), 'w') as file:
            pass
    except FileExistsError:
        if downloaderconstants:
            print('dirs exist')

    print ('number of subreddits to download: ', len(multi))

    while True:
        getposts(multi, limit)
        print ('Waiting for next update')
        time.sleep(downloaderconstants.timebetweenupdates)

    # print('runtime:', str(time.time() - start), 'seconds')