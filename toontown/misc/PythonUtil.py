# Some functions that once resided in Panda3D's PythonUtil module have since been
# deprecated. Rather than deprecating the possible several calls in our code, we'll
# just add back the removed functions to our own PythonUtil.

import __builtin__

def choice(condition, ifTrue, ifFalse):
    # equivalent of C++ (condition ? ifTrue : ifFalse)
    if condition:
        return ifTrue
    else:
        return ifFalse

__builtin__.choice = choice
