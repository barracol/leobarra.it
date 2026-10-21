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


def validate_supplies(data, project_ids):
    if data['schema_version'] != 1:
        raise ValueError('Invalid supplies version')
    def date(value):
        if value is not None:
            check(value, {'type': 'string', 'format': 'date'})
    date(data['updated_at'])
    orders = {o['id']: o for o in data['orders']}
    if len(orders) != len(data['orders']):
        raise ValueError('Duplicate order ids')
    items = {i['id']: i for i in data['items']}
    if len(items) != len(data['items']):
        raise ValueError('Duplicate item ids')
    def amount(value):
        if value is not None and (type(value) not in (int, float) or not 0 <= value < float('inf')):
            raise ValueError('Invalid amount')
    for o in orders.values():
        if o['status'] not in ('ordered', 'partially_received', 'received'):
            raise ValueError('Invalid order status')
        date(o['ordered_at'])
        amount(o['total_eur'])
        if not o['store']:
            raise ValueError('Missing store')
    for i in items.values():
        required = {'id', 'name', 'quantity', 'unit', 'category', 'projects', 'status', 'order_id', 'product_url', 'expected_delivery', 'actual_delivery', 'cost_eur', 'notes'}
        if not required <= i.keys() or not i['id'] or not i['name'] or not i['unit']:
            raise ValueError('Missing supply fields')
        if i['status'] not in ('to_evaluate', 'to_buy', 'ordered', 'received', 'in_use', 'excluded'):
            raise ValueError('Invalid supply status')
        if i['category'] not in ('equipment', 'consumable'):
            raise ValueError('Invalid category')
        if not i['projects'] or len(set(i['projects'])) != len(i['projects']) or set(i['projects']) - set(project_ids):
            raise ValueError('Invalid supply project references')
        if i['order_id'] is not None and i['order_id'] not in orders:
            raise ValueError('Unknown order')
        if i['status'] == 'ordered' and (i['order_id'] is None or i['actual_delivery'] is not None):
            raise ValueError('Ordered item must reference order and cannot be delivered')
        if i['order_id'] and i['status'] in ('received', 'in_use') and not i['actual_delivery']:
            raise ValueError('Delivery confirmation required for ordered goods')
        for field in ('expected_delivery', 'actual_delivery'):
            date(i[field])
            if i[field] and i['order_id'] and i[field] < orders[i['order_id']]['ordered_at']:
                raise ValueError('Delivery precedes order')
        amount(i['cost_eur'])
        if i['quantity'] is not None and (type(i['quantity']) not in (int, float) or not 0 < i['quantity'] < float('inf')):
            raise ValueError('Invalid quantity')
        if i['product_url'] is not None and not i['product_url'].startswith('https://'):
            raise ValueError('Product link must use HTTPS')
    for o in orders.values():
        lines = [i for i in items.values() if i['order_id'] == o['id']]
        received = [i for i in lines if i['actual_delivery']]
        expected = 'received' if lines and len(received) == len(lines) else 'partially_received' if received else 'ordered'
        if not lines or o['status'] != expected:
            raise ValueError('Order status inconsistent with deliveries')
    dates = [c['date'] for c in data['changelog']]
    for value in dates:
        date(value)
    if not dates or dates != sorted(dates) or dates[-1] != data['updated_at']:
        raise ValueError('Invalid supplies changelog')
    return data


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
        inventory = p['extensions'].get('network_inventory')
        if inventory is not None:
            refs = [d['ref'] for d in inventory['devices']]
            if len(refs) != len(set(refs)):
                raise ValueError(f'{id}: duplicate network device refs')
            for c in inventory['connections']:
                required = {'cable_id', 'source_device', 'source_port', 'destination_device', 'destination_port', 'type', 'verification_status'}
                if not required <= c.keys():
                    raise ValueError(f'{id}: missing connection fields')
                if c['source_device'] not in refs or c['destination_device'] not in refs:
                    raise ValueError(f'{id}: unknown network endpoint')
                if c['source_device'] == c['destination_device']:
                    raise ValueError(f'{id}: network self-link')
                if c['type'] not in ('ethernet', 'wifi') or c['verification_status'] not in ('verified', 'hypothesized', 'planned'):
                    raise ValueError(f'{id}: invalid connection type/status')
        projects.append(p)
    supplies = validate_supplies(read(root / 'supplies.json'), ids)
    item_ids = {i['id'] for i in supplies['items']}
    for p in projects:
        network = p['extensions'].get('network', {})
        inventory = p['extensions'].get('network_inventory', {})
        for node in network.get('planned_nodes', []) + inventory.get('devices', []):
            if 'supply_item_id' in node and node['supply_item_id'] not in item_ids:
                raise ValueError('Unknown network supply item')
    return dict(schema_version=1, projects=projects, context=read(root / 'context.json'), supplies=supplies)


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
    lines += ['## Acquisti e inventario condivisi', '```json', json.dumps(data['supplies'], ensure_ascii=False, indent=2), '```']
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
