import re
import json


def perl_to_python_dict(data, second=False):
    """
    :param data: string `$VAR1 = {'url' => 'http://kolobok1973.livejournal.com/','note' => ''};`
    :param second: bool True if it is second parse one and the same string
    :return: python dict {'url': 'http://kolobok1973.livejournal.com/', 'note': ''}
    """
    data = data[data.find("{") + 1: data.rfind("}")]
    if not second:
        data = (data.replace('\"', '\\\"').replace('\'', '\"').replace('=>', ':')
                .replace('\t', '').replace('\n', '')
                .replace('undef', 'null'))
        data = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', data)
    return json.loads('{' + data + '}')


def perl_to_python_list(data):
    """
    :param data: string `{123, 10, 8823309}`
    :return: python list [123, 10, 8823309]
    """
    if data and len(data) > 2:
        return [int(s.strip()) for s in data[1:-1].split(',') if s.strip()]
    return []
