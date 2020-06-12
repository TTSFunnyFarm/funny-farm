import inspect
from direct.directnotify.DirectNotifyGlobal import directNotify
notify = directNotify.newCategory('Cotebook')


class CoteError(Exception): pass

class Cotebook:
    def __init__(self):
        self.name2word = {}
        self.words = {}

    def addWord(self, word):
        if not __debug__:
            return
        name = word.name.lower()
        self.name2word[name] = word
        self.words[name] = word
        for alias in word.aliases:
            self.addAlias(alias.lower(), name)

    def addAlias(self, alias, name):
        if not self.words.get(name):
            return # yeah no buddy
        word = self.words[name]
        self.name2word[alias] = word

    def run(self, name, args):
        word = None
        try:
            word = self._runWord(name, args)
        except Exception as e:
            base.localAvatar.setSystemMessage(0, str(e))
            notify.warning(str(e))
            return False

        if word:
            base.localAvatar.setSystemMessage(0, word)
        else:
            notify.warning('Cotebook returned nothing when running %s?' % name)

    def _runWord(self, name, args):
        word = self.name2word.get(name)
        if not word:
            raise CoteError('Unknown magic word!')

        result = word.run(args)
        if result:
            return result
        return 'Magic word ran successfully!'

if __debug__:
    cotebook = Cotebook()

class MagicWord:
    def __init__(self, name, func, doc, argTypes, aliases):
        self.name = name
        self.func = func
        self.doc = doc
        self.argTypes = argTypes
        self.aliases = aliases

    def parseArgs(self, string):
        if string == '':
            return []
        spec = inspect.getfullargspec(self.func)
        maxArgs = len(spec.args)
        diff = maxArgs
        if spec.defaults:
            diff = len(spec.defaults)
        minArgs = maxArgs - maxArgs

        output = string.split(' ')
        if len(output) < minArgs:
            raise CoteError('Word %s requires a minimum of %d arguments!' % (self.name, len(output)))
        elif len(output) > maxArgs:
            raise CoteError('Args overflow! Word %s has a maximum of %d arguments!' % (self.name, len(output)))
        new_output = []
        for i in range(len(output)):
            arg = output[i]
            try:
                new_arg = self.argTypes[i](arg)
                new_output.append(new_arg)
            except ValueError as e:
                raise CoteError('Failed to convert arg %s to %s!' % (output[i], self.argTypes[i].__name__))

        return new_output

    def run(self, rawArgs):
        args = self.parseArgs(rawArgs)
        try:
            return self.func(*args)
        except TypeError as e:
            return 'Invalid arguments!'

class magicDecorator:
    def __init__(self, name=None, argTypes=[], aliases=[]):
        self.name = name
        self.types = argTypes
        self.aliases = aliases

    def __call__(self, mw):
        if not __debug__:
            return
        name = self.name
        if not name:
            name = mw.__name__

        cotebook.addWord(MagicWord(name, mw, mw.__doc__, self.types, self.aliases))
        return mw

magicWord = magicDecorator
