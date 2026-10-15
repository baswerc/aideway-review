"""Normalize the checked source register; never edit any reviewed project."""
from pathlib import Path
import collections, hashlib, json, re

root = Path(__file__).resolve().parents[2]
rows = json.loads((root / 'review2/evidence/prior-source-crosscheck.json').read_text())
rows = [r for r in rows if not (r['group'] == 'application review' and r['id'] in ('12', '13'))]

def row(group, ident):
    return next(r for r in rows if r['group'] == group and r['id'] == ident)

def override(group, ident, text, status=None):
    r = row(group, ident)
    r['evidence'] = text
    if status:
        r['status'] = status

override('harness issues', '8', 'Manual no longer promises --chain. `projects/harness/lib/tls.sh:209` checks parse/key/expiry only; `projects/harness/lib/tls.sh:646` uses alpine/openssl without verify_return_error or hostname verification. Bash pipefail propagates Docker failure; the older claim that sed always determines success was incorrect. R2-08.')
override('harness issues', '13', '`projects/harness/compose.yaml:88`, `:234`, `:318`, `:407` total 122.25 GiB in caps. `projects/harness/audit/checks/83-memory-budget.sh:88` compares host capacity. No physical OOM or actual HH MemTotal was measured; caps are not reservations. R2-07.')
override('harness issues', '18', '`projects/harness/audit/checks/50-container-flags.sh:51` also incorrectly requires nginx/vLLM read-only roots; isolated probe reproduces two FAILs. Tmpfs/key-backup/firewall drift remains. Nginx/application-layout tests pass after setting AIDEWAY_PROJECT_ROOT except host nginx -t (binary absent); seven separate nginx container tests pass. R2-02/R2-23.')
override('MVP', 'mvp-2', '`projects/aideway/backend/src/test/kotlin/org/aideway/workflow/nodes/types/triggers/file/FileTriggerJobDbTest.kt:113` proves identical redelivery after deletion launches again; 34 tests in that suite pass with DAC bypass removed. Fingerprint suppression while unchanged and optional filename dedupe are separate configured behavior. No universal content dedupe is claimed.', 'fixed')
override('remote management', 'Keep', '`projects/harness/compose.yaml:18` internal networks and `:27` hardened server anchor remain; `:149` read-only keyset; SSH/root checks remain. nginx/PostgreSQL/vLLM do not all use read_only. Preservation request satisfied, not an outstanding defect.', 'fixed')
for r in rows:
    if r['group'] == 'path review':
        r['status'] = 'fixed'
