import re, os, sys

def read_env(from_file):
    """Read and set environment variables from a file
    https://gist.github.com/bennylope/2999704"""
    try:
        with open(from_file) as f:
            content = f.read()
    except IOError:
        print "IOError: unable to open",from_file
        sys.exit(-1)

    new_env = {}
    for line in content.splitlines():
        m1 = re.match(r'\A([A-Za-z_0-9.:]+)=(.*)\Z', line)
        if m1:
            key, val = m1.group(1), m1.group(2)
            m2 = re.match(r"\A'(.*)'\Z", val)
            if m2:
                val = m2.group(1)
            m3 = re.match(r'\A"(.*)"\Z', val)
            if m3:
                val = re.sub(r'\\(.)', r'\1', m3.group(1))
            os.environ.setdefault(key, val)
            new_env[key]=val
    return new_env