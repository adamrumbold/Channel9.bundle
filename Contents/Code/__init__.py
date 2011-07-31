# PMS plugin framework
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *
import re

####################################################################################################

VERSION = 0.2

VIDEO_PREFIX = "/video/ch9"

NAME = L('Title')

# make sure to replace artwork with what you want
# these filenames reference the example files in
# the Contents/Resources/ folder in the bundle
ART           = 'art-ch9.jpg'
ICON          = 'icon-default.jpg'

FIX_PLAY_ROOT = "http://fixplay.ninemsn.com.au/"
FIX_PLAY_LIST = "http://fixplay.ninemsn.com.au/catalogue.aspx"
####################################################################################################
def Start():

    Plugin.AddPrefixHandler(VIDEO_PREFIX, MainMenu, L('VideoTitle'), ICON, ART)

    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

    MediaContainer.art = R(ART)
    MediaContainer.title1 = NAME
    DirectoryItem.thumb = R(ICON)
    
####################################################################################################
def MainMenu():
    dir = MediaContainer(viewGroup="List")
    content = XML.ElementFromURL(FIX_PLAY_LIST, True)
    for item in content.xpath('//div[@id="cat_hl_220089"]/span'):
        image = item.xpath('./span[@class="image"]/a/img')[0].get('src')
        image = FIX_PLAY_ROOT + image
        title = item.xpath('./span[@class="title"]/a[2]')[0].text
        link = item.xpath('./span[@class="title"]/a[2]')[0].get('href')
        link = FIX_PLAY_ROOT + link
        Log ("MainMenu -Link: " + link)
        dir.Append(Function(DirectoryItem(SeasonMenu, title=title, thumb=image), pageUrl = link, thumbUrl=image))
    return dir

####################################################################################################
def SeasonMenu(sender, pageUrl, thumbUrl):
    Log("In season menu")
    myNamespaces = {'ns1':'http://www.w3.org/1999/xhtml'}
    xpathQuery = '//div[@id="cat_hl_224591"]/span/span/a'
    Log ("reading pageUrl: " + pageUrl)
  
    dir = MediaContainer(title2=sender.itemTitle, viewGroup="InfoList")
    content = XML.ElementFromURL(pageUrl, True)
    videopage = HTTP.Request(pageUrl)
    #vidurl  = re.search("QTObject\(\"(.+?)\"", videopage).group(1)
    vidIter = re.finditer("\/section.aspx\?sectionid=.+?\<", videopage)
    seasons = {}
    
    for match in vidIter:
        Log("found match: "+ match.group())
        seasonURL = re.search("\/.+?\"", match.group()).group()
        lengthUrl = len(seasonURL)
        seasonURL = FIX_PLAY_ROOT + seasonURL[0:lengthUrl-1]
        seasonTxt = re.search("\>.+\s.+\<", match.group()).group()
        lengthTxt = len(seasonTxt)
        seasonTxt = seasonTxt[1:lengthTxt-1]
        if not seasons.has_key(seasonURL):
            seasons[seasonURL] = seasonTxt
            Log("seasonURL=" + seasonURL)
            Log("seasonTxt=" + seasonTxt)
            dir.Append(Function(DirectoryItem(VideoPage, title=seasonTxt, thumb=thumbUrl), pageUrl = seasonURL))
        
    return dir

####################################################################################################
def VideoPage(sender, pageUrl):
    dir = MediaContainer(title2=sender.itemTitle, viewGroup="InfoList")
    myNamespaces = {'ns1':'http://www.w3.org/1999/xhtml'}
    content = XML.ElementFromURL(pageUrl, True)
    Log ("reading pageUrl: " + pageUrl)
    xpathQuery = "//*[@id=\"season_table\"]/span/div"
    for item in content.xpath(xpathQuery, namespaces=myNamespaces):
        episode = item.xpath(".//div")[0].text
        title = item.xpath(".//div[@class='td col2']/h3")[0].text
        summary = item.xpath(".//div[@class='td col2']//span[@class='season_desc']")[0].text
        link = item.xpath(".//div[@class='td col3']/a")[0].get('href')
        link = FIX_PLAY_ROOT + link
        Log(link)
        dir.Append(WebVideoItem(link, title=title, summary=summary))
        
    return dir