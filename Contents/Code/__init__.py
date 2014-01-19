import re

VIDEO_PREFIX = "/video/ch9"
NAME = L('Title')
ART           = 'art-ch9.jpg'
ICON          = 'icon-default.png'
DEFAULT_CACHE_INTERVAL = 9000
JUMP_URL = 'http://jump-in.com.au/watch-now'
JUMP_BASE = 'http://jump-in.com.au'
####################################################################################################
def Start():

    Plugin.AddPrefixHandler(VIDEO_PREFIX, HomeMenu, L('VideoTitle'), ICON, ART)
    Plugin.AddViewGroup('InfoList', viewMode='InfoList', mediaType='items')
    Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
    MediaContainer.art = R(ART)
    MediaContainer.title1 = NAME
    DirectoryItem.thumb = R(ICON)
    
@route(VIDEO_PREFIX + '/home')
def HomeMenu():
     
    oc = ObjectContainer(title2='CH9 On Demand', view_group='List')
    oc.add(DirectoryObject(
                key=Callback(ShowMenu),
                title='By Program',
                thumb=R(ICON),
    ))
    
    oc.add(DirectoryObject(
                key=Callback(ShowMenu, filter='catalogue-most-recent'),
                title='Most recent',
                thumb=R(ICON),
    ))
    
    oc.add(DirectoryObject(
                key=Callback(ShowMenu, filter='catalogue-last-chance'),
                title='Last Chance',
                thumb=R(ICON),
    ))
    
    oc.add(DirectoryObject(
                key=Callback(ShowMenu, filter='catalogue-movies'),
                title='Movies',
                thumb=R(ICON),
    ))

    return oc
    
@route(VIDEO_PREFIX + '/show')
def ShowMenu(filter=None):
    
    oc = ObjectContainer(title2='shows', view_group='List')
    shows = HTML.ElementFromURL(JUMP_URL, cacheTime=DEFAULT_CACHE_INTERVAL)
    
    if filter is None:
        xpathQry = "//div[@id='catalogue-shows']/div[@id='entry-wrapper']/div"
    elif filter == 'catalogue-most-recent':
        xpathQry = "//div[@id='catalogue-most-recent']/div"
    elif filter == 'catalogue-last-chance':
        xpathQry = "//div[@id='catalogue-last-chance']/div"
    elif filter == 'catalogue-movies':
        xpathQry = "//div[@id='catalogue-movies']/div"
    
    for show in shows.xpath(xpathQry):
            showName = show.xpath("div[@class='details']/h3/a")[0].text
            showURL = JUMP_BASE + show.xpath("div[@class='details']/h3/a")[0].get('href')
            Log('Got show: ' + showName)
            Log('Got show url: ' + showURL)
            link = DirectoryObject(
                    key=Callback(EpisodeMenu, url=showURL),
                    title=showName,
                    )
            oc.add(link)    
    return oc        
 
@route(VIDEO_PREFIX + '/episode') 
def EpisodeMenu(url=None):
    oc = ObjectContainer(title2='episodes', view_group='InfoList')
    data = HTML.ElementFromURL(url)
    for episode in data.xpath("//div[@class='more-episodes']/div[@class='episodes module']/div"):
        episodeName = episode.xpath('div[2]/h4/a')[0].text
        episodeLink = JUMP_BASE + episode.xpath('div[2]/h4/a')[0].get('href')
        episodeSummary = episode.xpath("div[2]/p[@class='summary']")[0].text
        
        vco = VideoClipObject(
           url= episodeLink, 
           title=episodeName,
           summary=episodeSummary,
        )
        oc.add(vco)

        
    return oc        