override('path review', 'PR-6', '`projects/harness/lib/setup.sh:977` configures per-user build caches; `:989` EXIT trap runs operator_tree read even on failure. Existing harness cache tests pass.', 'fixed')
override('path review', 'PR-9', '`projects/harness/lib/runtime.sh:65` selects os-updates; `projects/harness/lib/os_update.py:73` sets generated output group/mode and `:96`/`:106` handle directory/artifact access. OS update Python tests pass.', 'fixed')
override('path review', 'PR-10', '`projects/harness/lib/runtime.sh:66` selects usb root; `projects/harness/lib/usb_devices.py:172` returns an existing mount before creating a new UUID mount. USB Python tests pass. Actual attached media was not tested.', 'fixed')
override('full project', '#53', '`projects/aideway/backend/src/main/kotlin/org/aideway/data/classification/api/DataClassificationApiController.kt:1` retains UUID parsing without a uniform bad-input conversion; same item as application 4.3.')
override('full project', '#58', '`projects/aideway/.github/workflows/release.yml:273` uses mutable installers/actions/base references; `:330` Trivy is report-only. R2-36.')
override('full project', '#61', '`projects/aideway/backend/src/main/kotlin/org/aideway/event/AuditSpoolProcessor.kt:266` processes one store per spool item; `projects/aideway/backend/src/main/kotlin/org/aideway/event/EventAudit.kt:252` transaction/lock per event. Same as application 7.3; no load benchmark establishes HH impact.')
override('full project', '#72', '`projects/aideway/frontend/scripts/check-bundle-size.mjs:1` checks bundle sizing, not absence of the dev token path; production mode guard remains. LOW latent hardening.')
override('full project', '#75', '`projects/aideway/backend/images/aideway-backend-base/Dockerfile:3` starts from JRE and installs build dependencies for Python packages. Compiler/git tools are distinct from Java jcmd/jstack (remote-management 3).')
override('harness improvements', '6', '`projects/harness/systemd/aideway-harness.service:16` uses doctor and the CLI wrapper; test_systemd_unit.bats passes. Same fix as harness issue 10.', 'fixed')
override('remote management', '3', '`projects/aideway/backend/images/aideway-backend-base/Dockerfile:3` uses eclipse-temurin:25-jre-noble. Java diagnostic tool availability is not guaranteed; no actual release-image inventory supplied.')
override('remote management', '6', '`projects/harness/bin/aideway:137` dispatch table has no generic exec verb; supported targeted CLI paths exist. Convenience request, not a pilot blocker.')
override('security guide limits', 'L-2', '`projects/aideway/backend/src/main/kotlin/org/aideway/data/audit/DataAuditTransmission.kt:1` has no production send caller. `projects/aideway/backend/src/main/kotlin/org/aideway/service/types/notification/email/EmailClient.kt:23` queues directly via RelayKt; EmailAuditQueue is not wired. R2-13.')

# The first report retained pre-extraction line numbers for several split engine files.
base = 'projects/aideway/backend/src/main/kotlin/org/aideway/workflow/execution/'
execution_evidence = {
 '5': f'`{base}engine/WorkflowLauncher.kt:196` carries restartAtNodeId into the retry; `:206` calls shared RestartDataCopier. `{base}engine/RestartDataCopier.kt:38` copies preserved nodes/input. The current partial-restart regression passes.',
 '7': f'`{base}engine/DbWorkflowLogger.kt:98` skips storage for purged executions before clearing buffered entries. The no-retention final-log regression passes.',
 '9': f'`{base}api/EventApiController.kt:26` caps lookback at five minutes and queries at 500 rows, clamps the cursor at :37 and limits both queries at :48/:61. Stale-cursor regression passes.',
 '10': f'`{base}engine/NodeRunner.kt:545` acknowledges after processing; `{base}NodeExecutionContext.kt:20` creates a fresh executionState map. Queued email/dataset side effects lack a universal report-level idempotency key; resume may repeat them. R2-22; source tests do not prove exactly-once clinical delivery.',
 'L2': f'`{base}WorkflowExecutionActions.kt:30` checks status/purge; `{base}WorkflowExecutionGraph.kt:71` similarly omits active/published checks from restartability. `{base}engine/WorkflowLauncher.kt:245` rejects at launch, so this is misleading availability/UI behavior, not authorization bypass.',
 'L4': f'`{base}engine/WorkflowCoordinator.kt:271` restores captured interruption in outer finalization; `{base}engine/NodeTaskExecutor.kt:52` drain captures/returns interrupt state. Current cancellation/pause regressions pass.',
 'L5': f'`{base}engine/WorkflowCoordinator.kt:288` drains tasks without job check-in; `{base}engine/WorkflowSuspension.kt:20` persists pause/resume work before final draining. Long-drain timeout remains a source-level risk; no appliance timing reproduction.',
 'L7': f'`{base}engine/DbWorkflowLogger.kt:110` promises buffered retry although a finished coordinator may discard the logger; :104 clears after nested db returns. Timeout callback in `{base}engine/WorkflowExecutionJob.kt:72` supplies an outer transaction, so a later outer failure can undo stored logs after the buffer cleared. No targeted race reproduction.',
 'L13': f'`{base}WorkflowExecutionGraph.kt:45` fetches topic details per port and :64 calls RestartEligibility per node; `{base}RestartEligibility.kt:29` walks upstream nodes and :39 queries broker state. Small pilot graph limits impact; no large-graph benchmark.',
 'R3': f'`{base}engine/README.md:125` describes timeout retry; `{base}engine/WorkflowJobRuntime.kt:110` loads budget from lastJobRecordId, while retry creates a new execution with no previous job. Fresh retry budget remains undocumented.',
 'R5': f'`{base}engine/README.md:297` documents purged-log dropping; `{base}engine/DbWorkflowLogger.kt:98` implements it. Same corrected behavior as execution 7.',
 'R11': f'`{base}README.md:36` promises prevention of concurrent runs; `{base}engine/WorkflowLauncher.kt:237` has no active-run prohibition. `{base}engine/WorkflowJobRuntime.kt:126` controls job concurrency instead, allowing queued executions. WebhookController retains the stronger wording.',
}
for ident, evidence in execution_evidence.items():
    override('execution', ident, evidence)

