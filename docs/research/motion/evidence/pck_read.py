"""Read selected unencrypted GDPC v3 records, validating source MD5. No game writes."""
from pathlib import Path
import hashlib, json, struct, sys

PCK = Path('/mnt/c/Program Files (x86)/Steam/steamapps/common/Slay the Spire 2/SlayTheSpire2.pck')
OUT = Path(__file__).resolve().parent

def index():
    with PCK.open('rb') as f:
        assert f.read(4) == b'GDPC'
        assert struct.unpack('<I', f.read(4))[0] == 3
        f.seek(24)
        base, directory = struct.unpack('<QQ', f.read(16))
        f.seek(directory)
        count = struct.unpack('<I', f.read(4))[0]
        entries = {}
        for _ in range(count):
            n = struct.unpack('<I', f.read(4))[0]
            path = f.read(n).rstrip(b'\0').decode('utf-8')
            offset, size = struct.unpack('<QQ', f.read(16))
            md5 = f.read(16).hex()
            flags = struct.unpack('<I', f.read(4))[0]
            entries[path] = dict(offset=base+offset, size=size, md5=md5, flags=flags)
        return entries

def read(path, entries=None):
    item = (entries or index())[path]
    assert item['flags'] == 0
    with PCK.open('rb') as f:
        f.seek(item['offset'])
        data = f.read(item['size'])
    assert hashlib.md5(data).hexdigest() == item['md5']
    return data

if __name__ == '__main__':
    entries = index()
    if sys.argv[1] == 'index':
        (OUT/'pck-index.json').write_text(json.dumps(entries, indent=2)+'\n')
    elif sys.argv[1] == 'read':
        sys.stdout.buffer.write(read(sys.argv[2], entries))
    elif sys.argv[1] == 'save':
        for path in sys.argv[2:]:
            dest = OUT/'resources'/path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(read(path, entries))
