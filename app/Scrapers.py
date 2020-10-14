# -*- coding: utf-8 -*-
import lxml.html
from multiprocessing.dummy import Pool
#import urllib.request, urllib.parse, urllib.error
from random import choice
from itertools import repeat
from functools import partial

#import pyDownload
from deezer import *

import time, json, random
import html

import sys, os, math, re
from datetime import datetime
import requests
import faster_than_requests as requests2
from base64 import *
from Riddim import *
#import globalsFile
from pprint import pprint

from unshortenit import UnshortenIt


spacer = ' ' * 5
domains = [ "adf.ly", "j.gs", "q.gs", "ay.gy", "zo.ee", "babblecase.com",
            "riffhold.com", "microify.com", "pintient.com", "tinyium.com",
            "atominik.com", "bluenik.com", "bitigee.com", "atomcurve.com",
            "picocurl.com", "tinyical.com", "casualient.com", "battleate.com",
            "mmoity.com", "simizer.com", "dataurbia.com", "viahold.com",
            "coginator.com", "cogismith.com", "kaitect.com", "yoalizer.com",
            "kibuilder.com", "kimechanic.com", "quainator.com", "tinyium.com",
            "pintient.com", "quamiller.com", "yobuilder.com", "skamason.com",
            "twineer.com", "vializer.com", "viwright.com", "yabuilder.com",
            "yamechanic.com", "kializer.com", "yoineer.com", "skamaker.com",
            "yoitect.com", "activeation.com", "brisktopia.com", "queuecosm.bid",
            "nimbleinity.com", "rapidtory.com", "swiftation.com",
            "velocicosm.com", "zipteria.com", "zipvale.com", "agileurbia.com",
            "briskrange.com", "threadsphere.bid", "dashsphere.com",
            "fasttory.com", "rapidteria.com", "sprysphere.com", "swifttopia.com",
            "restorecosm.bid", "bullads.net", "velociterium.com", "zipansion.com", "activeterium.com", "clearload.bid", "brightvar.bid", "activetect.net", "swiftviz.net", "kudoflow.com", "infopade.com", "linkjaunt.com", "combostruct.com", "turboagram.com", "wirecellar.com", "streamvoyage.com", "metastead.com", "briskgram.net", "swarife.com", "baymaleti.net", "dapalan.com", "cinebo.net", "stratoplot.com", "thouth.net", "atabencot.net", "ecleneue.com", "twiriock.com", "uclaut.net", "linkup.pro", "lopoteam.com", "keistaru.com", "gloyah.net", "cesinthi.com", "sluppend.com", "fainbory.com", "infopade.com", "onisedeo.com", "ethobleo.com", "evassmat.com", "aclabink.com", "optitopt.com", "tonancos.com", "clesolea.com", "thacorag.com", "xterca.net", "larati.net",
            #/** <-- full domains & subdomains --> */
           "chathu.apkmania.co", "alien.apkmania.co", "adf.acb.im", "packs.redmusic.pl", "packs2.redmusic.pl", "dl.android-zone.org", "out.unionfansub.com", "sostieni.ilwebmaster21.com", "fuyukai-desu.garuda-raws.net" ]

lockedLinksAdfLy = ['adf.ly', 'neswery.com', 'deciomm.com', 'j.gs', 'swarife.com', 'turboagram.com', 'atominik.com','microify.com','bluenik.com','tinyium.com','babblecase.com','riffhold.com','pintient.com','getrom.net']
lockedLinksSimple = ['bit.ly']
lockedLinks = lockedLinksAdfLy + lockedLinksSimple

_threaded = True

_per_page = 15

musicLinks = [
        'soundcloud.com',
        'youtube.com'
        ]
# regex to validate urls. pretty long, innit
pre_regex = r"""(?xi)
\b
(                           # Capture 1: entire matched URL
  (?:
    [a-z][\w-]+:                # URL protocol and colon
    (?:
      /{1,3}                        # 1-3 slashes
      |                             #   or
      [a-z0-9%]                     # Single letter or digit or '%'
                                    # (Trying not to match e.g. "URI::Escape")
    )
    |                           #   or
    www\d{0,3}[.]               # "www.", "www1.", "www2." ... "www999."
    |                           #   or
    [a-z0-9.\-]+[.][a-z]{2,4}/  # looks like domain name followed by a slash
  )
  (?:                           # One or more:
    [^\s()<>]+                      # Run of non-space, non-()<>
    |                               #   or
    \(([^\s()<>]+|(\([^\s()<>]+\)))*\)  # balanced parens, up to 2 levels
  )+
  (?:                           # End with:
    \(([^\s()<>]+|(\([^\s()<>]+\)))*\)  # balanced parens, up to 2 levels
    |                                   #   or
    [^\s`!()\[\]{};:'".,<>?]        # not a space or one of these punct chars
  )
)"""
regex = re.compile(pre_regex)
textToLower = 'translate(text(),"ABCDEFGHJIKLMNOPQRSTUVWXYZ", "abcdefghjiklmnopqrstuvwxyz")'