extra = [
('12.1','Self-service password reset and invitations','MEDIUM value','open','backend/src/main/kotlin/org/aideway/user/UserCredentials.kt:1','Reset fields exist but session routes expose no complete reset/invitation flow.'),
('12.2','Independent MFA factor','MEDIUM value','open','backend/src/main/kotlin/org/aideway/io/session/MfaService.kt:1','Email OTP remains the only implemented factor. Host recovery exists; R2-11.'),
('12.3','Resident classification service','HIGH value','fixed','backend/src/main/kotlin/org/aideway/data/classification/analysis/ner/PythonWorkerNerProvider.kt:27','Bounded resident worker pool replaces per-request process startup; latency claim still needs measurement.'),
('12.4','Server-side re-identification vault','MEDIUM value','open','backend/src/main/kotlin/org/aideway/workflow/nodes/types/transform/analyze/anonymize/AnonymizeDataNodeType.kt:53','Anonymization metadata still accompanies messages; no separate vault replaces it.'),
('12.5','Reasoned time-limited record elevation','MEDIUM value','open','backend/src/main/kotlin/org/aideway/data/authorization/DataAuthenticator.kt:1','Tier authorization has no implemented per-record break-glass grant. MFA host recovery is a different facility.'),
('12.6','Self-scoped active-session management','LOW value','open','frontend/src/features/profile/AccountSettingsPage.tsx:1','Account settings has no active-session list/sign-out-everywhere feature; administrator session management is separate.'),
('12.7','Audit export and SIEM forwarding','MEDIUM value','open','backend/src/main/kotlin/org/aideway/event/api/EventAuditApiController.kt:1','Audit paging exists; encrypted operational log export is not the proposed signed audit-event export/SIEM integration.'),
('12.8','Out-of-band alert delivery','MEDIUM value','open','backend/src/main/kotlin/org/aideway/alert/AlertGateway.kt:25','AlertGateway persists/suppresses alerts but does not dispatch email/webhooks. SMTP-independent operational monitoring is needed.'),
('12.9','Scoped machine tokens','LOW value','open','backend/src/main/kotlin/org/aideway/io/Routes.kt:1','Production routes use current session/webhook contracts; proposed machine-client scopes are absent. Gateways are dormant in HH.'),
('12.10','Startup security self-check','HIGH value','open','backend/src/main/kotlin/org/aideway/configuration/SecurityConfigurationChecks.kt:30','Distinct mandatory SEALED secrets are checked; the complete proposed MFA/proxy/deny-list acceptance gate is not implemented.'),
('12.11','Global execution quotas','LOW value','open','backend/src/main/kotlin/org/aideway/workflow/Workflow.kt:21','Workflow concurrency exists; no complete global launch-rate quota satisfies the suggestion.'),
('13.1','Secret separation and startup validation','suggestion','open','backend/src/main/kotlin/org/aideway/configuration/SecurityConfigurationChecks.kt:30','SEALED separation is enforced; lazy JWT validation and remaining startup-policy checks keep the broader item open.'),
('13.2','Authorization matrix per route','suggestion','open','backend/src/test/kotlin/org/aideway/io/RoutesTest.kt:1','Route coverage and selected AuthHttpIntegrationTest role cases exist; not a full expected-role matrix for every route.'),
('13.3','Concrete bug regression tests','suggestion','fixed','backend/src/test/kotlin/org/aideway/integration/AuthHttpIntegrationTest.kt:1','Current credential/password-lockout/audit-downgrade/proxy/webhook regression suites pass, including seven nginx container tests.'),
('13.4','Detekt baseline reduction','suggestion','open','backend/detekt-baseline.xml:1','Large suppression baseline remains. Passing detekt does not close baseline debt.'),
('13.5','End-to-end performance measurements','suggestion','open','backend/build.gradle.kts:1','Targeted benchmarks are not the requested classification/workflow/audit concurrency acceptance evidence; no Spark load measurement supplied.'),
('13.6','Operator trust-boundary documentation','suggestion','fixed','../docs/guides/security/06.md:1','Security guides 05/06 distinguish keyset/TPM/filesystem/backup/operator trust. Remaining implementation limits are listed separately.'),
]
for ident,title,severity,status,p,evidence in extra:
    path = (root/'projects/aideway'/p.split(':')[0]).resolve().relative_to(root)
    rows.append(dict(group='application review', id=ident, title=title, severity=severity,
                     status=status, reach='suggestion; evaluate against final HH configuration',
                     evidence=f'`{path}:{p.split(":")[-1]}` {evidence}', references=[]))

