# -*- coding: utf-8 -*-
import sys
import threading
#reload(sys)
#sys.setdefaultencoding('utf8')

#from kivy.uix.popup import Popup
#from kivy.uix.image import Image
#from kivy.loader import Loader
#Loader.num_workers = 10
#Loader.max_upload_per_frame = 14


class Riddim(dict):
    # TODO: getInfo on init! with thread! :)
    name = ''
    def __init__(self, name, url, query=None, scraper=None, urlCover=''):
        super(Riddim, self).__init__()
        self.name = name
        self.ready = False
        self.downloaded = False
        self.flagDownload = False
        self.urlForumThread = url
        if type(url) == list:
            self.urlForumThread = url[0]
        self.urlsDownloadDirty = []
        self.urlsDownloadClean = []
        self.urlsListen = []
        self.url_coverart = urlCover
        self.query = query
        self.scraper = scraper

    def setDownloadUrls(self, urls):
        self.urlsDownloadDirty = urls
        if (self.scraper.unlock_links):
            #self.unlockLinks()
            t = threading.Thread(target = self.unlockLinks)
            t.start()

    def writeLinksToFile(self):
        fileName = self.scraper.name + '.csv'
        fileDir = os.path.join(os.path.abspath(self.basePath), 'Links')
        filePath = os.path.join(fileDir, fileName)
        try:
            os.makedirs(fileDir)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
            else:
                print("\nBE CAREFUL! Directory %s already exists." % fileDir)
        print('writing to: ' + str(filePath))
        with open( filePath, 'w') as writeFile:
            writer = csv.writer(writeFile)
            writer.writerows(releaseLists[keySite])

    def unlockLinks(self):
        cleanLinks = [self.scraper.linkUnlock(link) for link in self.urlsDownloadDirty]
        #cleanLinks = [self.scraper.unshortener.unshorten(link) for link in self.urlsDownloadDirty]
        self.urlsDownloadClean = cleanLinks
        #print(cleanLinks)
        self.ready = True
        print(self.name + ' links unlocked!')

    def __str__(self):
        return self.name

    def printInfo(self):
       # import ipdb; ipdb.set_trace(context=11)
        print(':: -- INFO for: ' + self.name + '\n' + self.urlForumThread + '\n:: --' + self.urlCoverArt + '\n')
