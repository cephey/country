import math
from django import template

register = template.Library()


@register.filter(name='num_ending')
def num_ending(n, args):
    params = [arg.strip() for arg in args.split(',')]
    word, args = params[0], params[1:]
    return u'%d %s%s' % (n, word, args[0 if n % 10 == 1 and n % 100 != 11 else 1 if n % 10 >= 2 and n % 10 <= 4 and (
        n % 100 < 10 or n % 100 >= 20) else 2])


@register.filter(name='crop')
def crop(link, size):
    return link


@register.filter(name='partition')
def partition(lst, n):
    n = int(n)
    div = math.ceil(len(lst) / float(n))

    result = [[] for i in range(div)]
    for i, item in enumerate(lst):
        result[i % div].append(item)

    return result


@register.filter(name='group')
def group(lst, n):
    n = int(n)
    size = math.ceil(len(lst) / float(n))
    return [lst[i:i + size] for i in range(0, len(lst), size)]
