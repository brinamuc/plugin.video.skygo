import sys
import xbmcgui
import xbmc
import xbmcplugin
import urllib
import base64
import urlparse
import struct
from skygo import SkyGo



addon_handle = int(sys.argv[1])
plugin_base_url = sys.argv[0]
params = dict(urlparse.parse_qsl(sys.argv[2][1:]))
skygo = SkyGo()

xbmcplugin.setContent(addon_handle, 'movies')


def build_url(query):
    return plugin_base_url + '?' + urllib.urlencode(query)



if params:
    if params['action'] == 'play':
        id = params['id']
        xbmc.log('Play SkyGo Movie with id: ' + id)
        skygo.login()
        sessionId = skygo.sessionId


        licenseUrl = 'https://wvguard.sky.de/WidevineLicenser/WidevineLicenser'


        playInfo = skygo.getPlayInfo(id)
        initData = 'kid={UUID}&sessionId='+sessionId+'&apixId='+playInfo['apixId']+'&platformId=WEB&product=BW&channelId='
        initData = struct.pack('1B',*[30])+initData
        initData = base64.urlsafe_b64encode(initData)
        print initData

        listitem = xbmcgui.ListItem(path=playInfo['manifestUrl'])
        listitem.setProperty('inputstream.smoothstream.license_type', 'com.widevine.alpha')
        listitem.setProperty('inputstream.smoothstream.license_key', licenseUrl)
        listitem.setProperty('inputstream.smoothstream.license_data', initData)
        listitem.setProperty('inputstreamaddon', 'inputstream.smoothstream')

        xbmcplugin.setResolvedUrl(addon_handle, True, listitem=listitem)

    elif params['action'] == 'topMovies':
        mostWatchedMovies = skygo.getMostWatched()
        for movie in mostWatchedMovies:
            url = build_url({'action': 'play', 'id': movie['id']})

            #Try to find a hero img
            heroImg = ''
            videoWallImg = ''
            cover = ''


            for image in movie['main_picture']['picture']:
                if image['type'] == 'hero_img':
                    heroImg = skygo.baseUrl + image['path'] + '/' + image['file']
                if image['type'] == 'videowall_home':
                    videoWallImg = skygo.baseUrl + image['path'] + '/' + image['file']
                if image['type'] == 'gallery':
                    cover = skygo.baseUrl + image['path'] + '/' + image['file']

            if movie['dvd_cover']:
                cover = skygo.baseUrl + movie['dvd_cover']['path'] + '/' + movie['dvd_cover']['file']


            xbmc.log("Hro image: " + heroImg, xbmc.LOGDEBUG)


            li = xbmcgui.ListItem(label=movie['title'])
            li.setArt({'thumb': cover, 'poster': cover, 'fanart': heroImg})

            info = {
                'genre': movie['category']['main']['content'],
                'year': movie['year_of_production'],
                'mpaa': movie['parental_rating']['value'],
                'title': movie['title'],
                'mediatype': 'movie',
                'originaltitle': movie['original_title'],
                'plot': movie['synopsis']
            }
            li.setInfo('video', info)



            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                        listitem=li, isFolder=False)

        xbmcplugin.endOfDirectory(addon_handle, updateListing=True, cacheToDisc=False)


    elif params['action'] == 'liveTv':
        channels = skygo.getChannels()
        for channel in channels:
            url = build_url({'action': 'playTv', 'id': channel['id']})


            li = xbmcgui.ListItem(label=channel['name'])
            li.setArt({'poster': skygo.baseUrl+channel['logo']})

            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                        listitem=li, isFolder=False)

        xbmcplugin.endOfDirectory(addon_handle, updateListing=True, cacheToDisc=False)



else:

    url = build_url({'action': 'topMovies'})
    li = xbmcgui.ListItem(label='Top Filme')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                        listitem=li, isFolder=True)

    url = build_url({'action': 'liveTv'})
    li = xbmcgui.ListItem(label='Live TV')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                        listitem=li, isFolder=True)


    xbmcplugin.endOfDirectory(addon_handle, updateListing=True, cacheToDisc=False)