import urllib, urllib2, re, sys, cookielib, os
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
from xbmcgui import ListItem
import CommonFunctions
import hosts

# plugin constants
version = "0.0.1"
plugin = "ApniTV - " + version

__settings__ = xbmcaddon.Addon(id='plugin.video.apnitv')
rootDir = __settings__.getAddonInfo('path')
if rootDir[-1] == ';':
    rootDir = rootDir[0:-1]
rootDir = xbmc.translatePath(rootDir)
settingsDir = __settings__.getAddonInfo('profile')
settingsDir = xbmc.translatePath(settingsDir)
cacheDir = os.path.join(settingsDir, 'cache')
pluginhandle = int(sys.argv[1])
# For parsedom
common = CommonFunctions
common.plugin = plugin
common.dbg = False
common.dbglevel = 3

programs_thumb = os.path.join(__settings__.getAddonInfo('path'), 'resources', 'media', 'programs.png')
topics_thumb = os.path.join(__settings__.getAddonInfo('path'), 'resources', 'media', 'topics.png')
search_thumb = os.path.join(__settings__.getAddonInfo('path'), 'resources', 'media', 'search.png')
next_thumb = os.path.join(__settings__.getAddonInfo('path'), 'resources', 'media', 'next.png')
movies_thumb = os.path.join(__settings__.getAddonInfo('path'), 'resources', 'media', 'movies.jpg')
tv_thumb = os.path.join(__settings__.getAddonInfo('path'), 'resources', 'media', 'television.jpg')
shows_thumb = os.path.join(__settings__.getAddonInfo('path'), 'resources', 'media', 'shows.png')
video_thumb = os.path.join(__settings__.getAddonInfo('path'), 'resources', 'media', 'movies.png')



########################################################
## URLs
########################################################
BASE_URL = 'http://apni.tv'
VIDEOS_URL = BASE_URL + '/videos'
MOVIES_URL = BASE_URL + '/movies'

########################################################
## Modes
########################################################
M_DO_NOTHING = 0
M_BROWSE_CHANNELS = 10
M_BROWSE_CHANNEL_CONTENTS = 11
M_BROWSE_EPISODES = 12
M_BROWSE_MOVIES = 20
M_BROWSE_MOVIE_VIDEOS = 21
M_BROWSE_ALL_MOVIES = 22
M_BROWSE_VIDEOS = 30
M_PLAY_SERIAL = 40
M_PLAY_VIDEO = 41
M_PLAY_MOVIES = 42

##################
## Class for items
##################
class MediaItem:
    def __init__(self):
        self.ListItem = ListItem()
        self.Image = ''
        self.Url = ''
        self.Isfolder = False
        self.Mode = ''
        
## Get URL
def getURL(url):
    print plugin + ' getURL :: url = ' + url
    #cj = cookielib.LWPCookieJar()
    #opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    #opener.addheaders = [('User-Agent', 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2;)')]
    #usock = opener.open(url)
    #response = usock.read()
    #usock.close()
    #return response
    result = common.fetchPage({"link": url})
    if result["status"] == 200:
        return result["content"]
    else:
        return none

# Save page locally
def save_web_page(url, filename):
    f = open(os.path.join(cacheDir, filename), 'w')
    data = getURL(url)
    f.write(data)
    f.close()
    return data
    
# Read from locally save page
def load_local_page(filename):
    f = open(os.path.join(cacheDir, filename), 'r')
    data = f.read()
    f.close()
    return data


def cleanHtml(dirty):
    # Remove HTML codes
    clean = re.sub('&quot;', '\"', dirty)
    clean = re.sub('&#039;', '\'', clean)
    clean = re.sub('&#215;', 'x', clean)
    clean = re.sub('&#038;', '&', clean)
    clean = re.sub('&#8216;', '\'', clean)
    clean = re.sub('&#8217;', '\'', clean)
    clean = re.sub('&#8211;', '-', clean)
    clean = re.sub('&#8220;', '\"', clean)
    clean = re.sub('&#8221;', '\"', clean)
    clean = re.sub('&#8212;', '-', clean)
    clean = re.sub('&amp;', '&', clean)
    clean = re.sub("`", '', clean)
    clean = re.sub('<em>', '[I]', clean)
    clean = re.sub('</em>', '[/I]', clean)
    clean = re.sub('<strong>', '', clean)
    clean = re.sub('</strong>', '', clean)
    clean = re.sub('<br />', '\n', clean)
    return clean


