"""Context pose selection and fail-before-write checks; inputs never touch production assets."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from tools.assets.compile_rigs import CHARACTERS, compile_rigs

ROOT = Path(__file__).resolve().parents[2]


class CompileContexts(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.assets = Path(self.temp.name) / 'assets'
        self.namespace = self.assets / 'PopSpireWomen'
        # Existing fully authored rig is read-only input, never overwritten.
        self.rig = json.loads((ROOT/'mod/assets/PopSpireWomen/art/ironclad/rig.json').read_text())
        for character in CHARACTERS:
            folder = self.namespace/'art'/character
            folder.mkdir(parents=True)
            (folder/'rig.json').write_text(json.dumps(self.rig))
        self.overrides = Path(self.temp.name)/'overrides.json'
        self.overrides.write_text('{"schema":1,"characters":{}}')

    def write(self, name, surface, rig):
        (self.namespace/'art'/name/f'{surface}_rig.json').write_text(json.dumps(rig))

    def test_independent_pose_and_context_do_not_bleed_between_surfaces(self):
        merchant = deepcopy(self.rig)
        merchant.update(body='res://PopSpireWomen/art/ironclad/merchant_body.png',
                        surface='merchant', motion_profile='contextual_v02')
        merchant['markers']['hand_l'] = [123,456]
        self.write('ironclad','merchant',merchant)
        rest = deepcopy(self.rig)
        rest['body'] = 'res://PopSpireWomen/art/ironclad/rest_body.png'
        self.write('ironclad','rest',rest)
        receipts = compile_rigs(self.assets,self.overrides)
        root = self.namespace/'rigs/ironclad'
        output = {s:json.loads((root/f'{s}.json').read_text()) for s in ['combat','merchant','select','rest']}
        self.assertEqual(output['merchant']['body'],merchant['body'])
        self.assertEqual(output['merchant']['markers']['hand_l'],[123,456])
        self.assertEqual(output['merchant']['motion_profile'],'contextual_v02')
        for s in ['combat','select']:
            self.assertEqual(output[s]['body'],self.rig['body'])
            self.assertEqual(output[s]['markers'],self.rig['markers'])
            self.assertEqual(output[s]['surface'],s)
        self.assertEqual(output['rest']['body'],rest['body'])
        self.assertEqual(len(receipts),16)
        self.assertFalse((self.namespace/'rigs/silent/rest.json').exists())
        self.assertEqual(next(r for r in receipts if r['character']=='ironclad' and r['surface']=='merchant')['source_kind'],'surface')

    def test_all_twenty_current_rigs_still_compile_with_current_overrides(self):
        # Snapshot only the JSON authoring inputs; avoid writing parent's generated rigs.
        import shutil
        for source in (ROOT/'mod/assets/PopSpireWomen/art').glob('*/*rig.json'):
            shutil.copyfile(source,self.namespace/'art'/source.parent.name/source.name)
        receipts = compile_rigs(self.assets,ROOT/'tools/assets/rig-overrides.json')
        self.assertEqual(len(receipts),20)
        for receipt in receipts:
            selection = receipt['surface'] == 'select'
            self.assertEqual(receipt['motion_profile'], 'legacy_v01' if selection else 'contextual_v02')
            self.assertEqual(receipt['source_kind'], 'legacy_default' if selection else 'surface')

    def test_bad_present_source_never_falls_back_or_partially_rewrites(self):
        for patch in [{'schema':2},{'surface':'combat'},{'motion_profile':'typo'},
                      {'body':'res://PopSpireWomen/../../outside.png'}, {'markers':{}},
                      {'canvas':[float('nan'),1536]}]:
            with self.subTest(patch=patch):
                rig=deepcopy(self.rig); rig.update(patch)
                self.write('defect','merchant',rig)
                with self.assertRaises(ValueError): compile_rigs(self.assets,self.overrides)
                self.assertFalse((self.namespace/'rigs').exists())

    def test_symlink_input_and_output_refused(self):
        rig_path=self.namespace/'art/silent/merchant_rig.json'
        rig_path.symlink_to(self.namespace/'art/silent/rig.json')
        with self.assertRaises(ValueError): compile_rigs(self.assets,self.overrides)
        rig_path.unlink()
        destination=Path(self.temp.name)/'foreign'
        destination.mkdir()
        (self.namespace/'rigs').symlink_to(destination,target_is_directory=True)
        with self.assertRaises(ValueError): compile_rigs(self.assets,self.overrides)
        self.assertEqual(list(destination.iterdir()),[])


if __name__ == '__main__': unittest.main()
