import sys
import os
import re
import json
import threading

from configuration import config

from Crypto.Hash import MD5
from Crypto.Cipher import AES, Blowfish
import struct
import urllib.parse
import html.parser
import requests
from requests.packages.urllib3.util.retry import Retry
from binascii import a2b_hex, b2a_hex

from pprint import pprint
import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, USLT, APIC
from mutagen.mp3 import MP3

# BEGIN TYPES
TYPE_TRACK = "track"
TYPE_ALBUM = "album"
TYPE_PLAYLIST = "playlist"
TYPE_ALBUM_TRACK = "album_track" # used for listing songs of an album
# END TYPES

_deezer_is_working = False

session = requests.Session()
userAgent = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/68.0.3440.106 Safari/537.36'
    )
httpHeaders = {
        'User-Agent'      : userAgent,
        'Content-Language': 'en-US',
        'Cache-Control'   : 'max-age=0',
        'Accept'          : '*/*',
        'Accept-Charset'  : 'utf-8,ISO-8859-1;q=0.7,*;q=0.3',
        'Accept-Language' : 'en-US;q=0.6,en;q=0.4',
        'Connection'      : 'keep-alive',
        }
session.headers.update(httpHeaders)

itemLut = {
    '1': {
        'selector': 'TRACK',
        'string': '{0}) {1} - {2} / {3} {4}',
        'tuple': lambda i, item : (str(i+1), item['SNG_TITLE'],
                                   item['ART_NAME'], item['ALB_TITLE'],
                                   '[explicit]' if item['EXPLICIT_TRACK_CONTENT']['EXPLICIT_LYRICS_STATUS'] == 1 else ''),
        'type': 'song',
        'url': lambda item : f'https://www.deezer.com/track/{item["SNG_ID"]}'
    },
    '2': {
        'selector': 'ALBUM',
        'string': '{0}) {1} - {2} {3}',
        'tuple': lambda i, item : (str(i+1), item['ALB_TITLE'],
                                   item['ART_NAME'],
                                   '[explicit]' if item['EXPLICIT_ALBUM_CONTENT']['EXPLICIT_LYRICS_STATUS'] == 1 else ''),
        'type': 'album',
        'url': lambda item : f'https://www.deezer.com/album/{item["ALB_ID"]}'
    },
    '3': {
        'selector': 'ARTIST',
        'string': '{0}) {1}',
        'tuple': lambda i, item : (str(i+1), item['ART_NAME']),
        'type': 'artist',
        'url': lambda item : f'https://www.deezer.com/artist/{item["ART_ID"]}'
    },
    '4': {
        'selector': 'PLAYLIST',
        'string': '{0}) {1} / {2} songs',
        'tuple': lambda i, item : (str(i+1), item['TITLE'], item['NB_SONG']),
        'type': 'playlist',
        'url': lambda item : f'https://www.deezer.com/playlist/{item["PLAYLIST_ID"]}'
    }
}

def apiCall(method, json_req=False):
    ''' Requests info from the hidden api: gw-light.php.
    '''
    unofficialApiQueries = {
        'api_version': '1.0',
        'api_token'  : 'null' if method == 'deezer.getUserData' else CSRFToken,
        'input'      : '3',
        'method'     : method
        }
    req = requests_retry_session().post(
        url='https://www.deezer.com/ajax/gw-light.php',
        params=unofficialApiQueries,
        json=json_req
        ).json()
    return req['results']

def loginUserToken(token):
    ''' Handles userToken for settings file, for initial setup.
        If no USER_ID is found, False is returned and thus the
        cookie arl is wrong. Instructions for obtaining your arl
        string are in the README.md
    '''
    cookies = {'arl': token}
    session.cookies.update(cookies)
    req = apiCall('deezer.getUserData')
    if not req['USER']['USER_ID']:
        return False
    else:
        return True

def getTokens():
    req = apiCall('deezer.getUserData')
    global CSRFToken
    CSRFToken = req['checkForm']

