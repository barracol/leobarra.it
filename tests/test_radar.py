import copy
import datetime
import importlib.util
import json
import pathlib
import tempfile
import unittest
import shutil

spec = importlib.util.spec_from_file_location('radar', pathlib.Path(__file__).resolve().parents[1] / 'scripts/radar.py')
radar = importlib.util.module_from_spec(spec)
spec.loader.exec_module(radar)


class RadarTests(unittest.TestCase):
    def test_migration_and_export(self):
        data = radar.load()
        self.assertEqual(len(data['projects']), 9)
        foundry = next(p for p in data['projects'] if p['id'] == 'foundry')
        self.assertTrue(foundry['extensions']['print_queue'])
        self.assertIn('esp8266-case', [item['id'] for item in foundry['extensions']['print_queue']])
        self.assertIn('97 cm', foundry['context_markdown'])
        self.assertIn('Non comprare organizer', next(p for p in data['projects'] if p['id'] == 'labhub')['context_markdown'])
        exported = radar.markdown(data)
        for p in data['projects']:
            self.assertIn(p['context_markdown'], exported)

    def test_invalid_data_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp) / 'radar'
            shutil.copytree(radar.ROOT, root)
            file = root / 'projects/foundry.json'
            original = json.loads(file.read_text())
            mutations = [lambda p: p.update(status='available'),
                         lambda p: p.update(updated_at='2026-02-30'),
                         lambda p: p['dependencies'].append({'project':'unknown','description':'bad'}),
                         lambda p: p['extensions']['print_queue'].append(p['extensions']['print_queue'][0]),
                         lambda p: p.pop('next_actions'),
                         lambda p: p.update(updated_at='2026-10-07')]
            for mutation in mutations:
                with self.subTest(mutation=mutation):
                    project = copy.deepcopy(original)
                    mutation(project)
                    file.write_text(json.dumps(project))
                    with self.assertRaises(ValueError):
                        radar.load(root)

    def test_network_connections(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp) / 'radar'
            shutil.copytree(radar.ROOT, root)
            file = root / 'projects/backbone.json'
            project = json.loads(file.read_text())
            link = dict(cable_id=None, source_device='soggiorno', source_port=None,
                        destination_device='cantina', destination_port=None,
                        type='ethernet', verification_status='hypothesized')
            project['extensions']['network_inventory']['connections'] = [link]
            file.write_text(json.dumps(project))
            radar.load(root)
            for field, invalid in [('source_device', 'unknown'), ('type', 'other'),
                                   ('verification_status', 'assumed_verified')]:
                bad = copy.deepcopy(project)
                bad['extensions']['network_inventory']['connections'][0][field] = invalid
                file.write_text(json.dumps(bad))
                with self.assertRaises(ValueError):
                    radar.load(root)

    def test_shared_supplies_and_exports(self):
        data = radar.load()
        supplies = data['supplies']
        self.assertEqual(len(supplies['orders']), 1)
        ordered = [i for i in supplies['items'] if i['order_id']]
        self.assertEqual(len(ordered), 6)
        self.assertTrue(all(i['status'] == 'ordered' and i['actual_delivery'] is None for i in ordered))
        calipers = [i for i in supplies['items'] if i['id'] == 'caliper']
        self.assertEqual(len(calipers), 1)
        self.assertEqual(set(calipers[0]['projects']), {'foundry', 'labhub'})
        self.assertIn('supplies', json.loads(json.dumps(data)))
        for exported in (json.dumps(supplies), radar.markdown(data).split('## Acquisti e inventario condivisi')[1]):
            for field in ('cost_eur', 'total_eur', 'budget'):
                self.assertNotIn(field, exported)
        self.assertIn('amazon-2026-10-21', radar.markdown(data))

    def test_supply_integrity_and_partial_delivery(self):
        original = radar.load()['supplies']
        ids = [p['id'] for p in radar.load()['projects']]
        mutations = [
            lambda d: d['orders'].append(copy.deepcopy(d['orders'][0])),
            lambda d: d['items'].append(copy.deepcopy(d['items'][0])),
            lambda d: d['items'][0].update(order_id='missing'),
            lambda d: d['items'][0].update(projects=['missing']),
            lambda d: d['items'][0].update(status='received'),
            lambda d: d['items'][0].update(actual_delivery='2026-10-23'),
            lambda d: d['items'][0].update(expected_delivery='2026-02-30'),
            lambda d: d['items'][0].update(quantity=-1),
            lambda d: d['items'][0].update(cost_eur=1),
            lambda d: d['orders'][0].update(total_eur=1),
            lambda d: d['items'][0].update(budget=1),
            lambda d: d['orders'][0].update(status='received'),
        ]
        for mutation in mutations:
            data = copy.deepcopy(original)
            mutation(data)
            with self.assertRaises(ValueError):
                radar.validate_supplies(data, ids)
        data = copy.deepcopy(original)
        data['items'][0].update(status='received', actual_delivery='2026-10-23')
        data['orders'][0]['status'] = 'partially_received'
        radar.validate_supplies(data, ids)
        for item in data['items']:
            if item['order_id']:
                item.update(status='received', actual_delivery='2026-10-23')
        data['orders'][0]['status'] = 'received'
        radar.validate_supplies(data, ids)

    def test_project_update_and_extension(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp) / 'radar'
            shutil.copytree(radar.ROOT, root)
            file = root / 'projects/foundry.json'
            project = json.loads(file.read_text())
            next(item for item in project['extensions']['print_queue'] if item['id'] == 'esp8266-case')['status'] = 'done'
            project['extensions']['custom'] = {'example': [1, 2]}
            project['completed'].append('Case ESP8266 stampato')
            project['updated_at'] = (datetime.date.fromisoformat(project['updated_at']) + datetime.timedelta(days=1)).isoformat()
            project['changelog'].append({'date':project['updated_at'],'text':'Case ESP8266 stampato'})
            file.write_text(json.dumps(project))
            data = radar.load(root)
            updated = next(p for p in data['projects'] if p['id'] == 'foundry')
            self.assertEqual(updated['status'], 'in_progress')
            self.assertEqual(next(item for item in updated['extensions']['print_queue'] if item['id'] == 'esp8266-case')['status'], 'done')


if __name__ == '__main__':
    unittest.main()
