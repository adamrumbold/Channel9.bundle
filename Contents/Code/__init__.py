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
    
    oc = ObjectContainer(title2='shows', view_group='InfoList')
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
            showSummary = show.xpath("div[@class='details']/div[@class='extra-details']/p")[0].text
            showURL = JUMP_BASE + show.xpath("div[@class='details']/h3/a")[0].get('href')
            showThumb = show.xpath("div[@class='media']/a/img")[0].get('src'),
            showThumb = re.sub("(width=\d+&height=\d+)", "width=720&height=380", showThumb[0])
            Log('Got show: ' + showName)
            Log('Got show url: ' + showURL)
            link = TVShowObject(
                    key=Callback(EpisodeMenu, url=showURL),
                    rating_key = showURL,
                    title=showName,
                    thumb=showThumb,
                    summary=showSummary,
                    )
            oc.add(link)    
    return oc

@route(VIDEO_PREFIX + '/season')
def SeasonMenu(url=None):
    data = HTML.ElementFromURL(url)
    showName = data.xpath("//div[@class='content']/div[@class='episode-details']/h1")[0].text
    showThumb = data.xpath("//div[@class='episode-media']/img")[0].get('src')
    showThumb = re.sub("(width=\d+&height=\d+)", "width=720&height=380", showThumb)
    
    oc = ObjectContainer(title1=showName, view_group='InfoList')
    seasons = data.xpath("//ul[@id='season-selector']/li")
    seasons.reverse()
    for season in seasons:
        seasonObj = season.xpath("a")[0]
        seasonTitle = seasonObj.get('title')
        seasonURL = JUMP_BASE + seasonObj.get('href')

        vco = SeasonObject(
           key=Callback(EpisodeMenu, url=seasonURL),
           rating_key = seasonURL,
           title=seasonTitle,
           thumb=showThumb
        )
        oc.add(vco)
            

    return oc
 
@route(VIDEO_PREFIX + '/episode') 
def EpisodeMenu(url=None):
    data = HTML.ElementFromURL(url)
    showName = data.xpath("//div[@class='content']/div[@class='episode-details']/h1")[0].text
    
    seasons = data.xpath("//ul[@id='season-selector']/li")
    seasonText = data.xpath("//ul[@id='season-selector']/li/a[@class='active']")[0].get('title')
    
    if seasonText != None:
        matchObj = re.search('(\d+$)', seasonText, re.M)
        
        if matchObj:
            seasonNumber = int(matchObj.group())

    if len(seasons) > 1 and re.search("episodes\/$", url, re.M):
        return SeasonMenu(url)
    
    oc = ObjectContainer(title1=showName, view_group='InfoList')

    episodes = data.xpath("//div[@class='more-episodes']/div[@class='episodes module']/div")
    episodes.reverse()

    for episode in episodes:
        episodeText = episode.xpath('div[2]/h4/a')[0].text
        
        matchObj = re.search('(\d+$)', episodeText, re.M)
        
        if matchObj:
            episodeNumber = int(matchObj.group())
        
        episodeName = episodeText + (": " + episode.xpath("div[2]/p")[0].text if episode.xpath("div[2]/p")[0].text != None else '')
        episodeLink = JUMP_BASE + episode.xpath('div[2]/h4/a')[0].get('href')
        episodeSummary = episode.xpath("div[2]/p")[0].text
        episodeThumb = episode.xpath('div[1]/a/img')[0].get('src')
        episodeThumb = re.sub("(width=\d+&height=\d+)", "width=720&height=380", episodeThumb)

        vco = EpisodeObject(
           url= episodeLink, 
           title=episodeName,
           thumb=episodeThumb,
        )

        if episodeNumber != None:
            vco.index = episodeNumber

        if seasonNumber != None:
            vco.season = seasonNumber

        oc.add(vco)

        
    return oc        