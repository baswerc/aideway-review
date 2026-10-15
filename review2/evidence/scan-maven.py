"""Read-only advisory lookup for locked Maven coordinates. Sends package names only."""
import concurrent.futures
import json
import pathlib
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = pathlib.Path(__file__).resolve().parent
packages = {}
for lock in (ROOT / 'projects/aideway').rglob('*gradle.lockfile'):
    for line in lock.read_text().splitlines():
        if line.startswith('#') or '=' not in line:
            continue
        bits = line.split('=', 1)[0].split(':')
        if len(bits) == 3:
            name = ':'.join(bits[:2])
            packages.setdefault((name, bits[2]), []).append(str(lock.relative_to(ROOT)))

def query(item):
    (name, version), locks = item
    payload = {'package': {'name': name, 'ecosystem': 'Maven'}, 'version': version}
    req = urllib.request.Request('https://api.osv.dev/v1/query', data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            result = json.load(response)
        return {'name': name, 'version': version, 'locks': locks, 'result': result}
    except Exception as error:
        return {'name': name, 'version': version, 'locks': locks, 'error': str(error)}

with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
    result = list(pool.map(query, sorted(packages.items())))
(OUT / 'maven-osv.json').write_text(json.dumps(result, indent=2))
print(json.dumps({'packages': len(result), 'errors': sum('error' in x for x in result), 'affectedPackages': sum(bool(x.get('result', {}).get('vulns')) for x in result)}))
