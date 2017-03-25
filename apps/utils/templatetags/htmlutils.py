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
    division = len(lst) / float(n)
    return [lst[int(round(division * i)): int(round(division * (i + 1)))] for i in range(n)]
