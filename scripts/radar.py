#!/usr/bin/env python3
"""Validate canonical RADAR data or export it. Python 3, no dependencies."""
import argparse
import datetime
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1] / 'data/radar'


def check(value, schema, path='$'):
    def require(condition, message):
        if not condition:
            raise ValueError(f'{path}: {message}')
    if 'const' in schema:
        require(type(value) is type(schema['const']) and value == schema['const'], 'invalid constant')
    if 'enum' in schema:
        require(value in schema['enum'], 'invalid enum value')
    kind = schema.get('type')
    if kind:
        require(isinstance(value, {'object': dict, 'array': list, 'string': str}[kind]), f'expected {kind}')
    if kind == 'object':
        require(all(key in value for key in schema.get('required', [])), 'missing required fields')
        props = schema.get('properties', {})
        if schema.get('additionalProperties') is False:
            require(not set(value) - set(props), 'unknown fields')
        for key in value.keys() & props.keys():
            check(value[key], props[key], f'{path}.{key}')
    elif kind == 'array':
        require(len(value) >= schema.get('minItems', 0), 'too few items')
        for i, item in enumerate(value):
            check(item, schema['items'], f'{path}[{i}]')
    elif kind == 'string':
        require(len(value.strip()) >= schema.get('minLength', 0), 'empty string')
        if 'pattern' in schema:
            require(re.search(schema['pattern'], value), 'invalid pattern')
        if schema.get('format') == 'date':
            require(re.fullmatch(r'\d{4}-\d{2}-\d{2}', value), 'expected YYYY-MM-DD')
            datetime.date.fromisoformat(value)


def load(root=ROOT):
    read = lambda path: json.loads(path.read_text(encoding='utf-8'))
    index = read(root / 'index.json')
    ids = index['projects']
    if index['schema_version'] != 1 or not ids or len(ids) != len(set(ids)) or any(not re.fullmatch('[a-z][a-z0-9-]*', id) for id in ids):
        raise ValueError('Invalid project index')
    if set(ids) != {p.stem for p in (root / 'projects').glob('*.json')}:
        raise ValueError('Index and project files differ')
    schema = read(root / 'project.schema.json')
    projects = []
    for id in ids:
        p = read(root / 'projects' / f'{id}.json')
        check(p, schema, id)
        if p['id'] != id:
            raise ValueError(f'{id}: filename/id mismatch')
        if any(d['project'] not in ids or d['project'] == id for d in p['dependencies']):
            raise ValueError(f'{id}: invalid dependency')
        dates = [c['date'] for c in p['changelog']]
        if dates != sorted(dates) or dates[-1] != p['updated_at']:
            raise ValueError(f'{id}: changelog must be chronological and end at updated_at')
        queue = p['extensions'].get('print_queue', [])
        if len({item['id'] for item in queue}) != len(queue):
            raise ValueError(f'{id}: duplicate queue ids')
        projects.append(p)
    return dict(schema_version=1, projects=projects, context=read(root / 'context.json'))


def markdown(data):
    lines = ['# RADAR', '']
    for p in data['projects']:
        lines += [f"## {p['codename']} — {p['name']}", '']
        for key, value in p.items():
            if key == 'context_markdown':
                lines += ['### Contesto snapshot (storico)', value, '']
            else:
                lines += [f'### {key}', '```json', json.dumps(value, ensure_ascii=False, indent=2), '```', '']
    lines += ['## Contesto condiviso', '```json', json.dumps(data['context'], ensure_ascii=False, indent=2), '```']
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['validate', 'export'])
    parser.add_argument('--format', choices=['json', 'markdown'], default='json')
    args = parser.parse_args()
    try:
        data = load()
        if args.command == 'validate':
            print(f"RADAR valido: {len(data['projects'])} progetti")
        else:
            print(markdown(data) if args.format == 'markdown' else json.dumps(data, ensure_ascii=False, indent=2))
    except (ValueError, KeyError, OSError, TypeError) as error:
        print(f'RADAR: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
