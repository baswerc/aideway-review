# Installation kit and acceptance plan

**Preparation is documented; clinical installation is not approved.** The reviewed checkout does not establish a shippable release. Close engineering and clinical blockers before travel with a release intended for real intake. Do not invent a tag, model hash or HH endpoint from an example.

## Artifact identity

| Component | Reviewed identity | Required delivered identity |
|---|---|---|
| Application | `9e015e0fe15a50a04cf434c5a445798199f52c93` | Tagged frozen-baseline release, passing CI, signed image digests; pending |
| Harness | `5abce3b05b8c74dec60511b9b01929b3d52f8802`, `0.1.0-dev` | Signed package/hash and matching version; pending |
| Customer guides | `066268e932e8f4491c8d1cfb17fb6b0ce355fc8a` | Corrected build bound to release; pending |
| PostgreSQL | Major 17 | Exact aideway-postgres digest and compatible backup client; pending |
| vLLM | Dockerfile/release 26.08-py3; build.sh/setup 26.05.post1-py3 | One approved base/digest and final ARM64 image; pending |
| Clinical model | Example Qwen/Qwen3.6-27B-FP8 only | Actual repository commit, quantization and complete file manifest; pending |
| NER/OCR | Presidio worker/Tesseract code | Offline weights/tokenizer/languages, Python/CUDA stack and tested settings; pending |
| HH definitions | Dev seed plus generic importer | Signed site bundle and published graph/prompt/dataset/classifier revisions; pending |

These source SHA-256 values are comparison aids, **not approval of a prompt or trust key**:

```text
5fc24ffd795f427a7275c17f223dd77e0c099f6cd15c071d161ca491edd7bb7c  prompt/v3/system_prompt.md
8f05b370d3062c9f5540bdf78c2cfea29985ee0fc610113378991408f59a5fab  prompt/v3/response_schema.json
7e96c56835b804c295558bb2a6c8031909754469afa3d27194b22236c4353400  prompt/v2/system_prompt.md
ee41800cba1a5d565eadde90a1abf68348bca5a842e320886e9c3555f502a658  harness/keys/bundle.pub
040cf490d82c95bc06edde4142aefec3e1a99248ef22cb31a65b2f9923e02717  harness/keys/cosign.pub
```

Confirm signer fingerprints independently. Do not replace existing site trust roots merely to match this checkout. The first review's remote Hugging Face hash list is not an HH inventory. Require an authenticated manifest of every model/config/tokenizer/template file with size/hash; compare installed files using `sha256sum -c`. `aideway models verify` checks file presence only.

## Carry list

| Item | Before-travel acceptance |
|---|---|
| Signed harness/runtime and four OCI archives | Offline signatures/digests verified on ARM64; tags match Compose; local PostgreSQL client image and approved TLS diagnostic tool included. |
| Model/NER/OCR files | Authenticated manifest, license/access approval, tokenizer/chat template, languages and measured settings; no runtime download/token needed. |
| Site bundle and non-secret worksheet | Fresh-production rehearsal; users/services/tiers provisioned; correct paths/recipient and published revisions recorded. |
| Offline OS/client/tool packages | DGX-compatible versions and dependency closure; cifs-utils or nfs-common, TPM/clevis/LUKS, cosign/minisign and OpenSSL; signed update bundles. |
| Matching guides/runbooks | Built HTML/PDF/Markdown and hashes, corrected emergency commands, printed recovery steps/contacts; no appliance pandoc requirement. |
| Synthetic acceptance pack | Mark every fixture SYNTHETIC REVIEW TEST; no realistic patient identifiers. Include scanned/mixed/empty/corrupt/long/oversized and clinically labelled cases with expected dispositions. |
| Protected transfer/recovery media | Approved encryption and inventory, separate secret custody, signer trust roots, pre-change backup destination and isolated restore target. Never keep passphrase with a plaintext backup. |
| Evidence template | Date/operator/manifest, input ledger, execution/result/queue IDs, receipt, resource peaks, recovery times and sign-off. Exclude credentials and clinical content from general support evidence. |

