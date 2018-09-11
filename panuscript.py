#!/usr/bin/env python
'''
This module is designed to interface with Pandoc and ImageMagick using Python scripting.
'''

# Authors: Daniel R. Newman
# Created: 23/08/2018
# Last Modified: 23/08/2018
# License: MIT

from __future__ import print_function
import os
from os import path
import stat
import sys
import platform
import re
import shutil
import requests
import math
from subprocess import CalledProcessError, Popen, PIPE, STDOUT

class Panuscript(object):
    '''
    An object for interacting with the Pandoc and ImageMagick executables.
    '''

    def __init__(self):
        # system variables
        if platform.system() == 'Windows':
            self.ext = '.exe'
        else:
            self.ext = ''
        self.p_exe_name = "pandoc{}".format(self.ext)
        self.p_exe_path = os.path.dirname(shutil.which(
            self.p_exe_name) or path.dirname(path.abspath(__file__)))
        self.pc_exe_name = "pandoc{}".format(self.ext)
        self.pc_exe_path = os.path.dirname(shutil.which(
            self.pc_exe_name) or path.dirname(path.abspath(__file__)))
        self.m_exe_name = "magick{}".format(self.ext)
        self.m_exe_path = os.path.dirname(shutil.which(
            self.m_exe_name) or path.dirname(path.abspath(__file__)))
        self.work_dir = ""

        # general options
        self.verbosity = True
        self.ppi = 96

        # Pandoc options
        self.pdf_engine = "pdflatex"
        self.citations = False
        self.bibliography = ""
        self.citationstylesheet = ""
        self.toc_depth = 0
        self.atx_head = False
        self.preserve_tab = False
        self.link_cites = True

        # ImageMacick options
        self.re_size = 100
        self.gray_scale = False

    def info(self):
        '''
        Retrieves information for the executables.
        '''
        try:
            os.chdir(self.m_exe_path)
            args = []
            args.append("." + os.path.sep + self.m_exe_name)
            args.append("convert")
            args.append("--version")

            proc = Popen(args, shell=False, stdout=PIPE,
                         stderr=STDOUT, bufsize=1, universal_newlines=True)
            ret = ""
            while True:
                line = proc.stdout.readline()
                if line != '':
                    ret += line
                else:
                    break

            os.chdir(self.p_exe_path)
            args = []
            args.append("." + os.path.sep + self.p_exe_name)
            args.append("--version")

            proc = Popen(args, shell=False, stdout=PIPE,
                         stderr=STDOUT, bufsize=1, universal_newlines=True)
            ret += os.linesep
            while True:
                line = proc.stdout.readline()
                if line != '':
                    ret += line
                else:
                    break

            args = []
            args.append("." + os.path.sep + 'pandoc-citeproc')
            args.append("--version")

            proc = Popen(args, shell=False, stdout=PIPE,
                         stderr=STDOUT, bufsize=1, universal_newlines=True)
            ret += os.linesep
            while True:
                line = proc.stdout.readline()
                if line != '':
                    ret += line
                else:
                    break

            return ret
        except (OSError, ValueError, CalledProcessError) as err:
            return err

    def configure(self, working_dir='', verbose=True, dpi=96, engine='pdflatex',
                    citations=False, biblio='', csl='', toc=0, atx_header=False,
                    preserve_tabs=False, resize=100, grayscale=False, linkcites=True):
        '''
        Sets values for the Panuscript object
        '''
        self.working_dir(working_dir)
        self.verbose(verbose)
        self.dpi(dpi)
        self.engine(engine)
        if citations == True:
            if biblio != '' and csl != '':
                self.render_citations(bib_file=biblio, csl=csl)
            elif biblio != '':
                self.render_citations(bib_file=biblio)
            else:
                self.citations = True
        self.toc(toc)
        self.atx_header(atx_header)
        self.preserve_tabs(preserve_tabs)
        self.resize(resize)
        self.grayscale(grayscale)
        self.link_cites = linkcites
        ret = {'Working directory':self.work_dir, 'Verbose':self.verbosity,'DPI':self.ppi,
                'PDF engine':self.pdf_engine, 'Citations':self.citations,
                'Bibliographic file':self.bibliography,
                'Citation Style Sheet':self.citationstylesheet,
                'Table of Contents depth':self.toc_depth,
                'ATX/STX header mode':self.atx_head,
                'Tab reservation mode':self.preserve_tab,
                'Link citations':self.link_cites,
                'Resize (%)':self.re_size,
                'Grayscale colorspace':self.gray_scale}

        return ret

    def pandoc_exe_dir(self, path_str):
        '''
        Sets the path to the Pandoc executable file.
        '''
        self.p_exe_path = path_str
        return self.p_exe_path

    def magick_exe_dir(self, path_str):
        '''
        Sets the path to the ImageMagick executable file.
        '''
        self.m_exe_path = path_str
        return self.m_exe_path

    def citeproc_exe_dir(self, path_str):
        '''
        Sets the path to the pandoc-citeproc executable file.
        '''
        self.pc_exe_path = path_str
        return self.pc_exe_path

    def working_dir(self, path_str):
        '''
        Sets the working directory, i.e. the directory in which
        the data files are located. By setting the working
        directory, input parameters that are files need only
        specify the file name rather than the complete file path.
        '''
        self.work_dir = path_str
        print(self.work_dir)
        return self.work_dir

    def verbose(self, val):
        '''
        Sets verbose mode and returns the updated mode.
        Verbose mode set to False will suppress STDOUT,
        '''
        if type(val) is bool:
            self.verbosity = val
        return self.verbosity

    def dpi(self, val):
        '''
        Sets the pixels per inch by 'val' and returns the updated value.
        '''
        if type(val) is int:
            self.ppi = val
        return self.ppi

    def engine(self, engine):
        '''
        Sets the and returns the engine based on the argument.
        Options include: pdflatex, lualatex, xelatex, whktmltopdf, weasyprint, prince, context, pdfroff.
        '''
        engines = ["pdflatex", "lualatex", "xelatex", "whtmltopdf", "weasyprint", "prince", "context", "pdfroff"]
        if engine in engines:
            self.pdf_engine = engine
        else:
            print("Must use a supported PDF engine. Options include:")
            print(repr([e for e in engines]))
            print("See Pandoc documentation for more details.")
        return self.pdf_engine

    def fetch_csl(self, style, dir=""):
        '''
        Attempts to download the specified 'style' of CSL from the CSL repository
        (https://github.com/citation-style-language/styles) to the specified directory.
        Defaults to the working directory.
        Citation Style Language homepage: https://citationstyles.org/
        Sets the CSL file to the new or existing CSL file
        '''
        style = style.lower().strip()
        common_styles = {"mla": "modern-language-association",
                        "chicago": "chicago-author-date",
                        "acm": "association-for-computing-machinery",
                        "acs": "american-chemical-society",
                        "aaa": "american-athropological-association",
                        "apsa": "american-political-science-association"}

        if style in list(common_styles.keys()):
            style = common_styles.get(style)
        style += ".csl"

        if not os.path.isdir(dir):
            if self.work_dir != "":
                dir = self.work_dir
            else:
                dir = os.path.join(os.path.dirname(__file__), "csls")

        url = "https://raw.githubusercontent.com/citation-style-language/styles/master/" + style
        try:
            req = requests.get(url)
            if req.text.strip() != "404: Not Found":
                new_file = os.path.join(dir, style)
                if not os.path.isfile(new_file):
                    newf = open(new_file, "w")
                    newf.write(req.text)
                    newf.close()
                return new_file
            else:
                print("CSL format \'{}\' does not exist.".format(style))
        except (OSError, ValueError, CalledProcessError) as err:
            return err

    def render_citations(self, bib_file="", csl=""):
        '''
        Specify Bibliography and Citation Style Sheet files for citation rendering using the pandoc-citeproc extension.
        If pandoc-citeproc is not detected, the citation rendering is disabled.
        Assumes the bibliography is in the YAML metadata block if no bibliography file is specified.
        Defaults fo Chicago style citations if the CSL is not specified.
        '''
        try:
            # check for pandoc-citeproc with the citations extension
            pan_ex = self.pandoc_extensions()
            if "citations" in pan_ex:
                self.citations = True
                if os.path.dirname(bib_file):
                    path, f = os.path.split(bib_file)
                    fname, e = os.path.splitext(f)
                else:
                    fname, e = os.path.splitext(bib_file)
                    bib_file = os.path.join(self.work_dir, bib_file)
                if bib_file != "":
                    valid_extensions = self.supported_formats()[3]
                    if e in valid_extensions:
                        if os.path.isfile(bib_file):
                            self.bibliography = bib_file
                if csl != "":
                    if not os.path.dirname(csl):
                        csl = os.path.join(self.work_dir, csl)
                    if os.path.isfile(csl):
                        self.citationstylesheet = csl
            else:
                self.citations = False
                raise ValueError("Install the pandoc-citeproc extension for citation rendering.")

            return (self.bibliography, self.citationstylesheet)
        except (OSError, ValueError, CalledProcessError) as err:
            return err

    def toc(self, depth):
        '''
        Returns the table of content depth if depth greater than zero. Values greater than the maximum value (6) are lowered to (6).
        Sets the TOC depth and returns the new depth. If depth is not greater than zero, the TOC is disabled
        '''
        depth = math.floor(depth)
        if type(depth) is int:
            if depth >= 1 and depth <= 6:
                self.toc_depth = depth
            elif depth > 6:
                print("TOC depth was lowered to the maximum value of 6.")
                self.toc_depth = 6
            else:
                self.toc_depth = 0
        return self.toc_depth

    def atx_header(self, val):
        '''
        Sets the ATX header mode.
        If true, ATX headers are used in markdown, and if false, Setext headers are used.
        '''
        if type(val) is bool:
            self.atx_head = val
        return self.atx_head

    def preserve_tabs(self, val):
        '''
        Sets the tab preservation mode and returns the updated setting.
        True preserves tabs in literal code blocks, false converts tabs to spaces.
        '''
        if type(val) is bool:
            self.preserve_tab = val
        return self.preserve_tab

    def resize(self, val):
        '''
        Returns the image resize parameter in percent if no arguments are given.
        Sets the resize percentage and returns the updated setting.
        '''
        val = math.floor(val)
        if type(val) is int:
            self.re_size = val
        return self.re_size

    def grayscale(self, val):
        '''
        Sets the grayscale mode by the argument.
        If grayscale is enabled, images will be converted to grayscale.
        '''
        if type(val) is bool:
            self.gray_scale = val
        return self.gray_scale

    def supported_formats(self):
        '''
        Retrieves supported input[0] and output[1] Pandoc formats, image formats[2] and bibliographic formats[3].
        '''
        biblio_formats = {"BibLaTeX": ".bib", "BibTeX": ".bibtex", "Copac": ".copac",
                            "CSL JSON": ".json", "CSL YAML": ".yaml", "EndNote": ".enl",
                            "ISI": ".wos", "MEDLINE": ".medline", "MODS": ".mods",
                            "RIS": ".ris"}
        biblio = list(biblio_formats.values())

        try:
            os.chdir(self.p_exe_path)
            pdoc_in = []
            args = []
            args.append("." + os.path.sep + self.p_exe_name)
            args.append("--list-input-formats")

            proc = Popen(args, shell=False, stdout=PIPE,
                         stderr=STDOUT, bufsize=1, universal_newlines=True)

            while True:
                line = proc.stdout.readline()
                if line != '':
                    pdoc_in.append(line.strip())
                else:
                    break

            pdoc_out = ["pdf"]
            args = []
            args.append("." + os.path.sep + self.p_exe_name)
            args.append("--list-output-formats")

            proc = Popen(args, shell=False, stdout=PIPE,
                         stderr=STDOUT, bufsize=1, universal_newlines=True)

            while True:
                line = proc.stdout.readline()
                if line != '':
                    pdoc_out.append(line.strip())
                else:
                    break

            args = []
            args.append("." + os.path.sep + self.m_exe_name)
            args.append("-list")
            args.append('format')

            rw = []
            proc = Popen(args, shell=False, stdout=PIPE,
                         stderr=STDOUT, bufsize=1, universal_newlines=True)

            while True:
                line = proc.stdout.readline()
                if line != '':
                    line = line.strip()
                    match = re.search('   rw[-,+]   ', line)
                    if match:
                        rw.append(line)
                else:
                    break

            img_rw = []
            for f in rw:
                ext = "."
                for c in f:
                    if c == '*' or c == ' ':
                        break
                    else:
                        ext += c
                img_rw.append(ext.lower())

            return (pdoc_in, pdoc_out, img_rw, biblio)
        except (OSError, ValueError, CalledProcessError) as err:
            return err

    def pandoc_extensions(self):
        '''
        Retrieves installed Pandoc extensions.
        '''
        try:
            os.chdir(self.p_exe_path)
            args = []
            args.append("." + os.path.sep + self.p_exe_name)
            args.append("--list-extensions")

            pdoc_extensions = []
            proc = Popen(args, shell=False, stdout=PIPE,
                         stderr=STDOUT, bufsize=1, universal_newlines=True)

            while True:
                line = proc.stdout.readline()
                if line != '':
                    if line.strip()[0] == '+':
                        pdoc_extensions.append(line[1:].strip())
                else:
                    break

            return pdoc_extensions
        except (OSError, ValueError, CalledProcessError) as err:
            return err

    def abspath_info(self, abspath):
        path, file = os.path.split(abspath)
        fname, ext = os.path.splitext(file)
        return (abspath, path, fname, ext)

    def extract_media(self, file):
        '''
        Extracts images or other media from the file to the file's directory.
        '''
        if os.path.dirname(file):
            dir = os.path.dirname(file)
        else:
            dir = self.work_dir
            file = os.path.join(dir, file)
        try:
            os.chdir(self.p_exe_path)
            args = []
            args.append("." + os.path.sep + self.p_exe_name)
            if self.verbose:
                args.append("--verbose")
            else:
                args.append("--quiet")
            args.append("--extract-media={}".format(dir))
            args.append(file)

            if self.verbose:
                cl = ""
                for v in args:
                    cl += v + " "
                print(cl.strip())

            ret = []

            proc = Popen(args, shell=False, stdout=PIPE,
                         stderr=STDOUT, bufsize=1, universal_newlines=True)

            while True:
                line = proc.stdout.readline()
                sys.stdout.flush()
                if line != '':
                    if line[7:17] == 'Extracting':
                        s = line[18:].strip()
                        s = s[:-3]
                        if not os.path.dirname(s).endswith('media'):
                        #if not os.sep+"media"+os.sep in s:
                            ret.append(s[:-3])
                        if self.verbose:
                            print(line.strip())
                else:
                    break

            proc.communicate()

            # move files from the pandoc output to the specified directory
            media_dir = os.path.join(dir, "media")
            if os.path.isdir(media_dir):
                content = os.listdir(media_dir)
                src_fname = os.path.splitext(os.path.split(file)[1])[0]
                ret = []
                for file in content:
                    # rename based on input file name
                    f = os.path.join(media_dir, file)
                    new_file = os.path.join(media_dir, src_fname + "_" + file)
                    os.rename(f, new_file)
                    if os.path.isfile(os.path.join(dir, os.path.split(new_file)[1])):
                        os.remove(os.path.join(dir, os.path.split(new_file)[1]))
                    shutil.move(os.path.join(media_dir, new_file), dir)
                    ret.append(os.path.join(dir, os.path.split(new_file)[1]))
                shutil.rmtree(media_dir)

            if self.verbose:
                print("Extraction complete." + os.linesep)

            return ret
        except (OSError, ValueError, CalledProcessError) as err:
            return err

    def convert_document(self, read, write, input_file, output_file, *args):
        '''
        Converts a document from an input format to an output format.
        The user can provide additional flag options through a args list with no guarantees. Arguments must be compatible with Pandoc.
        Returns 0 if completes without error.
        Returns 1 if error encountered.
        '''

        if not os.path.dirname(input_file):
            input_file = os.path.join(self.work_dir, input_file)
        if read.lower() in self.supported_formats()[0] and write.lower() in self.supported_formats()[1]:
            try:
                os.chdir(self.p_exe_path)
                args2 = []
                args2.append("." + path.sep + self.p_exe_name)

                args2.append("-s") # output standalone documents instead of fragments (applies to html, tei, latex and rtf)
                if self.verbose:
                    args2.append("--verbose")
                else:
                    args2.append("--quiet")
                args2.append("--read={}".format(read))
                if write != 'pdf':
                    args2.append("--write={}".format(write))
                else:
                    args2.append("--pdf-engine")
                    args2.append(self.pdf_engine)
                    output_file = os.path.splitext(output_file)[0] + '.pdf'
                if self.preserve_tab == True:
                    args2.append("--preserve-tabs")
                if self.ppi != 96:
                    args2.append("--dpi={}".format(repr(self.ppi)))
                if self.toc_depth >= 1:
                    args2.append("--toc")
                    args2.append("--toc-depth={}".format(repr(self.toc_depth)))
                # ATX or Setext headers
                if "markdown" in write or write == "asciidoc":
                    if self.atx_head == True:
                        args2.append("--atx-headers")
                if self.citations == True:
                    args2.append("--filter")
                    args2.append("pandoc-citeproc")
                    if os.path.isfile(self.bibliography):
                        args2.append("--bibliography")
                        args2.append(self.bibliography)
                    if os.path.isfile(self.citationstylesheet):
                        args2.append("--csl")
                        args2.append(self.citationstylesheet)

                # PDF specific flags
                # if write == "pdf":
                #     args2.append("--pdf-engine")
                #     args2.append(self.pdf_engine)

                if type(args) is list:
                    [args2.append(a) for a in args]

                args2.append(input_file)
                args2.append("-o")
                args2.append(output_file)

                if self.verbose:
                    cl = ""
                    for v in args2:
                        cl += str(v) + " "
                    print(cl.strip())

                proc = Popen(args2, shell=False, stdout=PIPE,
                             stderr=STDOUT, bufsize=1, universal_newlines=True)

                while True:
                    line = proc.stdout.readline()
                    sys.stdout.flush()
                    if line != '':
                        if self.verbose:
                            print(line.strip())
                    else:
                        break

                proc.communicate()

                if self.verbose:
                    print("Conversion complete." + os.linesep)

                return 0
            except (OSError, ValueError, CalledProcessError) as err:
                print(err)
                return 1
        else:
            print('Cannot convert an unsupported format.')

    def convert_image(self, input, output, *args):
        '''
        Converts an image from the input format to the output format.
        The user can provide additional flag options through a args list with no guarantees. Arguments must be compatible with ImageMagick
        Returns 0 if completes without error.
        Returns 1 if error encountered.
        '''
        if not os.path.dirname(input):
            input = os.path.join(self.work_dir, input)
        if not os.path.dirname(output):
            output = os.path.join(self.work_dir, output)
        i_ext = self.abspath_info(input)[3]
        o_ext = self.abspath_info(output)[3]
        if i_ext.lower() in self.supported_formats()[2] and o_ext.lower() in self.supported_formats()[2]:
            try:
                os.chdir(self.m_exe_path)
                args2 = []
                args2.append("." + path.sep + self.m_exe_name)
                args2.append("convert")
                args2.append(input)
                ## configure flags ##
                if self.verbose:
                    args2.append("-verbose")
                else:
                    args2.append("-quiet")
                if self.ppi != 72:
                    args2.append("-density")
                    args2.append(repr(self.ppi))
                if self.re_size != 100:
                    args2.append("-resize")
                    args2.append(repr(self.re_size) + "%")
                if self.gray_scale == True:
                    args2.append("-colorspace")
                    args2.append("Gray")

                if type(args) is list:
                    [args2.append(a) for a in args]

                args2.append(output)

                if self.verbose:
                    cl = ""
                    for v in args2:
                        cl += str(v) + " "
                    print(cl.strip())

                proc = Popen(args2, shell=False, stdout=PIPE,
                             stderr=STDOUT, bufsize=1, universal_newlines=True)

                while True:
                    line = proc.stdout.readline()
                    sys.stdout.flush()
                    if line != '':
                        if self.verbose:
                            print(line.strip())
                    else:
                        break

                proc.communicate()

                if self.verbose:
                    print("Conversion complete." + os.linesep)

                return 0
            except (OSError, ValueError, CalledProcessError) as err:
                print(err)
                return 1
        else:
            print("Please enter a valid format.")

    def embed_yaml_bib(self, bib_file, *doc_file):
        '''
        Converts a supported bibliographic file to YAML metadata and appends it to the document file.
        If no document file is specified, a new .yaml file will be created.
        Returns 0 if completes without error.
        Returns 1 if error encountered.
        '''
        if doc_file:
            doc_file = doc_file[0]
        if not os.path.dirname(bib_file):
            bib_file = os.path.join(self.work_dir, bib_file)
        ext = self.abspath_info(bib_file)[3]
        biblio_formats = self.supported_formats()[3]
        if ext in biblio_formats:
            try:
                os.chdir(self.p_exe_path)
                args2 = []
                args2.append("." + path.sep + 'pandoc-citeproc')
                args2.append("--bib2yaml")
                args2.append(bib_file)

                if self.verbose:
                    cl = ""
                    for v in args2:
                        cl += str(v) + " "
                    print(cl.strip())

                proc = Popen(args2, shell=False, stdout=PIPE,
                             stderr=STDOUT, bufsize=1, universal_newlines=True)

                copy = False
                cite_str = ""
                if self.link_cites == True:
                    cite_str += 'link-citations: true' + os.linesep
                while True:
                    line = proc.stdout.readline()
                    sys.stdout.flush()
                    if line != '':
                        # if self.verbose:
                        #     print(line.strip())
                        if line.strip() == '---':
                            copy = True
                        elif line.strip() == '...' or line.strip() == '---':
                            copy = False
                        if copy == True and line.strip() != '---':
                            # temporary fix for title "{{" and "}}" in mendeley .bib output
                            cite_str += line.replace("<span class=\"nocase\">", "").replace("</span>", "")
                    else:
                        break

                proc.communicate()

                if doc_file and os.path.isfile(doc_file):
                    # place inside of the first YAML metadata block
                    lines = [line for line in open(doc_file, 'r')]
                    yaml_delimit = 0
                    in_str = ""
                    for line in lines:
                        if line.strip() == "---" or line.strip() == '...':
                            yaml_delimit += 1
                        if yaml_delimit == 2:
                            in_str += os.linesep + cite_str
                            yaml_delimit += 2 # only writes to the first YAML block
                        in_str += line
                    if yaml_delimit == 0:
                        # no YAML metadata, write bibliography to the start of the document
                        out_str = "---" + os.linesep
                        out_str += cite_str + "..." + os.linesep
                        out_str += in_str
                        old_fyle = open(doc_file, 'w')
                        old_fyle.write(out_str)
                    else:
                        old_fyle = open(doc_file, 'w')
                        old_fyle.write(in_str)
                else:
                    # create a new .yaml file
                    _, p, fn, _ = self.abspath_info(bib_file)
                    new_fyle = open(os.path.join(p,fn)+'.yaml', 'w')
                    out_str = "---" + os.linesep
                    out_str += cite_str + "..." + os.linesep
                    new_fyle.write(out_str)

                if self.verbose:
                    print("Conversion complete." + os.linesep)

                return 0
            except (OSError, ValueError, CalledProcessError) as err:
                print(err)
                return 1
