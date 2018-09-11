# Panuscript

**Contents**

1. [Description](#1-description)
2. [Downloads and Installation](#2-downloads-and-installation)
3. [Contributing](#3-contributing)
4. [License](#4-license)
5. [Usage](#5-usage)


## 1 Description

**Panuscript** is a wrapper for **Pandoc** and **ImageMagick** intended to promote productivity in academic writing by allowing easy image and document format conversion. **Pandoc** provides the flexibility convert between a wide variety of document formats and **ImageMagick** provides a similar function for image formats. For simplicity, however, many of the more powerful functions of both programs are excluded. Instead **Panuscript** provides a simple and efficient interface, granting freedom of choice with respect to software, format, and operating system. By focussing on features beneficial to academia (e.g. automated citation rendering, provided through pandoc-citeproc), productivity is greatly compared to manual alternatives by minimizing the responsibility of document formatting for the author. Lightweight markup languages like **Markdown** can be used to create rich text documents from plain text editors, allowing the author to focus on content.

This project was initiated primarily to learn and experiment programming with objects.

## 2 Downloads and Installation

### Prerequisites
The following need to be installed (or at least access to the binary executable)
  * [Python (version 3)](https://www.python.org/) **Panuscript assumes the user system is configured with Python 3 and may not run as expected using Python 2**
  * [Pandoc](https://pandoc.org/)
  * [ImageMagick](https://www.imagemagick.org/script/index.php)

### Additional functionality
  * Citation Rendering
    * [pandoc-citeproc](https://pandoc.org/installing.html) *links to installation instructions for depending on the operating system*
  * PDF Typsetting
    * [a PDF engine ex. LaTeX, ConTeXt etc.](https://pandoc.org/MANUAL.html#creating-a-pdf) *links to the Pandoc user manual for supported engines. LaTeX is recommended as the default engine.*
      * [LaTeX](https://www.latex-project.org/)
      * [Tex Live](https://www.tug.org/texlive/)

## 3 Contributing

Given the small size of the project, contributions are currently accepted in the form of functionality requests. Should the requests not be dealt with in a timely manner, contributes are urged to fork the project and add the desired functionality.  

Unless explicitly stated otherwise, any contribution intentionally submitted for inclusion in the work shall be licensed [as below](#4-license) without any additional terms or conditions.

## 4 License

The **Panuscript** wrapper is distributed under the [MIT license](LICENSE.txt), a permissive open-source (free software) license.

## 5 Usage

Currently, `scripting_interface.py` is the primary way to interact with Panuscript. In the future a simple TK gui may be added.

### Viewing information
Several functions are provided to view information about the underlying software.
  * `info()` returns shows the version and other relevant information for the ImageMagick, Pandoc and pandoc-citeproc executables.
  * `supported_formats()` returns a tuple of supported formats. \[0\] = Pandoc input formats, \[1\] = Pandoc output formats, \[2\] = ImageMagick read/write formats, and \[3\] = pandoc-citeproc bibliographic formats.
  * `pandoc_extensions()` returns  a list of installed Pandoc extensions.

### Configuring Panuscript
Keyword arguments are passed through the `configure()` function. Options include (keyword=default):
  * `working_dir=''` to set the working directory. Without a working directory, Full path names must be given.
  * `verbose=True` to set the verbosity mode. False mode suppresses the STDOUT.
  * `dpi=96` to set the resolution of the output documents and images.
  * `engine='pdflatex'` to set the PDF engine used by Pandoc to output PDF format documents.
  * `citations=False` to set the citation rendering mode. See [below](####-citation-rendering).
  * `biblio=''` to set the bibliographic information file.
  * `csl=''` to set the citation style.
  * `linkcites=False` to set the citation linking mode. If true, citations will be linked to the correponding item in the references.
  * `toc=0` to set the table of contents (TOC) depth. Depth refers to the heading level to include in the TOC.
  * `atx_header=False` sets the header mode in markdown and ASCII documents. True for ATX, false for Setext.
  * `preserve_tabs=False` sets the tab preservation mode for literal code blocks. If false, tabs are converted to four (4) spaces
  * `resize=100` sets the image resize value, in percent of the original image size.
  * `grayscale=False`set grayscale mode during image conversion. If True, images are converted to grayscale using.

  * `pandoc_exe_dir()`, `magick_exe_dir()`, `citeproc_exe_dir()` set the respective exe path (helpful if no system PATH variable is set)

### Extracting media
The `extract_media()` function extracts, reads, or downloads images or other media contained in the specified input document to the directory containing the input document. A list of the extracted files is returned to simplify further operations such as format conversion using the `convert_image()` function.

### Converting images
The `convert_image()` function uses ImageMagick to convert image formats from the input to the output format, as inferred from the file extensions. This can also be used to rename images. Through `configure()` function, grayscale transformations (`configure(grayscale=True)`) and a percent based image resizing (`configure(resize=NUMBER)`) can be applied to the output images.

Optional arguemnts provide the user with the means to further specify the behaviour of the ImageMagick conversion, as long as they are valid arguments for the ImageMagick `convert` program. However, if the flag is followed by a space, it must be entered as the list element immediately following the flag. For example to apply a median filter of radius 3:
  '''
  args = \['-median', 3\]
  '''

### Converting documents
The `convert_document()` function uses Pandoc to convert the input file format to another format. It should be noted that the the output format is specified by the `write` argument (position 2), regardless of the extension of the output file. Valid formats can be viewed from the `supported_formats()` function. However, it is the responsibility of the user to select an appropriate extension for the output file. Similar to `convert_image()`, optional arguments can b passed in a list, as long as they are recognized by Pandoc.

In addition to image format conversion, images can be resized using `configure(resize=INTEGER)` as a percent of the input image size, and converted to grayscale using `configure(grayscale=True)`.

#### PDF output
Pandoc cannot export to PDF format directly, but rather does so by first converting to LaTeX. Although other PDF engines are supported by Pandoc, LaTeX (`--pdf-engine pdflatex`) is the default, and is recommended for most applications. Pandoc also requires a variety of packages to be available to LaTeX, most of which are included with recent TeX Live releases (see Pandoc documentation for details).
Alternatively, users can export a LaTeX (.tex) file and convert it using custom typesetters.

#### Table of contents rendering
A table of contents can be generated and included in the output by setting the TOC depth to 1 or greater (limited to 6), or disabled with the default value of 0. The depth setting determines what level of heading to include in the table. For example, `configure(toc=3)` will include level 1, 2 and 3 headings in the output TOC.
The output TOC is not populated for some formats (latex, context, docx, odt, opendocument, rst, and ms) where only an instruction to insert a TOC is given. The TOC is not supported for man, docbook4, docbook5 and jats.

#### Citation rendering
To render citations in the document, **Panuscript** must be configured `configure(citations=True)`. In text citations can be linked to the corresponding reference item using `configure(linkcites=True)`. Link citations assumes that the entry `link-citations: true` exists in the document's YAML metadata block. The `embed_yaml_bib()` function can be used to ensure that the YAML metadata contains `link-citations: true`.
  * A bibliography file from a supported format can be specified using `configure(citations=True, biblo='path/to/file')`. For convenience, the bibliography can be embedded into a document file using `embed_yaml_bib()` to reduce the number of files. If citations are enabled and no bibliography file is specified, the bibliography is assumed to be included in the `references:` field of the document's YAML metadata.
  * Similarly, a Citation Style Language (CSL) file can be specified using `configure(citations=True, csl='path/to/file')`. If no CSL is specified the citation style will default to Chigaco. CSL files for all specified citation formats can be obtained from the `fetch_csl()` function, which will attempt to download the given style from the official repository. An optional `dir=` argument can be used to place the file in the working directory, else, the file if written to the 'csls' folder.
