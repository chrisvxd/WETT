#!/usr/bin/env python

import urllib
import urllib2

class HttpBot:
    """an HttpBot represents one browser session, with cookies."""
    def __init__(self):
        cookie_handler= urllib2.HTTPCookieProcessor()
        redirect_handler= urllib2.HTTPRedirectHandler()
        self._opener = urllib2.build_opener(redirect_handler, cookie_handler)

    def GET(self, url):
        return self._opener.open(url).read()

    def POST(self, url, parameters):
        return self._opener.open(url, urllib.urlencode(parameters)).read()


if __name__ == "__main__":
    bot = HttpBot()
    ignored_html = bot.POST('https://example.com/authenticator', {'passwd':'foo'})
    print bot.GET('https://example.com/interesting/content')
    ignored_html = bot.POST('https://example.com/deauthenticator',{})
