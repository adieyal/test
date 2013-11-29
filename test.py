import re

def repl(match):
    s = match.group(0)
    return {
        "aa" : "xx",
        "bb" : "yy"
    }[s]

print re.sub("(aa)", repl, "hello aa")