def BuildMainDirectory():
    ########################################################
    ## Mode = None
    ## Build the main directory
    ########################################################
    # set content type so library shows more views and info
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    
    # Get featured homepage contents
    data = save_web_page(BASE_URL, 'apnitv.html')
    #data = load_local_page('apnitv.html')
    items = common.parseDOM(data, "div", attrs={ "class": "update [^a].+?[^']"})
    
    MediaItems = []
    for item in items:
        #print item
        Mediaitem = MediaItem()
        Title = common.parseDOM(item, "img", ret="alt")[0]
        #print Title
        
        Mediaitem.Image = common.parseDOM(item, "img", ret="src")[0]
        IsSerials = False
        if Mediaitem.Image.find('serials') > 0:
            IsSerials = True
	Url = None
        if IsSerials:
            spans = common.parseDOM(item, "span", attrs={ "class": "lowbeam"})
            for span in spans:
                href = common.parseDOM(span, "a", ret="href")
                if len(href) > 0:
                    Url = href[0]
                    Title = common.parseDOM(span, "a", ret="title")[0]
                else:
                    Plot = span
            Mediaitem.Mode = M_PLAY_SERIAL
        else:
	    continue
            Url = common.parseDOM(item, "a", ret="href")[0]
            Plot = common.parseDOM(item, "span", attrs={ "class": "highbeam"})[0]
            Mediaitem.Mode = M_PLAY_MOVIES
        if not Url:
	    continue
	#print Url
        Plot = cleanHtml(Plot)
        
        #print Url
        Title = Title.encode('utf-8')
        #print Title
        Mediaitem.Url = sys.argv[0] + "?url=" + urllib.quote_plus(Url) + "&mode=" + str(Mediaitem.Mode) + "&name=" + urllib.quote_plus(Title)
        Mediaitem.ListItem.setInfo('video', { 'Title': Title, 'Plot': Plot})
        Mediaitem.ListItem.setThumbnailImage(Mediaitem.Image)
        Mediaitem.ListItem.setLabel(Title)
        MediaItems.append(Mediaitem)
    
    Menu = [(__settings__.getLocalizedString(30010), '', tv_thumb, M_BROWSE_CHANNELS),
            (__settings__.getLocalizedString(30011), MOVIES_URL, movies_thumb, M_BROWSE_MOVIES),
            (__settings__.getLocalizedString(30012), VIDEOS_URL, programs_thumb, M_BROWSE_VIDEOS)]
    for Title, Url, Thumb, Mode in Menu:
        Mediaitem = MediaItem()
        Mediaitem.Url = sys.argv[0] + "?url=" + urllib.quote_plus(Url) + "&mode=" + str(Mode) + "&name=" + urllib.quote_plus(Title)
        Mediaitem.ListItem.setThumbnailImage(Thumb)
        Mediaitem.ListItem.setLabel(Title)
        Mediaitem.Isfolder = True
        MediaItems.append(Mediaitem)
    
    addDir(MediaItems)

    # End of Directory
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    ## Set Default View Mode. This might break with different skins. But who cares?
    SetViewMode()
   
 
def BrowseChannels():
    ###########################################################
    ## Mode == M_BROWSE_CHANNELS
    ## BROWSE CHANNELS
    ###########################################################   
    # set content type so library shows more views and info
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    
    # Get featured homepage contents
    data = load_local_page('apnitv.html')
    items = common.parseDOM(data, "div", attrs={ "id": "dropmenu1_a", "class": "menudrop"})[0] 
    ChannelName = common.parseDOM(items, "a")
    ChannelUrl = common.parseDOM(items, "a", ret="href")
    MediaItems = []
    for i in range(len(ChannelName)):
        #print ChannelName[i] + ' ' + ChannelUrl[i]
        Mediaitem = MediaItem()
        Title = ChannelName[i]
        Url = ChannelUrl[i]
        #print Url
        Mediaitem.Image = tv_thumb
        Mediaitem.Mode = M_BROWSE_CHANNEL_CONTENTS
        #print Url
        Title = Title.encode('utf-8')
        #print Title
        Mediaitem.Url = sys.argv[0] + "?url=" + urllib.quote_plus(Url) + "&mode=" + str(Mediaitem.Mode) + "&name=" + urllib.quote_plus(Title)
        Mediaitem.ListItem.setInfo('video', { 'Title': Title})
        Mediaitem.ListItem.setThumbnailImage(Mediaitem.Image)
        Mediaitem.ListItem.setLabel(Title)
        Mediaitem.Isfolder = True
        MediaItems.append(Mediaitem)
    addDir(MediaItems)
    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
    # End of Directory
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    ## Set Default View Mode. This might break with different skins. But who cares?
    #xbmc.executebuiltin("Container.SetViewMode(503)")
    SetViewMode()
    

