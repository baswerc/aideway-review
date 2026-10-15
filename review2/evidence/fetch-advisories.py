import concurrent.futures,json,pathlib,subprocess
out=pathlib.Path(__file__).resolve().parent
inventory=json.loads((out/'maven-lock-inventory.json').read_text())
batch=json.loads((out/'maven-osv-batch.json').read_text())['results']
assert len(inventory)==len(batch)
ids=sorted({v['id'] for r in batch for v in r.get('vulns',[])})
(out/'advisories').mkdir(exist_ok=True)
def fetch(ident):
 p=out/'advisories'/(ident+'.json')
 r=subprocess.run(['curl','-sS','--max-time','15','https://api.osv.dev/v1/vulns/'+ident,'-o',str(p)],capture_output=True)
 return {'id':ident,'exit':r.returncode,'error':r.stderr.decode()}
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool: statuses=list(pool.map(fetch,ids))
rows=[dict(p,advisories=r.get('vulns',[])) for p,r in zip(inventory,batch) if r.get('vulns')]
(out/'maven-affected.json').write_text(json.dumps(rows,indent=2))
(out/'maven-scan-summary.json').write_text(json.dumps({'packages':len(inventory),'affectedCoordinates':len(rows),'advisories':len(ids),'fetches':statuses},indent=2))
print(len(inventory),len(rows),len(ids));print('\n'.join(x['name']+'@'+x['version']+': '+','.join(v['id'] for v in x['advisories']) for x in rows))
