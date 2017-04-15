from urllib.parse import urlparse, parse_qs


def get_video_code(youtube_link):
    query_string = urlparse(youtube_link).query
    query_dict = parse_qs(query_string)
    code = query_dict.get('v')
    if isinstance(code, (list, tuple)):
        return code[0]
    return code


def preview_for_video(youtube_link):
    code = get_video_code(youtube_link)
    return 'http://img.youtube.com/vi/{}/default.jpg'.format(code)
