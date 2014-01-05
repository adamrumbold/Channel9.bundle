

BASE_URL = 'http://channelnine.ninemsn.com.au/video'
VIDEO_PREFIX = "/video/ch9"
NAME = L('Title')

# make sure to replace artwork with what you want
# these filenames reference the example files in
# the Contents/Resources/ folder in the bundle
ART           = 'art-ch9.jpg'
ICON          = 'icon-default.jpg'

SHOW_LIST_URL = 'http://api.brightcove.com/services/library?command=find_all_playlists&page_size=50&get_item_count=true&playlist_fields=id,name,shortDescription'
API_URL = 'http://api.brightcove.com/services/library?command='
CAT_URL = API_URL + 'find_all_playlists' + '&page_size=50&get_item_count=true&playlist_fields=id,name,shortDescription'
PLAYLIST_URL = API_URL + 'find_playlist_by_id' #+ '&playlist_fields=id,name,shortDescription,videoIds,videos'
TOKEN = 'Vb3fqavTKFDDZbnnGGtbhKxam7uHduOnob-2MJlpHmUnzSMWbDe5bg..'
#find_video_by_id(token:String, video_id:long, fields:Set, video_fields:EnumSet, custom_fields:Set, media_delivery:Enum, output:Enum):
VIDEO_URL = API_URL +'find_video_by_id' + '&video_fields=id,name,shortDescription,longDescription,creationDate,publishedDate,thumbnailURL,length,FLVURL'


####################################################################################################
def Start():

    Plugin.AddPrefixHandler(VIDEO_PREFIX, PlaylistMenu, L('VideoTitle'), ICON, ART)

    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

    MediaContainer.art = R(ART)
    MediaContainer.title1 = NAME
    DirectoryItem.thumb = R(ICON) 
    
####################################################################################################
@route(VIDEO_PREFIX + '/playlist')
def PlaylistMenu(playlistID=None):
       
    if playlistID is None:
        Log('Attempting: ' + CAT_URL + '&token=' + TOKEN)
        content = JSON.ObjectFromURL(CAT_URL + '&token=' + TOKEN)
        title = 'CH9 On Demand'
    
    else:
        content = JSON.ObjectFromURL(PLAYLIST_URL + '&playlist_id=' + str(playlistID) + '&token=' + TOKEN)
        title = content['name']
    
    oc = ObjectContainer(title2=title, view_group='InfoList')
    
    if playlistID is None:
        for item in content['items']:
            if item['name'] in ('Breaking News','World','Finance','Sport','Entertainment','National'):
                link = DirectoryObject(
                key=Callback(PlaylistMenu, playlistID=item['id']),
                title=item['name']
                )
                oc.add(link)
    else:
        for item in content['videos']:
        
            Log('got video ' + str(item))
            oc.add(VideoClipObject(
                url=VIDEO_URL+ '&video_id='+str(item['id'])+'&token='+ TOKEN,
                title=item['name'],
                thumb = item['thumbnailURL'],
                duration = item['length'],
                #originally_available_at = DateTime.FromTimestamp(int(item['publishedDate'])),            
            ))
          
    return oc
