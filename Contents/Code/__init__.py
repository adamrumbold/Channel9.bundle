import re

BASE_URL = 'http://channelnine.ninemsn.com.au/video'
VIDEO_PREFIX = "/video/ch9"
NAME = L('Title')
ART           = 'art-ch9.jpg'
ICON          = 'icon-default.jpg'
API_URL = 'http://api.brightcove.com/services/library?command='
CAT_URL = API_URL + 'find_all_playlists' + '&page_size=50&get_item_count=true&playlist_fields=id,name,shortDescription'
PLAYLIST_URL = API_URL + 'find_playlist_by_id' #+ '&playlist_fields=id,name,shortDescription,videoIds,videos'
TOKEN = 'Vb3fqavTKFDDZbnnGGtbhKxam7uHduOnob-2MJlpHmUnzSMWbDe5bg..'
VIDEO_URL = API_URL +'find_video_by_id' + '&video_fields=id,linkURL,renditions,name,shortDescription,longDescription,creationDate,publishedDate,thumbnailURL,length,FLVURL'
SEARCH_URL = API_URL +'search_videos' + '&video_fields=id,name,shortDescription,longDescription,creationDate,publishedDate,thumbnailURL,length,FLVURL'
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
    link = DirectoryObject(
                key=Callback(ShowMenu),
                title='By Program',
                thumb=R(ICON),
                )
    oc.add(link)
    
    link = DirectoryObject(
                key=Callback(ShowMenu, filter='catalogue-most-recent'),
                title='Most recent',
                thumb=R(ICON),
                )
    oc.add(link)
    
    link = DirectoryObject(
                key=Callback(ShowMenu, filter='catalogue-last-chance'),
                title='Last Chance',
                thumb=R(ICON),
    )
    oc.add(link)
    
    link = DirectoryObject(
                key=Callback(ShowMenu, filter='catalogue-movies'),
                title='Movies',
                thumb=R(ICON),
    )
    oc.add(link)
    
    
    
    return oc
    
@route(VIDEO_PREFIX + '/show')
def ShowMenu(filter=None):
    
    oc = ObjectContainer(title2='shows', view_group='List')
    shows = HTML.ElementFromURL(JUMP_URL, cacheTime=DEFAULT_CACHE_INTERVAL)
    Log('got shows')
    
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
    oc = ObjectContainer(title2='episodes', view_group='List')
    data = HTML.ElementFromURL(url)
    Log('Got episodes page')
    for episode in data.xpath("//div[@class='more-episodes']/div[@class='episodes module']/div"):
        Log('Got episode')
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
        
    

    #if showQuery is None:
    #    oc = ObjectContainer(title2='shows', view_group='List')
    #    shows = HTML.ElementFromURL(BASE_URL, cacheTime=DEFAULT_CACHE_INTERVAL)
    #    Log('got shows')
    #    for show in shows.xpath("id('nav')/li/ul/li/a"):
    #        showName = show.get('title')
    #        Log('Got show ' + showName)
    #        showQry = show.get('query')
    #        Log('Got show query pre reg exp: ' + showQry)
    #        try:
    #            RE_QRY = Regex('tag=(.*)&?',  Regex.DOTALL)    
    #            showQuery = RE_QRY.search(showQry).group(1)
    #            Log('got show query: ' + showQuery)
    #            link = DirectoryObject(
    #                key=Callback(ShowMenu, showQuery=showQuery),
    #                title=showName,
    #                )
    #            oc.add(link)
    #        except:
    #            Log('Failed to get tag')
    #        
    #else:
    #    oc = ObjectContainer(title2=showQuery, view_group='InfoList')
    #    content = JSON.ObjectFromURL(SEARCH_URL + '&token=' + TOKEN + '&all=tag:' + showQuery, cacheTime=DEFAULT_CACHE_INTERVAL)
    #    for show in content['items']:
    #        Log('Adding show:' + str(show['id']))
    #        oc.add(VideoClipObject(
    #            url=VIDEO_URL+ '&video_id='+str(show['id'])+'&token='+ TOKEN,
    #            title=show['name'],
    #            thumb = show['thumbnailURL'],
    #            duration = show['length'],
    #            originally_available_at = Datetime.FromTimestamp(int(show['publishedDate'])/1000),            
    #        ))
    #    
    #    if len(oc) == 0:
    #        oc.add(DirectoryObject(
    #            key=Callback(ShowMenu),
    #            title='..',
    #            thumb=R(ICON),
    #        ))    
    #
    #oc.objects.sort(key=lambda obj: obj.title)        
    #return oc
        
    
####################################################################################################
@route(VIDEO_PREFIX + '/playlist')
def PlaylistMenu(playlistID=None):
                    
    if playlistID is None:
        content = JSON.ObjectFromURL(CAT_URL + '&token=' + TOKEN, cacheTime= DEFAULT_CACHE_INTERVAL)
        title = 'Playlists'
        oc = ObjectContainer(title2=title, view_group='List')
    
    else:
        content = JSON.ObjectFromURL(PLAYLIST_URL + '&playlist_id=' + str(playlistID) + '&token=' + TOKEN, cacheTime = DEFAULT_CACHE_INTERVAL)
        title = content['name']
        oc = ObjectContainer(title2=title, view_group='InfoList')
    
    if playlistID is None:
        
        for item in content['items']:
            if item['name'] in ('Breaking News','World','Finance','Sport','Entertainment','National'):
                link = DirectoryObject(
                key=Callback(PlaylistMenu, playlistID=item['id']),
                title=item['name'],
                thumb=R(ICON),
                )
                oc.add(link)
    else:
        for item in content['videos']:
        
            oc.add(VideoClipObject(
                url=VIDEO_URL+ '&video_id='+str(item['id'])+'&token='+ TOKEN,
                title=item['name'],
                thumb = item['thumbnailURL'],
                duration = item['length'],
                originally_available_at = Datetime.FromTimestamp(int(item['publishedDate'])/1000),            
            ))
            
        if len(oc) == 0:
            oc.add(DirectoryObject(
                key=Callback(PlaylistMenu),
                title='..',
                thumb=R(ICON),
            ))
    
    oc.objects.sort(key=lambda obj: obj.title)
    return oc
