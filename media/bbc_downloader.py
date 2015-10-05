import re
import urllib

url=urllib.urlopen("http://www.bbc.co.uk/programmes/p02nq0gn/episodes/downloads").read()
#r = re.compile('(?<=href=").*?(?=")')
r = re.compile('(http?:\/\/[^\s]+mp3)')
res = r.findall(url)
print res
urllib.urlretrieve(res[0],'/home/amour/test_media/RootioNew/Northern Uganda Pilot/BBC Podcasts/{0}'.format(res[0].split('/')[-1]))