## Non-secret Appendix A worksheet

| Field | Known / pending |
|---|---|
| Site/week | HH data center, week of 2026-10-19 |
| Hardware | DGX Spark, GB10, nominal 128 GB unified memory; actual MemTotal/serial/MAC/OS and rack receipt pending |
| Web | Intended `aideway.hhsys.org`; IP/VLAN/gateway/DNS/trusted certificate pending |
| Sender | Intended `aideway@hhsys.org`; relay authorization pending |
| Recipient | Intended `pathology.reports@hhsys.org`; membership/forwarding/coverage approval pending |
| Users/roles | Named accounts/private MFA/Security Officer owner pending; shared guide login is not final access approval |
| SMTP | **Unknown actual endpoint**; `smtp.hhsys.org` is an example. Confirm 587 STARTTLS or 465 SSL, auth/IP policy, CA/pin and renewal |
| Share | **Unknown actual endpoint**; `//files.hhsys.org/pathology/aideway` is an example. Confirm SMB/NFS/security mode |
| Report paths | `/opt/aideway/drop` → `/mnt/drop`; do not import dev `/opt/drop` unchanged |
| Runtime paths | `/opt/aideway/config`, `keys`, `tls`, `models`, `audit`, `logs`, `backups`, `data/postgres`; record overrides/filesystems |
| Container identity | UID 1001; actual operator and TPM GIDs pending, not necessarily 1001 |
| Clinical identity | Approved model/prompt/schema/OCR/NER/classifier hashes and published IDs pending |
| Producer | Atomic rename, non-PHI names, stable report/correction IDs, expected size/volume/redelivery window pending |
| Retention | Separate workflow/dataset/audit/log/mailbox/source/backup schedules pending |
| Custody | Named passphrase, state.key and disk recovery custodians/escrow references pending; **no values here** |
| Owners | TekFive engineering/install and HH network/mail/file/pathology/security contacts, response targets and sign-off pending |

## On-appliance verification sequence

1. **Record identity.** Compare authenticated manifests, images and model files; record host/mount/memory facts. Verify media offline and preserve current system/database before an upgrade.
2. **Establish host/network protection.** Prove SSH/root policy, clock/DNS, container-inclusive firewall, web trust, disk protection and actual TPM unseal/recovery. Never print `.env` or private keys into evidence.
3. **Establish the share.** Verify source/type and UID/GID/ACL with a uniquely named marked synthetic file. Mount before server recreation. Prove identical container-visible content and read/delete permissions; protect credentials separately.
4. **Start and inspect.** Run `aideway doctor`, `aideway status`, `aideway audit --json`; inspect all findings as well as status until R2-02 is fixed. Verify `systemctl is-enabled aideway-harness.service` and effective unit. Test HTTPS trust from HH workstations.
5. **Inspect clinical configuration.** Verify graph edges, path, prompt/schema hashes, decision/review branches, fields/encryption/tiers, recipient and actual notification target. Require exactly one tested system mail service. A dev screenshot is not evidence.
6. **Test mail then MFA.** Prove service and flagged-result receipt and sender/transport policy. Enable MFA with an available recovery custodian; demonstrate fresh login, outage recovery, named roles and negative access tests.
7. **Run the matrix.** Reconcile all inputs/results/dispositions, measure latency/resource peaks, and keep real intake disabled while blockers or unexplained differences remain.
8. **Reboot and interrupt.** Include maintenance down/reboot, share absent at boot/later remount, model/server restart, interrupted email and failed unseal. Reconcile unfinished/duplicate work after each case.
9. **Recover and hand off.** Restore authenticated material to an isolated target, verify data/audits, demonstrate daily tasks and obtain HH clinical/security approval tied to the manifest.

## Synthetic acceptance matrix

HH must approve labels and thresholds. This matrix defines technical behavior, not invented clinical sensitivity targets.

