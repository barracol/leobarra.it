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
