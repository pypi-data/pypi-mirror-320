from . import filepath, iter


def rowchars(text, char, start=0):
    count = 0
    for ch in text[start:]:
        if ch == char:
            count += 1
        elif count != 0:
            break
    return -1 if count == 0 else count


def strip_indexes(source, indexes):
    removed = 0
    for index in indexes:
        del source[index - removed]
        removed += 1

def trymap(func, value, default=None, allow=None):
    if allow is None:
        allow = Exception

    try:
        return func(value)
    except allow:
        return default
