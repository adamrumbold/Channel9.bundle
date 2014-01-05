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
VIDEO_URL = API_URL +'find_video_by_id' + '&video_fields=id,name,shortDescription,longDescription,creationDate,publishedDate,thumbnailURL,length,FLVURL'
SEARCH_URL = API_URL +'search_videos' + '&video_fields=id,name,shortDescription,longDescription,creationDate,publishedDate,thumbnailURL,length,FLVURL'
DEFAULT_CACHE_INTERVAL = 9000
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
                key=Callback(PlaylistMenu),
                title='By Category',
                thumb=R(ICON),
    )
    oc.add(link)
    return oc
    
@route(VIDEO_PREFIX + '/show')
def ShowMenu(showQuery=None):
    
    if showQuery is None:
        oc = ObjectContainer(title2='shows', view_group='List')
        shows = XML.ElementFromURL('http://vod.ten.com.au/config/windows8/?includeAll=Sites.VideoQueries&appid=F%2fuisp9hN%2bE%3d', cacheTime=DEFAULT_CACHE_INTERVAL)
        for show in shows.xpath("/application/home/videoGroups/videoGroup[@title='TV Shows']/items/item"):
            showName = show.xpath("name")[0].text
            thumb = show.xpath("image")[0].text            
            showQuery = show.xpath("query")[0].text
            showQuery = re.findall('tv_show:(.*?)(?:&+.*|$)', showQuery, re.DOTALL)[0]
            link = DirectoryObject(
                key=Callback(ShowMenu, showQuery=showQuery),
                title=showName,
                thumb=thumb
                )
            oc.add(link)
            
    else:
        oc = ObjectContainer(title2=showQuery, view_group='InfoList')
        content = JSON.ObjectFromURL(SEARCH_URL + '&token=' + TOKEN + '&all=' + showQuery, cacheTime=DEFAULT_CACHE_INTERVAL)
        for show in content['items']:
            oc.add(VideoClipObject(
                url=VIDEO_URL+ '&video_id='+str(show['id'])+'&token='+ TOKEN,
                title=show['name'],
                thumb = show['thumbnailURL'],
                duration = show['length'],
                originally_available_at = Datetime.FromTimestamp(int(show['publishedDate'])/1000),            
            ))
        
        if len(oc) == 0:
            oc.add(DirectoryObject(
                key=Callback(ShowMenu),
                title='..',
                thumb=R(ICON),
            ))    
    
    oc.objects.sort(key=lambda obj: obj.title)        
    return oc
        
    
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
