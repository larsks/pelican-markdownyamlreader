'''
This is a reader for Markdown files with YAML metadata, such as those used
with [Jekyll][], the formatter used with [GitHub Pages][].  For example:

    ---
    layout: post
    title: Blogging Like a Hacker
    ---

    This is my blog post.

[jekyll]: http://jekyllrb.com/docs/frontmatter/
[github pages]: https://pages.github.com/
'''

import datetime

from markdown import Markdown
from pelican.readers import BaseReader, METADATA_PROCESSORS
from pelican.contents import Category, Tag, Author
from pelican.utils import get_date, pelican_open


class MarkdownYAMLReader(BaseReader):
    """Reader for Markdown files"""

    enabled = bool(Markdown)
    file_extensions = ['md', 'markdown', 'mkd', 'mdown']

    def __init__(self, *args, **kwargs):
        super(MarkdownYAMLReader, self).__init__(*args, **kwargs)
        self.metadata_processors = METADATA_PROCESSORS
        self.metadata_processors.update({
            'date': self.parse_date,
            'modified': self.parse_date,
            'tags': lambda x, y: [Tag(tag, y) for tag in x],
            'category': Category,
            'author': Author,
            'authors': lambda x, y: [Author(author) for author in x],
        })

    def parse_date(self, dateval, settings):
        if isinstance(dateval, datetime.date):
            return datetime.datetime.combine(
                dateval, datetime.datetime.min.time())
        else:
            return get_date(dateval)

    def process_metadata(self, name, value):
        if name in self.metadata_processors:
            value = self.metadata_processors[name](value, self.settings)

        return value

    def _parse_metadata(self, meta):
        """Return the dict containing document metadata"""
        output = {}
        for name, value in meta.items():
            name = name.lower()
            if name == "summary":
                # reset the markdown instance to clear any state
                self._md.reset()
                summary = self._md.convert(value)
                output[name] = self.process_metadata(name, summary)
            else:
                # handle list metadata as list of string
                output[name] = self.process_metadata(name, value)
        return output

    def read(self, source_path):
        """Parse content and metadata of markdown files"""

        self._md = Markdown(extensions=['yamlmd'],
                            **self.settings['MARKDOWN'])
        with pelican_open(source_path) as text:
            content = self._md.convert(text)

        metadata = self._parse_metadata(self._md.Meta)
        return content, metadata
