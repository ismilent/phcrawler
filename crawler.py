#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Author: SMilent
'''

import os
import sys

from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QUrl
from PyQt4.QtCore import QObject
from PyQt4.QtCore import QIODevice
from PyQt4.Qt import QApplication
from PyQt4.QtWebKit import QWebView
from PyQt4.QtWebKit import QWebPage
from PyQt4.QtWebKit import QWebFrame
from PyQt4.QtWebKit import QWebSettings
from PyQt4.QtWebKit import QWebElement
from PyQt4.QtNetwork import QNetworkAccessManager
from PyQt4.QtNetwork import QNetworkRequest
from PyQt4.QtNetwork import QNetworkReply

from const import METHOD_OPERATION
from const import HANDLE_TAGS

from pprint import pprint



class WebPage(QWebPage):
    '''
    WebPage class
    处理webpage DOM javascript
    '''
    def __init__(self):
        QWebPage.__init__(self)

    def javaScriptConsoleMessage(self, message, lineNumber, source_id):
        print '----- javascriptConsoleMessage Start -----'
        sys.stderr.write('JavaScript error at line number %d\n' % lineNumber)
        sys.stderr.write('%s\n' % message)
        sys.stderr.write('Source ID: %s\n' % source_id)
        print '----- javascriptConsoleMessage End -----'

    def javaScriptAlert(self, frame, p_str):
        pass


class NetworkAccessManager(QNetworkAccessManager):
    '''
    NetworkAccessManager
    Hook http request
    '''
    def __init__(self, header=None, post_data=None):
        QNetworkAccessManager.__init__(self)
        self.connect(self, SIGNAL('finished(QNetworkReply*)'), self.finished)

    def createRequest(self, operation, request, data=None):
        '''
        Hook create request
        :param operation: http method
        :param request: http request header
        :param data: http post data
        :return: QNetworkReply
        '''
        request_data = {}
        method = [x for x in METHOD_OPERATION.iterkeys() if METHOD_OPERATION[x] == operation][0]
        request_data['method']= method

        url = str(request.url().toString())
        request_data['url'] = url
        request.setHeader( QNetworkRequest.ContentTypeHeader, 'application/x-www-form-urlencoded')

        request_data['data'] = None

        if data:
            request_data['data'] = str(data.readAll())

        pprint(request_data)
        return QNetworkAccessManager.createRequest(self, operation, request, data)

    def finished(self, reply):
        print 'finished'


class Crawler(QApplication):
    '''
    Crawler Class
    '''
    def __init__(self, url, cookie=None, auth=None, post_data=None, timeout=None):
        '''
        Crawler class
        :param url: url
        :param cookie: cookie
        :param auth: http base auth
        :param post_data: post data
        :param timeout: timeout
        '''
        QApplication.__init__(self, sys.argv)
        self.url = url
        self.web_view = QWebView()
        self.web_page = WebPage()
        self.web_frame = self.web_page.mainFrame()
        self.web_view.setPage(self.web_page)

        # set networkaccessmanager
        self.network_manager = NetworkAccessManager()
        self.web_page.setNetworkAccessManager(self.network_manager)

        # set page
        '''
        self.settings = self.web_page.settings().globalSettings()
        self.settings.setAttribute(QWebSettings.AutoLoadImages, False)
        self.settings.setAttribute(QWebSettings.PluginsEnabled, False)
        self.settings.clearMemoryCaches()
        '''

        # connect
        self.connect(self.web_view, SIGNAL('loadFinished(bool)'), self.loadFinished)

        # load url
        self.web_page.currentFrame().load(QUrl(url))


    def handle_tag(self, tag, src):
        '''
        handle tag
        :param tag:
        :param src:
        :return:
        '''
        for element in self.document.findAll(tag):
            if element.hasAttribute(src):
                print element.attribute(src)

    def load(self, url):
        '''
        Load url
        :param url:
        :return:
        '''
        print url
        self.web_page.currentFrame().load(QUrl(self.url))

    def loadFinished(self, ok):
        self.document =  self.web_frame.documentElement()
        map(lambda x: self.handle_tag(x[0], x[1]), HANDLE_TAGS.items())
        print 'loadfinished'

if __name__ == '__main__':
    url = 'http://localhost:8000/aisec.html'
    url = 'http://demo.aisec.cn/demo/aisec/'
    crawler = Crawler(url)
    sys.exit(crawler.exec_())