def BrowseChannelContents(ChUrl=''):
    ###########################################################
    ## Mode == M_BROWSE_CHANNEL_CONTENTS
    ## BROWSE CHANNEL CONTENTS
    ###########################################################   
    # set content type so library shows more views and info
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    
    # Get featured homepage contents
    #data = load_local_page('sony.htm')
    data = getURL(ChUrl)
    items = common.parseDOM(data, "div", attrs={ "class": "serial[ desc]*"})
    MediaItems = []
    print 'item count: ' + str(len(items))
    for item in items:
        #print item
        Mediaitem = MediaItem()
        strong = common.parseDOM(item, "strong")[0]
        Title = common.parseDOM(strong, "a")[0]
        Url = common.parseDOM(strong, "a", ret="href")[0]
        #print Url
        Mediaitem.Image = shows_thumb
        Mediaitem.Mode = M_BROWSE_EPISODES
        try:
            highbeam = common.parseDOM(item, "span", attrs={ "class": "highbeam"})[0]
        except:
            highbeam = ''
        lowbeam = common.parseDOM(item, "span", attrs={ "class": "lowbeam"})
        if lowbeam:
            lbeam = lowbeam[0]
            lastupdate = common.parseDOM(lbeam, "a")[0]
            Plot = highbeam + '\n' + lastupdate
        else:
            Plot = highbeam
        #print Url
        Title = Title.encode('utf-8')
        #print Title
        Mediaitem.Url = sys.argv[0] + "?url=" + urllib.quote_plus(Url) + "&mode=" + str(Mediaitem.Mode) + "&name=" + urllib.quote_plus(Title)
        Mediaitem.ListItem.setInfo('video', { 'Title': Title, 'Plot': Plot})
        Mediaitem.ListItem.setThumbnailImage(Mediaitem.Image)
        Mediaitem.ListItem.setLabel(Title)
        Mediaitem.Isfolder = True
        MediaItems.append(Mediaitem)
    
    Menu = [(__settings__.getLocalizedString(30010), '', tv_thumb, M_BROWSE_CHANNELS),
            (__settings__.getLocalizedString(30011), MOVIES_URL, movies_thumb, M_BROWSE_MOVIES),
            (__settings__.getLocalizedString(30012), VIDEOS_URL, programs_thumb, M_BROWSE_VIDEOS)]
    for Title, Url, Thumb, Mode in Menu:
        Mediaitem = MediaItem()
        Mediaitem.Url = sys.argv[0] + "?url=" + urllib.quote_plus(Url) + "&mode=" + str(Mode) + "&name=" + urllib.quote_plus(Title)
        Mediaitem.ListItem.setThumbnailImage(Thumb)
        Mediaitem.ListItem.setLabel(Title)
        Mediaitem.Isfolder = True
        MediaItems.append(Mediaitem)
        
    addDir(MediaItems)

    # End of Directory
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    ## Set Default View Mode. This might break with different skins. But who cares?
    #xbmc.executebuiltin("Container.SetViewMode(503)")
    SetViewMode()
    
def BrowseEpisodes(ShowUrl=''):
    ###########################################################
    ## Mode == M_BROWSE_EPISODES
    ## BROWSE EPISODES
    ###########################################################   
    # set content type so library shows more views and info
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    
    # Get featured homepage contents
    #data = load_local_page('episodes.htm')
    data = getURL(ShowUrl)
    ShowTitle = common.parseDOM(data, "h1")[0]
    table = common.parseDOM(data, "table", attrs={ "class": "list"})[0]
    MediaItems = []
    items = common.parseDOM(table.replace("<tr>", "<tr />"), "tr")
    print 'item count: ' + str(len(items))
    for item in items:
        #print item
        Mediaitem = MediaItem()
        Title = ShowTitle + ' - ' + common.stripTags(common.parseDOM(item, "td")[0])
        Url = common.parseDOM(item, "a", ret="href")
        if len(Url) < 1:
            continue
        Url = Url[0]
        #print Url
        Mediaitem.Image = video_thumb
        Mediaitem.Mode = M_PLAY_SERIAL
        Plot = Title
        #print Url
        Title = Title.encode('utf-8')
        #print Title
        Mediaitem.Url = sys.argv[0] + "?url=" + urllib.quote_plus(Url) + "&mode=" + str(Mediaitem.Mode) + "&name=" + urllib.quote_plus(Title)
        Mediaitem.ListItem.setInfo('video', { 'Title': Title, 'Plot': Plot})
        Mediaitem.ListItem.setThumbnailImage(Mediaitem.Image)
        Mediaitem.ListItem.setLabel(Title)
        MediaItems.append(Mediaitem)
    
    Menu = [(__settings__.getLocalizedString(30010), '', tv_thumb, M_BROWSE_CHANNELS),
            (__settings__.getLocalizedString(30011), MOVIES_URL, movies_thumb, M_BROWSE_MOVIES),
            (__settings__.getLocalizedString(30012), VIDEOS_URL, programs_thumb, M_BROWSE_VIDEOS)]
    for Title, Url, Thumb, Mode in Menu:
        Mediaitem = MediaItem()
        Mediaitem.Url = sys.argv[0] + "?url=" + urllib.quote_plus(Url) + "&mode=" + str(Mode) + "&name=" + urllib.quote_plus(Title)
        Mediaitem.ListItem.setThumbnailImage(Thumb)
        Mediaitem.ListItem.setLabel(Title)
        Mediaitem.Isfolder = True
        MediaItems.append(Mediaitem)
        
    addDir(MediaItems)

    # End of Directory
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    ## Set Default View Mode. This might break with different skins. But who cares?
    #xbmc.executebuiltin("Container.SetViewMode(503)")
    SetViewMode()

