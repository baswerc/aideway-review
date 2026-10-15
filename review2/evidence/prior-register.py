from pathlib import Path
import re,json,hashlib
root=Path(__file__).resolve().parents[2]
lines=(root/'review/prior-findings-status.md').read_text().splitlines()
sections=[(26,117,'application review'),(118,211,'full project'),(212,259,'execution'),(260,268,'MVP'),(269,281,'frontend suggestions'),(353,376,'harness issues'),(377,387,'harness improvements'),(388,399,'remote management'),(400,414,'path review'),(415,425,'security guide limits')]
rows=[]
def resolve(s,group):
 s=s.removeprefix('projects/')
 if s.startswith('related/harness/'):s='harness/'+s[16:]
 if s.startswith('harness/'):return root/'projects'/s
 if s.startswith('aideway/'):return root/'projects'/s
 if s.startswith('docs/guides/'):return root/'projects'/s
 if s.startswith(('backend/','frontend/','api/','.github/','gradle/','gradle.properties')):return root/'projects/aideway'/s
 if group.startswith(('harness','remote','path')):return root/'projects/harness'/s
 return root/'projects/aideway'/s
for start,end,group in sections:
 for line in lines[start-1:end]:
  if not line.startswith('| '):continue
  # Preserve literal pipes escaped in the evidence.
  cells=re.split(r'(?<!\\)\|',line)[1:-1]
  cells=[c.strip() for c in cells]
  if len(cells)!=6 or cells[0] in ['id','source']:continue
  ident,title,severity,status,reach,evidence=cells
  refs=[]
  for token in re.findall(r'`([^`]+)`',evidence):
   m=re.match(r'([^:]+\.(?:kt|tsx?|sh|py|yml|yaml|md|xml|kts|toml|bats|template|lockfile))(?::(\d+))?',token)
   if not m:continue
   p=resolve(m[1],group)
   if not p.is_file():continue
   contents=p.read_text().splitlines(); n=int(m[2] or 1)
   refs.append({'path':str(p.relative_to(root)),'line':n,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'excerpt':'\n'.join(f'{i+1}: {contents[i]}' for i in range(max(0,n-4), min(len(contents),n+8)))})
  state='fixed' if status.startswith(('fixed','implemented','not reproducible')) else 'open'
  if 'part' in status:state='open'
  rows.append(dict(group=group,id=ident,title=title,severity=severity,status=state,oldStatus=status,reach=reach,evidence=evidence,references=refs))
(root/'review2/evidence/prior-source-crosscheck.json').write_text(json.dumps(rows,indent=2))
print('rows',len(rows),'references',sum(len(x['references']) for x in rows),'no references',[(x['group'],x['id']) for x in rows if not x['references']])
for x in rows:
 if any(s in x['severity'].upper() for s in ['HIGH','CRITICAL','MEDIUM']) and x['status']=='open':
  print(x['group'],x['id'],x['title'])