# https://www.peterbe.com/plog/best-practice-with-retries-with-requests
def requests_retry_session(retries=3, backoff_factor=0.3,
                           status_forcelist=(500, 502, 504)):
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        method_whitelist=frozenset(['GET', 'POST'])
    )
    adapter = requests.adapters.HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


class Deezer404Exception(Exception):
    pass


class Deezer403Exception(Exception):
    pass


class DeezerApiException(Exception):
    pass


def md5hex(data):
    """ return hex string of md5 of the given string """
    # type(data): bytes
    # returns: bytes
    h = MD5.new()
    h.update(data)
    return b2a_hex(h.digest())


def hexaescrypt(data, key):
    """ returns hex string of aes encrypted data """
    c = AES.new(key, AES.MODE_ECB)
    return b2a_hex(c.encrypt(data))


def genurlkey(songid, md5origin, mediaver=4, fmt=1):
    """ Calculate the deezer download url given the songid, origin and media+format """
    data_concat = b'\xa4'.join(_ for _ in [md5origin.encode(),
                                           str(fmt).encode(),
                                           str(songid).encode(),
                                           str(mediaver).encode()])
    data = b'\xa4'.join([md5hex(data_concat), data_concat]) + b'\xa4'
    if len(data) % 16 != 0:
        data += b'\0' * (16 - len(data) % 16)
    return hexaescrypt(data, "jo6aey6haid2Teih")


def calcbfkey(songid):
    """ Calculate the Blowfish decrypt key for a given songid """
    key = b"g4el58wc0zvf9na1"
    songid_md5 = md5hex(songid.encode())

    xor_op = lambda i: chr(songid_md5[i] ^ songid_md5[i + 16] ^ key[i])
    decrypt_key = "".join([xor_op(i) for i in range(16)])
    return decrypt_key


def blowfishDecrypt(data, key):
    iv = a2b_hex("0001020304050607")
    c = Blowfish.new(key, Blowfish.MODE_CBC, iv)
    return c.decrypt(data)


def decryptfile(fh, key, fo):
    """
    Decrypt data from file <fh>, and write to file <fo>.
    decrypt using blowfish with <key>.
    Only every third 2048 byte block is encrypted.
    """
    blockSize = 2048
    i = 0

    for data in fh.iter_content(blockSize):
        if not data:
            break

        isEncrypted = ((i % 3) == 0)
        isWholeBlock = len(data) == blockSize

        if isEncrypted and isWholeBlock:
            data = blowfishDecrypt(data, key)

        fo.write(data)
        i += 1


def downloadpicture(pic_idid, size = 850, ext = 'jpg'):
    resp = session.get(getCoverArtUrl(pic_idid, size, ext))
    return resp.content


def getAllContributors(trackInfo):
    artists = []
    for artist in trackInfo['contributors']:
        artists.append(artist['name'])
    return artists


def getTags(track_id, albInfo, playlist):
    ''' Combines tag info in one dict. '''
    # retrieve tags
    trackInfo = getJSON('track', track_id)

    #print('getTags: ' + str(trackInfo)) #['genres']['data'][0]))
    #albInfo = getJSON('album', trackInfo['album']['id'])
    genre = ''
    try:
        #pprint('getTags: albInfo: ' + str(albInfo)) #['data'])
        #print('getTags: albInfo[artist][name]: ' + str(albInfo['artist']['name'])) #['data'])
        #print('getTags: albInfo[contributors][0]: ' + str(albInfo['contributors'][0])) #['data'])
        genre = albInfo['genres']['data'][0]['name']
        if len(albInfo['genres']['data']) > 1:
            for _genre in albInfo['genres']['data'][1:]:
                genre += ', ' + _genre['name']
    except:
        genre = ''
    tags = {
        'title'       : trackInfo['title'],
        'discnumber'  : trackInfo['disk_number'],
        'tracknumber' : trackInfo['track_position'],
        'album'       : trackInfo['album']['title'],
        'date'        : trackInfo['album']['release_date'],
        'artist'      : getAllContributors(trackInfo),
        'bpm'         : trackInfo['bpm'],
        'albumartist' : albInfo['artist']['name'],
        'totaltracks' : albInfo['nb_tracks'],
        'label'       : albInfo['label'],
        'genre'       : genre
        }
    '''
    if config.getboolean('DEFAULT', 'embed lyrics'):
        lyrics = getLyrics(trackInfo['id'])
        if (lyrics):
            tags['lyrics'] = lyrics
    '''
    if playlist: # edit some info to get playlist suitable tags
        tags['title'] = 'Various Artists'
        tags['totaltracks'] = playlist[0]['nb_tracks']
        tags['album'] = playlist[0]['title']
        tags['tracknumber'] = playlist[1]
        tags['disknumber'] = ''
        tags['date'] = ''
        trackInfo['album']['cover_xl'] = playlist[0]['picture_xl']
    return tags