def BrowseVideos(VidUrl=''):
    ###########################################################
    ## Mode == M_BROWSE_VIDEOS
    ## BROWSE VIDEOS
    ###########################################################   
    # set content type so library shows more views and info
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    #print 'Browing Videos at url: ' + VidUrl
    
    # Get featured homepage contents
    #data = load_local_page('videos.htm')
    data = getURL(VidUrl)
    Categories = common.parseDOM(data, "div", attrs={ "id": "categoriesbar"})[0]
    CatTitle = common.parseDOM(Categories, "a")
    CatUrl = common.parseDOM(Categories, "a", ret="href")
    MediaItems = []
    for i in range(len(CatTitle)):
        #print item
        Mediaitem = MediaItem()
        Title = CatTitle[i]
        Url = CatUrl[i]
        #print Url
        Mediaitem.Image = video_thumb
        Mediaitem.Mode = M_BROWSE_VIDEOS
        Plot = Title
        #print Url
        Title = Title.encode('utf-8')
        #print Title
        Mediaitem.Url = sys.argv[0] + "?url=" + urllib.quote_plus(Url) + "&mode=" + str(Mediaitem.Mode) + "&name=" + urllib.quote_plus(Title)
        Mediaitem.ListItem.setInfo('video', { 'Title': Title, 'Plot': Plot})
        Mediaitem.ListItem.setThumbnailImage(Mediaitem.Image)
        Mediaitem.ListItem.setLabel(Title)
        Mediaitem.Isfolder = True
        MediaItems.append(Mediaitem)
        #print Url
        #print VidUrl
        if Url == VidUrl:
            MediaItems.extend(GetVideos(data))
        else:
            splitTest = VidUrl.rsplit('/', 2)
            if len(splitTest) > 0:
                TestUrl = splitTest[0]
                if Url == TestUrl:
                    MediaItems.extend(GetVideos(data))
    
    Menu = [(__settings__.getLocalizedString(30010), '', tv_thumb, M_BROWSE_CHANNELS),
            (__settings__.getLocalizedString(30011), MOVIES_URL, movies_thumb, M_BROWSE_MOVIES),
            (__settings__.getLocalizedString(30012), VIDEOS_URL, programs_thumb, M_BROWSE_VIDEOS)]
    for Title, Url, Thumb, Mode in Menu:
        Mediaitem = MediaItem()
        Mediaitem.Url = sys.argv[0] + "?url=" + urllib.quote_plus(Url) + "&mode=" + str(Mode) + "&name=" + urllib.quote_plus(Title)
        Mediaitem.ListItem.setThumbnailImage(Thumb)
        Mediaitem.ListItem.setLabel(Title)
        Mediaitem.Isfolder = True
        MediaItems.append(Mediaitem)
        
    addDir(MediaItems)

    # End of Directory
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    ## Set Default View Mode. This might break with different skins. But who cares?
    #xbmc.executebuiltin("Container.SetViewMode(503)")
    SetViewMode()
    
