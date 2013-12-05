#!/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4 
import urllib
from urllib2 import Request, urlopen, URLError, HTTPError
import socket

class emoncms:
    def __init__(self,key=None,url='http://emoncms.org/input/post.json'):
        self.apikey = key
        self.url = url

    def publish(self,input):
        data = {}
        data['json'] = '{'+input[0]+':'+str(input[1])+'}'
        if self.apikey is not None:
            data['apikey'] = self.apikey
        url_values = urllib.urlencode(data)
        url = self.url+'?'+url_values
        print(url)
        try: response = urlopen(url)
        except HTTPError as e:
            print('The server couldn\'t fulfill the request.')
            print('Error code: ', e.code)
        except URLError as e:
            print('We failed to reach a server.')
            print('Reason: ', e.reason)
        except socket.timeout as e:
            print('Timeout Error')
        else:
            rc = response.read()
            if rc != 'ok':
                print("Failed: %s" % (rc))