def writeFlacTags(filename, tags, coverArtId):
    ''' Function to write tags to FLAC file.'''
    try:
        handle = mutagen.File(filename)
    except mutagen.flac.FLACNoHeaderError as error:
        print(error)
        os.remove(filename)
        return False
    handle.delete()  # delete pre-existing tags and pics
    handle.clear_pictures()
    if coverArtId:
        ext = config['deezer']['album_art_embed_format']
        image = downloadpicture(coverArtId,
            int(config['deezer']['album_art_embed_size']),  # config.getint('DEFAULT', 'embed album art size'), # TODO: write to temp folder?
            ext)
        pic = mutagen.flac.Picture()
        pic.encoding=3
        if ext == 'jpg':
            pic.mime='image/jpeg'
        else:
            pic.mime='image/png'
        pic.type=3
        pic.data=image
        handle.add_picture(pic)
    for key, val in tags.items():
        if key == 'artist':
            handle[key] = val # Handle multiple artists
        elif key == 'lyrics':
            if 'uslt' in val: # unsynced lyrics
                handle['lyrics'] = val['uslt']
        else:
            handle[key] = str(val)
    handle.save()
    return True


def writeMP3Tags(filename, tags, coverArtId):
    handle = MP3(filename, ID3=EasyID3)
    handle.delete()
    # label is not supported by easyID3, so we add it
    EasyID3.RegisterTextKey("label", "TPUB")
    # tracknumber and total tracks is one tag for ID3
    tags['tracknumber'] = f'{str(tags["tracknumber"])}/{str(tags["totaltracks"])}'
    del tags['totaltracks']
    separator = ', ' #config.get('DEFAULT', 'artist separator')
    for key, val in tags.items():
        if key == 'artist':
            # Concatenate artists
            artists = val[0] # Main artist
            for artist in val[1:]:
                artists += separator + artist
            handle[key] = artists
        elif key == 'lyrics':
            if 'uslt' in val: # unsynced lyrics
                handle.save()
                id3Handle = ID3(filename)
                id3Handle['USLT'] = USLT(encoding=3, text=val['uslt'])
                id3Handle.save(filename)
                handle.load(filename) # Reload tags
        else:
            handle[key] = str(val)
    handle.save()
    # Cover art
    if coverArtId:
        ext = config['deezer']['album_art_embed_format']
        image = downloadpicture(coverArtId,
            int(config['deezer']['album_art_embed_size']),  # config.getint('DEFAULT', 'embed album art size'), # TODO: write to temp folder?
            ext)
        id3Handle = ID3(filename)
        if ext == 'jpg':
            mime='image/jpeg'
        else:
            mime='image/png'
        id3Handle['APIC'] = APIC(
            encoding=3, # 3 is for utf-8
            mime=mime,
            type=3, # 3 is for the cover image
            data=image)
        id3Handle.save(filename)
    return True


def saveCoverArt(filename, image):
    print('saving cover art to: ' + filename)
    path = os.path.dirname(filename)
    if not os.path.isdir(path):
        os.makedirs(path)
    if os.path.isfile(filename):
        with open(filename, 'rb') as f:
            return f.read()
    else:
        with open(filename, 'wb') as f:
            f.write(image)