def GetVideos(content):
    Videos = common.parseDOM(content, "div", attrs={ "class": "video"})
    if len(Videos) < 1:
        return None
    MediaItems = []
    for video in Videos:
        Mediaitem = MediaItem()
        Duration = common.parseDOM(video, "div", attrs={ "class": "vidtime"})[0]
        Info = common.parseDOM(video, "div", attrs={ "class": "vidinfo lowbeam"})[0]
        #print Info
        Info = re.compile('div>(.+?ago)').findall(Info)[0]
        Mediaitem.Image = common.parseDOM(video, "img", ret="src")[0]
        strong = common.parseDOM(video, "strong")[0]
        Url = common.parseDOM(strong, "a", ret="href")[0]
        Title = common.parseDOM(strong, "a")[0]
        Plot = Title + '\n' + Info
        Title = '* ' + Title.encode('utf-8')
        Mediaitem.Mode = M_PLAY_VIDEO
        Mediaitem.Url = sys.argv[0] + "?url=" + urllib.quote_plus(Url) + "&mode=" + str(Mediaitem.Mode) + "&name=" + urllib.quote_plus(Title)
        Mediaitem.ListItem.setInfo('video', { 'Title': Title, 'Plot': Plot, 'Duration': Duration})
        Mediaitem.ListItem.setThumbnailImage(Mediaitem.Image)
        Mediaitem.ListItem.setLabel(Title)
        MediaItems.append(Mediaitem)
    Next = re.compile("href='([^']+)'><strong>Next</strong>").findall(content)
    if len(Next) > 0:
        Mediaitem = MediaItem()
        Title = __settings__.getLocalizedString(30014)
        Url = Next[0]
        Mediaitem.Image = next_thumb
        Mediaitem.Mode = M_BROWSE_VIDEOS
        Mediaitem.Url = sys.argv[0] + "?url=" + urllib.quote_plus(Url) + "&mode=" + str(Mediaitem.Mode) + "&name=" + urllib.quote_plus(Title)
        Mediaitem.ListItem.setInfo('video', { 'Title': Title})
        Mediaitem.ListItem.setThumbnailImage(Mediaitem.Image)
        Mediaitem.ListItem.setLabel(Title)
        Mediaitem.Isfolder = True
        MediaItems.append(Mediaitem)
    return MediaItems
        
   
def BrowseMovies(MvUrl=''):
    ###########################################################
    ## Mode == M_BROWSE_MOVIES
    ## BROWSE MOVIES
    ###########################################################
    # set content type so library shows more views and info
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    
    # Get contents for given url
    #data = getURL(url)
    data = save_web_page(MvUrl, 'movies.html')
    #data = load_local_page('movies.html')
    items = common.parseDOM(data, "div", attrs={ "class": "movie"})
    MediaItems = []
    for item in items:
        Mediaitem = MediaItem()
        span = common.parseDOM(item, "span", attrs={ "class": "movieposter"})[0]
        Title = common.parseDOM(span, "img", ret="alt")[0]
        Url = common.parseDOM(span, "a", ret="href")[0]
        #print Url
        Mediaitem.Image = common.parseDOM(span, "img", ret="src")[0]
        Plot = common.parseDOM(span, "a", ret="title")[0]
        Mediaitem.Mode = M_PLAY_MOVIES
        #print Url
        Title = Title.encode('utf-8')
        #print Title
        Mediaitem.Url = sys.argv[0] + "?url=" + urllib.quote_plus(Url) + "&mode=" + str(Mediaitem.Mode) + "&name=" + urllib.quote_plus(Title)
        Mediaitem.ListItem.setInfo('video', { 'Title': Title, 'Plot': Plot})
        Mediaitem.ListItem.setThumbnailImage(Mediaitem.Image)
        #Mediaitem.ListItem.setProperty('IsPlayable', 'true')
        Mediaitem.ListItem.setLabel(Title)
        MediaItems.append(Mediaitem)
    
    Menu = [(__settings__.getLocalizedString(30016), '', programs_thumb, M_BROWSE_MOVIE_VIDEOS),
            (__settings__.getLocalizedString(30017), '', movies_thumb, M_BROWSE_ALL_MOVIES),
            (__settings__.getLocalizedString(30010), '', tv_thumb, M_BROWSE_CHANNELS),
            (__settings__.getLocalizedString(30011), MOVIES_URL, movies_thumb, M_BROWSE_MOVIES),
            (__settings__.getLocalizedString(30012), VIDEOS_URL, programs_thumb, M_BROWSE_VIDEOS)]
    for Title, Url, Thumb, Mode in Menu:
        Mediaitem = MediaItem()
        Mediaitem.Url = sys.argv[0] + "?url=" + urllib.quote_plus(Url) + "&mode=" + str(Mode) + "&name=" + urllib.quote_plus(Title)
        Mediaitem.ListItem.setThumbnailImage(Thumb)
        Mediaitem.ListItem.setLabel(Title)
        Mediaitem.Isfolder = True
        MediaItems.append(Mediaitem)
        
    addDir(MediaItems)

    # End of Directory
    xbmcplugin.endOfDirectory(pluginhandle)
    ## Set Default View Mode. This might break with different skins. But who cares?
    #xbmc.executebuiltin("Container.SetViewMode(503)")
    SetViewMode()
    
