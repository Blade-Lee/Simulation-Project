import urllib
import urllib2
import json

values = {
    'client_id': '67a5c2fe0ac1c936',
    'video_url': 'http://v.youku.com/v_show/id_XMTMxOTM3Mjg5Ng==.html'
}
data = urllib.urlencode(values)
url = "https://openapi.youku.com/v2/videos/show_basic.json"
request = urllib2.Request(url, data)
response = urllib2.urlopen(request)

json_load = json.load(response)
print json_load