"""Sensitivity checks against disposable copies; never changes input/."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from audit_architecture import audit


class AuditSensitivity(unittest.TestCase):
    def setUp(self):
        self.workspace = Path(__file__).resolve().parent
        self.temp = tempfile.TemporaryDirectory(prefix='audit-test-', dir=self.workspace)
        self.root = Path(self.temp.name).resolve()
        self.assertTrue(self.root.is_relative_to(self.workspace))
        self.base = self.root / 'input'
        shutil.copytree(self.workspace / 'input', self.base)
        self.manifest = self.workspace / 'MANIFEST.json'

    def tearDown(self):
        # Confirm containment before recursive temporary-directory cleanup.
        self.assertTrue(self.root.is_relative_to(self.workspace))
        self.temp.cleanup()

    def check_failure(self, code):
        result = audit(self.base, self.manifest)
        self.assertEqual(result['accounting_status'], 'FAIL')
        self.assertIn(code, {i['code'] for i in result['inconsistencies']})

    def test_supplied_packet(self):
        result = audit(self.base, self.manifest)
        self.assertEqual(result['inconsistencies'], [])
        self.assertEqual(result['counts']['turns'], result['counts']['snapshots'])
        self.assertEqual(result['counts']['turns'], 232)
        self.assertEqual(result['groups']['R2 maintenance']['manifests'], 72)
        self.assertTrue(result['workspace_byte_integrity'].startswith('NOT_VERIFIABLE'))

    def test_missing_direct_stage_manifest(self):
        (self.base / 'runs/R2-F01-direct-A-r1-maintenance/stages/01-C1/manifest.json').unlink()
        self.check_failure('snapshot_cardinality')

    def test_changed_manifest_bytes(self):
        path = self.base / 'runs/F01-C1-V01-r1/final/manifest.json'
        path.write_bytes(path.read_bytes() + b'\n')
        self.check_failure('layout_manifest_hash_mismatch')

    def test_episode_aggregate_disagreement(self):
        path = self.base / 'runs/F01-C1-V01-r1/episode.json'
        doc = json.loads(path.read_text())
        doc['native']['turn_id'] = 'altered-turn'
        path.write_text(json.dumps(doc), encoding='utf-8')
        self.check_failure('aggregate_episode_mismatch')

    def test_unreferenced_snapshot(self):
        extra = self.base / 'runs/extra/final'
        extra.mkdir(parents=True)
        shutil.copyfile(self.base / 'runs/F01-C1-V01-r1/final/manifest.json', extra / 'manifest.json')
        self.check_failure('orphan_snapshot_manifest')


if __name__ == '__main__':
    unittest.main(verbosity=2)