def BrowseMovieVideos():
    ###########################################################
    ## Mode == M_BROWSE_MOVIE_VIDEOS
    ## BROWSE MOVIE VIDEOS
    ###########################################################
    # set content type so library shows more views and info
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    
    # Get contents for given url
    #data = getURL(url)
    #data = save_web_page(MvUrl, 'movies.html')
    data = load_local_page('movies.html')
    Videos = common.parseDOM(data, "div", attrs={ "class": "videocontainer"})
    MediaItems = []
    for video in Videos:
        Mediaitem = MediaItem()
        Duration = common.parseDOM(video, "div", attrs={ "class": "vidtime"})[0]
        Info = common.parseDOM(video, "div", attrs={ "class": "vidinfo lowbeam"})[0]
        #print Info
        Info = re.compile('div>(.+?ago)').findall(Info)[0]
        Mediaitem.Image = common.parseDOM(video, "img", ret="src")[0]
        strong = common.parseDOM(video, "strong")[0]
        Url = common.parseDOM(strong, "a", ret="href")[0]
        Title = common.parseDOM(strong, "a")[0]
        Plot = Title + '\n' + Info
        Title = '* ' + Title.encode('utf-8')
        Mediaitem.Mode = M_PLAY_VIDEO
        Mediaitem.Url = sys.argv[0] + "?url=" + urllib.quote_plus(Url) + "&mode=" + str(Mediaitem.Mode) + "&name=" + urllib.quote_plus(Title)
        Mediaitem.ListItem.setInfo('video', { 'Title': Title, 'Plot': Plot, 'Duration': Duration})
        Mediaitem.ListItem.setThumbnailImage(Mediaitem.Image)
        Mediaitem.ListItem.setLabel(Title)
        MediaItems.append(Mediaitem)
    
    Menu = [(__settings__.getLocalizedString(30017), '', movies_thumb, M_BROWSE_ALL_MOVIES),
            (__settings__.getLocalizedString(30010), '', tv_thumb, M_BROWSE_CHANNELS),
            (__settings__.getLocalizedString(30011), MOVIES_URL, movies_thumb, M_BROWSE_MOVIES),
            (__settings__.getLocalizedString(30012), VIDEOS_URL, programs_thumb, M_BROWSE_VIDEOS)]
    for Title, Url, Thumb, Mode in Menu:
        Mediaitem = MediaItem()
        Mediaitem.Url = sys.argv[0] + "?url=" + urllib.quote_plus(Url) + "&mode=" + str(Mode) + "&name=" + urllib.quote_plus(Title)
        Mediaitem.ListItem.setThumbnailImage(Thumb)
        Mediaitem.ListItem.setLabel(Title)
        Mediaitem.Isfolder = True
        MediaItems.append(Mediaitem)
        
    addDir(MediaItems)

    # End of Directory
    xbmcplugin.endOfDirectory(pluginhandle)
    ## Set Default View Mode. This might break with different skins. But who cares?
    #xbmc.executebuiltin("Container.SetViewMode(503)")
    SetViewMode()
    
def BrowseAllMovies():
    ###########################################################
    ## Mode == M_BROWSE_ALL_MOVIES
    ## BROWSE ALL MOVIES
    ###########################################################
    # set content type so library shows more views and info
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    
    # Get contents for given url
    #data = getURL(url)
    #data = save_web_page(MvUrl, 'movies.html')
    data = load_local_page('movies.html')
    ul = common.parseDOM(data, "ul", attrs={ "class": "basiclist multicolumn"})[0]
    Videos = common.parseDOM(ul, "li")
    MediaItems = []
    for video in Videos:
        Mediaitem = MediaItem()
        Url = common.parseDOM(video, "a", ret="href")[0]
        Title = common.parseDOM(video, "a")[0]
        Plot = Title
        Title = '* ' + Title.encode('utf-8')
        Mediaitem.Mode = M_PLAY_MOVIES
        Mediaitem.Image = video_thumb
        Mediaitem.Url = sys.argv[0] + "?url=" + urllib.quote_plus(Url) + "&mode=" + str(Mediaitem.Mode) + "&name=" + urllib.quote_plus(Title)
        Mediaitem.ListItem.setInfo('video', { 'Title': Title, 'Plot': Plot})
        Mediaitem.ListItem.setThumbnailImage(Mediaitem.Image)
        Mediaitem.ListItem.setLabel(Title)
        MediaItems.append(Mediaitem)
    
    Menu = [(__settings__.getLocalizedString(30016), '', programs_thumb, M_BROWSE_MOVIE_VIDEOS),
            (__settings__.getLocalizedString(30010), '', tv_thumb, M_BROWSE_CHANNELS),
            (__settings__.getLocalizedString(30011), MOVIES_URL, movies_thumb, M_BROWSE_MOVIES),
            (__settings__.getLocalizedString(30012), VIDEOS_URL, programs_thumb, M_BROWSE_VIDEOS)]
    for Title, Url, Thumb, Mode in Menu:
        Mediaitem = MediaItem()
        Mediaitem.Url = sys.argv[0] + "?url=" + urllib.quote_plus(Url) + "&mode=" + str(Mode) + "&name=" + urllib.quote_plus(Title)
        Mediaitem.ListItem.setThumbnailImage(Thumb)
        Mediaitem.ListItem.setLabel(Title)
        Mediaitem.Isfolder = True
        MediaItems.append(Mediaitem)
        
    addDir(MediaItems)

    # End of Directory
    xbmcplugin.endOfDirectory(pluginhandle)
    ## Set Default View Mode. This might break with different skins. But who cares?
    #xbmc.executebuiltin("Container.SetViewMode(503)")
    SetViewMode()
    

