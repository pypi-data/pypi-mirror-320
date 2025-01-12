# Convert to Confluence Wiki Formate

## Overview

The `convert_to_confluence_wiki` package is a utility for converting Markdown text into a format compatible with Atlassian Confluence. It handles the transformation of various Markdown elements into their Confluence equivalents, making it easier to migrate or integrate content into Confluence pages.

## Features

- Converts headers (`#`, `##`, etc.) into Confluence headers and panels.
- Transforms code blocks and inline code into Confluence code macros.
- Processes nested and numbered lists for proper indentation and syntax.
- Converts bold, italic, and strikethrough text.
- Replaces Markdown-style links and images with Confluence-compatible formats.
- Handles tables, blockquotes, and horizontal rules.
- Provides support for Confluence-specific macros like notes and warnings.
- Ensures clean and well-structured formatting by removing unnecessary empty lines.

## Requirements

- Python 3.6+

## Usage

1. Place the `convert_to_confluence.py` script in your project directory.
2. Import the `markdown_to_confluence` function into your Python script:

```python
from .convert_to_confluence import MarkdownToConfluenceConverter
```

3. Pass your Markdown text to the function:

```python
markdown_text = """
# Sample Header

This is a **bold text** and this is _italic text_.

- Item 1
  - Sub-item 1.1

```python
print("Hello, World!")
# add stoping statement also(i.e. ```)

"""

converter = MarkdownToConfluenceConverter(markdown_text)
confluence_text = converter.convert()
print(confluence_text)
```

4. The output will be formatted for Confluence.

## Example Output

Input Markdown:

```markdown
# Header 1

This is **bold** and _italic_ text.

- Item 1
  - Sub-item 1.1

#Added as comment for readme ```
python
print("Hello, World!")
#Added as comment for readme ```

![Alt Text](image.png)
```

Converted Confluence Markup:

```
h1. Header 1

This is *bold* and _italic_ text.

* Item 1
** Sub-item 1.1

{code:language=python|theme=Midnight}
print("Hello, World!")
{code}

!image.png|alt=Alt Text!
```


## Limitations

- Custom Markdown extensions or non-standard syntax may not be fully supported.
- The script assumes well-formed Markdown input; malformed Markdown may lead to unexpected results.

## License

This script is open-source and can be modified as needed for personal or commercial use.

## Contributing

Contributions are welcome! Feel free to submit pull requests or open issues for bugs or feature requests.

## Contact
Email: aryamangurjar6@gmail.com

Github: https://github.com/AryamanGurjar

Linkedin: https://www.linkedin.com/in/aryaman-gurjar-251ab2201/


