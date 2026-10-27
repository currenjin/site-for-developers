"""Exact-source, offline localization for the README catalogue and HTML shell.

The English cache is deliberately private build input. Cache misses (including
invalid values) keep the original text visible and are reported, not guessed.
"""
import copy
import html
import json
from pathlib import Path
import re

HANGUL = re.compile(r'[\u1100-\u11ff\u3130-\u318f\ua960-\ua97f\uac00-\ud7af\ud7b0-\ud7ff]')
PLACEHOLDER = re.compile(r'\{\{([A-Za-z_][A-Za-z0-9_]*)\}\}')
RESERVED = {'lang', 'canonical_url', 'alternate_ko_url', 'alternate_en_url',
            'asset_prefix', 'locale_switch_href', 'locale_switch_lang'}


def needs_translation(text):
    return bool(HANGUL.search(text))


def read_json(path):
    path = Path(path)
    if path.is_symlink():
        raise ValueError('Unsafe localization input: ' + str(path))
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        raise ValueError('Invalid localization JSON: ' + str(path)) from exc


def load_translations(path):
    path = Path(path)
    if not path.exists() and not path.is_symlink():
        return {}
    translations = read_json(path)
    if not isinstance(translations, dict):
        raise ValueError('English cache must be a flat source-to-translation object')
    return translations


def translated(text, translations):
    if not needs_translation(text):
        return text, False
    value = translations.get(text)
    if not isinstance(value, str) or not value.strip() or needs_translation(value):
        return text, True
    return value, False


def translation_status(data, translations):
    pending = set()
    resources = categories = 0
    for resource in data['resources']:
        missing = [resource[key] for key in ('name', 'description')
                   if translated(resource[key], translations)[1]]
        pending.update(missing)
        resources += bool(missing)
    for category in data['categories']:
        if translated(category['name'], translations)[1]:
            pending.add(category['name'])
            categories += 1
    return {'pendingStrings': sorted(pending), 'pendingResources': resources,
            'pendingCategories': categories}


def localize_catalogue(data, locale, translations, ui):
    if locale not in ('ko', 'en'):
        raise ValueError('Unsupported locale: ' + locale)
    result = copy.deepcopy(data)
    result['locale'] = locale
    result['ui'] = copy.deepcopy(ui)
    result['translationStatus'] = translation_status(data, translations)
    for resource in result['resources']:
        aliases = []
        untranslated = []
        for key in ('name', 'description'):
            original = resource[key]
            value, pending = translated(original, translations)
            if locale == 'en':
                resource['original' + key.capitalize()] = original
                resource[key] = value
                if pending:
                    untranslated.append(key)
                if original:
                    aliases.append(original)
            elif value and not pending:
                aliases.append(value)
        resource['searchAliases'] = list(dict.fromkeys(aliases))
        if locale == 'en':
            resource['untranslatedFields'] = untranslated
    for category in result['categories']:
        original = category['name']
        value, pending = translated(original, translations)
        if locale == 'en':
            category.update(name=value, originalName=original, untranslated=pending)
            category['searchAliases'] = [original] if original else []
        else:
            category['searchAliases'] = [value] if value and not pending else []
    return result


def load_ui(path):
    ui = read_json(path)
    if not isinstance(ui, dict) or set(ui) != {'ko', 'en'}:
        raise ValueError('UI must contain exactly ko and en locale objects')
    for locale, values in ui.items():
        if not isinstance(values, dict) or not values:
            raise ValueError('Missing UI dictionary: ' + locale)
        if any(not isinstance(key, str) or not isinstance(value, str)
               for key, value in values.items()):
            raise ValueError('UI keys and values must be strings')
        if RESERVED.intersection(values):
            raise ValueError('UI keys conflict with reserved template context')
    if set(ui['ko']) != set(ui['en']):
        raise ValueError('UI locale key coverage differs')
    return ui


def render_template(template, locale, ui, site_url):
    if locale not in ('ko', 'en'):
        raise ValueError('Unsupported locale: ' + locale)
    # Reject malformed/unresolved template syntax before creating any artifacts.
    remainder = PLACEHOLDER.sub('', template)
    if '{{' in remainder or '}}' in remainder:
        raise ValueError('Malformed HTML template placeholder')
    context = dict(ui)
    context.update(lang=locale, canonical_url=site_url + ('en/' if locale == 'en' else ''),
                   alternate_ko_url=site_url, alternate_en_url=site_url + 'en/',
                   asset_prefix='../' if locale == 'en' else '',
                   locale_switch_href='../' if locale == 'en' else 'en/',
                   locale_switch_lang='ko' if locale == 'en' else 'en')
    missing = set(PLACEHOLDER.findall(template)) - set(context)
    if missing:
        raise ValueError('Missing UI/template keys: ' + ', '.join(sorted(missing)))
    return PLACEHOLDER.sub(lambda match: html.escape(context[match[1]], quote=True), template)
