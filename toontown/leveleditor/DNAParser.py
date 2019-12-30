from toontown.leveleditor import SuitPoint, Group
from direct.directnotify import DirectNotifyGlobal
keywords = {"store_suit_point": SuitPoint.SuitPoint, "group": Group.Group}
opener = '['
closer = ']'
splitter = ','

def depth(d):
    if isinstance(d, dict):
        return 1 + (max(map(depth, d.values())) if d else 0)
    return 0

def get_keyset(d, keys):
    if isinstance(d, dict):
        for k, v in d.items():
            if not isinstance(v, dict):
                continue
            if depth(d) == 2:
                keys.append(list(d.keys())[0])
                return keys
            else:
                keys.append(k)
                return get_keyset(d[k], keys)

class DNAParser:
    notify = DirectNotifyGlobal.directNotify.newCategory('DNAParser')

    def __init__(self):
        self.directory = []
        self.keyword = None
        self.tree = None
        self.contents = None
        self.parent = None

    def parse_file(self):
        print("hhh")
        f = open('resources/phase_14/dna/toontown_central_2100.dna')
        i = 0
        for line in f:
            i += 1
            current = line.split()
            index = -1
            try:
                index = current.index(opener)
            except ValueError as e:
                print("Opener not found!")
            #if index > -1:
                #self.notify.error('Found opener without pre-existing closer at ')
            if self.tree:
                keyset = get_keyset(self.tree, [])
                d = self.tree
                exec_str = "self.contents"
                for k in keyset:
                    exec_str += '["' + str(k) + '"]'
                exec_str += " = [{}, []]"
            else:
                self.tree = {{}, {i: []}}

            self.keyword = {current[index - 1]: {i: }}
            if '"' in self.keyword:
                self.keyword = current[index - 2]
            print(self.parent, index)
        f.close()
