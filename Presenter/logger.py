
import time
import colorama

_print = print
_hook = {
    'FATAL':[],
    'DEBUG':[],
    'EXCEPTION':[],
    'HANEX':[],
    'ALERT':[],
    'REPORT':[]
}

def hook(flag, func):
    if not callable(func):
        return False
    if flag in _hook and func in _hook[flag]:
        return False
    if flag not in _hook:
        _hook[flag]=[func]
    else:
        _hook[flag].append(func)
    
    return True


def report(*args, sep=' ', start='    ', nident=True, **kw):
    'This reports to wechatwork'
    if kw:
        do_print(*args, str(kw), flag='REPORT',
                 sep=sep, start=start, nident=nident)
    else:
        do_print(*args, flag='REPORT', sep=sep, start=start, nident=nident, color=colorama.Style.DIM)

def print(*args, sep=' ', start='    ', nident=True, **kw):
    if kw:
        do_print(*args, str(kw), flag='PRINT',
                 sep=sep, start=start, nident=nident)
    else:
        do_print(*args, flag='PRINT', sep=sep, start=start, nident=nident, color=colorama.Style.DIM)

def temp(*args, sep=' ', start='    ', nident=True, **kw):
    if kw:
        do_print(*args, str(kw), flag='TEMP',
                 sep=sep, start=start, nident=nident)
    else:
        do_print(*args, flag='TEMP', sep=sep, start=start, nident=nident, color=colorama.Fore.WHITE+colorama.Style.DIM)

def error(*args, sep=' ', start='    ', nident=True, **kw):
    if kw:
        do_print(*args, str(kw), flag='ERROR',
                 sep=sep, start=start, nident=nident)
    else:
        do_print(*args, flag='ERROR', sep=sep, start=start, nident=nident, color=colorama.Fore.RED)

def warn(*args, sep=' ', start='    ', nident=True, **kw):
    if kw:
        do_print(*args, str(kw), flag='WARN',
                 sep=sep, start=start, nident=nident)
    else:
        do_print(*args, flag='WARN', sep=sep, start=start, nident=nident, color=colorama.Fore.YELLOW)

def fatal(*args, sep=' ', start='    ', nident=True, **kw):
    if kw:
        do_print(*args, str(kw), flag='FATAL',
                 sep=sep, start=start, nident=nident)
    else:
        do_print(*args, flag='FATAL', sep=sep, start=start, nident=nident, color=colorama.Fore.WHITE+colorama.Style.BRIGHT+colorama.Back.RED)


def alert(*args, sep=' ', start='    ', nident=True, **kw):
    if kw:
        do_print(*args, str(kw), flag='ALERT',
                 sep=sep, start=start, nident=nident)
    else:
        do_print(*args, flag='ALERT', sep=sep, start=start, nident=nident, color=colorama.Back.WHITE+colorama.Fore.BLACK)

def debug(*args, sep=' ', start='    ', nident=True, **kw):
    if kw:
        do_print(*args, str(kw), flag='DEBUG',
                 sep=sep, start=start, nident=nident)
    else:
        do_print(*args, flag='DEBUG', sep=sep, start=start, nident=nident, color=colorama.Style.BRIGHT+colorama.Fore.BLUE)

def warning(*args, sep=' ', start='    ', nident=True, **kw):
    if kw:
        do_print(*args, str(kw), flag='WARN',
                 sep=sep, start=start, nident=nident)
    else:
        do_print(*args, flag='WARN', sep=sep, start=start, nident=nident, color=colorama.Fore.YELLOW)

def do_print(*args, flag=None, color=None, sep=' ', start='    ', nident=True):
    argv = []
    for x in args:
        argv.append(str(x))

    content = ''.join([flag, start, str(sep.join(argv)).replace('\n', str(
        str('\n'+' '*len(flag) if flag else 0) + start) if nident else '\n')]).strip()
    
    _print(str('' if not color else color) + content +
          colorama.Back.RESET+colorama.Fore.RESET+colorama.Style.RESET_ALL)
    if flag in _hook:
        for _hookedfunc in _hook[flag]:
            _hookedfunc(flag, content)


def exception(*args, sep=' ', start='    ', nident=True, **kw):
    if kw:
        do_print(*args, str(kw), flag='EXCEPTION',
                 sep=sep, start=start, nident=nident)
    else:
        do_print(*args, flag='EXCEPTION', sep=sep, start=start, nident=nident, color=colorama.Fore.RED)

def log(*args, sep=' ', start='    ', nident=True, **kw):
    if kw:
        do_print(*args, str(kw), flag='LOG',
                 sep=sep, start=start, nident=nident)
    else:
        do_print(*args, flag='LOG', sep=sep, start=start, nident=nident, color=colorama.Style.DIM)

def info(*args, sep=' ', start='    ', nident=True, **kw):
    if kw:
        do_print(*args, str(kw), flag='INFO',
                 sep=sep, start=start, nident=nident, color=colorama.Fore.GREEN)
    else:
        do_print(*args, flag='INFO', sep=sep, start=start, nident=nident, color=colorama.Fore.GREEN)

def handled_exception(*args, sep=' ', start='    ', nident=True, **kw):
    if kw:
        do_print(*args, str(kw), flag='HANEX',
                 sep=sep, start=start, nident=nident)
    else:
        do_print(*args, flag='HANEX', sep=sep, start=start, nident=nident)


def hanex(*args,**kw):
    'A shorthand for handled_exception'
    handled_exception(*args,**kw)