desktop_agents = ['Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14',
                 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
                 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
                 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0']

def random_headers_list():
    return (('User-Agent', choice(desktop_agents)),('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'))
def random_headers():
    return {'User-Agent': choice(desktop_agents),'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}

GOODPROXY=None
# can take list of xpaths and returns list of return values
def scrapeViaXPath(url, xpathList, use_proxy=False, referer=''):
    #print('xpat scrape called for: ' + str(url)+ ': ' +str(type(url)))
    if isinstance(url, str): # or isinstance(url, unicode):
        if (referer != ''):
            page = requests.get(url, headers=random_headers(), timeout=10)#{'User-Agent': 'Mozilla/5.0', 'referer': referer})
        else:
            forbidden = True
            if use_proxy == True:
                while forbidden:
                    proxies = getProxies()
                    for proxy in proxies:
                        print('proxy: ' + str(proxy))
                        try:
                            page = requests.get(url, headers=random_headers(), timeout=8,proxies=proxy)#{'User-Agent': 'Mozilla/5.0'})
                            page.raise_for_status()
                        except requests.exceptions.ProxyError:
                            print('Proxy Error: ' + proxy['https'])
                        except requests.exceptions.ConnectionError:
                            print('Conn Error: ' + proxy['https'])
                        except requests.exceptions.Timeout:
                            print('Proxy Timeout: ' + proxy['https'])
                        except requests.HTTPError as e:
                            status_code = e.response.status_code
                            print(status_code)
                        else:
            #                titleStr = lxml.html.fromstring(page.content).xpath('//title/text()')
            #                print(titleStr)
            #                print(page.content)
            #                if not '403' in titleStr:
                            forbidden = False
                            retProxy = proxy
                            print('set GOODPROXY to ' + str(GOODPROXY))
                            break
                    proxies = getProxies()
            else:
                while forbidden:
                    try:
                        page = requests.get(url, headers=random_headers())#{'User-Agent': 'Mozilla/5.0'})
                        page.raise_for_status()
                        if 'error.php' in page.url:
                            print('error.php detected in url')
                        time.sleep(.5)
                    except requests.HTTPError as e:
                        status_code = e.response.status_code
                        print('status_code: "' + str(status_code) + '"')
                        #if status_code == '503':
                        #    pass
                        if status_code == '404':
                            print('Four-O-Four!')
                            #return []
                    except:
                        print('retrying download: ' + str(url))

                    else:
                        forbidden = False
            #page = requests.get(url, headers=random_headers())#{'User-Agent': 'Mozilla/5.0'})
        tree = lxml.html.fromstring(page.content)
    else:
        tree = url
    content = []
    contents = []
    #print('Tree: ' + str(tree))
    #print '____COOKIES: ' + str(page.cookies)
    if type(xpathList) is str:
        xpathList = [xpathList]
    for xpath in xpathList:
        #print('searching with xpath: ' + xpath)
        content = tree.xpath(xpath)
        if len(content) == 0:

            #print(tree)
            print('nothing found.')
        for result in content:
            #print('result type: ' + str(type(result)))
            if 'html' in str(type(result)):
                result = lxml.html.tostring(result)
            while type(result) is list:
  #              print('list found!')
                result = result[0]
            #result = result.encode('utf-8')
            #print('line! ' + result)
        contents.append(content)
        content = []
    if use_proxy:
        return contents[0], retProxy
    else:
        #if len(contents) == 1:
        #    contents = contents[0]
        return contents

#def handledRequest(url, proxy=False):


def getProxies():
    print('getting proxy')
    countries = ['belgium', 'france', 'ukraine', 'brazil','netherlands', 'canada' ]
    index = int(random.random()*len(countries))
    niceProxies = []
    while len(niceProxies) == 0:
        index = (index + 1) % len(countries)
        country = countries[(index)]
        url = 'http://www.gatherproxy.com/proxylist/country/?c=' + country
        print('using proxy from ' + country)
        data = scrapeViaXPath(url, '//table/script')[0]
        for proxyStr in data:
            d = json.loads(proxyStr.text.split('(')[1].split(')')[0])
            if d['PROXY_TYPE'] == 'Elite' and int(d['PROXY_TIME']) < 200:
                proxyString = d['PROXY_IP'] + ':' + str(int(d['PROXY_PORT'], 16))
                niceProxies.append({'https':proxyString})
    #print(niceProxies)
    return niceProxies

def unlockAdfLy(adfLyURL):
    #print('unlockAdfLy called with ' + adfLyURL)
    try:
        adfly_data = requests.get(adfLyURL).content
        ysmm = adfly_data.split(b"ysmm = '")[1].split(b"';")[0] # Find encrypted URL code in URL source
        #print 'YSMM: ' + ysmm
    except:
        print(('An Error occured unlocking ' + adfLyURL))
        return ''
    key=[]
    code = ysmm
    zeros, ones = '', ''
    for num, letter in enumerate(code):
        if num % 2 == 0: zeros += chr(code[num])
        else: ones = chr(code[num]) + ones
    code = zeros + ones
    U = [str(x) for x in code]#''.split(code)
    num = 0
    while num < len(U):# val in enumerate(U):
        #print('in adfly unlock loop')
        letter = (U[num])
        if letter.isdigit():#math.isnan(letter)
            R = num+1
            while R < len(U):
                if (U[R]).isdigit():#math.isnan(R):
                    # xor yields different results than js version
                    S = int(letter) ^ int(U[R])
                    if (S < 10):
                        U[num] = S#.encode('utf-8')
                    num = R
                    R = len(U)
                else:
                    R = R + 1
        num = num + 1
    code = ''.join(str(x) for x in U)
    ##print('CODE: ' + code)
    code = b64decode(code)#.encode('latin1')
    ret = code[16:-16].decode()
    #print('adfly unlock returns: ' + str(ret) + ' type ' + str(type(ret)))
    return ret

def unlockBitLy(bitLyURL):
    print('unlocking bit.ly link: ' + bitLyURL)
    #start = time.time()
    
    #rand_headers = random_headers_list()
    #print(str(type(rand_headers)))
    #print(str((rand_headers)))
    
    bitLyData = requests.get(bitLyURL + '+', headers=random_headers())
    #bitLyData = requests2.requests(bitLyURL + '+', 'GET', '', http_headers=rand_headers)
    #print(bitLyData)
    
    #mid = time.time()
    #print('got site in: ' + str(mid - start))
    #soup = (bitLyData['body'])
    soup = (bitLyData.content).decode()
    link = soup.split('"long_url": "')[1].split('",')[0]
    
    #end = time.time()
    #print('got link in: ' + str(end - mid))
    
    #print(str(len(link)) + ' got bitly data: ' + str(link))
    print(link)
    return link

def unlockClearload(link, referer):
    # wont work because we need a cookie with some information to fake a real user
    data = requests.get(link, headers={'referer': 'eyJ1cmwiOiJodHRwOlwvXC9jbGVhcmxvYWQuYmlkIiwiZG9tYWluIjoiaHR0cDpcL1wvY2xlYXJsb2FkLmJpZFwvLTEyRlZNQVwvMVVaUCJ9'}).content
    print(('CLAR: ' + data))
    toReturn = scrapeViaXPath(link, '//a[0]/@href', '')
    print(toReturn)



class Scraper(object):
    """The Scraper Class is a base class for scrapers of specific websites.
       It acts as an interface so that the Downloader class can call the same methods for every scraper."""
    '''
    updated = QtCore.pyqtSignal()
    releaseItemReady = QtCore.pyqtSignal(object)
    riddimReady = QtCore.pyqtSignal(Riddim)
    increase_page_count = QtCore.pyqtSignal(int)
    increase_processed_page_count = QtCore.pyqtSignal(int)
    '''
    def __init__(self):
        """docstrign"""
        super(Scraper, self).__init__()

        self.PATH_CUR = ''
        self.query = ''
        self.results = []
        self.coverArtQueue = []
        self.riddims_failed = []
        self.password = ''
        self.folderName = ''
        self.scrapeFlag = False
        self.logoUrl = ''
        self.base_url = ''
        self.name = ''
        self.startedYear = 0
        self.searchYear = 'All'
        self.searchMonth = 'All'
        self.lastPages = 'All'
        #self.proxyIP = self.getProxy()
        self.slowScrape = False
        self.scraping = False
        self.unlock_links = True

        self.xpath_pageAmount = ''
        self.xpath_releases = ''
        self.xpath_relative_link = ''
        self.xpath_relative_coverArt = ''
        self.xpath_relative_name = ''
#        self.coverArtQueueLoPrio = []
        self.unshortener = UnshortenIt()

        self.nogoes = [
                'mailto:',
                '.jpg',
                '.png'
                '.jpeg'
                'plus.goole.com/share',
                'twitter.com',
                'facebook.com',
                'automattic.com',
                'instagram.com',
                'mn2s.com',
                'api.whatsapp',
                'whatsapp://',
                '#cancel',
                'jetpack.com',
                'paypal.com',
                'share=email',
                'http://bit.ly/2FH0rfE',
                'http://bit.ly/2d6mON0',
                'amazon.com',
                'stumbleupon.com'
                ]
    def __str__(self):
        return self.name

    def set_result_target(self, target_list):
        self.results = target_list

    def getProxy(self):
        url = 'https://free-proxy-list.net/'
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Cafari/537.36'}
        source = str(requests.get(url, headers=headers, timeout=10).text)
        data = [list(filter(None, i))[0] for i in re.findall('<td class="hm">(.*?)</td>|<td>(.*?)</td>', source)]
        groupings = [dict(zip(['ip', 'port', 'code', 'using_anonymous'], data[i:i+4])) for i in range(0, len(data), 4)]
        final_groupings = [{'full_ip':"{ip}:{port}".format(**i)} for i in groupings]
        print(final_groupings)

    def linkUnlock(self, link):
        """ unlocks bit.ly links and similar"""
        #print('trying to unlock ' + str(link) + '\ntype: ' + str(type(link)))
        if not any(lockedLink in link for lockedLink in lockedLinks):
            #print 'Link ' + link + ' cannot be unlocked! '
            return link
        if any(adfLyLink in link for adfLyLink in lockedLinksAdfLy):
            newlink = unlockAdfLy(link)
            if 'clearload' in newlink:
                return link
            #else:
                #linkClean = unlockAdfLy(link)
            #    link = unlockClearload(link, link)
        #print '__link: ' + link
        if any(lockedLink in link for lockedLink in lockedLinksSimple):
            newlink = unlockBitLy(link)
        #print 'unlocked! ' + link
        if 'clearload.bid' in newlink:
            return link
        else:
            return self.linkUnlock(newlink)

    def get_releases(self, search_string):
        self.scraping = True
        if self.rest_api_support:
            return self.get_releases_from_rest_api(search_string, self.searchYear, self.searchMonth)
        else:
            return self.get_releases_from_search(search_string)

    def get_releases_from_rest_api_old(self, search_string, start_year='ALL'):
        self.query = search_string
        rest_string = '/wp-json/wp/v2/posts?search=' + search_string + '&per_page=100'
        if start_year != 'ALL':
            rest_string += '&after=' + start_year + '-01-01T00:00:00'
        found_releases_amount = 100
        start_page = 1
        found_releases = []
        found_releases_par = []
        url = self.base_url + rest_string + '&page='
        while(found_releases_amount == 100):
            url_page = url + str(start_page)
            #url_page = "{:}{:}".format(url, start_page)
            start_page += 1
            print(url_page)
            result = requests.get(url_page, headers=random_headers())
            json_result = json.loads(result.content)
            if len(json_result) < 5:
                print(str(type(json_result)))
                print('result in json: ' + str(json_result))
            found_releases_amount = len(json_result)
            print(found_releases_amount)
            #LINK_REGEX = re.compile(r'href="(.*?)"')
            start = time.time()
            for entry in json_result:
                new_riddim = self.handle_rest_release(entry)
                found_releases.append(new_riddim)
            end = time.time()
            startpar = time.time()
            p = Pool(processes = found_releases_amount)
            found_releases_par += p.map(self.handle_rest_release, json_result)
            p.terminate()
            p.join()
            endpar = time.time()
            print('__HANDLING RELEASES SERIALLY TOOK: ' + str(end - start))
            print('__HANDLING RELEASES IN PARALLEL TOOK: ' + str(endpar - startpar))
            #self.increase_processed_page_count.emit(1)
        #print('found: ' + str(len(found_releases)))
        self.scraping = False
        return found_releases

    def clean_name_for_search(self, name_passed, chunk_amount=2):
        clean_name = name_passed
		# TODO for each year from 1960 till now -> add to not wanted eg. [1960]
        not_wanted =  ['[full promo]', ' ft ', ' ep', ' lp', '[promo]', '&', 'riddim driven', ' (reggae)', ' (dancehall)', ' x ', ',']
        for date in range(1900, datetime.today().year):
            not_wanted.append('[' + str(date) + ']')
            not_wanted.append(str(date))
        for nw in not_wanted:
            clean_name = clean_name.lower().replace(nw, ' ')
        #name_split = clean_name.split(u'u\2013')
        name_split = clean_name.split('–')
        print(name_split)
        if 'riddim' in name_split[0].strip().lower():
            clean_name = name_split[0].split('riddim')[0] + ' riddim'
        else:
            clean_name = ' '.join(name_split[:int(chunk_amount)])
        '''
        elif self.query in name_split[0].strip().lower():
            if len(name_split) == 2:
                clean_name = ' '.join(name_split)
            if len(name_split) == 3:
                clean_name = ' '.join(name_split[:-1])
            if len(name_split) == 4:
                clean_name = ' '.join(name_split[:-2])
        '''
        print('changed ' + name_passed + ' to ' + clean_name)
        return clean_name

    def handle_rest_release(self, entry):
        title = html.unescape(entry['title']['rendered'])
        #name = '-'.join(html.unescape(title).split(u'\u2013')[:-1])
        #name = html.unescape(entry['title']['rendered']).split(u'\u2013')[0]
        #name = self.clean_name_for_search(title)
        name = ''
        clean_links = []
        cover = ''
        deezer_link = ''
        #deezer_results_album = findDeezerReleases(name)
        deezer_results_album = []
        #print(deezer_results_album)
        candidates = []
        
        print('before for loop.')
        for i in [2,1]:
            print('in for loop: ' + str(i))
            name = self.clean_name_for_search(title, i)
            deezer_results_album = findDeezerReleases(name)
            if len(deezer_results_album) != 0:
                break
        if len(deezer_results_album) == 0:
            name = name.replace('riddim', '')
            deezer_results_album = findDeezerReleases(name)

        if len(deezer_results_album) != 0:
            top_candidates = deezer_results_album[0:15]
            for top_candidate in top_candidates:
        #        pprint('CANDIDATE: ' + str(top_candidate))
                string = itemLut['2']['tuple'](0, top_candidate)
                candidates.append({
                    "deezer_album": top_candidate["ALB_TITLE"], 
                    "deezer_artist": top_candidate["ART_NAME"], 
                    "deezer_name": top_candidate["ALB_TITLE"] if top_candidate["__TYPE__"] == "album" else top_candidate["SONG_TITLE"],
                    "deezer_id": itemLut['2']['url'](top_candidate).split('/')[-1], # Song id if type track?
                    "deezer_link": itemLut['2']['url'](top_candidate), 
                    "deezer_cover": getCoverArtUrl(top_candidate['ALB_PICTURE'], 90, 'jpg'), 
                    "type": top_candidate['__TYPE__']
                })
                print('found deezer album: ' + string[1])
        #else:
        #    deezer_results_playlist = findDeezerReleases(name, itemType = '4')
        #    if len(deezer_results_playlist) != 0:
        #        top_candidate = deezer_results_playlist[0]
#
#                string = itemLut['4']['tuple'](0, top_candidate)
#                deezer_name = string[1]
#                deezer_link = itemLut['4']['url'](top_candidate)
#                print('found deezer playlist: ' + name + ': ' + link)
        #start = time.time()
        xpath_links = '//a/@href'
        xpath_cover = '//img/@src'
        tree = lxml.html.fromstring(str(entry['content']))
        links = tree.xpath(xpath_links)
        #xpath = time.time()
        #links_regex = LINK_REGEX.finditer(str(entry))
        #regex = time.time()
        #print('xpath took: ' + str(xpath - start))
        #print('regex took: ' + str(regex - xpath))
        #for l in links_regex:
        #    print(str(l))
        try:
            yoast_tree = lxml.html.fromstring(str(entry['yoast_head']))
            xpath_cover = '//meta[@property="og:image"]/@content'
            cover = yoast_tree.xpath(xpath_cover)
            print('cover: ' + str(cover))
            if cover != []:
                # if we found coverArt URL strings, use the first one
                cover = cover[0]
        except Exception as e:
            print('cover acquiration Error: ' + e)
        #clean_links = [self.linkUnlock(link) for link in links if not any([nogo in link for nogo in self.nogoes])e
        #if self.unlock_links:
        #    clean_links = [self.unshortener.unshorten(link) for link in links if not any([nogo in link for nogo in self.nogoes])]
        #else:
        clean_links = [link for link in links if not any([nogo in link for nogo in self.nogoes])]
        if len(clean_links) == 0:
            return
        thread_link = entry['link']
            #print( name + ': ' + str(clean_links))
        new_riddim = {"name": title, "deezer_candidates": candidates, "thread_link": thread_link, "query": self.query, "url_cover": cover}
        #new_riddim = Riddim(name, link, self.query, self, urlCover=cover)
        #new_riddim = Riddim(name.replace(u'\u2013', ' - ').replace(U'\u2018', "'").replace(u'\u2019', "'").replace(u'\u201C', '"').replace(u'\u201D', '"'), entry['link'], self.query, self, cover)
        #if len(clean_links) > 0:
        #    new_riddim.setDownloadUrls(clean_links)
        #new_riddim.ready = True
        #self.riddimReady.emit(new_riddim)
        # emit signal with new_riddim
        return new_riddim

    ''' returns releases from a specific page number '''
    def get_page_no(self, page_number):
        if self.pages_processed[page_number] == '':
            self.pages_processed[page_number] = []
            for entry in self.pages[page_number]:
                #print('ENTRY: ' + str(entry))
                new_release = self.handle_rest_release(entry)
                self.pages_processed[page_number].append(new_release)
        return self.pages_processed[page_number]

    ''' downloads all pages of the search result from REST api
        returns the first page, processed.
    '''
    def get_releases_from_rest_api(self, search_string, start_year='ALL', start_month=None):
        self.query = search_string
        rest_string = '/wp-json/wp/v2/posts?search=' + search_string + '&per_page=' + str(_per_page)
        if start_year.lower() != 'all':
            before_string = '&before=' + str(int(start_year) + 1) + '-01-01T00:00:00'
            after_string = '&after=' + start_year
            month_string = '-01-01T00:00:00'
            if start_month != 'All':
                before_string = '&before=' + str(start_year) + '-' + "{:0>2}".format(str(int(start_month) + 1)) + '-01T00:00:00'
                month_string = '-' + start_month + '-01T00:00:00'
            after_string += month_string
            rest_string += after_string + before_string
        # add blog-specific excluders (news etc)
        rest_string += self.exclude_string
        found_releases_amount = _per_page
        start_page = 0
        found_releases = []
        #found_releases_par = []
        self.pages = []
        self.pages_processed = []
        url = self.base_url + rest_string + '&page='
        while(found_releases_amount == _per_page):
            start_page += 1
            url_page = url + str(start_page)
            print(url_page)
            result = requests.get(url_page, headers=random_headers())
            json_result = json.loads(result.content)
            self.pages.append(json_result)
            self.pages_processed.append("")
            if len(json_result) < 5:
                print(str(type(json_result)))
                print('result in json: ' + str(json_result))
            if len(json_result) == 0:
                return []
            found_releases_amount = len(json_result)
            print(found_releases_amount)
            #LINK_REGEX = re.compile(r'href="(.*?)"')
        #self.pages_processed = [len(self.pages) * '']
        
        '''
        startpar = time.time()
        p = Pool(processes = found_releases_amount)
        found_releases_par += p.map(self.handle_rest_release, json_result)
        p.terminate()
        p.join()
        endpar = time.time()
        print('__HANDLING RELEASES SERIALLY TOOK: ' + str(end - start))
        print('__HANDLING RELEASES IN PARALLEL TOOK: ' + str(endpar - startpar))
        '''
        print('length pages: ' + str(len(self.pages)))
        print('length pages_processed: ' + str(len(self.pages_processed)))
        found_releases = self.get_page_no(0)
        return {'pages': start_page, 'releases': found_releases}


    def get_releases_from_search(self, query):
        global _threaded
        results = []
        addIn = ''
        if self.searchYear != 'All':
            addIn = self.searchYear
        pageString = self.base_url + addIn + '?s=' + query
        print(addIn + 'searching for ' + query + ' on ' + self.name)
        num_pages = 1
        num_pages_str = ''
      #  import ipdb; ipdb.set_trace(context=11)
        [pageNumFound, pageContent] = scrapeViaXPath(pageString, [self.xpath_pageAmount, '/html'])
        print('page number found: '+ str(pageNumFound))
        if len(pageNumFound) > 0:
            num_pages_str = pageNumFound[0]
            num_pages = int(str.split(num_pages_str)[-1])
            if self.lastPages != 'All':
                num_pages = min(num_pages, self.lastPages)

        self.query = query
        cataloguePages = []
        results = self.get_releases_from_page(pageContent[0])
        #self.increase_page_count.emit(num_pages)
        if num_pages > 1:
            for x in range(2,num_pages+1):
                cataloguePage = self.base_url + addIn + '/page/' + str(x) + '/?s=' + query
                cataloguePages.append(cataloguePage)
                if not _threaded:
                    print('not threaded!')
                    self.get_releases_from_page(cataloguePage) #, cataloguePage)

            if _threaded:
                print('scraping search result pages with threads.')
                p = Pool(processes=self.max_parallel_scrapes)
                results.extend(r for l in p.map(partial(self.get_releases_from_page), cataloguePages) for r in l)
                p.terminate()
                p.join()

        print('Done scraping!')
        self.scraping = False
        self.results = results
        return results

    def get_releases_from_page(self, _page):
        global _threaded
        if isinstance(_page, str):
            print(('scraping riddims from: ' + _page + ' ...'))
        riddims = []
        foundReleases = scrapeViaXPath(_page, [self.xpath_releases])[0]
        if len(foundReleases) == 0:
            print('nothing found.')
            return []
        #print(page.content)
        for release in foundReleases:
            releaseCoverArt = ''
            [releaseName, releaseLink, releaseCoverArt] = scrapeViaXPath(release, [self.xpath_relative_name, self.xpath_relative_link, self.xpath_relative_coverArt])
            #print('xpath got through.')
            #print 'lengths: ' + str(len(releaseName)) + str(len(releaseLink)) + str(len(releaseCoverArt))
            #if len(releaseCoverArt) == 1:
            #    releaseCoverArt = releaseCoverArt[0]
            while type(releaseName) is list:# and len(releaseName) == 1:
                releaseName = releaseName[0]
            while type(releaseLink) is list:# and len(releaseLink) == 1:
                releaseLink = releaseLink[0]
            while type(releaseCoverArt) is list:# and len(releaseCoverArt) == 1:
                releaseCoverArt = releaseCoverArt[0]
            if len(releaseName) != 0 and len(releaseLink) != 0:
                print('RELEASE NAME: ' + releaseName) #.encode('utf-8'))
            #print('\nCoverArt: ' + releaseCoverArt.encode('utf-8'))
                newRiddim = Riddim(releaseName.replace(u'\u2013', ' - ').replace(U'\u2018', "'").replace(u'\u2019', "'").replace(u'\u201C', '"').replace(u'\u201D', '"'), releaseLink, self.query, self, releaseCoverArt)
                riddims.append(newRiddim)
                #if not _threaded:
                #self.scrape_riddimInfo(newRiddim)
            #print('appended riddim to Scrapers foundreleases.')
        #if _threaded:
        process_amount = len(riddims)
        if self.slowScrape:
            process_amount = self.max_parallel_scrapes
        pool = Pool(processes=process_amount)
        pool.map(self.scrape_riddimInfo, riddims)
        pool.terminate()
        pool.join()

        #for riddim in riddims:
        #    self.scrape_riddimInfo(riddim)
        time.sleep(.01)
        #self.updated.emit()
        print('finished!')
        return riddims

    def scrape_riddimInfo(self, riddim):
        pageUrl = riddim.urlForumThread #.decode()
        print(('scraping riddim: ' + str(pageUrl)))
        content = scrapeViaXPath(pageUrl, self.xpath_links)
        #print(('---recieved content from ' + riddim.name + "'s site: " + pageUrl))
        cleanLinks = []
        #print 'Content: ' + str(content)
        if len(content) != 0:
            dlLinks = content[0]
            for link in dlLinks:
                #link = urllib.unquote(link.split('url=')[1])
                #print('LINK: ' + str(link))
                if not any([nogo in link for nogo in self.nogoes]):
                    if not any([musicLink in link for musicLink in musicLinks]):
                        cleanLinks.append(str(self.linkUnlock(link))) #Unlock(link)) #.encode('utf-8'))
                    else:
                        riddim.urlsListen.append(link)
            #print(("CleanLinks: " + str(cleanLinks)))
            #print('Music Links: ' + str(riddim.urlsListen))
            #riddim.urlsListen = [link if any(musicLink in link for musicLink in musicLinks) for link in cleanLinks)]
            riddim.urlsDownload = cleanLinks
        else:
            print(('Nothing found for ' + riddim.name))
        riddim.ready = True
        #self.riddimReady.emit(riddim)
        return cleanLinks

    def tryToUnpack(self, filePath, releaseName=''):
        print(('trying to unpack: ' + filePath))
        truncated_file, ext = os.path.splitext(filePath)
        new_folder = os.path.abspath(truncated_file.encode('utf-8'))
        print(new_folder)
        if releaseName != '':
            new_folder = os.path.join(self.PATH_CUR, releaseName)
        if not os.path.exists(new_folder):
            os.makedirs(new_folder)
        if ext == '.rar':
            arch_ref = rarfile.RarFile(filePath,'r')
        elif ext == '.zip':
            arch_ref = zipfile.ZipFile(filePath,'r')
        nameList = arch_ref.namelist()
        #print nameList
        for i in nameList:
    #            print i
            base, ext = os.path.splitext(i)
            if ext.lower() in '.mp3 .wav .ogg .flac .m4a .jpg .jpeg .gif .png'.split():
                #i = i.encode('utf-8')
                #print i
                data = arch_ref.read(i, self.password)
                myfile_path = os.path.join(new_folder, i.split("/")[-1])
                myfile = open(myfile_path, "wb")
                myfile.write(data)
                myfile.close()

    def get_link_mediafire(self, div_tag):
        script_tag = div_tag("script")[0]
        link = re.findall(regex, script_tag.contents[0])[0][0]
        div_tag = soup.find_all(id="lrbox")[0]
        return link

    def get_link_zippyshare(self, zippySite):
        path_link = '//a[id()="dlbutton"]/following::script[1]/text():'
        print(path_link)
        div_tag = soup.find_all(id="lrbox")[0]
        script_tag = div_tag("script")[1]

        # We take apart the script tag and read out the parts of the download link
        script_tag = str(script_tag).replace("(","").replace('"','').replace(')', '')

        link_bits = script_tag.split('\n')[1].split('=')[1].split('+')
        hashval = str(eval(link_bits[1]) + eval(link_bits[2]))
        link = link_bits[0]  + hashval + link_bits[-1]
        link = link.replace(";", "")

        url_base = link.rsplit('/', 3)[0]

        ns = vars(math).copy()
        ns ['__builtins__'] = None
        #print "Math: " +  link_bits[1]
        link = link.replace(' ','')

        if len(div_tag("script")) == 5:
            pass
        return link


    def notifyPossibleError(self, riddim, dl_links_string, possibleWrongDownload):
        #print makeLookCool(spacer +'Could not Download ' + riddim[0].encode('utf-8') + '\n')
        print((spacer + ( spacer + 'Sites not supported or Files Deleted.')))
        riddim_fail_string = '\n' + riddim.name.encode('utf-8') + '\n' + riddim.urlForumThread.encode('utf-8') + '\n'
        if possibleWrongDownload:
            riddim_fail_string += 'INFO: ONLY GOT MP3. Please download Riddim Release Manually IF THIS ISNT A SINGLE RELEASE.\n'
        else:
            riddim_fail_string += 'INFO: UNSUPPORTED sites, or files NO LONGER AVAILABLE.\n'
        riddim_fail_string += dl_links_string
        self.riddims_failed.append(riddim_fail_string)
        #print makeLookCool(riddim_fail_string)
        f = open(os.path.join(self.PATH_CUR,'failed.txt'), 'a')
        f.write(riddim_fail_string)
        f.close()

    def getCoverArtThread(self, riddim):
        t = Thread(target=self.scrape_riddimInfo, args=[riddim])
        t.start()

class RiddimsCoScraper(Scraper):
    """docstring for RiddimsCoScraper"""
    ''' categories:
            News: 1378

    '''

    ## TODO: update scraper to use
    def __init__(self):
        super(RiddimsCoScraper, self).__init__()
        self.password = ''
        self.exclude_string = '&categories_exclude=1378'
        self.rest_api_support = True
        self.folderName = 'RiddimsWorld.com'
        #self.logoUrl = 'https://i1.wp.com/www.riddims.co/wp-content/uploads/2018/08/riddims-dancehall-reggae-soca-world.jpg'
        self.logoUrl = 'https://riddimsworld.com/wp-content/uploads/2019-Stream-Download-Riddims-World.png'
        self.base_url = 'https://riddimsworld.com/'
        self.name = 'RiddimsWorld.com'
        self.startedYear = 2012
        self.xpath_pageAmount = '//div[contains(@class,"page-nav")]//a[@class="last"]/text()'
        self.xpath_releases = '//div[contains(@class,"td_module_16")]//div[contains(@class, "td-module-thumb")]'
        self.xpath_relative_link = './/a[contains(@class, "td-image-wrap")]/@href'
        self.xpath_relative_name = './/a[contains(@class, "td-image-wrap")]/@title'
        self.xpath_relative_coverArt = './/a[contains(@class, "td-image-wrap")]//img[contains(@class, "entry-thumb")]/@src'
        self.xpath_links = '//div[contains(@class, "td-post-content")]//a[contains(@target,"_blank")]/@href'
        self.max_parallel_scrapes = 8
'''
    def handle_rest_release(self, entry):
        title = html.unescape(entry['title']['rendered'])
        #name = '-'.join(html.unescape(title).split(u'\u2013')[:-1])
        #name = html.unescape(entry['title']['rendered']).split(u'\u2013')[0]
        name = self.clean_name_for_search(title)
        clean_links = []
        cover = ''
        deezer_results_album = findDeezerReleases(name)
        deezer_results_playlist = findDeezerReleases(name, itemType = '4')
        #print('deezer_results_album: ' + deezer_results_album)
        if len(deezer_results_album) != 0:
            top_candidate = deezer_results_album[0]

            string = itemLut['2']['tuple'](0, top_candidate)
            name = string[1]
            link = itemLut['2']['url'](top_candidate)
            print(name)
            print(link)
        elif len(deezer_results_playlist) != 0:
            top_candidate = deezer_results_playlist[0]

            string = itemLut['4']['tuple'](0, top_candidate)
            name = string[1]
            link = itemLut['4']['url'](top_candidate)
            print(name)
            print(link)
        else:
            #start = time.time()
            xpath_links = '//a/@href'
            xpath_cover = '//img/@src'
            tree = lxml.html.fromstring(str(entry['content']))
            links = tree.xpath(xpath_links)
            #xpath = time.time()
            #links_regex = LINK_REGEX.finditer(str(entry))
            #regex = time.time()
            #print('xpath took: ' + str(xpath - start))
            #print('regex took: ' + str(regex - xpath))
            #for l in links_regex:
            #    print(str(l))
            cover = ''
            try:
                cover = tree.xpath(xpath_cover)
                #print('cover: ' + str(cover))
                if cover != []:
                    # if we found coverArt URL strings, use the first one
                    cover = cover[0]
            except Exception as e:
                print('cover acquiration Error: ' + e)
            #clean_links = [self.linkUnlock(link) for link in links if not any([nogo in link for nogo in self.nogoes])e
            #if self.unlock_links:
            #    clean_links = [self.unshortener.unshorten(link) for link in links if not any([nogo in link for nogo in self.nogoes])]
            #else:
            clean_links = [link for link in links if not any([nogo in link for nogo in self.nogoes])]
            if len(clean_links) == 0:
                return
            name = html.unescape(entry['title']['rendered'])
            link = entry['link']
            #print( name + ': ' + str(clean_links))
        new_riddim = {"name": name, "link": link, "query": self.query, "url_cover": cover}
        #new_riddim = Riddim(name, link, self.query, self, cover)
        #new_riddim = Riddim(name.replace(u'\u2013', ' - ').replace(U'\u2018', "'").replace(u'\u2019', "'").replace(u'\u201C', '"').replace(u'\u201D', '"'), entry['link'], self.query, self, cover)
        #if len(clean_links) > 0:
        #    new_riddim.setDownloadUrls(clean_links)
        #new_riddim.ready = True
        #self.riddimReady.emit(new_riddim)
        # emit signal with new_riddim
        return new_riddim
'''

class DancehallArenaScraper(Scraper):
    def __init__(self):
        super(DancehallArenaScraper, self).__init__()
        self.password = ''
        self.exclude_string = '&categories_exclude=27388, 4'
        self.rest_api_support = True
        self.folderName = 'DancehallArena.com'
        self.name = 'DancehallArena.com'
        self.logoUrl = 'https://dancehallarena.com/wp-content/uploads/2017/12/logo-2017.jpg'
        self.base_url = 'https://dancehallarena.com/'
        self.max_parallel_scrapes = 25

        self.xpath_pageAmount = '//div[contains(@class, "page-nav")]/a[last()-1]/text()'
        self.xpath_releases = '//div[contains(@class, "td-main-content-wrap")]//div[contains(@class, "td-module-thumb")]'
        self.xpath_relative_coverArt = './/a[contains(@class, "td-image-wrap")]//img[contains(@class, "entry-thumb")]/@src'
        self.xpath_relative_link = './/a[contains(@class, "td-image-wrap")]/@href'
        self.xpath_relative_name = './/a[contains(@class, "td-image-wrap")]/@title'
        self.xpath_links = '//a[@rel="nofollow" ]/@href'
        self.startedYear = 2013


class DancehallStarScraper(Scraper):
    def __init__(self):
        super(DancehallStarScraper, self).__init__()
        self.splitScrape = True
        self.password = ''
        self.exclude_string = '&categories_exclude='
        self.rest_api_support = False
        self.folderName = 'DancehallStar.net'
        self.name = 'DancehallStar.net'
        #self.logoUrl = 'https://www.dancehallstar.net/wp-content/uploads/2014/10/OG_BIGImagePM.jpg'
        self.logoUrl = 'https://www.dancehallstar.net/wp-content/uploads/2014/10/logo.png'
        self.base_url = 'https://www.dancehallstar.net/'
        #self.logoUrl = 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/STS-116_spacewalk_1.jpg/1024px-STS-116_spacewalk_1.jpg'
        self.startedYear = 2011
        self.max_parallel_scrapes = 1
        self.url = 'https://www.dancehallstar.net/'
        self.slowScrape = True

        self.xpath_releases = '/html/body/ section[@class="main-container"] / div[@class="container"] / div[@class="content"] // div[contains(@class,"post-blog")] // a[@class="image-wrap"]'
        self.xpath_relative_link = './@href'
        self.xpath_relative_name = './/img/@alt'
        self.xpath_relative_coverArt = './/img/@src'
        self.xpath_pageAmount = '//ul[@class="list-inline"]/li[last()-1]/a/text()'
        self.xpath_links = '//div[contains(@class, "download-url")]/div[@class="pull-left"]//a/@href'
        self.xpath_links_second = '//h3/a[contains(@class, "btn")]/@href'

    def scrape_riddimInfo(self, riddim):
        pageUrl = riddim.urlForumThread #.decode()
        print(('scraping riddim: ' + str(pageUrl)))
        content = scrapeViaXPath(pageUrl, self.xpath_links)
        cleanLinks = []
        if len(content) != 0:
            dlLinks = content[0]
            for link in dlLinks:
                print('LINK: ' + (link))
                if 'dancehallstar.net' in link:
                    checkme = scrapeViaXPath(link, self.xpath_links_second)[0][0]
                    print("got: " + str(checkme))
                else:
                    checkme = link
                if not any([nogo in checkme for nogo in self.nogoes]):
                    if not any([musicLink in checkme for musicLink in musicLinks]):
                        cleanLinks.append(str(self.linkUnlock(checkme)))
                    else:
                        riddim.urlsListen.append(checkme)
            #print(("CleanLinks: " + str(cleanLinks)))
            #print('Music Links: ' + str(riddim.urlsListen))
            #riddim.urlsListen = [link if any(musicLink in link for musicLink in musicLinks) for link in cleanLinks)]
            riddim.urlsDownload = cleanLinks
        else:
            print(('Nothing found for ' + riddim.name))
        riddim.ready = True
        #self.riddimReady.emit(riddim)
        return cleanLinks


class DancehallWorldScraper(Scraper):
    def __init__(self):
        super(DancehallWorldScraper, self).__init__()
        self.password = ''
        self.exclude_string = '&categories_exclude=4146, 1075, 10,   4149, 1078, 1079, 1080, 22, 23, 25'#, 17, ' 17 is video
        self.rest_api_support = True
        self.folderName = 'DancehallWorld.net'
        self.name = 'DancehallWorld.net'
        self.logoUrl = 'https://dancehallworld.net/wp-content/uploads/2018/04/DancehallWorld-BANNER-1485-x-318.png'
        self.base_url = 'https://www.dancehallworld.net/'
        self.startedYear = 2011
        self.max_parallel_scrapes = 2

        self.xpath_releases = '//div[contains(@class, "td-ss-main-content")]//div[contains(@class, "td-module-thumb")]'
        self.xpath_relative_coverArt = './/img[contains(@class, "entry-thumb")]/@src'
        self.xpath_relative_link = './/a[contains(@class, "td-image-wrap")]/@href'
        self.xpath_relative_name = './/a[contains(@class, "td-image-wrap")]/@title'
        self.xpath_pageAmount = '//div[contains(@class, "page-nav")]/a[last()-1]/text()'
        self.xpath_links = '//a[@rel= "nofollow"]/@href'


class ReggaeFreshScraper(Scraper):
    def __init__(self):
        super(ReggaeFreshScraper, self).__init__()
        self.password = ''
        self.exclude_string = '&categories_exclude=4'
        self.rest_api_support = True
        self.folderName = 'ReggaeFresh.com'
        self.name = 'ReggaeFresh.com'
        self.logoUrl = 'https://reggaefresh.com/wp-content/uploads/2019/04/main272_whitebg.png'
        self.base_url = 'https://www.reggaefresh.com/'
        self.startedYear = 2017
        self.max_parallel_scrapes = 50

        self.xpath_releases = '//div[contains(@class, "td-main-content-wrap")]//div[contains(@class, "td_module_16")]'
        self.xpath_relative_coverArt = './/img[contains(@class, "entry-thumb")]/@src'
        self.xpath_relative_link = './/a[contains(@rel, "bookmark")]/@href'
        self.xpath_relative_name = './/a[contains(@rel, "bookmark")]/@title'
        self.xpath_pageAmount = '//div[contains(@class, "page-nav")]/a[last() - 1]/text()'
        self.xpath_links = '//div[@class = "td-post-content"]//a/@href'

class DreamSoundScraper(Scraper):
    def __init__(self):
        super(DreamSoundScraper, self).__init__()
        self.password = ''
        self.folderName = 'Dream-Sound.com'
        self.name = 'Dream-Sound.com'
        self.logoUrl = 'https://reggaefresh.com/wp-content/uploads/2019/04/main272_whitebg.png'
        self.base_url = 'https://www.dream-sound.com/'
        self.startedYear = 2017
        self.max_parallel_scrapes = 6

        self.xpath_releases = '//div[contains(@class, "td-main-content")]//div[contains(@class, "td_module_1")]'
        self.xpath_relative_coverArt = './/img[contains(@class, "entry-thumb")]/@data-img-url'
        self.xpath_relative_link = './/a[contains(@rel, "bookmark")]/@href'
        self.xpath_relative_name = './/a[contains(@rel, "bookmark")]/@title'
        self.xpath_pageAmount = '//div[contains(@class, "page-nav")]/a[@class = "last"]/text()'
        self.xpath_links = '//div[@class = "panel-block"]//a[@rel= "nofollow"]/@href'

class AllTimeRiddimScraper(Scraper):
    def __init__(self):
        super(AllTimeRiddimScraper, self).__init__()
        self.password = 'ALLTIMERIDDIM.blogspot.com'
        self.folderName = 'AllTimeRiddim.blogspot.com'
        self.name = 'AllTimeRiddim.blogspot.com'
        self.logoUrl = 'https://1.bp.blogspot.com/-sSAhTQe_NJc/XOtMoLoP05I/AAAAAAAAASI/MBL9AwrV_csZFYed2zW_SYomg7pkK47SACK4BGAYYCw/w800/riddim.PNG'
        self.base_url = 'https://alltimeriddim.blogspot.com/'
        self.startedYear = 2015
        self.max_parallel_scrapes = 50

       #  TODO: fix all paths
        self.xpath_releases = '//div[contains(@class, "td-main-content-wrap")]//div[contains(@class, "td_module_16")]'
        self.xpath_relative_coverArt = './/img[contains(@class, "entry-thumb")]/@src'
        self.xpath_relative_link = './/a[contains(@rel, "bookmark")]/@href'
        self.xpath_relative_name = './/a[contains(@rel, "bookmark")]/@title'
        self.xpath_pageAmount = '//div[contains(@class, "page-nav")]/a[last() - 1]/text()'
        self.xpath_links = '//div[@class = "td-post-content"]//a/@href'

scrapers = [
#        DancehallStarScraper(), no REST API anymore?
        #DancehallWorldScraper(), # dead?
        DancehallArenaScraper(),
        ReggaeFreshScraper(),
        RiddimsCoScraper(),
        ]
DEBUG = False
if __name__ == "__main__":
    #link = unlockAdfLy('http://j.gs/CHHF')
    #print(link)
    sys.argv.pop(0)
    if len(sys.argv) != 0:
    #    scraper = ReggaeFreshScraper()
    #    print(('Scraping infos for: ' +  str(sys.argv)))
    #    for arg in sys.argv:
    #        riddim = Riddim('test', arg)
    #        print((scraper.scrape_riddimInfo(riddim)))
        search_term = sys.argv[0]
    else:
        search_term = 'bada bada riddim'

    for scraper in scrapers:
        try:
            start = time.time()
    #scraper.get_releases_from_rest_api_old('capleton reggae')
            mid = time.time()
            scraper.get_releases_from_rest_api(search_term)
            end = time.time()
            print('scraping took: ' + str(end - mid))
            time.sleep(10)
        except:
            print(scraper.name + ' was not succesfull.')

  ### TODO: fix multiple site search / link recognition for dancehallstar
  ###       fix coverart loading for dancehallstar/dancehallarena
            #print 'lengths:' + str(len(releaseName)) + str(len(releaseLink))