group_order = list(dict.fromkeys(r['group'] for r in rows))
def ident_key(r):
    return tuple(int(x) if x.isdigit() else x for x in re.split(r'(\d+)', r['id']))

# Normalize source paths inside code spans; retain adjacent abbreviated line numbers.
def normalize(text, group):
    def replace(m):
        token=m.group(1)
        if token.startswith('projects/') or not '/' in token:
            return m.group(0)
        if token.startswith('related/harness/'):
            token='projects/harness/'+token[len('related/harness/'):]
        elif token.startswith(('harness/','aideway/','docs/guides/')):
            token='projects/'+token
        elif token.startswith(('backend/','frontend/','api/','.github/','.agents/','gradle/','prompt/','scripts/')):
            token='projects/aideway/'+token
        elif group.startswith(('harness','remote','path')) and token.startswith(('lib/','tests/','docs/','audit/','systemd/')):
            token='projects/harness/'+token
        token=token.replace('backend/.../', 'backend/src/main/kotlin/org/aideway/')
        return '`'+token+'`'
    return re.sub(r'`([^`]+)`',replace,text).replace('\n',' ')

out=['# Prior findings — current source status','',
'Reviewed 2026-10-15 against the three commits in [00-baseline.md](00-baseline.md). **Fixed** means the original defect/request is resolved in current source (including an incorrect original premise, explicitly explained). **Open** includes partial fixes and unmet suggestions. **Regressed** means a previously corrected issue has returned; none was established. These are source conclusions, not claims of appliance acceptance.', '',
'This register contains one row per named source item, including the individual section 12 suggestions and six section 13 bullets. Related items across separate artifacts intentionally retain their original IDs; they are aliases, not distinct product defects. Harness issues-confirmed/unconfirmed qualify the same 19 issue IDs and do not create another 38 findings. Path-review changes are recorded as fixed when present. The duplicated delivery table in the first review is omitted.', '',
'Prior severity below preserves the originating label; value/prioritization labels are not vulnerability severities. Current HH priority and fixes are in [findings.md](findings.md). Dormant gateways, webhooks, chains and human-review nodes are LOW for the intended pilot; their original HIGH/MEDIUM labels do not make them go-live blockers. Actual HH accounts, tiers, service rows and artifact contents were unavailable, so earlier assumptions about installed values/roles are not evidence.', '',
'Evidence combines re-read current source, fresh tests, and the hashed excerpts in [current-source-citations.json](evidence/current-source-citations.json). The source commits match review 1, but its conclusions were challenged; fixes below generally predate both reviews. A source row is not marked tested merely because a surrounding suite passed.', '',
'| Source | Fixed | Open | Regressed | Total |','|---|---:|---:|---:|---:|']
for group in group_order:
    rs=[r for r in rows if r['group']==group]; c=collections.Counter(r['status'] for r in rs)
    out.append(f'| {group} | {c["fixed"]} | {c["open"]} | {c["regressed"]} | {len(rs)} |')
