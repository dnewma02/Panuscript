import os

def run(args):
    from src.ps_obj import Panuscript
    ps = Panuscript()
    ps.configure(link_citations=False, verbose=False,
                                atx_header=False, preserve_tabs=False,
                                grayscale=False)

    func = args[1].strip().lower().strip('-')
    if len(args) > 2: cargs = args[2:]
    else: cargs = []
    fargs = []
    cite_info = (False, None, None, False)
    # configure panuscript
    for a in cargs:
        a = a.replace('--', '-').strip()
        if a.startswith('-p-exe='):
            ps.set_pandoc_dir(a.split('=',1)[1])
        elif a.startswith('-pc-exe='):
            ps.set_citeproc_dir(a.split('=',1)[1])
        elif a.startswith('-m-exe='):
            ps.set_magick_dir(a.split('=',1)[1])
        elif a.startswith('-wd='):
            key, val = a.split('=',1)
            ps.set_working_directory(a.split('=',1)[1])
        elif a.startswith('-v'): ps.set_verbose(True)
        elif a.startswith('-ppi='):
            ps.set_ppi(a.split('=',1)[1])
        elif a.startswith('-pdf-engine='):
            ps.set_pdf_engine(a.split('=',1)[1])
        elif a.startswith('-citations'): cite_info[0] = True
        elif a.startswith('-bib='):
            cite_info[1] = a.split('=',1)[1]
        elif a.startswith('-csl='):
            cite_info[2] = a.split('=',1)[1]
        elif a.startswith('-link-citations'): cite_info[3] = True
        elif a.startswith('-toc-depth='):
            ps.set_toc_depth(a.split('=',1)[1])
        elif a.startswith('-atx'): ps.set_atx_header(True)
        elif a.startswith('-preserve-tabs'): ps.set_tab_preservation(True)
        elif a.startswith('-resize='):
            ps.set_resizing_factor(a.split('=',1)[1])
        elif a.startswith('-grayscale'): ps.set_grayscale(True)
        else: fargs.append(a.strip('-'))
    ps.set_citations(cite_info[0], cite_info[1], cite_info[2], cite_info[3])

    # run function
    f = Function(ps, func, fargs)
    if func not in ['h','help','i','info']:
        print('Results: {}'.format(f.result))

class Function:
    def __init__(self, ps, function, arglist):
        if function == 'fetch-csl': self.result = FETCHCSL(ps, arglist).result
        elif function =='extract-media': self.result = EXTRACTMEDIA(ps, arglist).result
        elif function == 'convert-document': self.result = CONVERTDOCUMENT(ps, arglist).result
        elif function == 'convert-image': self.result = CONVERTIMAGE(ps, arglist).result
        elif function == 'xref': self.result = XREF(ps, arglist).result
        elif function in ['i','info']: self.result = INFO(ps, arglist).result
        elif function in ['h','help']: self.result = HELP(ps, arglist).result
        else: self.result = None

class FETCHCSL(Function):
    def __init__(self, ps, args):
        self.help = '''
Attempts to download the csl for a style from the official repository.
Required arguments:
    --style= >> a STRING of the name of the citation style
Optional arguments:
    --update= >> a BOOL of specifying whether existing files should be overwritten with new content
Example usage: ... fetch-csl --style=apa --update=False
'''
        self.args = {'style':None,'update':False}
        if 'h' in args or 'help' in args: self.result = self.help
        else:
            for a in args:
                if a.strip('-') == 'update': self.args['update'] = True
                else:
                    key, val = a.split('=')
                    self.args[key] = val
            self.result = ps.fetch_csl(self.args['style'], self.args['update'])

class EXTRACTMEDIA(Function):
    def __init__(self, ps, args):
        self.help = '''
Extracts media content from the speficied file to the file's directory.
Required arguments:
    --input= >> a STRING of the path to the input file
Example usage: ... extract-media --input='/path/to/file'
'''
        self.args = {'input':None}
        if 'h' in args or 'help' in args: self.result = self.help
        else:
            for a in args:
                if a in ['h','help']: return print(self.help)
                else:
                    key, val = a.split('=')
                    self.args[key] = val
            self.result = ps.extract_media(self.args['input'])

class CONVERTDOCUMENT(Function):
    def __init__(self, ps, args):
        self.help = '''
Converts between document formats. See [info] for a supported formats.
Required Arguments:
    --input= >> a STRING of the path to the input file
Optional Arguments:
    --read= >> a STRING specifying the inputfile format. Panuscript will attempt to infer the format if unspecified. Default is raw text.
    --write= >>  a STRING specifying the inputfile format. Panuscript will attempt to infer the format if unspecified. Default is raw text.
    --args= >> a STRING containing custom formated arguments for Pandoc, delimited by ';'. Must be properly formatted for Pandoc.
Example usage: ... convert-document --input='/path/to/file' --output='/path/to/file' --read=markdown --write=docx --args=--dpi=96;--pdf-engine;pdflatex
'''
        self.args = {'input':None,'read':None,'write':None,'args':None}
        if 'h' in args or 'help' in args: self.result = self.help
        else:
            for a in args:
                key, val = a.split('=')
                if key == 'args': self.args[key] = val.split(";")
                else: self.args[key] = val
            self.result = ps.convert_doc(self.args['input'], self.args['read'],
                                    self.args['write'], self.args['args'])

