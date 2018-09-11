#!/usr/bin/env python
'''
This module is designed to interface with Pandoc and ImageMagick using Python scripting.
'''

# Authors: Daniel R. Newman
# Created: 24/08/2018
# Last Modified: 27/08/2018
# License: MIT

import os
import sys, stat
from panuscript import Panuscript

def main():
    try:
        ps = Panuscript()
        '''View information '''
        # print(ps.info()) # Retrieves information about the Pandoc and ImageMagick executables.
        # [print(f) for f in ps.supported_formats()] # Returns a tuple of supported extensions. [0]=Pandoc Inputs [1]=Pandoc Outputs [2]=Image Formats [3]=Bibliographic Formats.
        # print(ps.pandoc_extensions()) # Returns a list of installed Pandoc extensions.

        '''Panuscript can be configured using keyword arguments'''
        # print(ps.configure(working_dir='', verbose=True, dpi=96, engine='pdflatex',
        #                citations=False, biblio='', csl='', linkcites=True, toc=0,
        #                atx_header=False, preserve_tabs=False, resize=100, grayscale=False))

        # ps.pandoc_exe_dir() # set the directory to the Pandoc executable.
        # ps.magick_exe_dir() # set the directory to the ImageMagick exectable.
        # ps.citeproc_exe_dir() # set the directory to the pandoc-citeproc executable.


        '''Panuscript Operations'''
        doc = "/path/to/document"
        img = "/path/to/image"
        bib = "/path/to/bib"
        # print([f for f in ps.extract_media(doc)]) # Returns a list of absolute paths for extracted graphical media from the specified document to document's directory.
        # ps.convert_document('markdown', 'latex', doc, doc.replace(".md",".tex")) # Coverts the input format to the output format. Custom commands (if supported by Pandoc) can be passed in an option args list.
        # ps.convert_document('latex', 'pdf', doc.replace('.md','.tex'), doc.replace('.md','.pdf'))
        # ps.convert_document('markdown', 'docx', doc, doc.replace('.md','.docx'))
        # ps.convert_image(img, img.replace('.png','.tif')) # Converts the input format to the output format
        # ps.embed_yaml_bib(bib, test) # Converts a supported bibliography to YAML metadata block, and embeds it in the document metadata. If the existing document doesn't not exist, a new .yaml file is created.
        # ps.fetch_csl("apa") # Attempts to download the CSL file from the official CSL repository. If 'dir=' is not given, files are written to the 'csls' folder.
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise
main()
