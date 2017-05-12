import json


def perl_to_python_dict(data):
    """
    :param data: string `$VAR1 = {'url' => 'http://kolobok1973.livejournal.com/','note' => ''};`
    :return: python dict {'url': 'http://kolobok1973.livejournal.com/', 'note': ''}
    """
    data = data[data.find("{") + 1: data.rfind("}")]
    data = data.replace('\"', '\\\"').replace('\'', '\"').replace('=>', ':').replace('\t', '')
    data = '{' + data + '}'
    return json.loads(data)
