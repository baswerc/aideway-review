"""Read-only product probes; all fixtures/output live in review2 or temporary storage."""
from pathlib import Path
import os,subprocess,tempfile,json
root=Path(__file__).resolve().parents[2]; harness=root/'projects/harness'
results=[]
def run(name,args,env=None):
 p=subprocess.run(args,env=env,capture_output=True,text=True)
 results.append({'probe':name,'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
with tempfile.TemporaryDirectory(prefix='aideway-review2-') as td:
 t=Path(td); checks=t/'checks';checks.mkdir()
 (checks/'broken.sh').write_text('#!/bin/sh\nexit 42\n');(checks/'broken.sh').chmod(0o755)
 env=os.environ|{'HARNESS_ROOT':str(harness),'LIB_DIR':str(harness/'lib'),'__AIDEWAY_COMMON_LOADED':'1','AIDEWAY_AUDIT_CHECKS_DIR':str(checks)}
 run('audit crash is reported as success',['bash','-c','source "$LIB_DIR/audit.sh"; cmd_audit --json'],env)
 run('documented multi-prefix audit command',['bash','-c','die() { echo "$1" >&2; exit "${2:-1}"; }; source "$LIB_DIR/audit.sh"; cmd_audit --only 65-keyset 67-keyset-sealed 68-keyset-recovery'],env)
 fakebin=t/'bin';fakebin.mkdir()
 (fakebin/'docker').write_text('''#!/bin/bash
case "$*" in
 *State.Running*) echo true;;
 *ReadonlyRootfs*) [[ "$*" == *server-1* ]] && echo true || echo false;;
 *SecurityOpt*) echo '["no-new-privileges:true"]';;
 *CapDrop*) echo '["ALL"]';;
 *Devices*) echo '/dev/tpmrm0';;
 *Tmpfs*) echo '{"/tmp":"size=2g,mode=1777"}';;
esac
''');(fakebin/'docker').chmod(0o755)
 run('container audit against declared Compose flags',['bash',str(harness/'audit/checks/50-container-flags.sh')],os.environ|{'PATH':str(fakebin)+':'+os.environ['PATH']})
 run('docs build without pandoc',['bash',str(harness/'bin/aideway'),'docs','build','--out',str(t/'manual.html')])
 envfile=t/'synthetic.env';envfile.write_text('AIDEWAY_HOSTNAME=$(printf REVIEW2_SENTINEL)\n')
 run('shell evaluation of an inert config value',['bash','-c','source "$HARNESS_ROOT/lib/common.sh"; load_env; printf "%s\\n" "$AIDEWAY_HOSTNAME"'],os.environ|{'HARNESS_ROOT':str(harness),'AIDEWAY_ENV_FILE':str(envfile)})
output=root/'review2/evidence/harness-probes.json';output.write_text(json.dumps(results,indent=2)+'\n')
for row in results:print(row['probe'],row['exit'],row['stdout'][:120].strip(),row['stderr'][:120].strip())
