import re

class MarkdownToConfluenceConverter:
    def __init__(self, markdown_text):
        self.markdown_text = markdown_text

    def convert(self):
        try:
            self.process_headers()
            self.process_code_blocks()
            self.process_inline_code()
            self.process_lists()
            self.process_bold_and_italic()  # Combined method for bold and italic
            self.process_strikethrough()
            self.process_links()
            self.process_images()
            self.process_horizontal_rules()
            self.process_blockquotes()
            self.process_tables()
            self.cleanup_lists()
            self.process_notes_warnings()
            return self.markdown_text.strip()
        except Exception as err:
            raise err

    def process_headers(self):
        def replace_header(match):
            level = len(match.group(1))
            title = match.group(2)
            if level == 1:
                return f'{{panel:title={title}|borderStyle=solid|borderColor=#ccc|titleBGColor=#f7f7f7|titleColor=#333|bgColor=#fff}}\n\n'
            return f'h{level}. {title}\n\n'
        
        self.markdown_text = re.sub(r'^(#{1,6}) (.+)$', replace_header, self.markdown_text, flags=re.MULTILINE)

    def process_code_blocks(self):
        def replace_code_block(match):
            lang = match.group(1) or ''
            code = match.group(2)
            return f'{{code:language={lang}|theme=Midnight}}\n{code}\n{{code}}\n\n'
        
        self.markdown_text = re.sub(r'```(\w*)\n(.*?)```', replace_code_block, self.markdown_text, flags=re.DOTALL)

    def process_inline_code(self):
        self.markdown_text = re.sub(r'`([^`\n]+)`', r'{{{\1}}}', self.markdown_text)

    def process_lists(self):
        def replace_nested_list(match):
            content = match.group(0)
            lines = content.split('\n')
            result = []
            for line in lines:
                indent = len(line) - len(line.lstrip())
                bullet = '*' if line.lstrip().startswith('-') else '#'
                text = line.lstrip().lstrip('- ').lstrip('1234567890. ')
                result.append(f"{' ' * (indent // 2)}{bullet} {text}")
            return '\n'.join(result)
        
        self.markdown_text = re.sub(r'(^|\n)(( {2})*[-*] .+\n?)+', replace_nested_list, self.markdown_text)
        self.markdown_text = re.sub(r'(^|\n)(( {2})*\d+\. .+\n?)+', replace_nested_list, self.markdown_text)

    def process_bold_and_italic(self):
        # First, temporarily replace bold with a unique marker
        self.markdown_text = re.sub(r'\*\*(.+?)\*\*', r'__BOLD__\1__BOLD__', self.markdown_text)
        
        # Process single asterisks for italics
        self.markdown_text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'_\1_', self.markdown_text)
        
        # Replace the bold markers back with Confluence bold syntax
        self.markdown_text = re.sub(r'__BOLD__(.+?)__BOLD__', r'*\1*', self.markdown_text)

    def process_strikethrough(self):
        self.markdown_text = re.sub(r'~~(.+?)~~', r'-\1-', self.markdown_text)

    def process_links(self):
        def replace_plain_url(match):
            url = match.group(0)
            title = url.split('/')[-1].replace('+', ' ')
            return f'[{title}|{url}]'
        
        self.markdown_text = re.sub(r'(?<!\[)https?://\S+(?!\])', replace_plain_url, self.markdown_text)

    def process_images(self):
        self.markdown_text = re.sub(r'!\[(.+?)\]\((.+?)\)', r'!\2|alt=\1!', self.markdown_text)

    def process_horizontal_rules(self):
        self.markdown_text = re.sub(r'^-{3,}$', r'----', self.markdown_text, flags=re.MULTILINE)

    def process_blockquotes(self):
        self.markdown_text = re.sub(r'^> (.+)$', r'bq. \1', self.markdown_text, flags=re.MULTILINE)

    def process_tables(self):
        def replace_table(match):
            table = match.group(0)
            rows = table.strip().split('\n')
            header = rows[0]
            body = rows[2:]

            # Process header
            header_cells = [cell.strip() for cell in header.split('|')[1:-1]]
            confluence_header = '||' + '||'.join(header_cells) + '||'

            # Process body
            confluence_body = []
            for row in body:
                cells = [cell.strip() for cell in row.split('|')[1:-1]]
                confluence_body.append('|' + '|'.join(cells) + '|')

            return confluence_header + '\n' + '\n'.join(confluence_body)

        self.markdown_text = re.sub(r'\|.+\|\n\|[-:|\s]+\|\n(\|.+\|\n)+', replace_table, self.markdown_text)

    def cleanup_lists(self):
        def remove_empty_lines_between_numbered_items(text):
            lines = text.split('\n')
            result = []
            in_list = False

            for i, line in enumerate(lines):
                stripped_line = line.strip()
                if stripped_line.startswith('#'):
                    if in_list and result[-1].strip() == '':
                        result.pop()
                    result.append(line)
                    in_list = True
                elif stripped_line:
                    result.append(line)
                    in_list = False
                elif not in_list or (i < len(lines) - 1 and not lines[i + 1].strip().startswith('#')):
                    result.append(line)

            return '\n'.join(result)

        self.markdown_text = remove_empty_lines_between_numbered_items(self.markdown_text)

    def process_notes_warnings(self):
        self.markdown_text = re.sub(r'> \*\*Note:\*\* (.+)', r'{note}\1{note}', self.markdown_text)
        self.markdown_text = re.sub(r'> \*\*Warning:\*\* (.+)', r'{warning}\1{warning}', self.markdown_text)


