import os, platform, shutil, sys, math, re, requests
from subprocess import CalledProcessError, Popen, PIPE, STDOUT
try: from src.library import Library
except: from library import Library

class Panuscript(object):
    '''
    An object for interacting with the Pandoc, Pandoc-citeproc and ImageMagick executables.
    '''
    def __init__(self):
        self.VERSION = '0.0.2'
        # system variables
        if platform.system() == 'Windows':
            self.ext = '.exe'
        else:
            self.ext = ''
        self.p_exe_name = "pandoc{}".format(self.ext)
        self.p_exe_path = os.path.dirname(shutil.which(
            self.p_exe_name) or path.dirname(path.abspath(__file__)))
        self.pc_exe_name = "pandoc-citeproc{}".format(self.ext)
        self.pc_exe_path = os.path.dirname(shutil.which(
            self.pc_exe_name) or path.dirname(path.abspath(__file__)))
        self.m_exe_name = "magick{}".format(self.ext)
        self.m_exe_path = os.path.dirname(shutil.which(
            self.m_exe_name) or path.dirname(path.abspath(__file__)))
        self.work_dir = ""
        self.verbose = True
        self.ppi = 96
        self.pdf_engine = 'pdflatex'
        self.citations = False
        self.bibliography = None
        self.csl = 'apa'
        self.link_citations = False
        self.toc_depth = 0
        self.atx_header = False
        self.tab_preservation = False
        self.sizing_factor = 100
        self.grayscale = False

        self.update_exe_info()

    def get_exe_info(self):
        '''
        Retrieves package information from the executables.
        '''
        ret = run_shell(os.path.join(self.p_exe_path, self.p_exe_name),
                        args=['--version']) + os.linesep
        ret += run_shell(os.path.join(self.pc_exe_path, self.pc_exe_name),
                        args=['--version']) + os.linesep
        ret += run_shell(os.path.join(self.m_exe_path, self.m_exe_name),
                        args=['convert', '--version']) + os.linesep
        return ret

    def update_exe_info(self):
        '''
        Updates exe information with current exe paths.
        '''
        self.info = self.get_exe_info()
        self.pandoc_extensions = self.installed_pandoc_extensions()
        self.pandoc_formats, self.bib_formats, self.magick_formats = self.supported_formats()
        return self

    def set_pandoc_dir(self, path_str):
        '''
        Sets the path to the Pandoc executable file.
        '''
        path = os.path.normpath(path_str)
        if os.path.isdir(path): self.p_exe_path = path
        self.update_exe_info()
        return self.p_exe_path

    def set_citeproc_dir(self, path_str):
        '''
        Sets the path to the pandoc-citeproc executable file.
        '''
        path = os.path.normpath(path_str)
        if os.path.isdir(path): self.pc_exe_path = path
        self.update_exe_info()
        return self.pc_exe_path

    def set_magick_dir(self, path_str):
        '''
        Sets the path to the ImageMagick executable file.
        '''
        path = os.path.normpath(path_str)
        if os.path.isdir(path): self.m_exe_path = path
        self.update_exe_info()
        return self.m_exe_path

    def set_working_directory(self, path_str):
        '''
        Sets the path to the working directory.
        '''
        path = os.path.normpath(path_str)
        if os.path.isdir(path): self.work_dir = path
        return self.work_dir

    def set_verbose(self, val):
        '''
        Sets verbose mode and returns the updated mode.
        Verbose mode set to False will suppress STDOUT,
        '''
        if type(val) is bool:
            self.verbose = val
        return self.verbose

    def set_ppi(self, val):
        '''
        Sets the pixels per inch by 'val' and returns the updated value.
        '''
        if type(val) is int:
            self.ppi = val
        return self.ppi

    def set_pdf_engine(self, val):
        '''
        Sets the and returns the engine based on the argument.
        Options include: pdflatex, lualatex, xelatex, whktmltopdf, weasyprint, prince, context, pdfroff.
        '''
        engines = ["pdflatex", "lualatex", "xelatex", "whtmltopdf", "weasyprint", "prince", "context", "pdfroff"]
        if val in engines:
            self.pdf_engine = val
        else:
            print("Must use a supported PDF engine. Options include:")
            print(repr([e for e in engines]))
            print("See Pandoc documentation for more details.")
        return self.pdf_engine

    def set_citations(self, val, biblio=None, csl='apa', link_citations=False):
        if val is True:
            self.citations = True
            if biblio != None:
                bibf = self.normalize_path(biblio)
                if os.path.splitext(bibf)[1] in self.bib_formats:
                    self.bibliography = bibf
            else: self.citations = False
            if csl != None:
                self.csl = self.fetch_csl(self.normalize_path(csl))
            self.link_citations = link_citations
        return self

    def set_toc_depth(self, depth):
        '''
        Returns the table of content depth if depth greater than zero. Values greater than the maximum value (6) are lowered to (6).
        Sets the TOC depth and returns the new depth. If depth is not greater than zero, the TOC is disabled
        '''
        depth = math.floor(depth)
        if type(depth) is int:
            if depth >= 1 and depth <= 6:
                self.toc_depth = depth
            elif depth > 6:
                if self.ps.verbose: print("TOC depth was lowered to the maximum value of 6.")
                self.toc_depth = 6
            else:
                self.toc_depth = 0
        return self.toc_depth

    def set_atx_header(self, val):
        '''
        Sets the ATX header mode.
        If true, ATX headers are used in markdown, and if false, Setext headers are used.
        '''
        if type(val) is bool:
            self.atx_head = val
        return self.atx_head

    def set_tab_preservation(self, val):
        '''
        Sets the tab preservation mode and returns the updated setting.
        True preserves tabs in literal code blocks, false converts tabs to spaces.
        '''
        if type(val) is bool:
            self.preserve_tab = val
        return self.preserve_tab

    def set_resizing_factor(self, val):
        '''
        Returns the image resize parameter in percent if no arguments are given.
        Sets the resize percentage and returns the updated setting.
        '''
        val = math.floor(val)
        if type(val) is int:
            self.re_size = val
        return self.re_size

    def set_grayscale(self, val):
        '''
        Sets the grayscale mode by the argument.
        If grayscale is enabled, images will be converted to grayscale.
        '''
        if type(val) is bool:
            self.gray_scale = val
        return self.gray_scale

    def configure(self, verbose=None, workdir=None, ppi=None, pdf_engine=None,
                    citations=None, biblio=None, csl='apa', link_citations=False,
                    toc=None, atx_header=None,preserve_tabs=None, resize_percent=None,
                    grayscale=None):
        if verbose != None: self.set_verbose(verbose)
        if workdir != None: self.set_working_directory(workdir)
        if ppi != None: self.set_ppi(ppi)
        if pdf_engine != None: self.set_pdf_engine(pdf_engine)
        if citations != None and biblio != None:
            self.set_citations(citations, biblio, csl, link_citations)
        if toc != None: cfg.set_toc_depth(toc)
        if atx_header != None: self.set_atx_header(atx_header)
        if preserve_tabs != None: self.set_tab_preservation(preserve_tabs)
        if resize_percent != None: self.set_resizing_factor(resize_percent)
        if grayscale != None: self.set_grayscale(grayscale)
        ret = {'Working Directory':self.work_dir, 'Verbose':self.verbose,
                'PPI':self.ppi, 'PDF engine':self.pdf_engine, 'Citations':self.citations,
                'Bibliography file':self.bibliography, 'CSL file':self.csl,
                'Linked citations': self.link_citations, 'Table of Contents':self.toc_depth,
                'ATX headers':self.atx_header, 'Preserve tabs':self.tab_preservation,
                'Resizing factor (%)':self.sizing_factor, 'Grayscale':self.grayscale}
        return '~Configuration~{}{}'.format(os.linesep, dict_to_table(ret))

    def installed_pandoc_extensions(self):
        '''
        Returns a list of installed Pandoc extensions.
        '''
        ret = run_shell(os.path.join(self.p_exe_path, self.p_exe_name),
                        args=['--list-extensions'])
        return sorted([x[1:].strip() for x in ret.split(os.linesep) if x.strip().startswith('+')])

    def supported_formats(self):
        '''
        Retrieves supported input[0] and output[1] Pandoc formats, image formats[2] and bibliographic formats[3].
        '''
        biblio_formats = {"BibLaTeX": ".bib", "BibTeX": ".bibtex", "Copac": ".copac",
                            "CSL JSON": ".json", "CSL YAML": ".yaml", "EndNote": ".enl",
                            "ISI": ".wos", "MEDLINE": ".medline", "MODS": ".mods",
                            "RIS": ".ris"}
        bibio = list(biblio_formats.values())
        pexe = os.path.join(self.p_exe_path,self.p_exe_name)
        mexe = os.path.join(self.m_exe_path,self.m_exe_name)
        pdin = sorted([x.strip() for x in run_shell(pexe, args=['--list-input-formats']).split(os.linesep) if x.strip() != ''])
        # pdout = sorted(['pdf'].append([x.strip() for x in run_shell(pexe,
        #                     args=['--list-output-formats']).split(os.linesep)]))
        pdout = sorted(['pdf']+[x.strip() for x in run_shell(pexe,
                            args=['--list-output-formats']).split(os.linesep) if x.strip() != ''])
        mrw = sorted([x for x in run_shell(mexe, args=['-list', 'format'],
                                        match=' rw[+|-] ').split(os.linesep) if x.strip() != ''])
        mio = []
        for f in mrw:
            ext = "." + f.strip().split(' ', 1)[0].replace('*', '')
            mio.append(ext.lower())

        pdio = {}
        pdfmts = [pdin, pdout]
        for x in range(len(pdfmts)):
            pdf = {}
            for fmt in pdfmts[x]:
                if fmt in ['commonmark','gfm','markdown','markdown_github','markdown_mmd','markdown_phpextra','markdown_strict']:
                    pdf[fmt] = ['.md','.markdown']
                elif fmt in ['creole','dokuwiki','man','mediawiki','muse','t2t','tikiwiki','twiki','vimwiki','asciidoc','asciidoctor','jira','ms','plain','tei','xwiki','zimwiki']:
                    pdf[fmt] = ['.txt']
                elif fmt in ['docbook','docbook4','docbook5']: pdf[fmt] = ['.dbk','.xml']
                elif fmt in ['docx']: pdf[fmt] = ['.docx']
                elif fmt in ['epub','epub2','epub3']: pdf[fmt] = ['.epub']
                elif fmt in ['f2b', 'jats','icml','opendocument']: pdf[fmt] = ['.xml']
                elif fmt in ['haddock','native']: pdf[fmt] = ['.hs','.lhs']
                elif fmt in ['html','dzslides','html4','html5','revealjs','s5','slideous','slidy']: pdf[fmt] = ['.html']
                elif fmt in ['ipynb']: pdf[fmt] = ['.ipynb']
                elif fmt in ['json']: pdf[fmt] = ['.json']
                elif fmt in ['latex','beamer','context']: pdf[fmt] = ['.tex']
                elif fmt in ['odt']: pdf[fmt] = ['.odt']
                elif fmt in ['opml']: pdf[fmt] = ['.opml']
                elif fmt in ['org']: pdf[fmt] = ['.org']
                elif fmt in ['rst']: pdf[fmt] = ['.rst']
                elif fmt in ['textile']: pdf[fmt] = ['.textile']
                elif fmt in ['pdf']: pdf[fmt] = ['.pdf']
                elif fmt in ['pptx']: pdf[fmt] = ['.pptx']
                elif fmt in ['rtf']: pdf[fmt] = ['.rtf']
                elif fmt in ['texinfo']: pdf[fmt] = ['.texinfo']
                else: pdf[fmt] = ['.txt']
            if x == 0: pdio['input'] = pdf
            else: pdio['output'] = pdf

        return (pdio, bibio, mio)

    def normalize_path(self, path_str):
        if os.path.dirname(path_str): return path_str
        else: return os.path.join(self.work_dir, path_str)

    def fetch_csl(self, style, update=False):
        '''
        Attempts to download the specified 'style' of CSL from the CSL repository
        (https://github.com/citation-style-language/styles) to the specified directory.
        Defaults to the working directory.
        Citation Style Language homepage: https://citationstyles.org/
        Sets the CSL file to the new or existing CSL file
        '''
        style = os.path.splitext(style.lower().strip())[0]
        common_styles = {"mla": "modern-language-association",
                        "chicago": "chicago-author-date",
                        "acm": "association-for-computing-machinery",
                        "acs": "american-chemical-society",
                        "aaa": "american-athropological-association",
                        "apsa": "american-political-science-association"}

        if style in list(common_styles.keys()):
            style = common_styles.get(style)
        style += ".csl"

        file = os.path.join(os.path.join(os.path.dirname(
                            os.path.dirname(__file__)),'csls'),style)
        if os.path.isfile(file) and update == False:
            return file
        else:
            url = "https://raw.githubusercontent.com/citation-style-language/styles/master/{}".format(style)
            text = scrape_text(url)
            if text:
                with open(file, 'w') as newf:
                    newf.write(text)
                return file
            else:
                if self.verbose: print('Could not fetch CSL for \'{}\'. Please refer to the CSL homepage: https://citationstyles.org/.'.format(style))

    def extract_media(self, file):
        '''
        Extracts images or other media from the file to the file's directory.
        '''
        file = self.normalize_path(file)
        dir = os.path.dirname(file)
        cmd = ['.' + os.path.sep + self.p_exe_name]
        if self.verbose: a = ['--verbose']
        else: a = ['--quiet']
        a += ['--extract-media={}'.format(dir), file]

        if self.verbose: print(' '.join([x for x in cmd+a]).strip())

        files = [x for x in run_shell(os.path.join(self.p_exe_path, self.p_exe_name),
                        args=a).split(os.linesep) if x.startswith('[INFO]')]
        if len(files) >= 1: files = [''.join(x.split('Extracting ',1)[1].split('..')[:-1]) for x in files]
        # move files from the pandoc output to the specified directory
        ret = []
        if len(files) >= 1:
            for f in files:
                path, fn = os.path.split(f)
                newname = os.path.join(path, os.path.split(file)[1] + "_" + fn)
                os.rename(f, newname)
                newf = os.path.join(os.path.dirname(path), os.path.split(newname)[1])
                shutil.move(newname, newf)
                ret.append(newf)
            shutil.rmtree(path)

            if self.grayscale or self.sizing_factor != 100:
                [self.convert_image(f,f) for f in ret]

        return ret

    def convert_doc(self, input, read, write, *args):
        '''
        Converts input file, interpreted from read, and creates a new file of the same name
        in the format specific by write. Returns the new file's path.
        The user can provide additional flag options through a args list with no guarantees. Arguments must be compatible with Pandoc.
        '''
        file = self.normalize_path(input)
        ext = os.path.splitext(file)[1]
        read = read.lower()
        write = write.lower()
        pdinf = self.pandoc_formats['input']
        pdouf = self.pandoc_formats['output']
        if read in pdinf.keys() and write in pdouf.keys():
            cmd = ['.' + os.path.sep + self.p_exe_name]
            if self.verbose: a = ['--verbose']
            else: a = ['--quiet']
            a += ['--read={}'.format(read)]
            if write != 'pdf': a += ['--write={}'.format(write)]
            else: a += ['--pdf-engine', self.pdf_engine]
            if self.ppi != 96: a += ['--dpi={}'.format(self.ppi)]
            if self.tab_preservation: a += ['--preserve-tabs']
            if self.toc_depth >= 1: a += ['--toc', '--toc-depth={}'.format(self.toc_depth)]
            if write in ['markdown', 'asciidoc', 'asciidoctor'] and self.atx_header:
                a += ['--atx-headers']
            if self.citations:
                a += ['--filter', 'pandoc-citeproc']
                if os.path.isfile(self.bibliography):
                    a += ['--bibliography', self.bibliography]
                if os.path.isfile(self.csl):
                    a += ['--csl', self.csl]
            if type(args) is list: a += args
            out_file = os.path.splitext(file)[0] + pdouf[write][0]
            a += [file, '-o', out_file]

            if self.verbose: print(' '.join([x for x in cmd+a]).strip())

            ret = run_shell(os.path.join(self.p_exe_path, self.p_exe_name), args=a)
            print(ret)
            if self.verbose: print(ret + os.linesep)

            if os.path.isfile(out_file): return out_file
            else: return 'Unknown error'
        else: print('Cannot convert unsupported formats.')

    def convert_image(self, input, output, *args):
        '''
        Converts an image from the input format to the output format.
        Returns the path of the output file.
        The user can provide additional flag options through a args list with no guarantees. Arguments must be compatible with ImageMagick.
        '''
        input = self.normalize_path(input)
        iext = os.path.splitext(input)[1].lower()
        output = self.normalize_path(output)
        oext = os.path.splitext(output)[1].lower()
        m_fmts = self.magick_formats
        if iext in m_fmts and oext in m_fmts:
            cmd = ['.' + os.path.sep + self.m_exe_name]
            a = ['convert', input]
            if self.verbose: a += ['-verbose']
            else: a += ['-quiet']
            if self.ppi != 72: a += ['-density', '{}'.format(self.ppi)]
            if self.sizing_factor != 100:
                a += ['-resize', '{}%'.format(self.sizing_factor)]
            if self.grayscale: a += ['-colorspace', 'Gray']
            if type(args) is list: a += args
            a += [output]

            if self.verbose: print(' '.join([x for x in cmd+a]).strip())

            ret = run_shell(os.path.join(self.m_exe_path, self.m_exe_name), args=a)

            if self.verbose: print(ret + os.linesep)

            if os.path.isfile(output): return output
            else: return 'Unknown error'
        else: print('Cannot convert unsupported formats.')

    def embed_yaml_bib(self, bibliography=None, *doc_file):
        '''
        Converts a supported bibliographic file to YAML metadata and appends it to the document file.
        If no document file is specified, a new .yaml file will be created.
        Returns the path of the yaml file.
        Note: doc_file format must support YAML.
        Assumes YAML block occurs at the begining of the document.
        '''
        if doc_file: doc_file = self.normalize_path(doc_file[0])
        if bibliography != None: bib_file = self.normalize_path(bibliography)
        else: bib_file = self.bibliography
        if os.path.splitext(bib_file)[1] in self.bib_formats:
            cmd = ['.' + os.path.sep + self.pc_exe_name]
            a = ['--bib2yaml', bib_file]

            if self.verbose: print(' '.join([x for x in cmd+a]).strip())

            yaml_block = run_shell(os.path.join(self.pc_exe_path, self.pc_exe_name), args=a)
            bib_yaml = "".join([x for x in re.split('\-{3}\n|\.{3}\n', yaml_block) if x != ''])

            if doc_file and os.path.isfile(doc_file):
                with open(doc_file, 'r') as df:
                    delim = [x for x in re.split('\-{3}\n|\.{3}\n', df.read()) if x != '']
                    yaml1 = delim[0].split(os.linesep)
                    rest = ''.join(delim[1:])
                    out_str = '---' + os.linesep
                    for line in yaml1:
                        if 'link-citations: ' in line:
                            link_line = line
                        else: out_str += line
                    if self.link_citations is True: out_str += link_line.repalce(
                                    'link-citations: false', 'link-citations: true')
                    out_str += '{}...{}{}'.format(bib_yaml, os.linesep, rest)
                    with open(doc_file, 'w') as newf:
                        newf.write(out_str)

                    if self.verbose: print("Conversion complete." + os.linesep)

                    return doc_file
            else: # new .yaml file
                with open(os.path.splitext(bib_file)[0] + ".yml", 'w') as newf:
                    newf.write('---{}{}...{}'.format(os.linesep, bib_yaml, os.linesep))

                if self.verbose: print("Conversion complete." + os.linesep)

                return os.path.splitext(bib_file)[0] + ".yml"

    def yaml_bib_str(self, bibliography=None):
        if bibliography != None: bib_file = self.normalize_path(bibliography)
        else: bib_file = self.bibliography
        if os.path.splitext(bib_file)[1] in self.bib_formats:
            cmd = ['.' + os.path.sep + self.pc_exe_name]
            a = ['--bib2yaml', bib_file]
            if self.verbose: print(' '.join([x for x in cmd+a]).strip())
            return run_shell(os.path.join(
                                self.pc_exe_path, self.pc_exe_name), args=a)

    def json_bib(self, bibliography=None):
        if bibliography != None: bib_file = self.normalize_path(bibliography)
        else: bib_file = self.bibliography
        if os.path.splitext(bib_file)[1] in self.bib_formats:
            a = ['--bib2json', bib_file]
            return run_shell(os.path.join(
                                self.pc_exe_path, self.pc_exe_name), args=a)

    def xref_md(self, md_file, bibliography=None):
        if bibliography != None: bib_file = self.normalize_path(bibliography)
        else: bib_file = self.bibliography
        md_refs = set(self.md_references(md_file))
        lib = Library(bib_file, ps=self)
        missing = [i for i in md_refs if i not in [
                                        e.id for e in lib.entries if e.id in md_refs]]
        out_str = 'Missing bibliographic entries for:{}{}'.format(
                    os.linesep, '{}'.format(os.linesep).join(missing))
        if self.verbose: print(out_str)
        return out_str


    def md_references(self, md_file):
        with open(self.normalize_path(md_file), 'r') as md:
            # , ; : ] delimiters
            return [re.split('\,|\:|\;|\]',m.split(' ',1)[0])[0] for m in md.read().split('@')[1:]]

