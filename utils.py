import io
import string
import subprocess as sp

def shell_exec(cmd):
    p = sp.run(cmd, stdout=sp.PIPE, stderr=sp.PIPE)
    return p.stdout


def shell_get_strings(file, prefix):
    cmd = ['strings', file]
    sio = io.StringIO(shell_exec(cmd).decode())
    strings = []
    for line in sio:
        strings.append(line.rstrip())
    strings.sort()
    return strings


def get_strings(data, prefix):
    s = ""
    printable = set(string.printable)
    strings = set()
    i = 0
    for c in data:
        if 0 == i % 2**20:
            T("%d", i >> 20)
        if c in printable:
            s += c
        else:
            if "" != s:
                if s.startswith(prefix):
                    strings.add(s)
                s = ""
        i += 1
    strings = list(strings)
    strings.sort()
    return strings
