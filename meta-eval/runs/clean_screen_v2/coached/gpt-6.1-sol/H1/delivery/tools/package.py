"""Build a manifest-checked ZIP excluding development state and caches."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    names = ['README.md', 'TASK.md', 'REVIEW-RUBRIC.md', 'CONTROLS.md', 'VERIFICATION.md',
             'verification.json', 'clean-verification.json', 'input/E1.md', 'input/README.md',
             'tools/clean_check.py', 'tools/package.py']
    names += [path.relative_to(ROOT).as_posix() for path in (ROOT / 'e1eval').iterdir()
              if path.is_file() and path.suffix in ('.py', '.json')]
    contents = {name: (ROOT / name).read_bytes() for name in sorted(names)}
    manifest = {'schema_version': 'e1-package/v1',
                'sha256': {name: hashlib.sha256(data).hexdigest() for name, data in contents.items()}}
    archive = ROOT / 'e1-eval.zip'
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as output:
        for name, data in contents.items():
            output.writestr(name, data)
        output.writestr('MANIFEST.json', json.dumps(manifest, indent=2) + '\n')
    with zipfile.ZipFile(archive) as packaged:
        assert packaged.testzip() is None
        actual_manifest = json.loads(packaged.read('MANIFEST.json'))
        assert set(packaged.namelist()) == set(contents) | {'MANIFEST.json'}
        for name, digest in actual_manifest['sha256'].items():
            assert hashlib.sha256(packaged.read(name)).hexdigest() == digest, name
    print(json.dumps({'archive': archive.name, 'files': len(contents) + 1,
                      'bytes': archive.stat().st_size, 'manifest_verified': True}))


if __name__ == '__main__':
    main()
