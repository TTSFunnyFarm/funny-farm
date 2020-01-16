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
        self.name2word[word.name] = word
        self.words[word.name] = word
        for alias in word.aliases:
            self.addAlias(alias, word.name)

    def addAlias(self, alias, name):
        if not self.words.get(name):
            return # yeah no buddy
        self.name2word[alias] = name

    def run(self, name, args):
        word = None
        try:
            word = self._runWord(name, args)
        except CoteError as e:
            base.localAvatar.setSystemMessage(0, str(e))
            notify.warning(str(e))

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

        return output

    def run(self, rawArgs):
        args = self.parseArgs(rawArgs)
        return self.func(*args)

class magicDecorator:
    def __init__(self, name=None, argTypes=[], aliases=[]):
        self.name = name
        self.types = argTypes
        self.aliases = aliases

    def __call__(self, mw):
        name = self.name
        if not name:
            name = mw.__name__

        cotebook.addWord(MagicWord(name, mw, mw.__doc__, self.types, self.aliases))
        return mw

magicWord = magicDecorator
