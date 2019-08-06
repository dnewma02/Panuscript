import os, re, json

class Entry:
    def __init__(self, d):
        for a, b in d.items():
            # if isinstance(b, (list, tuple)):
            #    setattr(self, a, [Entry(x) if isinstance(x, dict) else x for x in b])
            # else:
               setattr(self, a, Entry(b) if isinstance(b, dict) else b)

class Library:
    def __init__(self, file, ps=None):
        self.ps = ps
        self.entries = []
        self.read(file)

    def read(self, path):
        if os.path.isfile(path):
            if os.path.splitext(path)[1] in self.ps.bib_formats:
                with open(path, 'r') as text:
                    lib = [Entry(e) for e in json.loads(self.ps.json_bib(path))]
                    # clean entries
                    for e in lib:
                        if hasattr(e, 'keyword'): e.keyword = e.keyword.split(',')
                        if hasattr(e, 'issued') and hasattr(e.issued, 'date-parts'):
                            e.issued = {'year': e.issued.__dict__.get('date-parts')[0][0]}
                    self.entries = lib
        else: print("File does not exist.")

    def querry_id(self, id):
        for e in self.entries:
            if e.id == id:
                if self.ps.verbose: print(dict_to_table(e.__dict__))
                return e

def dict_to_table(dictionary, space=3):
    assert(isinstance(dictionary, dict) == True)
    d = {}
    for f in ['id','author','title','issued']: # convenient field order
        d[f] = ''
    for i in dictionary:
        if i == 'author': d[i] = ' and '.join(
                    ['{} {}'.format(a['given'], a['family']) for a in dictionary[i]])
        elif i == 'issued': d[i] = dictionary[i]['year']
        elif i == 'keyword': d[i] = ", ".join([k for k in dictionary[i]])
        elif i == 'container-title': d['title'] = dictionary[i]
        else: d[i] = dictionary[i]
    width_col1 = max([len(x) for x in d.keys()]) + space
    width_col2 = max([len(x) for x in str(d.values())])
    out_str = ""
    for i in d:
        k = (i[0].upper() + i[1:] + ":").replace("_", " ")
        v = d[i]
        if isinstance(v, float): v = float("{:.4f}".format(v))
        else: v = str(v)
        out_str += "{0:<{col1}}{1:<{col2}}".format(k,v,col1=width_col1, col2=width_col2).strip()
        out_str += os.linesep
    return out_str

if __name__ == '__main__':
    from ps_obj import Panuscript
    test_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)),'test')
    l = Library(os.path.join(test_dir,'test.bib'), ps=Panuscript())
    l.querry_id('Test')
