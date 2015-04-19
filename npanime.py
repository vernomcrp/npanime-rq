#!/usr/bin/env python

import sys, os
import urllib2
from redis import Redis
from rq import Queue
from tasks import down


try:
    from bs4 import BeautifulSoup
except ImportError as e:
    print 'You must have beautifulsoup pkg, install by pip install beautifulsoup4'.upper()
    sys.exit(1)

HEADERS={
    'User-Agent': 'Mozilla/5.0'
}

def get_good_html(file_like_object):
    # original html have 2 body tags, it's suck.
    # this function gonna wipe that out.
    flag=False
    done=[]
    for line in file_like_object.readlines():
        if "<html" in line:flag=True
        flag and done.append(line)
    return ''.join(done)

def get_pics_list(soup):
    #[ (referrer, url), ...]
    # We can implement handle for each image server
    find_ahref_in_soup = soup.find('div',{'class':'post'}).find_all('a')
    if find_ahref_in_soup:
        print 'Found ahref in soup.[oozha.com]'
        return [(a.attrs['href'], a.findChild('img').attrs['src']) for a in find_ahref_in_soup if a.findChild('img')]

    find_img_in_soup = soup.find_all('img',{'class':'bbc_img'})
    if find_img_in_soup:
        print 'Found img in soup.[impur.com]'
        return [('', i.attrs['src']) for i in find_img_in_soup]

    return []



def center_ops(url):
    
    good_html_string = get_good_html(urllib2.urlopen(url))
    soup = BeautifulSoup(good_html_string)
    
    q = Queue(connection=Redis(host='localhost', port=6379))
    
    for index, dat in enumerate(get_pics_list(soup)):
        #down(index, dat, folder_name)
        q.enqueue(down, index, dat, folder_name)

if __name__ == '__main__':
    assert len(sys.argv) == 3, 'Hey, let\'s params like this -> <url> <folder_name>'
    url = sys.argv[1]
    folder_name = sys.argv[2]

    if not os.path.isdir(folder_name):
        os.mkdir('./%s' % folder_name)
    center_ops(url)