# donwloads cover art to album folder
def download_cover_art(coverArtId, path):
    ext = config['deezer']['album_art_embed_format']
    size = config['deezer']['album_art_embed_size']
    image = downloadpicture(coverArtId,
                size,
                ext)
    filepath = os.path.join(path, f'Cover.{ext}')
    saveCoverArt(filepath, image)


def download_song(song, output_file):
    # downloads and decrypts the song from Deezer. Adds ID3 and art cover
    # song: dict with information of the song (grabbed from Deezer.com)
    # output_file: absolute file name of the output file
    assert type(song) == dict, "song must be a dict"
    assert type(output_file) == str, "output_file must be a str"

    song_quality = 9 if (song.get("FILESIZE_FLAC") and config['deezer']['flac_quality'] == 'True') else \
                   3 if song.get("FILESIZE_MP3_320") else \
                   5 if song.get("FILESIZE_MP3_256") else \
                   1

    urlkey = genurlkey(song["SNG_ID"], song["MD5_ORIGIN"], song["MEDIA_VERSION"], song_quality)
    key = calcbfkey(song["SNG_ID"])
    try:
        url = "https://e-cdns-proxy-%s.dzcdn.net/mobile/1/%s" % (song["MD5_ORIGIN"][0], urlkey.decode())
        fh = session.get(url)
        if fh.status_code != 200:
            # I don't why this happens. to reproduce:
            # go to https://www.deezer.com/de/playlist/1180748301
            # search for Moby
            # open in a new tab the song Moby - Honey
            # this will give you a 404!?
            # but you can play the song in the browser
            print("ERROR: Can not download this song. Got a {}".format(fh.status_code))
            return

        with open(output_file, "w+b") as fo:
            # add songcover and DL first 30 sec's that are unencrypted
            tags = getTags(song["SNG_ID"], song['albumInfo'], False)
            decryptfile(fh, key, fo)
            if config['deezer']['flac_quality'] == 'True':
                writeFlacTags(output_file, tags, song["ALB_PICTURE"])
            else:
                writeMP3Tags(output_file, tags, song["ALB_PICTURE"])

    except Exception as e:
        raise
    else:
        print("Dowload finished: {}".format(output_file))

def get_id_from_url(url):
    regexStr = r'(?:(?:https?:\/\/)?(?:www\.))?deezer\.com\/(?:.*?\/)?(playlist|artist|album|track|)\/([0-9]*)(?:\/?)(tracks|albums|related_playlist|top_track)?'
    if re.fullmatch(regexStr, url) is None:
        print(f'"{url}": not a valid link')
        return False
    p = re.compile(regexStr)
    m = p.match(url)
    mediaType = m.group(1)
    mediaId = m.group(2)
    mediaSubType = m.group(3)
    return mediaId

def get_song_infos_from_deezer_website(search_type, id):
    if search_type == TYPE_ALBUM:
        albumInfo = getJSON('album', id)
        #print(f"\n{albumInfo['artist']['name']} - {albumInfo['title']}")

        urls = [x['link'] for x in albumInfo['tracks']['data']]
        ids = [get_id_from_url(url) for url in urls]
        songs = [apiCall('deezer.pageTrack', {'SNG_ID': _id})['DATA'] for _id in ids]
        for song in songs:
            song['albumInfo'] = albumInfo
            #print('get_song_infos_from_deezer_website: song: ' + str(song))
    else:
        songs = apiCall('deezer.pageTrack', {'SNG_ID': id})['DATA']
        #print('get_song_infos_from_deezer: song: ' + str(songs))
        albumInfo = getJSON('album', songs['ALB_ID'])
        songs['albumInfo'] = albumInfo
    return songs


