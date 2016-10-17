# -*- coding: utf-8 -*-
import os, unicodedata, re
from lektor.pluginsystem import Plugin
from lektor.build_programs import BuildProgram
from lektor.sourceobj import VirtualSourceObject
from lektor.utils import build_url
from lektor.types import Type
from lektor.db import Page

def slugify(value):
    """Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    see: http://stackoverflow.com/a/295466/3482692
    """
    if isinstance(value, str):
        value = unicode(value, 'utf-8')
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    value = re.sub('[-\s]+', '_', value)
    return value


class DataPagesObject(object):
    def __init__(self, record, items_path, name_key, template):
        self.record = record
        self.items_path = items_path
        self.name_key = name_key
        self.template = template

    @property
    def items(self):
        return self.record.pad.databags.lookup(self.items_path)

    def __iter__(self):
        items = self.items
        assert isinstance(items, list)

        for i, item in enumerate(items):
            name_path = '%s.%s.%s' % (self.items_path, i, self.name_key)
            name = self.record.pad.databags.lookup(name_path)
            assert isinstance(name, basestring)
            yield DataPage(self.record, item, name, self)


class DataPage(VirtualSourceObject):
    def __init__(self, record, item, name, pages):
        VirtualSourceObject.__init__(self, record)
        self.i_want_to_live = self.pad # see: https://github.com/ajdavis/lektor-tags/issues/2
        self.item = item
        self.item_name = name
        self.pages = pages

    def __getitem__(self, name):
        return self.record[name]

    def __getattr__(self, name):
        return getattr(self.record, name)

    @property
    def parent(self):
        return self.record

    @property
    def path(self):
        return build_url([self.record.path, slugify(self.item_name)])

    @property
    def url_path(self):
        return build_url([self.record.url_path, slugify(self.item_name)])


class DataPagesBuildProgram(BuildProgram):
    def produce_artifacts(self):
        self.declare_artifact(
            os.path.join(self.source.url_path, 'index.html'),
            sources=list(self.source.iter_source_filenames()))

    def build_artifact(self, artifact):
        # TODO: put page_item and page_name into context? (may not be necessary)
        artifact.render_template_into(self.source.pages.template,
                                      this=self.source)


class DataPagesDescriptor(object):
    def __init__(self, items_path, name_key, template):
        self.items_path = items_path
        self.name_key = name_key
        self.template = template

    def __get__(self, obj, type=None):
        return DataPagesObject(obj, self.items_path, self.name_key, self.template)


class DataPagesType(Type):
    widget = 'singleline-text'

    def value_from_raw(self, raw):
        assert raw.value.count(',') == 2
        items_path, name_key, template = raw.value.split(',')
        return DataPagesDescriptor(items_path.strip(), name_key.strip(), template.strip())


class DataPagesPlugin(Plugin):
    name = u'data-pages'
    description = u'Traverse databag while creating pages for data'
    url_map = {}

    def on_setup_env(self, **extra):
        self.env.add_type(DataPagesType)
        self.env.add_build_program(DataPage, DataPagesBuildProgram)

        @self.env.urlresolver
        def url_resolver(node, url_path):
            u = build_url([node.url_path] + url_path)
            return DataPagesPlugin.url_map.get(u)

        @self.env.generator
        def generate_pages(source):
            # TODO: allow developer to use any field name (don't hardcode it as "pages")
            if not isinstance(source, Page) or not 'pages' in source:
                return

            pages = source['pages']
            if not isinstance(pages, DataPagesObject):
                return

            for page in pages:
                DataPagesPlugin.url_map[page.url_path] = page
                yield page