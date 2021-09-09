import re


def is_facebook(url):
    if not url:
        return None

    return __match(url)


def get_embed_url(url):
    match = __match(url)
    if match:
        return 'https://www.facebook.com/plugins/video.php?href=https://www.facebook.com/' + match.group(
            1) + '/live'

    return None


def __match(url):
    return re.match("^https://(?:www)?\.facebook\.com/([^/]+)", url)