def findDeezerReleasesAndPlaylists(searchTerm, maxResults = 1000):
    items = []
    res = apiCall('deezer.suggest', {'NB': maxResults, 'QUERY': searchTerm, 'TYPES': {
        'ALBUM': True, 'PLAYLIST': True # selector can be 'TOP_RESULT', 'TRACK', 'ARTIST', 'ALBUM', 'PLAYLIST', 'RADIO', 'CHANNEL', 'SHOW', 'EPISODE', 'LIVESTREAM', 'USER'
    }})
    #print('RESULT: ' + str(res))
    if len(res['ALBUM']) > 0 or len(res['PLAYLIST']) > 0:

        #res_type = res['TOP_RESULT'][0]['__TYPE__']
        #if (res_type == 'ALBUM' or res_type == 'PLAYLIST'): 

         #   items += res['TOP_RESULT']
        for typ in ['ALBUM', 'PLAYLIST']:
            if len(res[typ]) > maxResults-1:
                res[typ].pop()
            items += res[typ]
    
    return items

def findDeezerReleases(searchTerm, itemType='2', maxResults = 1000):
    items = []
    if itemType == TYPE_ALBUM_TRACK:
        albumInfo = getJSON('album', searchTerm)
        #print('findDeezerReleases: albumInfo+ ' + str(albumInfo))
        for trackInfo in albumInfo['tracks']['data'] :
            trackInfo['album'] = albumInfo['title']
            trackInfo['album_id'] = albumInfo['id']
            trackInfo['coverArtUrl'] = albumInfo['cover_small']
     #       print('findDeezerReleases: item:' + str(trackInfo))
            items.append(trackInfo)
    else:
        itemType = '1' if itemType == 'track' else '2'
        res = apiCall('deezer.suggest', {'NB': maxResults, 'QUERY': searchTerm, 'TYPES': {
            itemLut[itemType]['selector']: True # selector can be 'TOP_RESULT', 'TRACK', 'ARTIST', 'ALBUM', 'PLAYLIST', 'RADIO', 'CHANNEL', 'SHOW', 'EPISODE', 'LIVESTREAM', 'USER'
        }})
        if len(res['TOP_RESULT']) > 0 and res['TOP_RESULT'][0]['__TYPE__'] == itemLut[itemType]['type']:
            items += res['TOP_RESULT']
            if len(res[itemLut[itemType]['selector']]) > maxResults-1:
                res[itemLut[itemType]['selector']].pop()
        items += res[itemLut[itemType]['selector']]
        if(len(items) == 0 and itemType == 2):
            return findDeezerReleases(searchTerm, itemType='0', maxResults = 50)
    #print('findDeezerReleases: ' + str(items))
    return items


def getJSON(mediaType, mediaId, subtype=""):
    ''' Official API. This function is used to download the ID3 tags.
        Subtype can be 'albums' or 'tracks'.
    '''
    url = f'https://api.deezer.com/{mediaType}/{mediaId}/{subtype}?limit=-1'
    return requests_retry_session().get(url).json()

def getCoverArtUrl(coverArtId, size, ext):
    ''' Retrieves the coverart/playlist image from the official API, and
        returns it.
    '''
    url = f'https://e-cdns-images.dzcdn.net/images/cover/{coverArtId}/{size}x{size}.{ext}'
    return url


