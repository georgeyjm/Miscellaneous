# PapaCrawler

A crawler for IGCSE past papers on PapaCambridge.

## Usage

1. Run the program.

```python PapaCambridge.py```

2. Type in the 4-digit course codes you want to crawl, multiple course codes should be separated by a space.  
For example, `0620 0625 0500` will download the past papers for Chemistry (0620), Physics (0625) and English as First Language (0500)

3. Type in the paper numbers you want to crawl, multiple paper numbers should be separated by a space. If you don't input anything, the program will default to download all available papers.  
For example, `1 2 3` will only download all available papers 1, 2 and 3.

4. Type in the document types you want to crawl, multiple document types should be separated by a space. If you don't input anything, the program will default to download `qp`, `ms`, `in` and `pre`, a list of available document types can be found [here](#document-types).  
For example, `qp ms` will only download question papers and mark schemes.

5. Type in the last two digits of the range of years you want to crawl, separated by a dash (`-`). If you don't input anything, the program will default to download papers from any year.  
For example, `08-15` will only download all available papers from 2008 to 2015, inclusive.

6. Wait and enjoy studying!

## Document Types

- **`qp`** - Question paper
- **`ms`** - Mark scheme
- **`in`** - Insert
- **`pre`**, **`pm`** - Pre-release
- **`gt`** - Grade thresholds
- **`er`** - Examiner report
- **`ir`** - Instrument requirements (?)

## Changelog

**2018-04-26:**
- Fix bug where default values won't match any file
- First public release!
