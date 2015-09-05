"""Searches wikipedia and returns first sentence of article
Scaevolus 2009"""
import types
import re
import requests
from yapsy.IPlugin import IPlugin
from lxml import etree

class WikipediaListener(IPlugin):
    def __init__(self):
        super(WikipediaListener, self).__init__()
        self.bot = None
        str_matches = ["wiki", "wikipedia", "w"]
        self._matches = [re.compile(s) for s in str_matches]

    # FIXME: this API is not permenant
    def set_bot(self, bot):
        self.bot = bot

    
    def call(self, regex_command, string_argument, done=None):
        if regex_command in self._matches:
            result = wiki(string_argument)
            if isinstance(done, types.FunctionType):
                done()
            done = True
            return result, done

# security
parser = etree.XMLParser(resolve_entities=False, no_network=True)

api_prefix = "http://en.wikipedia.org/w/api.php"
search_url = api_prefix + "?action=opensearch&format=xml"
random_url = api_prefix + "?action=query&format=xml&list=random&rnlimit=1&rnnamespace=0"

paren_re = re.compile('\s*\(.*\)$')


def wiki(text):
    """wiki <phrase> -- Gets first sentence of Wikipedia article on <phrase>."""

    try:
        request = requests.get(search_url, params={'search': text.strip()})
        request.raise_for_status()
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
        return "Could not get Wikipedia page: {}".format(e)
    x = etree.fromstring(request.text, parser=parser)

    ns = '{http://opensearch.org/searchsuggest2}'
    items = x.findall(ns + 'Section/' + ns + 'Item')

    if not items:
        if x.find('error') is not None:
            return 'Could not get Wikipedia page: %(code)s: %(info)s' % x.find('error').attrib
        else:
            return 'No results found.'

    def extract(item):
        return [item.find(ns + i).text for i in
                ('Text', 'Description', 'Url')]

    title, desc, url = extract(items[0])

    if 'may refer to' in desc:
        title, desc, url = extract(items[1])

    title = paren_re.sub('', title)

    if title.lower() not in desc.lower():
        desc = title + desc

    desc = ' '.join(desc.split())  # remove excess spaces

    return '{} :: {}'.format(desc, requests.utils.quote(url, ':/'))