c=collections.Counter(r['status'] for r in rows)
out.append(f'| **Total source items** | **{c["fixed"]}** | **{c["open"]}** | **{c["regressed"]}** | **{len(rows)}** |')
for group in group_order:
    out += ['',f'## {group}', '', '| ID | Prior severity | Status | Item and current evidence |', '|---|---|---|---|']
    for r in sorted((r for r in rows if r['group']==group),key=ident_key):
        e=normalize(r['evidence'],group)
        out.append(f'| {r["id"]} | {r["severity"]} | **{r["status"]}** | {r["title"]}. {e} |')
out += ['', '## Material corrections to review 1', '',
'- SMTP hostname verification is present in the exact locked custom socket factory; pinning compares public keys and custom CA trust replaces default roots.',
'- MFA host recovery is documented. The remaining blocker is mail-dependent login with no independently proved recovery/alert path, not absence of every recovery tool (R2-11).',
'- Boot failure depends on a stopped stack, mount/unit state and reboot sequence. Docker restart policy makes an unconditional “every reboot stops everything” conclusion unsupported (R2-10).',
'- The provisioning gap is HIGH as explicitly required by instructions, and missing artifacts here do not prove no factory artifact exists elsewhere (R2-17).',
'- Source deletion occurs after durable launch; encrypted execution input remains subject to retention. Identical redelivery after deletion is tested, not universally swallowed (R2-15/R2-22).',
'- Backup helpers now use a local image. TLS still has an offline helper/trust gap. Shell pipefail means its exit code is not always sed\'s (R2-08).',
'- Memory caps do not establish simultaneous physical allocation or OOM. The actual Spark must be measured (R2-07).',
'- PDF.js scripting exploit prerequisites and Jackson parser/configuration prerequisites were not established in the pilot; package matches are LOW pending reachability, not confirmed patient-data exploits (R2-29).',
'- MFA resend SMTP exceptions propagate to the UI error path. The misleading 204 success is the invalid/expired challenge case (R2-34).',
'- A stale PENDING mail item can be requeued; stale SENDING is TIMED_OUT and requires reconciliation. Generic retry claims do not cover every failure class (R2-13).',
'- No actual clinical-model false-negative rate, calibration, HH model hash inventory or end-to-end release run was established by either this checkout or the supplied clinical artifacts (R2-30/R2-31).', '']
(root/'review2/prior-findings-status.md').write_text('\n'.join(out))
(root/'review2/evidence/prior-status-summary.json').write_text(json.dumps({'total':len(rows),'counts':dict(c)},indent=2))
crosscheck=[]
for r in rows:
    refs=[]
    for path,n in re.findall(r'`(projects/[^`:]+)(?::(\d+)[^`]*)?`',normalize(r['evidence'],r['group'])):
        p=root/path
        if not p.is_file():
            continue
        contents=p.read_text().splitlines(); n=int(n or 1)
        assert n <= len(contents), (path,n)
        refs.append({'path':path,'line':n,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
                     'excerpt':'\n'.join(f'{i+1}: {contents[i]}' for i in range(max(0,n-4),min(len(contents),n+8)))})
    crosscheck.append({'group':r['group'],'id':r['id'],'status':r['status'],'references':refs})
(root/'review2/evidence/current-source-citations.json').write_text(json.dumps(crosscheck,indent=2))
print(len(rows),dict(c))
