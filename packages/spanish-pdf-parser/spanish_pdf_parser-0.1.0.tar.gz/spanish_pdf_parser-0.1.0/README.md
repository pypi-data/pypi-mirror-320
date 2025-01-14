# PDF Section Parser

A Python package for automatically detecting and extracting headers, body text, and footers from PDF documents. The package supports multiple languages and provides both visual boundary detection and structured text extraction.

## Features

- 📄 Automatic detection of headers, footers, and body sections in PDF documents
- 🌍 Multi-language support 
- 🎯 Precise boundary detection for consistent text extraction
- 📊 JSON output with structured content
- 👁️ Visual PDF output showing detected boundaries
- 📁 Process single files or entire directories
- ⚙️ Flexible configuration options

## Installation

```bash
pip install pdf-section-parser
```

## Quick Start

```python
from pdf_section_parser import PDFSectionParser, ParserConfig

# Use default settings (generate both PDF and JSON)
parser = PDFSectionParser()
parser.parse("path/to/document.pdf")

# Custom configuration
config = ParserConfig(
    generate_boundaries_pdf=True,
    generate_json=True,
    output_dir="custom/output/dir"
)
parser = PDFSectionParser(config)
parser.parse("path/to/pdf/directory")
```

## Command Line Usage

```bash
# Process a single file with default settings
pdf-section-parser single-file.pdf

# Process a directory of PDFs
pdf-section-parser path/to/pdf/directory

# Customize processing options
pdf-section-parser --no-boundaries-pdf path/to/document.pdf

# Get help
pdf-section-parser --help
```

## Configuration Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `generate_boundaries_pdf` | True | Generate PDF with visual boundary markers |
| `generate_json` | True | Generate JSON output with structured content |
| `output_dir` | None | Custom output directory (default: same as input) |

## Output Format

### JSON Output
```json
{
    "pdf_with_lines": "document_final_boundaries.pdf",
    "pages": [
        {
            "number": 1,
            "header": "Header text...",
            "body": "Main content...",
            "footer": "Footer text..."
        }
    ]
}
```

### Visual PDF Output
The package generates a PDF file with colored lines showing detected boundaries:
- 🔵 Blue lines: Header boundaries
- 🟢 Green lines: Bottom footer boundaries
- 🔴 Red lines: Right footer boundaries

## Requirements

- Python 3.8 or higher
- PyMuPDF (1.24.0 or higher)
- PyMuPDF4LLM (0.0.17 or higher)
- tqdm

## Examples

### Process Single File
```python
from pdf_section_parser import PDFSectionParser

parser = PDFSectionParser()
parser.parse("document.pdf")
```

### Process Directory
```python
parser = PDFSectionParser()
parser.parse("path/to/pdf/directory")
```

### Custom Configuration
```python
from pdf_section_parser import PDFSectionParser, ParserConfig

config = ParserConfig(
    generate_boundaries_pdf=False,  # Skip boundary PDF generation
    generate_json=True,            # Generate JSON output
    output_dir="output"           # Custom output directory
)

parser = PDFSectionParser(config)
parser.parse("document.pdf")
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the GNU Affero General Public License v3 (AGPL-3.0).

This program incorporates work covered by the following copyright and permission notices:

PyMuPDF (https://github.com/pymupdf/PyMuPDF)
Copyright (c) 2016-2024 Artifex Software, Inc.
Licensed under GNU Affero General Public License version 3

## Contact

Tamara Orlich - [tamara.orlich@borah.agency]

Project Link: [https://github.com/BorahLabs/spanish_pdf_parser]