def PlaySerial(url):
    ###########################################################
    ## Mode == M_PLAY_SERIAL
    ## Try to get a list of playable items and play it.
    ###########################################################
    if url == None or url == '':
        return
    
    # Get contents for given url
    data = getURL(url)
    data = data.replace('\r\n', '').replace('\r', '').replace('\n', '')
    
    centerblocks = common.parseDOM(data, "div", attrs={ "id": "centerblocks"})[0]
    h1 = common.parseDOM(centerblocks, "h1")[0]
    h3 = common.parseDOM(centerblocks, "h3")[0]
    Title = h1 + ' - ' + h3
    Thumb = common.parseDOM(centerblocks, "img", attrs={ "class": "thumb"}, ret="src")[0]
    Title = Title.encode('utf-8')
    
    tables = common.parseDOM(centerblocks, "table", attrs={ "class": "list"})
    Mirrors = []
    for item in tables:
        Host = common.parseDOM(item, "td", attrs={ "width": "75%"})[0]
        Mirrors.append((Host, item))
    Hosts = []
    for Host, _ in Mirrors:
        Hosts.append(Host)
    dialog = xbmcgui.Dialog()
    index = dialog.select('Choose Mirror', Hosts)
    if index > -1:
        #print 'so far so good ' + str(index)
        Matches = None
        try:
            xbmc.executebuiltin( "ActivateWindow(busydialog)" )
            _, src = Mirrors[index]
            #print src
            URLs = []
            #src = re.sub('\n', '', src)
            #NavPages = common.parseDOM(src, "a", attrs={ "rel": "nofollow"}, ret="href")
            NavPages = re.compile("href='(.+?)'").findall(src)
            #print 'Num Links found: ' + str(len(NavPages))
            for Page in NavPages:
                #print 'URL one: ' + Page
                data2 = getURL(Page)
                data2 = data2.replace('\r\n', '').replace('\r', '').replace('\n', '')
                dataHtml = common.parseDOM(data2, "div", attrs={ "id": "centerblocks"})[0]
                #print dataHtml
                #print 'centerblocks: ' + dataHtml
                Matches = hosts.resolve(dataHtml)
                #print 'Matches after first try: ' + str(len(Matches))
                #break
                if not Matches:
                    NavPage2 = common.parseDOM(dataHtml, "a", attrs={ "rel": "nofollow"}, ret="href")[0]
                    data3 = getURL(NavPage2)
                    #print data3
                    Matches = hosts.resolve(data3)
                    #print 'Matches after second try: ' + str(len(Matches))
                
                if Matches:
                    URLs.extend(Matches)
        except:
            print 'Error occured in try block in PlaySerial'
        finally:
            xbmc.executebuiltin( "Dialog.Close(busydialog)" )
        
        if Matches is None or len(Matches) == 0:
            #xbmcplugin.setResolvedUrl(pluginhandle, False, xbmcgui.ListItem())
            dialog = xbmcgui.Dialog()
            dialog.ok('Nothing to play', 'A playable url could not be found.')
            return
        playList = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playList.clear()
        count = 1
        for PlayItem in URLs:
            Title = Title + ' Part ' + str(count)
            listitem = ListItem(Title, iconImage=Thumb, thumbnailImage=Thumb)
            listitem.setInfo('video', { 'Title': Title})
            #listitem.setProperty("IsPlayable", "true")
            playList.add(url=PlayItem, listitem=listitem)
            count = count + 1
        xbmcPlayer = xbmc.Player()
        xbmcPlayer.play(playList)
    #listitem.setPath(Url)
    #vid = xbmcgui.ListItem(path=url)
    #xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play(url, vid)
    #xbmc.executebuiltin("xbmc.PlayMedia("+url+")")
    #xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
    