| Test | Required outcome/evidence |
|---|---|
| Clearly unexpected finding | Durable result, correct true decision, agreed visible notification and mailbox receipt; correlate IDs. |
| Expected abnormal / benign negative | Durable result and explicit valid negative for unexpectedness, distinct from invalid extraction/output. |
| Missing history/CPT, conflicting intent, low confidence | Approved uncertainty/manual review; never silently accepted as routine negative. |
| Image-only / mixed-page PDF | Faithful nonempty extraction of relevant pages; partial/failed OCR quarantines visibly. |
| Empty/encrypted/corrupt/unsupported/oversized file | Counted rejection/quarantine; no successful negative or hidden oversized skip. |
| Long/context-limit input, MAX_TOKENS | No silent truncation; invalid completion rejected and reviewed. |
| Malformed JSON, `{}`, null/wrong-type/out-of-range fields | Required schema enforced before decision/side effects. |
| Dataset failure, invalid notification, enqueue failure | Missing required outcome visible; sibling success cannot conceal it. |
| Mail outage/4xx/5xx/partial send/certificate or credential rotation | Correct retry/terminal state and independently monitored alert; reconcile receipt. |
| Restart while PENDING/SENDING | Requeue or explicit uncertain/timed-out reconciliation; no unnoticed loss/blind resend. |
| Service disabled/tier lowered while queued | Reauthorize current activity/tier/transport before sending. |
| Initial backlog/same-name correction/identical redelivery | Agreed semantics and reconciled report/correction IDs; duplicates identified. |
| Atomic rename versus paused in-place write | Atomic delivery works; unsupported in-place behavior prohibited or safely detected. |
| Delete denied, absent/late/disconnected share, stale handle | Visible failure/recovery within target; no false healthy placeholder. |
| Model/server restart, timeout/cancel/retry/resume | No missing result, erased execution or untracked repeated side effect. |
| Peak vLLM+NER+OCR+database workload | No OOM; bounded backlog/latency; record memory/GPU/queue evidence. |
| Role denial/offboarding/URL-log canary/purge | Correct denial/revocation, no canary in unapproved stores, approved retention. |
| Corrupt backup/wrong key/interrupted restore | Reject before destructive writes; existing database retained and isolated recovery succeeds. |

## Recovery and rollback

- **Before commissioning:** keep the pathology system and existing clinical review authoritative. Agree how to pause export/workflow and retain/redeliver reports. Preserve an intake ledger and separate recoverable database backup before changes.
- **If the first test fails:** keep real intake disabled, preserve synthetic evidence and repair or return to the last accepted manifest. Do not erase evidence by recreating the database. A schema rollback requires a tested database procedure, not merely an older image.
- **If intake later starts under an approved release:** suspend intake using the agreed procedure, retain source reports, reconcile in-flight/deleted inputs and consult the clinical owner before replay. At-least-once execution can duplicate email/records; inspect mailbox/queue/result IDs first.
- **For database recovery:** current `backup restore` is destructive without a displaced-database snapshot. Do not use it as an unqualified rollback recipe. Authenticate with the protected original `state.key` or approved portable signature; never waive HMAC mismatch. Restore/validate on an isolated target, switch through the rehearsed procedure, and preserve the old target until acceptance.
- **For mail-dependent MFA outage:** the documented host `MFA_ENABLED=false` override supports authorized recovery. Use named host access, record the change without secrets, recreate the server per runbook, repair/test SMTP, then restore `MFA_ENABLED=true`, recreate and prove fresh MFA sign-in. Password reset does not fix mail outage; CLI password changes do not presently revoke sessions.
- **For evidence:** valid forms include `aideway logs export --out <approved-path>` and one prefix per `aideway audit --only <prefix>`. Do not use rejected `logs --export`, `backup create --label`, or multiple positional audit prefixes. Protect exports; current `--encrypt-to` does not encrypt backups.

Carry approved custody references, not plaintext secret values. No acceptance/recovery command was run against HH during this review.
