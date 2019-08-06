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

The primary way to interact with panuscripy is through the `scripting_interface.py` file. `panuscript.py` is a command line option, and may feature a simply TK gui in the future..

### Scripting Interface

#### Viewing information
Several functions are provided to view information about the underlying software.
  * `get_exe_info()` returns shows the version and other relevant information for the ImageMagick, Pandoc and pandoc-citeproc executables.
  * `supported_formats()` returns a tuple of dictionaries containing supported formats. \[0\] = Pandoc formats, both input and output, \[1]\ = supported bibliographic formats, \[2\] = ImageMagick read/write formats.
  * `pandoc_extensions()` returns  a list of installed Pandoc extensions.

#### Configuring Panuscript
Keyword arguments are passed through the `configure()` function. Only given arguments can change the configuration (i.e., does not revert to default values). Options include:
  * `workdir='path_string'` to set the working directory. Without a working directory, full path names must be given.
  * `verbose=True` to set the verbosity mode. False mode suppresses the STDOUT.
  * `dpi=96` to set the resolution of the output images and applicable documents.
  * `engine='pdflatex'` to set the PDF engine used by Pandoc to output PDF format documents.
  * `citations=False` to set the citation rendering mode. See [below](#####-citation-rendering).
  * `biblio='path_string'` to set the bibliographic file for citation rending.
  * `csl=''` to set the citation style. This can reference a file, or the name of a file in the `/csls` directory. If the style is unrecognized, the CSL official repository will be searched for a style of the same name and automatically downloaded to `/csls`.
  * `linkcites=False` to set the citation linking mode. If true, citations will be linked to the correponding item in the references.
  * `toc=0` to set the table of contents (TOC) depth. Depth refers to the heading level to include in the TOC.
  * `atx_header=False` sets the header mode in markdown and ASCII documents. True for ATX, false for Setext.
  * `preserve_tabs=False` sets the tab preservation mode for literal code blocks. If false, tabs are converted to four (4) spaces
  * `resize_percent=100` sets the image resize value, in percent of the original image size. 100 does not change the image size.
  * `grayscale=False`set grayscale mode during image conversion. If True, images are converted to grayscale using.

Additionally, `pandoc_exe_dir()`, `magick_exe_dir()`, `citeproc_exe_dir()` can be used to set the respective exe path (helpful if no system PATH variable is set).

#### Extracting media
The `extract_media()` function extracts, reads, or downloads images or other media contained in the specified input document to the directory containing the input document. A list of the extracted files is returned to simplify further operations such as format conversion using the `convert_image()` function.

#### Converting images
The `convert_image()` function uses ImageMagick to convert image formats from the input to the output format, as inferred from the file extensions. Through the `configure()` function, grayscale transformations (`configure(grayscale=True)`) and a percent based image resizing (`configure(resize=NUMBER)`) can be applied to the output image.

Optional arguemnts provide the user with the means to further specify the behaviour of the ImageMagick conversion, as long as they are valid arguments for the ImageMagick `convert` program. Additional arugments must be formated as a list, ordered as they would appear in the ImageMagick CLI. For example to apply a median filter of radius 3:
  '''
  args = \['-median', 3\]
  '''

#### Converting documents
The `convert_document()` function uses Pandoc to convert the input file format to another format. The `read` argument (second position) must be a string matching a supported Pandoc input format, thus defining how the input file should be interpreted.  The output format is specified by the `write` argument (third position) from which the extension of the output file is inferred. Valid formats can be viewed from the `supported_formats()` function. Similar to `convert_image()`, a list of optional arguments can be passed as long as they are recognized by Pandoc.

##### PDF output
Pandoc cannot export to PDF format directly, but rather does so by first converting to LaTeX. Although other PDF engines are supported by Pandoc, LaTeX (`--pdf-engine pdflatex`) is the default, and is recommended for most applications. Pandoc also requires a variety of packages to be available to LaTeX, most of which are included with recent TeX Live releases (see Pandoc documentation for details).
Alternatively, users can export a LaTeX (.tex) file and convert it using custom typesetters.

##### Table of contents rendering
A table of contents can be generated and included in the output by setting the TOC depth to 1 or greater (limited to 6), or disabled with the default value of 0. The depth setting determines what level of heading to include in the table. For example, `configure(toc=3)` will include level 1, 2 and 3 headings in the output TOC.
The output TOC is not populated for some formats (latex, context, docx, odt, opendocument, rst, and ms) where only an instruction to insert a TOC is given. The TOC is not supported for man, docbook4, docbook5 and jats.

##### Citation rendering
To render citations in the document, **Panuscript** must be configured `configure(citations=True)`. In text citations can be linked to the corresponding reference item using `configure(linkcites=True)`. Link citations assumes that the entry `link-citations: true` exists in the document's YAML metadata block, if applicable.
  * A bibliography file from a supported format can be specified using `configure(citations=True, biblo='path/to/file')`. If citations are enabled and no bibliography file is specified, the bibliography is assumed to be included in the `references:` field of the document's YAML metadata.
  * Similarly, a Citation Style Language (CSL) file can be specified using `configure(citations=True, csl='path/to/file')`. If no CSL is specified the citation style will default to Chigaco. CSL files for all specified citation formats can be obtained from the `fetch_csl()` function, which will attempt to download the given style from the official repository.

#### Citation cross referencing (markdown format only)
The `xref_md()` function cross references from a markdown document with a bibliography. The bibliography file can be specified with the keyword `bibliography=`, else the bibliography attached to the Panuscript object via `configure()` will be used. This function is useful for identifying missing bibliographic entries.

### Command Line interface

To use Panuscript's command line options run `./ python panuscripy.py function`, where the 'function' is a supported function below. Running it without a function is currently reserved for the GUI, and will not work as intended.

#### Main functions
The first arugment must be the fuction command. The following function commands are recognized:
  * h, -h, help, --help -> Prints help information
  * fetch-csl -> Downloads a citation style language.
  * extract-media -> Extracts media files from an input file.
  * convert-document -> Converts document file formats. Must be configured to render citations.
  * convert-image -> Converts image formats.
  * xref -> Cross references citations from a markdown file with entries from bibliography file.

#### Configuration arguments
Arguments can be placed anywhere after the function command.
The -h or --help flag can also be used after a function command for function additional specific information.
Non-boolean arguments follow a argument=value format.
Boolean arguments without a '-' flag will produce a parsing error.

The following universal arguments are be used to configure Panuscript behaviour:
  * --p-exe= -> Sets the Pandoc executable directory
  * --pc-exe= -> Sets the Pandoc-citeproc executable directory
  * --m-exe= -> Sets the ImageMagick executable directroy
  * --wd= -> Sets the working directory. Avoids the need to specify full paths.
  * -v -> Sets verbose to True
  * --ppi= -> Sets the output resolution in pixels per inch
  * --pdf-engine= -> Sets the pdf engine used for typesetting
  * -citations -> Allows citations where applicable
  * --bib= -> Sets the bibliographic file used for citation rendering
  * --csl= -> Sets the citation style. Defaults to APA. Can specify a file, or a style in the /csls folder.
  * -link-citations -> Hyperlinks in-text citations the the entry in the references
  * --toc-depth= -> Sets the table of contents depth level. 0 turns of TOC rendering.
  * -atx -> Use ATX headers where approriate. Else Setext headers are used.
  * -preserve-tabs -> Preserves tabs while rendering code blocks
  * --resize= -> Sets the percent by which images are resized during conversion
  * -grayscale -> Conversion outputs are in grayscale

#### Example usage
`>> ./python pansuscrupt.py convert-document -v --wd=/path/to/ --input=file.md --read=markdown --write=docx --toc-depth=3 -citations --bib=/path/to/file --csl=apa`