def PlayVideo(url):
    ###########################################################
    ## Mode == M_PLAY_VIDEO
    ## Try to get a list of playable items and play it.
    ###########################################################
    if url == None or url == '':
        return
    xbmc.executebuiltin( "ActivateWindow(busydialog)" )
    # Get contents for given url
    data = getURL(url)
    data = data.replace('\r', '')
    
    YTPlayer = common.parseDOM(data, "div", attrs={ "id": "ytplayer"})
    if not YTPlayer:
        return
    URLs = []
    for Player in YTPlayer:
        Matches = hosts.resolve(Player)
        if Matches:
            URLs.extend(Matches)
    xbmc.executebuiltin( "Dialog.Close(busydialog)" )
    if Matches == None or len(Matches) == 0:
        #xbmcplugin.setResolvedUrl(pluginhandle, False, xbmcgui.ListItem())
        dialog = xbmcgui.Dialog()
        dialog.ok('Nothing to play', 'A playable url could not be found.')
        return
    playList = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playList.clear()
    #count = 1
    for PlayItem in URLs:
        #Title = Title + ' Part ' + str(count)
        #listitem = ListItem(Title, iconImage=Thumb, thumbnailImage=Thumb)
        listitem = ListItem('Video')
        #listitem.setInfo('video', { 'Title': Title})
        listitem.setProperty("IsPlayable", "true")
        playList.add(url=PlayItem, listitem=listitem)
        #count = count + 1
    xbmcPlayer = xbmc.Player()
    xbmcPlayer.play(playList)
    
def PlayMovies(url):
    print 'apnitv PlayMovies'

# Set View Mode selected in the setting
def SetViewMode():
    try:
        # if (xbmc.getSkinDir() == "skin.confluence"):
        if __settings__.getSetting('view_mode') == "1": # List
            xbmc.executebuiltin('Container.SetViewMode(502)')
        if __settings__.getSetting('view_mode') == "2": # Big List
            xbmc.executebuiltin('Container.SetViewMode(51)')
        if __settings__.getSetting('view_mode') == "3": # Thumbnails
            xbmc.executebuiltin('Container.SetViewMode(500)')
        if __settings__.getSetting('view_mode') == "4": # Poster Wrap
            xbmc.executebuiltin('Container.SetViewMode(501)')
        if __settings__.getSetting('view_mode') == "5": # Fanart
            xbmc.executebuiltin('Container.SetViewMode(508)')
        if __settings__.getSetting('view_mode') == "6":  # Media info
            xbmc.executebuiltin('Container.SetViewMode(504)')
        if __settings__.getSetting('view_mode') == "7": # Media info 2
            xbmc.executebuiltin('Container.SetViewMode(503)')
            
        if __settings__.getSetting('view_mode') == "0": # Default Media Info for Quartz
            xbmc.executebuiltin('Container.SetViewMode(52)')
    except:
        print "SetViewMode Failed: " + __settings__.getSetting('view_mode')
        print "Skin: " + xbmc.getSkinDir()


## Get Parameters
def get_params():
        param = []
        paramstring = sys.argv[2]
        if len(paramstring) >= 2:
                params = sys.argv[2]
                cleanedparams = params.replace('?', '')
                if (params[len(params) - 1] == '/'):
                        params = params[0:len(params) - 2]
                pairsofparams = cleanedparams.split('&')
                param = {}
                for i in range(len(pairsofparams)):
                        splitparams = {}
                        splitparams = pairsofparams[i].split('=')
                        if (len(splitparams)) == 2:
                                param[splitparams[0]] = splitparams[1]
        return param

def addDir(Listitems):
    if Listitems is None:
        return
    Items = []
    for Listitem in Listitems:
        Item = Listitem.Url, Listitem.ListItem, Listitem.Isfolder
        Items.append(Item)
    handle = pluginhandle
    xbmcplugin.addDirectoryItems(handle, Items)


if not os.path.exists(settingsDir):
    os.mkdir(settingsDir)
if not os.path.exists(cacheDir):
    os.mkdir(cacheDir)
                    
params = get_params()
url = None
name = None
mode = None
titles = None
try:
        url = urllib.unquote_plus(params["url"])
except:
        pass
try:
        name = urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode = int(params["mode"])
except:
        pass
try:
        titles = urllib.unquote_plus(params["titles"])
except:
        pass

xbmc.log("Mode: " + str(mode))
#print "URL: " + str(url)
#print "Name: " + str(name)
#print "Title: " + str(titles)

if mode == None:
    BuildMainDirectory()
elif mode == M_DO_NOTHING:
    print 'Doing Nothing'
elif mode == M_BROWSE_CHANNELS:
    BrowseChannels()
elif mode == M_BROWSE_CHANNEL_CONTENTS:
    BrowseChannelContents(url)
elif mode == M_BROWSE_EPISODES:
    BrowseEpisodes(url)
elif mode == M_BROWSE_MOVIES:
    BrowseMovies(url)
elif mode == M_BROWSE_MOVIE_VIDEOS:
    BrowseMovieVideos()
elif mode == M_BROWSE_ALL_MOVIES:
    BrowseAllMovies()
elif mode == M_BROWSE_VIDEOS:
    BrowseVideos(url)
elif mode == M_PLAY_SERIAL:
    PlaySerial(url)
elif mode == M_PLAY_VIDEO:
    PlayVideo(url)
elif mode == M_PLAY_MOVIES:
    PlayMovies(url)
