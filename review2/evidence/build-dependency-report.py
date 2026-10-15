from pathlib import Path
import json, re

root = Path(__file__).resolve().parents[2]
e = root/'review2/evidence'
affected=json.loads((e/'maven-affected.json').read_text())
npm=json.loads((e/'npm-audit.json').read_text())
lock=json.loads((root/'projects/aideway/frontend/package-lock.json').read_text())
out=['# Dependency review — 2026-10-15', '',
'The scan submitted all 376 unique Maven coordinates from committed Gradle lockfiles to OSV, then fetched all 82 distinct returned GitHub advisory records. Twenty-eight coordinates match an affected range. npm audit reports 19 affected dependency nodes (2 critical, 14 high, 3 moderate); transitive parent entries are not separate unique vulnerabilities. Raw requests, responses, full advisory records and the runtime dependency tree are retained beside this report. No dependencies were installed or upgraded for this scan.', '',
'All package-only matches remain LOW for the intended HH pilot until a vulnerable operation is established. Scanner severity is preserved below and is not a claim of clinical exploitability. Development/build dependencies still need remediation on builders. This is lockfile SCA, not a scan of the actual ARM64 release images, OS, Python environment or model code. Those artifact inventories were unavailable.', '',
'## Reachability conclusions', '',
'- PDF.js 5.6.205 matches [GHSA-hq66-cqwq-w95j](https://github.com/advisories/GHSA-hq66-cqwq-w95j), fixed in 6.2.108. The advisory requires scripting enabled and a permissive execution context. Current TypedContentViewer uses getDocument, canvas and TextLayer, not PDFScriptingManager; the application CSP uses script-src self. The first review’s confirmed arbitrary-script-execution claim is unsupported for this viewer. Upgrade and test the viewer; do not label a lockfile hit a reproduced exploit.',
'- Seroval 1.6.2 matches [GHSA-jp82-f5mq-hwhp](https://github.com/advisories/GHSA-jp82-f5mq-hwhp), fixed in 1.6.3. It enters via TanStack tooling; no attacker-controlled deserialize call was established in the served static application. Confirm the final bundle and upgrade the dependency chain.',
'- Jackson core/databind 2.19.4 are runtime dependencies. The returned advisories have differing entry conditions (async/DataInput parsers, coercion/polymorphic configuration and utility methods). Production HTTP/clinical JSON uses JFK/Kotlin serialization; no relevant vulnerable parser invocation was demonstrated. [GHSA-7hhh-6rmp-j9qf](https://github.com/advisories/GHSA-7hhh-6rmp-j9qf) specifically concerns DataInput constraints. Reconcile transitive users before selecting a supported patched line; the retained records contain branch-specific fixed versions.',
'- Jetty 12.1.7 matches three advisories. [Host/authority ambiguity](https://github.com/advisories/GHSA-7p3p-8qv8-m2vh) requires HTTP/2 or HTTP/3; the current native connector and nginx upstream use HTTP/1.1. [Trailer leakage](https://github.com/advisories/GHSA-f4v5-65jj-pcr2) needs relevant trailer consumption, not found in the app. [Path parameter traversal](https://github.com/advisories/GHSA-w7x5-g22v-xqhr) concerns Jetty path-mapped constraints; current authorization is KViaSH routing/gates. Upgrade to an appropriate fixed branch (12.1.10 covers these three) and verify proxy/auth behavior.',
'- Netty 4.1.114 and Undertow 2.3.21 are on the production runtime classpath, but the application listener is Jetty. Their presence does not prove a vulnerable inbound Netty/Undertow server. Outbound TLS/HTTP codec, DNS, decompression and trust-manager use require dependency-path triage before closure. Test-only 4.1.130/Vert.x/Rhino and dev-only archive dependencies are identified separately below.',
'- PostgreSQL JDBC 42.7.11 matches [GHSA-j92g-9f8w-j867](https://github.com/advisories/GHSA-j92g-9f8w-j867), fixed in 42.7.12. The downgrade involves unsupported certificate algorithms and channel-binding policy. That state was not established for the private database connection; verify the release TLS/certificate configuration.',
'- Logback and Bouncy Castle advisories depend on configuration, attacker-supplied certificate/ASN.1 material or particular processing paths. No exploit proof was run. Resolve these runtime matches before release or document a specific non-reachability rationale for each retained advisory.', '',
'## Maven matches', '', '| Coordinate | Lockfile scope | GHSA records |', '|---|---|---|']
for p in affected:
    configs=[]
    for path in p['locks']:
        for line in (root/path).read_text().splitlines():
            if line.startswith(p['name']+':'+p['version']+'='):
                label='dev' if '/dev/' in path else 'backend'
                configs.append(label+': '+line.split('=',1)[1])
    links=', '.join(f'[{a["id"]}](https://github.com/advisories/{a["id"]})' for a in p['advisories'])
    out.append(f'| `{p["name"]}:{p["version"]}` | {"; ".join(configs)} | {links} |')
out += ['', '## npm matches', '', '| Package | Locked version and scope | npm severity | Direct advisory or affected dependency |', '|---|---|---|---|']
for name,v in npm['vulnerabilities'].items():
    versions=[]
    for path,item in lock['packages'].items():
        if path.endswith('node_modules/'+name):
            versions.append(item['version']+(' (dev)' if item.get('dev') else ' (non-dev lock entry)'))
    refs=[]
    for a in v['via']:
        refs.append(a if isinstance(a,str) else f'[{a["title"]}]({a["url"]})')
    out.append(f'| {name} | {", ".join(sorted(set(versions)))} | {v["severity"]} | {"; ".join(refs)} |')
out += ['', '## Maven advisory inventory', '', '| GHSA | Severity in retained record | Subject |', '|---|---|---|']
for path in sorted((e/'advisories').glob('*.json')):
    a=json.loads(path.read_text())
    out.append(f'| [{a["id"]}](https://github.com/advisories/{a["id"]}) | {a.get("database_specific",{}).get("severity","not supplied")} | {a.get("summary","").replace("|","/")} |')
out += ['', 'Reproduction: `npm audit --json` in the frontend; OSV batch request body is `maven-osv-queries.json`, response is `maven-osv-batch.json`, and `fetch-advisories.py` fetches each returned GHSA. An earlier sequential scan was abandoned after network timeouts; its partial output is not the reported result. No exploit payloads were sent to HH or any external target.', '']
(e/'dependency-review.md').write_text('\n'.join(out))
print('wrote dependency-review.md')
