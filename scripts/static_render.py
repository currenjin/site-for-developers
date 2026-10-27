"""Escaped, dependency-free initial HTML matching app.js's card DOM."""
import html
import json
from urllib.parse import urlsplit


def render_cards(data):
    escape = lambda value: html.escape(str(value), quote=True)
    categories = {c['id']: c for c in data['categories']}
    english = data['locale'] == 'en'
    cards = []
    for resource in data['resources']:
        url = resource['url']
        parsed = urlsplit(url)
        if parsed.scheme not in ('http', 'https') or not parsed.netloc or parsed.username or parsed.password or any(c.isspace() or c == '\\' for c in url):
            raise ValueError('Unsafe resource URL: ' + url)
        pending = resource.get('untranslatedFields', []) if english else []
        title_lang = ' lang="ko"' if 'name' in pending else ''
        description_lang = ' lang="ko"' if 'description' in pending else ''
        path = ' / '.join('<span' + (' lang="ko"' if english and categories[c].get('untranslated') else '') + '>' + escape(categories[c]['name']) + '</span>' for c in resource['categoryPath'])
        description = '<p' + description_lang + '>' + escape(resource['description']) + '</p>' if resource['description'] else ''
        badge = '<span class="original-badge">' + escape(data['ui']['korean_original']) + '</span>' if pending else ''
        labels = '<span class="labels">' + ''.join('<span class="label">' + escape(label) + '</span>' for label in resource['labels']) + '</span>' if resource['labels'] else ''
        cards.append('<article class="resource" data-id="' + escape(resource['id']) + '"><a href="' + escape(url) + '" target="_blank" rel="noopener noreferrer"><div class="resource-top"><h3' + title_lang + '>' + escape(resource['name']) + '</h3><span class="outbound" aria-hidden="true">↗</span></div>' + description + '<div class="resource-meta"><span class="resource-path">' + path + '</span>' + badge + labels + '</div></a></article>')
    return ''.join(cards)


def structured_data(locale, site_url, title, description):
    canonical = site_url + ('en/' if locale == 'en' else '')
    graph = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'WebSite', '@id': site_url + '#website', 'url': site_url, 'name': 'Site for Developers'},
        {'@type': 'CollectionPage', '@id': canonical + '#collection', 'url': canonical,
         'name': title, 'description': description, 'inLanguage': locale,
         'isPartOf': {'@id': site_url + '#website'}}]}
    # Script-data is not HTML text: JSON escapes prevent an embedded closing tag.
    return json.dumps(graph, ensure_ascii=True, separators=(',', ':')).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')


def render_snapshot(page, data, site_url):
    count = len(data['resources'])
    status = data['ui']['result_count'].format(count=count, total=count)
    page = page.replace('<div id="results" class="results"></div>', '<div id="results" class="results">' + render_cards(data) + '</div>')
    page = page.replace('<span id="category-total"></span>', '<span id="category-total">' + str(len(data['categories'])) + '</span>')
    page = page.replace('>' + html.escape(data['ui']['loading']) + '</p>', '>' + html.escape(status) + '</p>', 1)
    script = '<script type="application/ld+json">' + structured_data(data['locale'], site_url, data['ui']['page_title'], data['ui']['meta_description']) + '</script>'
    page = page.replace('<body ', '<body data-static-load-error="' + html.escape(data['ui']['static_load_error'], quote=True) + '" ', 1)
    return page.replace('</head>', script + '</head>', 1)