class CONVERTIMAGE(Function):
    def __init__(self, ps, args):
        self.help = '''
Converts between image formats. See [info] for a list of supported formats.
Required Arguments:
    --input= >> a STRING of the path to the input file
    --output= >> a STRING of the path to the output file
Optional Arguments:
    --args= >> a STRING containing custom formated arguments for Pandoc, delimited by ';'. Must be properly formatted for ImageMagick.
Example usage: ... convert-image --input='/path/to/file' --output='/path/to/file' --args=-density;72;-colorspace;Gray
'''
        self.args = {'input':None,'output':None,'args':None}
        if 'h' in args or 'help' in args: self.result = self.help
        else:
            for a in args:
                key, val = a.split('=')
                if key == 'args': self.args[key] = val.split(";")
                else: self.args[key] = val
            self.result = ps.convert_image(self.args['input'], self.args['output'], self.args['args'])

class XREF(Function):
    def __init__(self, ps, args):
        self.help = '''
Cross references citations used in a markdown(.md) file with entries in a bibliographic file.
Required arguments:
    --md= >> a STRING of the path to the markdown(.md) file. Currently only markdown @mentions are supported.
    --bib= >> a STRING of the path to bibliographic file of a supported format.
Example usage: ... extract-media --input='/path/to/file'
'''
        self.args = {'md':None, 'bib':None}
        if 'h' in args or 'help' in args: self.result = self.help
        else:
            for a in args:
                key, val = a.split('=')
                self.args[key] = val
            self.result = ps.xref_md(self.args['md'], self.args['bib'])

class INFO(Function):
    def __init__(self, ps, args):
        out = 'Panuscript v.{}{}'.format(ps.VERSION, os.linesep*2)
        out += 'Executable info:{}{}'.format(os.linesep, ps.info)
        out += '''Supported formats:
Documents formats - Input:
{}

Documents formats - Output:
{}

Bibliographic formats:
{}

Image formats:
{}
'''.format(' '.format(os.linesep).join(list(ps.pandoc_formats['input'].keys())),
            ' '.format(os.linesep).join(list(ps.pandoc_formats['output'].keys())),
            ' '.format(os.linesep).join(ps.bib_formats),
            ' '.format(os.linesep).join(ps.magick_formats))
        self.result = print(out)

class HELP(Function):
    def __init__(self, ps, args):
        help = '''
Panuscript Help.

The first command must be the fuction command. The following function commands are recognized:
fetch-csl           Downloads a citation style language.
extract-media       Extracts media files from an input file.
convert-document    Converts document file formats. Must be configured to render citations.
convert-image       Converts image formats.
xref                Cross references citations from a markdown file with entries from bibliography file.
-h, --help          Prints additional information.

The -h or --help flag can also be used after a function command for function specific information.

Arguments can be placed anywhere after the function command.
Non-boolean arguments follow a argument=value format.
Boolean arguments without a '-' flag will produce a parsing error.

The following univeral arguments are be used to configure Panuscript behaviour:
--p-exe=            Sets the Pandoc executable directory
--pc-exe=           Sets the Pandoc-citeproc executable directory
--m-exe=            Sets the ImageMagick executable directroy
--wd=               Sets the working directory. Avoids the need to specify full paths.
-v                  Sets verbose to True
--ppi=              Sets the output resolution in pixels per inch
--pdf-engine=       Sets the pdf engine used for typesetting
-citations          Allows citations where applicable
--bib=              Sets the bibliographic file used for citation rendering
--csl=              Sets the citation style. Defaults to APA. Can specify a file, or a style in the /csls folder.
-link-citations     Hyperlinks in-text citations the the entry in the references
--toc-depth=        Sets the table of contents depth level. 0 turns of TOC rendering.
-atx                Use ATX headers where approriate. Else Setext headers are used.
-preserve-tabs      Preserves tabs while rendering code blocks
--resize=           Sets the percent by which images are resized during conversion
-grayscale          Conversion outputs are in grayscale


Example Usage:
>> ./python pansuscrupt.py convert-document -v --wd=/path/to/ --input=file.md --read=markdown --write=docx --toc-depth=3 -citations --bib=/path/to/file --csl=apa
'''
        self.result = print(help)

if __name__ == '__main__':
    import os
    from subprocess import CalledProcessError, Popen, PIPE, STDOUT
    os.chdir(os.path.dirname(os.path.dirname(__file__)))
    testdir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test')
    base_args = ['python', 'panuscript.py']
    tests = [['fetch-csl', '-v', '-wd={}'.format(testdir), '-style=apa', '--update'],
            ['extract-media', '-v', '-wd={}'.format(testdir), '---input=test.docx'],
            ['convert-document', '-v', '-wd={}'.format(testdir), 'input=test.md', 'read=markdown', 'write=html5'],
            ['convert-image', '-v', '-wd={}'.format(testdir), 'input=test.docx_image1.png', 'output=test_gray.tiff', '-grayscale', 'resize=500'],
            ['xref', '-v', '-wd={}'.format(testdir), 'md=test.md', 'bib=test.bib'],
            ['xref', '-v', '-wd={}'.format(testdir), 'md=test.md', 'bib=test.bib', 'help'],
            ['xref', '-v', '-wd={}'.format(testdir), 'md=test.md', 'bib=test.bib', '-h'],
            ['help'],
            ['info']]

    for t in tests:
        print('Testing: {}'.format(t[0]))
        a = base_args + t
        proc = Popen(a, shell=False, stdout=PIPE,
                     stderr=STDOUT, bufsize=1, universal_newlines=True)

        while True:
            line = proc.stdout.readline()
            if line != '' and proc.poll() is None:
                print(line.strip())
            else: break
        proc.communicate()