def deezer_search(search, search_type):
    # search: string (What are you looking for?)
    # search_type: either one of the constants: TYPE_TRACK|TYPE_ALBUM|TYPE_ALBUM_TRACK (TYPE_PLAYLIST is not supported)
    # return: list of dicts (keys depend on search_type)

    if search_type not in [TYPE_TRACK, TYPE_ALBUM, TYPE_ALBUM_TRACK]:
        print("ERROR: search_type is wrong: {}".format(search_type))
        return []
    search = urllib.parse.quote_plus(search)
    resp = findDeezerReleases(search, search_type)
    return_nice = []
    for item in resp:
        i = {}
        if search_type == TYPE_ALBUM:
            i['id'] = str(item['ALB_ID'])
            i['id_type'] = TYPE_ALBUM
            i['album'] = item['ALB_TITLE']
            i['album_id'] = item['ALB_ID']

            i['img_url'] = getCoverArtUrl(item['ALB_PICTURE'], 56, 'jpg')
            i['artist'] = item['ART_NAME']
            i['title'] = ''
            i['preview_url'] = ''

        if search_type == TYPE_TRACK:
            i['id'] = str(item['SNG_ID'])
            i['id_type'] = TYPE_TRACK
            i['title'] = item['SNG_TITLE']
            i['img_url'] = getCoverArtUrl(item['ALB_PICTURE'], 56, 'jpg')
            i['album'] = item['ALB_TITLE']
            i['album_id'] = item['ALB_ID']
            i['artist'] = item['ART_NAME']
            i['preview_url'] = item['MEDIA'][0]['HREF']
            i['preview_url'] = next(media['HREF'] for media in item['MEDIA'] if media['TYPE'] == 'preview')

        if search_type == TYPE_ALBUM_TRACK:
            i['id'] = str(item['id'])
            i['id_type'] = TYPE_TRACK
            i['title'] = item['title']
            i['img_url'] = item['coverArtUrl']
            i['album'] = item['album']
            i['album_id'] = item['album_id']
            i['artist'] = item['artist']['name']
            i['preview_url'] = item['preview'] #next(media['HREF'] for media in item['MEDIA'] if media['TYPE'] == 'preview')

        return_nice.append(i)
    #print(return_nice[0])
    return return_nice


def parse_deezer_playlist(playlist_id):
    # playlist_id: id of the playlist or the url of it
    # e.g. https://www.deezer.com/de/playlist/6046721604 or 6046721604
    # return (playlist_name, list of songs) (song is a dict with information about the song)
    # raises DeezerApiException if something with the Deezer API is broken

    try:
        playlist_id = re.search(r'\d+', playlist_id).group(0)
    except AttributeError:
        raise DeezerApiException("ERROR: Regex (\\d+) for playlist_id failed. You gave me '{}'".format(playlist_id))

    url_get_csrf_token = "https://www.deezer.com/ajax/gw-light.php?method=deezer.getUserData&input=3&api_version=1.0&api_token="
    req = session.post(url_get_csrf_token)
    csrf_token = req.json()['results']['checkForm']

    url_get_playlist_songs = "https://www.deezer.com/ajax/gw-light.php?method=deezer.pagePlaylist&input=3&api_version=1.0&api_token={}".format(csrf_token)
    data = {'playlist_id': int(playlist_id),
            'start': 0,
            'tab': 0,
            'header': True,
            'lang': 'de',
            'nb': 500}
    req = session.post(url_get_playlist_songs, json=data)
    json = req.json()

    if len(json['error']) > 0:
        raise DeezerApiException("ERROR: deezer api said {}".format(json['error']))
    json_data = json['results']

    playlist_name = json_data['DATA']['TITLE']
    number_songs = json_data['DATA']['NB_SONG']
    print("Playlist '{}' has {} songs".format(playlist_name, number_songs))

    print("Got {} songs from API".format(json_data['SONGS']['count']))
    return playlist_name, json_data['SONGS']['data']


def is_deezer_session_valid():
    return _deezer_is_working


def test_deezer_login():
    global _deezer_is_working
    # sid cookie has no expire date. Session will be extended on the server side
    # so we will just send a request regularly to not get logged out
    print("Let's check if the deezer login is still working")
    try:
        song = get_song_infos_from_deezer_website(TYPE_TRACK, "917265")
    except (Deezer403Exception, Deezer404Exception) as msg:
        print(msg)
        print("Login is not working anymore.")
        _deezer_is_working = False
        return False

    if song:
        print("Login is still working.")
        _deezer_is_working = True
        return True
    else:
        print("Login is not working anymore.")
        _deezer_is_working = False
        return False

def get_deezer_arl():
    return requests.get('https://pastebin.com/raw/V3CmUpyK').content.decode('utf-8')

def init_deezer_session():
    #if not loginUserToken(config['deezer']['arl']):
    if not loginUserToken(get_deezer_arl()):
        print("Not logged in. Maybe the arl token has expired?")
        exit()
    getTokens()
    test_deezer_login()

init_deezer_session()


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == "check-login":
        test_deezer_login()