def run_shell(executable, args, match=None):
    '''
    Returns the string printed to the Std.out from the executable.
    Args must be a list of arguments
    '''
    try:
        assert(isinstance(args, list))
        path, exe = os.path.split(executable)
        os.chdir(path)
        a = [".{}{}".format(os.path.sep, exe)]
        a += args

        proc = Popen(a, shell=False, stdout=PIPE,
                     stderr=STDOUT, bufsize=1, universal_newlines=True)

        ret = []
        while True:
            line = proc.stdout.readline()
            if line != '' and proc.poll() is None:
                if match == None: ret.append(line)
                elif re.search(match, line): ret.append(line)
            else: break
        proc.communicate()

        return "".join(ret)

    except (OSError, ValueError, CalledProcessError) as err:
        return err

def dict_to_table(dictionary, space=3):
    assert(isinstance(dictionary, dict) == True)
    d = {}
    for i in dictionary:
        d[i] = dictionary[i]
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

def abspath_parts(self, abspath):
    path, file = os.path.split(abspath)
    fname, ext = os.path.splitext(file)
    return (path, fname, ext)

def scrape_text(url):
    try:
        req = requests.get(url)
        if req.text.strip() != '404: Not Found':
            return req.text
    except: return

if __name__ == '__main__':
    ps = Panuscript()
    testdir = os.path.join(os.path.dirname(os.path.dirname(__file__)),'test')
    bibf = os.path.join(testdir,'test.bib')
    mdf = os.path.join(testdir, 'test.md')
    #print(ps.info)
    print(ps.configure(verbose=True, citations=True, biblio=bibf, csl='ieee', link_citations=True, resize_percent=200, grayscale=True))
    # print(ps.pandoc_extensions)
    # print(ps.pandoc_formats)
    # print(ps.bib_formats)
    # print(ps.magick_formats)
    # print(ps.fetch_csl('sage-harvard'))
    # print(ps.extract_media(os.path.join(testdir, 'test.docx')))
    # print(ps.convert_doc(os.path.join(testdir,'test.docx'), 'docx', 'markdown'))
    # print(ps.convert_image(os.path.join(testdir, 'test.png'), os.path.join(testdir, 'test.tiff')))
    # print(ps.embed_yaml_bib(bibliography=bibf))
    # print(ps.xref_md(mdf, bibliography=bibf))
