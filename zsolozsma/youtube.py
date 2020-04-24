import urllib
import json


def get_video(channel):
    API_KEY = os.getenv('YOUTUBE_API_KEY')
    request = urllib.request.urlopen(
        'https://www.googleapis.com/youtube/v3/search/?part=snippet&type=video&maxResults=1&order=date&channelId=' + channel + '&key=' + API_KEY)
    body = request.read()
    data = body.decode('utf-8')

    videos = json.loads(data)['items']
    video = videos[0]

    return {'id': video['id']['videoId']}
