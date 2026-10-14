# AIDEWAY Go-Live Review: Instructions

## 1. Purpose

Find problems before the install. The AIDEWAY appliance is installed in the Huntsville Hospital
(HH) data center the week of 2026-10-19 by the person running this review. Every finding is ranked
by its effect on that install and the weeks after it: what stops the install on site, what fails
the first end-to-end test, what breaks in daily operation, and what is a latent defect. Code,
harness, documentation, email integration, network file share, model, and anything else likely to
fail are all in scope. An issue that is theoretical but not reachable in the HH configuration is
reported at LOW and does not block.

Perform a full, source-based review of AIDEWAY (https://aideway.org) before it goes live at HH. AIDEWAY is a governed workflow platform for healthcare, similar in shape
to n8n, built around local LLM inference so PHI never leaves the facility. The pilot runs in HH's
data center on one NVIDIA DGX Spark appliance that holds the whole solution: the AIDEWAY
application (nginx, Kotlin server), PostgreSQL, and vLLM.

The deliverable is a go/no-go recommendation backed by verified findings, a go-live checklist,
and a list of questions only HH or TekFive can answer. The review covers code, appliance harness,
documentation, and the shipped pilot configuration. It does not modify the projects under review
unless the user asks for a fix.

## 2. Workspace

| Path | What it is |
|---|---|
| `projects/aideway/` | Application: `backend/` (Kotlin/JVM, Java 25), `frontend/` (React + TypeScript + Vite), `api/openapi.yml`, container images, `site/` (public web page), `prompt/` (LLM prompt revisions), `docs/` (HIPAA references, prior reviews, design notes). |
| `projects/harness/` | Appliance harness for the DGX Spark: `bin/aideway` CLI, `lib/*.sh` and `lib/*.py`, `compose.yaml`, `audit/checks/*.sh`, `systemd/`, `tests/*.bats`, operator manual under `docs/manual/`. |
| `projects/docs/` | Customer guides as Markdown: `guides/getting-started/` (the HH install and start guide), `installation/`, `operation/`, `security/`, `user/`. |
| `docs/Invoice-2026071235.pdf` | Rack mount kit for the DGX Spark (racknex UM-NVI-201), ordered 2026-07-23, 7 to 8 week lead time. Confirms the appliance is rack-mounted at HH. |
| `.agents/skills/` | Review skills available here: `hipaa-compliance`, `healthcare-phi-compliance`, `healthcare-eval-harness`, `healthcare-emr-patterns`, `healthcare-cdss-patterns`, `hermes-imports`. |

Each project directory is its own git checkout. The AIDEWAY README refers to the harness as
`related/harness`; in this workspace it lives at `projects/harness` and `projects/aideway/related/`
is empty. Translate paths accordingly, or symlink `projects/aideway/related/harness` to
`../../harness` before running anything that expects it.

Read these first, in order:

1. `projects/aideway/AGENTS.md` and `projects/aideway/.agents/rules/*.md` (project priorities, coding and logging rules, especially the PHI logging rules).
2. `projects/aideway/README.md` and `projects/aideway/PRODUCT.md`.
3. `projects/docs/guides/getting-started/01.md` through `13.md` (the HH procedure, end to end).
4. `projects/harness/README.md`, `projects/harness/.env.example`, `projects/harness/compose.yaml`.
5. `projects/docs/guides/security/01.md` through `06.md` and `security/REVIEW.md`.
6. Every prior review listed in section 6.

## 3. The initial use case: Pathology Report Review at Huntsville Hospital

The pilot runs one preconfigured workflow, **Pathology Report Review**. The public site describes
it as using local AI to analyze pathology reports and identify unexpected findings that may
warrant clinical review, including findings that do not trigger existing rules or safeguards.

How it works (from `projects/docs/guides/getting-started/` and `projects/aideway/prompt/v3/`):

- **Input.** HH's pathology system publishes each report as one PDF to a network share
  (SMB or NFS) at `//files.hhsys.org/pathology/aideway` or an NFS equivalent. The appliance mounts
  it at `/opt/aideway/drop`, which Compose maps to `/mnt/drop` inside the server. A watched
  directory trigger sweeps it about once a minute and treats a file as complete once it stops
  changing. Reports must be written to a temporary name then renamed. Filenames must not contain
  patient identifiers, because they appear in the UI, alerts, and email subjects.
- **Analysis.** The local model (vLLM on the Spark; the shipped `VLLM_REASONING_PARSER=qwen3`
  default suggests a Qwen3-family model, confirm which) classifies the report on two independent
  axes defined in `prompt/v3/system_prompt.md`:
  - *Abnormal*: a finding outside its normal histologic state (malignancy, dysplasia, atypia,
    active infection), judged from the report alone.
  - *Unexpected*: a significant finding unrelated to the reason the specimen was obtained,
    creating a new clinical problem. Example from the guide: malignancy in bone from a kyphoplasty
    for a compression fracture. Cancer confirmed by a biopsy ordered to find cancer is abnormal but
    expected. The prompt uses CPT codes and clinical history to classify `procedure_intent`.
  - The model returns one JSON object conforming to `prompt/v3/response_schema.json`.
- **Record.** A record for every report is written to the **Pathology Results** dataset.
- **Decision.** A filter node ends the run when the report is not flagged. When flagged
  unexpected, the **Email Administrator** node emails `pathology.reports@hhsys.org` and the
  **Alert Administrator** node raises an alert under Administration > Alerts.
- **Cleanup.** The workflow deletes the report from the share after processing. The pathology
  system remains the system of record.
- **Who uses it.** HH staff sign in as `pathology.reports@hhsys.org` (Administrator) over HTTPS at
  `https://aideway.hhsys.org/` from HH workstations. MFA codes are emailed to that same mailbox.
  Daily operation is: read the mailbox, check Executions, Alerts, Email Queue, and Watched
  Directories in the app, and run `aideway status` and `aideway audit` on the appliance.

Clinical stakes: the workflow is a safety net for missed or unexpected pathology results. A false
negative (an unexpected finding not flagged) is silent and is the worst failure mode. A false
positive costs clinician attention. Weigh findings accordingly.

Provisioning gap to resolve during the review: the getting-started guide says the workflow, the
**HH Email Service** record, and the **Pathology Results** dataset are "shipped" and the operator
only edits them. The only source that names them is the development seeder
(`backend/dev/src/main/kotlin/org/aideway/dev/DevSeedCatalog.kt`, `DevWorkflowSeeder.kt`), whose
graph differs from the one the guide describes, and the offline definition import path
(`backend/src/main/kotlin/org/aideway/harness/update/README.md`). Establish exactly how the pilot
configuration reaches the appliance, that it is version-pinned and signed, and that the graph,
prompt revision, dataset revision, filter condition, recipient, and delete-after-processing
setting match the guide. Treat an undocumented or manual provisioning step as a HIGH finding.

## 4. The Huntsville Hospital email system

Email is a hard dependency of the pilot: it carries MFA codes for every sign-in, system alerts,
and the unexpected-result notifications. Without it nobody can sign in once MFA is on.

What the guides specify (`getting-started/06.md`, `installation/03.md`, `user/16.md`):

| Item | Value |
|---|---|
| Integration | SMTP submission to an HH mail relay. AIDEWAY has no Exchange, Graph, or OAuth mail integration; SMTP is the only email service type (`service/types/notification/email/smtp/SmtpServiceType.kt`). |
| Relay host | Internal HH relay, example `smtp.hhsys.org`. Use the name, not the IP, so TLS hostname checks agree. |
| Port and transport | 587 with STARTTLS, or 465 with SSL. Never both. Blank port means 587. |
| Authentication | Optional. If the relay requires a login, HH issues a service credential for AIDEWAY; no personal accounts. |
| Sender | `SYSTEM_FROM_EMAIL_ADDRESS=aideway@hhsys.org`, set in the appliance `.env`. The default `system@aideway.org` is rejected by most relays. |
| Recipient and login mailbox | `pathology.reports@hhsys.org`. |
| Certificate trust | Public CA: nothing. HH private CA: paste the CA bundle on the service. Self-signed or HH mandates a pin: paste the relay certificate as a pinned certificate and document the renewal procedure. |
| Service record | **HH Email Service**, Active, Environment On-Premises, BAA Status Active, Use for System Emails Yes, Secure Connection Yes, Issues tab empty. |
| Paths | System mail (MFA codes, alerts) sends immediately through the service marked for system email. Workflow mail (Send Email node) is queued, delivered by `DispatchQueuedMessagesJob` every 20 seconds, and visible under Administration > Email Queue. |
| Network | Outbound TCP 587 or 465 from the appliance to the relay, allowed on the appliance firewall and HH's. The relay must accept connections from the appliance address. |
| Testing | Service "Test service" to the mailbox, then an MFA sign-in test after MFA is enabled. |

What public DNS shows for `hhsys.org` (queried 2026-10-14, read-only; nothing was sent to HH
systems):

- MX records point at HH-operated hosts (`mail1.hhsys.org`, `mx1.hhsys.org`, `mx2.hhsys.org`,
  `mail3` to `mail5`). `huntsvillehospital.org` uses the same MX set.
- SPF is `v=spf1 ip4:192.151.87.96/27 include:res.cisco.com mx -all`. The `res.cisco.com` include
  is the Cisco Secure Email Encryption Service (Registered Envelope Service), which normally pairs
  with a Cisco Secure Email Gateway (IronPort). Expect a Cisco gateway in HH's mail path and
  encrypted-envelope delivery for outbound mail.
- A `MS=ms42504559` TXT record is a Microsoft 365 domain verification, so HH has a Microsoft
  tenant verified for this domain. Mailboxes are most likely Exchange, on-premises or Exchange
  Online. Confirm which, because it decides whether the relay is an Exchange receive connector or
  an Exchange Online SMTP relay connector with an IP allowlist.
- DMARC is `p=reject`.
- `smtp.hhsys.org` has no public address. It is an internal name or a placeholder in the guide.

Implications the review must check:

- The relay AIDEWAY uses must be an internal connector that accepts the appliance by IP or by
  credential. An Exchange receive connector or a Cisco gateway relay policy both need HH to
  allowlist the appliance address. Get the actual host, port, and auth mode from HH mail
  administration and record them in the Appendix A worksheet.
- With DMARC `p=reject`, any message that leaves HH's domain must pass SPF or DKIM through HH's
  authorized path. Internal delivery to `pathology.reports@hhsys.org` is fine; forwarding rules or
  external recipients on the mailbox are not. Note this as an operational constraint.
- MFA codes and result notifications travel to a shared mailbox that is also the sign-in
  identity. Shared account plus shared mailbox weakens MFA to "whoever reads the mailbox" and
  removes individual accountability in the audit trail. Review and report; recommend named HH
  accounts after handoff (the guide already allows additional accounts in step 9).
- Mail content: confirm what the unexpected-result email and the alert contain. Email subjects
  include the filename. Verify no PHI beyond what HH accepts enters email bodies, subjects, the
  Email Queue UI, the audit events, or server logs. The user guide says to review classification,
  the service's maximum send tier, and recipients before sending sensitive data by email; verify
  the shipped workflow's settings do that.
- MFA delivery failure modes: relay down, credential rotation, certificate renewal with a pinned
  certificate, sender policy changes, spam filtering, and queue backlog. Each one locks users out.
  Check that alerts fire, that an administrator can still get in, and that the guide's recovery
  steps work.
- Only one active service may have Use for System Emails on; if several qualify the server picks
  one at random per message. Verify the shipped configuration has exactly one.

## 5. Deployment architecture on the DGX Spark

- Hardware: NVIDIA DGX Spark, GB10, 128 GB unified CPU/GPU memory, rack-mounted (racknex kit).
  DGX OS (Ubuntu-based). CUDA 13 is required for DeBERTa NER on this GPU.
- Containers (`projects/harness/compose.yaml`): `nginx` (publishes 80 and `PROXY_HTTPS_PORT`,
  default 443), `server` (JVM plus a Python Presidio NER subprocess plus Tesseract OCR), `postgres`
  (`aideway-postgres`, PostgreSQL 17), `vllm` (built on `nvcr.io/nvidia/vllm:26.05.post1-py3`,
  model weights mounted read-only, `HF_HUB_OFFLINE=1`). Only nginx and server share the ingress
  subnet `172.30.250.0/29`; postgres and vLLM are internal-only. Internal TLS between every hop.
- Host state under `/opt/aideway`: `config/.env` (all secrets), `tls/`, `audit/`, `drop/` (the
  report share mount), `models/`, `backups/`. Encryption keyset is Tink, TPM-sealed via clevis
  (`AIDEWAY_KEYSET_MODE=SEALED`), with a recovery passphrase. Disk is expected to be LUKS encrypted.
- Images are cosign-signed; transfer bundles and OS update bundles are minisign-signed; the
  appliance is expected to run offline after install (`aideway images`, `aideway models`,
  `aideway transfer`, `aideway os`).
- Resource defaults: vLLM `VLLM_GPU_MEMORY_UTILIZATION=0.80`, `VLLM_MEM_LIMIT=102g`, server 12g
  (4g heap), postgres 8g. A prior finding (harness issue 13) says these overcommit the Spark.
- Operations: `aideway setup host`, `setup todo`, `doctor`, `audit`, `backup`, `tls`, `keys`,
  `logs`, `status`, `device`; systemd unit `aideway-harness.service`.

## 6. Prior review artifacts: build on them, do not redo them

Every finding below must be re-checked for fix status against the current checkouts. Report each
as fixed, still open, or regressed, with evidence. Do not re-derive findings that are still open;
cite them.

| Artifact | Content |
|---|---|
| `projects/aideway/docs/review.md` | Deep review, running document: 0 CRITICAL, 9 HIGH, 29 MEDIUM, 47 LOW across backend, frontend, API, harness. Defines the severity scale used everywhere. |
| `projects/aideway/docs/reviews/full-project-review.md` | Full project review started 2026-09-11, follow-up 2026-09-12 against commit `b6de35be`: 2 HIGH, 27 MEDIUM, 60 LOW. Defines the finding format and area split (A security core, B data and services, C workflow domain, D frontend and delivery). |
| `projects/aideway/docs/reviews/workflow-execution-review.md` | Execution engine review: 1 CRITICAL (job cleanup cascades into executions), 2 HIGH, 8 MEDIUM, plus README drift and a recommended fix order. |
| `projects/harness/issues.md`, `issues-confirmed.md`, `issues-unconfirmed.md` | 19 harness findings (1 critical, 11 high), all confirmed against `features/data_classification`; three with severity caveats. |
| `projects/harness/issues-improvements.md`, `issues-remote-management.md` | Remote management and support-bundle gaps, dated 2026-09-02. |
| `projects/harness/docs/path-review.md` | Default path review with changes already applied (for example the `/tmp/swap_err` fix). |
| `projects/docs/guides/security/REVIEW.md` | Security guide source review of 2026-09-12 against harness `a12739e` and AIDEWAY `e5a513f1`, with a list of implementation limits requiring separate work (release identity, data-audit coverage, HTTP redirect, TPM enrollment proof, proxy identity). |
| `projects/aideway/docs/todo/mvp.md`, `projects/aideway/frontend/suggestions.md` | Open MVP items (verify classification logic, duplicate-file processing, initial configuration and data, new prompt test) and frontend suggestions. |

Also available inside the application repo: `.agents/agents/hipaa-compliance-auditor.md`,
`security-checkpoint-reviewer.md`, `lighthouse-a11y-reviewer.md`, and skills under
`.agents/skills/` (`code-review`, `blast-radius`, `why`, `package-readme`). Use them where they
fit; they are not a substitute for reading the source.

## 7. Review phases

Phases are ordered by install impact: what stops the on-site install comes first, latent code
defects last. Work through them in order. Each phase ends with findings appended to
`review/findings.md` and its checklist items marked in `review/go-live-checklist.md`.

### Phase 0: Baseline

1. Record the HEAD commit, branch, and dirty state of `projects/aideway`, `projects/harness`,
   and `projects/docs`. Record versions: `projects/harness/VERSION`, `IMAGE_TAG_SERVER`,
   `gradle.properties`, Node and npm pins, the vLLM base image, PostgreSQL major.
2. Build and test what the sandbox allows: `./gradlew build` in `projects/aideway`
   (`:backend:detekt`, `:backend:test`, `:frontend:npmLint`, `:frontend:npmTest`,
   `:frontend:npmBuild`), `./run-tests.sh` in `projects/harness` (bats and Python tests; bats is
   not installed here, use `npx --yes bats` or install it), `python3 -B scripts/test_*.py` in
   `projects/aideway`. Record every failure and every test that was skipped for a missing
   dependency, model, or container. A skipped test is not a pass.
3. Note that `org.gradle.dependency.verification=off` is set project-wide. Treat it as a finding
   unless a release pipeline re-enables verification.
4. Map every prior finding (section 6) to a status row in `review/prior-findings-status.md`.

### Phase 1: The install path on the appliance (harness)

Walk `projects/docs/guides/getting-started/02.md` through `05.md` and `10.md` against the
harness source as if executing them on the Spark. For each command the guide gives, confirm it
exists in `projects/harness/bin/aideway` and `lib/*.sh` with the same verbs, flags, and output.

1. `setup host`, `setup todo`, `device`, `doctor`, `config`: `.env` parsing and quoting (harness
   issue 2), secrets generation, `AIDEWAY_HOSTNAME` derivation, operator group and GID.
2. Network: fixed address, DNS for HH services, firewall rules versus the port table in
   `03.md`, SSH keys and password disable, NTP via `timesyncd`.
3. TLS: `tls generate-csr`, `tls install`, `tls test`, `tls generate-selfsigned`, hostname and
   chain validation (harness issue 8), renewal, and what happens to the appliance if HH's CA is
   slow to issue (the guide's "If the certificate is not ready" path).
4. Keyset: `keys init`, TPM sealing via clevis, recovery passphrase, `AIDEWAY_TSS_GID`,
   LUKS and TPM proof (harness issue 5), what `RECOVERY` mode does, and who holds the passphrase.
5. Startup: `aideway up` prerequisites, `${VAR:?}` interpolations, systemd unit versus the CLI
   wrapper (harness issue 10), ordering after network and remote mounts, restart loops when the
   keyset cannot unseal, and `doctor` coverage (harness issue 11).
6. Images and model: cosign verification, tag consistency (harness issue 7), offline model
   install, model pin and hash, `HF_TOKEN` exposure (issue 15).
7. Resources: memory budget on unified memory (issue 13), vLLM IPC and shm (issue 14), the
   `83-memory-budget` and `86-vllm-tuning` audit checks against the shipped `.env` defaults.
8. Audit and logs: audit runner exit status (issue 9), journald retention (issue 17), drifted
   checks (issue 18), the support bundle gap (`issues-improvements.md` 1), rolling log files.
9. Backup: `backup create` encryption (issue 3), foreign restore (issue 4), restore safety
   (issue 6), restore on a replacement device, USB handling, and the first backup in `10.md`.
10. Build the operator manual (`aideway docs`) and confirm it renders without pandoc on the
    appliance; pandoc is absent here too.
11. Run the bats suite and read every script under `audit/checks/`.

### Phase 2: Email and MFA

Verify everything in section 4 in source and in the shipped configuration. Read
`service/types/notification/email/` (`EmailServiceType`, `EmailClient`, `LimitedEmailProvider`,
`EmailAuditQueue`, `EmailAuditJob`, `ServiceRegistrationResolver`, `smtp/SmtpServiceType`),
`service/ServiceTlsSettings.kt`, `ServiceTlsPolicy.kt`, `service/validation/`,
`system/api/EmailQueueApiController.kt` and the Keep queue dispatch, `io/session` (`MfaService`,
`PasswordLoginController`), `workflow/nodes/types/notify/email/`, `alert/`, and
`configuration/`. The SMTP provider is RelayKt, a TekFive library resolved through JitPack:
inspect the jar or sources in the Gradle cache, do not assume its behavior. Answer with evidence:

1. Does port 465 implicit SSL work, or only STARTTLS? Do "Use SSL" with 587, or STARTTLS with
   465, fail clearly at save or test time?
2. Is hostname verification enforced on the SMTP TLS connection? Does the CA Certificate field
   replace platform trust for SMTP? Does the pinned certificate apply to the SMTP socket?
3. Relay down at sign-in with MFA on: what the user sees, what alert fires, lockout and resend
   budgets, and how an administrator gets back in without email (CLI, `MFA_ENABLED` override,
   recovery).
4. Zero or two services with Use for System Emails: behavior and error text.
5. What the unexpected-result email contains: subject (filename?), body, attachments, PHI.
6. Queue: retry schedule, maximum attempts, meaning of failed, alert on failure, survival across
   server restart, `DispatchQueuedMessagesJob` interval and stall recovery.
7. Sender handling that trips Exchange or a Cisco gateway: From versus envelope sender, missing
   `Message-ID` or `Date`, EHLO name (a container hostname such as `server`), 8-bit content,
   line length, sender address not in an accepted domain.
8. Timeout defaults and whether a slow relay stalls the login request thread.
9. Whether a non-administrator can use Test service to send arbitrary mail.
10. Whether the Test service dialog uses the exact labels in `06.md` and `user/16.md`.
11. Logging on the send and failure paths against `.agents/rules/logging.md`: no address,
    subject, body, or credential.

### Phase 3: Network file share and the file trigger

Walk `getting-started/08.md` and Appendix B in `13.md` against
`workflow/nodes/types/triggers/file/` (`README.md`, `FileTriggerJob.kt`,
`WatchedDirectoryScanner.kt`, `ProtectedFileSystemRoots.kt`), the PDF path
(`transform/markdown`, `transform/analyze/file`, `document/`, `workflow/message/types/file`), and
the harness (`lib/setup.sh`, `lib/permissions.sh`, `lib/volume.sh`, `compose.yaml`,
`config/drop.cred.example`, `systemd/`, `audit/checks/70-file-perms.sh`,
`docs/manual/12-storage-layout.md`, `operation/07.md`). Answer with evidence:

1. Do the mount commands and fstab lines in `08.md` work on DGX OS: cifs options (`uid=1001`,
   `gid=<operator gid>`, `file_mode`, `dir_mode`, `vers=3.x`, `credentials=`, `_netdev`,
   `x-systemd.automount`, `nofail`), NFS uid mapping with `root_squash` or `all_squash`, and
   whether `cifs-utils` and `nfs-common` are present on DGX OS by default.
2. Credentials file: mode, owner, whether backups and audit checks cover it.
3. Mount propagation: if the share is mounted after the container started, does the container
   see it (`rprivate` versus `rslave`)? Confirm why the guide says "Recreate the server" and what
   the automount does after a reboot while the file server is down.
4. uid 1001 inside the container: does delete work on SMB with `uid=` mapping and on NFS with
   squash? Does Compose pass `AIDEWAY_OPERATOR_GID` as a supplementary group?
5. Rename-into-place and stability detection: inotify or polling, the stability window, and
   what happens if the pathology system writes in place.
6. Duplicates (`docs/todo/mvp.md`): dedupe by name, hash, or inode; a correction delivered with
   the same name; a re-delivered identical file.
7. First sweep records existing files without processing them: confirm, and state the
   consequence if the share already holds reports at go-live.
8. Delete after processing: node or trigger setting, on in the shipped workflow, behavior when
   the ACL denies delete, behavior when the run fails mid-way (file retried, left, or lost).
9. Non-PDF, hidden, temporary, lock, zero-byte, encrypted, scanned, and very large files;
   subdirectories; OCR and `PYTHON_BRIDGE_TIMEOUT_SECONDS`.
10. Share disconnect (`ENOENT`, `EIO`, stale NFS handle) and reconnect: Directory Not Found and
    Directory Not Readable states, alerts, and recovery without operator action.
11. Filename exposure: UI, alerts, email subjects, plaintext columns (prior finding #13).
12. Docker `read_only` root, `cap_drop`, `no-new-privileges`, AppArmor: any interaction that
    blocks writes or deletes on the bind mount.
13. Whether `doctor` or `audit` checks the drop mount and warns when it is absent.

### Phase 4: The pilot workflow, end to end

Trace Pathology Report Review through source, not documentation:

1. Provisioning: how the workflow, the HH Email Service, the Pathology Results dataset, and the
   prompt revision reach the appliance (section 3 gap). Confirm the graph, filter condition,
   recipient, sender, delete-after-processing setting, prompt revision, dataset revision, and
   service binding match the guide, and that the artifact is version-pinned and signed.
2. Classification before inference: the Kotlin rules plus Presidio NER pipeline, the active
   pipeline revision pinned at launch, tier assignment, what the vLLM service's tier allows it to
   see, and behavior when classification is unknown or incomplete.
3. Inference: prompt revision pinning, response schema enforcement, malformed or truncated JSON,
   reasoning parser behavior, context length versus long reports, concurrency limits
   (`VLLM_MAX_NUM_SEQS`, workflow max concurrent executions), vLLM restart during a run,
   heartbeat and max runtime defaults.
4. Decision and notification: a flagged report always produces both an email and an alert; a
   failed email produces an alert; nothing on the unflagged path is silent by mistake.
5. Dataset record: fields, encryption defaults, blind indexes, retention, what a Security
   Officer can search, and what an HH reader needs from the record.
6. Retention and purge: workflow messages, dataset, audit, logs, backups. PHI lifetime on the
   appliance must match what HH agreed to.
7. Failure branches on this graph: node failure, restart, resume, retry, cancel, with the
   execution-engine findings from the prior review in mind (the CRITICAL job-cleanup cascade
   first).
8. Run the flow in the dev container or Testcontainers with synthetic reports where the sandbox
   allows it. Never use real HH data.

### Phase 5: Documentation accuracy

For every step in `projects/docs/guides/getting-started/`, confirm the command, path, menu name,
dialog name, field name, default, and expected output against the current source and UI. Do the
same for the chapters the guide links to in the Installation, Operations, User, and Security
guides. Confirm screenshots show the current UI. Record every drift as a finding; a wrong command
in step 5 or 7 stops the install. Confirm the Appendix A worksheet covers everything the review
found HH must supply. Confirm the guides HH receives are built from the current source and
reference the same version as the appliance.

### Phase 6: Code, security, and HIPAA

Apply `hipaa-compliance` and `healthcare-phi-compliance` from `.agents/skills/` and the project's
own `docs/hipaa/`. Cover: authentication, sessions, JWT and refresh handling, MFA default,
password policy, roles and route gates versus `x-aideway-roles`, webhook and gateway exposure
(are MCP and A2A gateways reachable on the pilot appliance, and should they be?), PHI in logs,
URLs, browser storage, error strings, and audit events, encryption at rest and key handling,
audit chain integrity, data-audit coverage limits named in `security/REVIEW.md`, dependency
vulnerabilities (SCA against the GitHub Advisory Database for `gradle.lockfile` and
`package-lock.json`), secrets in the repos, CodeQL and CI gates, and the BAA position for every
service type that can be registered (OpenAI, Anthropic, Google endpoints exist in the code; confirm
they are absent or blocked on the pilot appliance). Re-verify every open HIGH and MEDIUM from the
prior reviews that is reachable in the HH configuration.

### Phase 7: Model and prompt evaluation

Apply `healthcare-eval-harness`. Establish how prompt v3 was evaluated: the corpus
(`:backend:classificationCorpus`, `scripts/feed-reports.sh`, any held-out pathology set), the
false-negative rate on unexpected findings, calibration of the confidence field, behavior on
reports without clinical history or CPT codes, and regression between v1, v2, and v3. If no
evaluation evidence exists, that is a HIGH finding for a clinical safety-net workflow. Record the
exact model name, revision, quantization, and hash that the appliance will run, and confirm the
harness pins it and that it fits the memory budget with the shipped vLLM settings.

### Phase 8: Frontend and HH user experience

Review what the `pathology.reports@hhsys.org` user sees daily: sign-in with MFA, Executions,
Alerts, Email Queue, Watched Directories, Datasets, and Notifications. Check accessibility
(`lighthouse-a11y-reviewer`), text size settings, both themes, session expiry behavior, and that
no PHI enters URLs, history state, or browser storage. Check CI type-checks the frontend (prior
finding 57).

### Phase 9: Release and supply chain

Review `.github/workflows/*.yml` in both repos: test gates that are report-only, mutable tags,
signature verification, generated API model checks, the release schema freeze
(`scripts/check_release_schema.py`), and whether the artifact HH receives is reproducible from a
tagged commit. Confirm the schema policy: AIDEWAY has never been released and schema changes
recreate the database. Before go-live the schema must be frozen and the upgrade path from that
baseline tested, or every update will require a database rebuild at HH.

### Phase 10: Install-week readiness

Produce the list the installer carries on site: the exact harness package and image versions to
bring, the model files and their hashes, the guides at the matching version, USB media contents,
the Appendix A worksheet pre-filled with everything already known, the values still needed from
HH (section 4 and Phase 3 lists), the recovery passphrase and `state.key` custody plan, a
rollback plan if the end-to-end test fails, and the verification steps that could not be done in
this sandbox and must be done on the appliance (GPU, TPM, LUKS, the real relay, the real share).

## 8. Severity, confidence, and finding format

Use the scale from `projects/aideway/docs/review.md`:

- CRITICAL: exploitable now, PHI exposure or auth bypass, or data loss. Also: a silent false
  negative path in the pilot workflow, any condition that locks HH out of the appliance, or a
  defect that stops the on-site install or the first end-to-end test.
- HIGH: security weakness or bug with real impact under realistic conditions, or an install or
  operations step that fails as documented.
- MEDIUM: correctness, performance, or security issue worth scheduling.
- LOW: hygiene, hardening, minor bugs, small improvements.

Every finding uses the format from `full-project-review.md`:

```
### [SEVERITY] Title
- Phase: 0-10
- Location: `project/path:line`
- Defect: one sentence
- Scenario: concrete state and event sequence leading to the wrong outcome
- Fix: concrete change
- Confidence: confirmed | plausible
- Tests: covered | none
- Prior: new | review.md 5.3 | full-project-review #77 | harness issue 13 (and current status)
```

Confirmed means reproduced in source or by running it. Plausible means the reasoning is sound but
not reproduced; say what would confirm it. Verify framework behavior (Keep, KViaSH, JFK, RelayKt,
PolyglotKt) against library sources or bytecode, not assumptions. Cite `path:line`. Quote the
guide text when a documentation finding depends on wording.

## 9. Deliverables

Write to `review/` in this repository:

| File | Content |
|---|---|
| `review/00-baseline.md` | Commits, versions, build and test results, skipped tests, environment limits. |
| `review/prior-findings-status.md` | One row per prior finding: id, severity, status (fixed, open, regressed), evidence. |
| `review/findings.md` | All new findings in the format above, sorted by severity, with a count table at the top. |
| `review/go-live-checklist.md` | Every item HH or TekFive must complete before go-live, grouped by owner (TekFive engineering, TekFive field install, HH network, HH mail, HH file server, HH pathology system, HH security). Each item has a verification step. |
| `review/open-questions.md` | Questions only HH or TekFive can answer, including the exact mail relay host, port, auth, certificate issuer, Exchange on-premises or Exchange Online, mailbox ownership, share protocol and service account, pathology system export mechanism, model name and revision, and who holds the recovery passphrase and `state.key`. |
| `review/install-kit.md` | Phase 10 output: what to bring, what HH must have ready, pre-filled worksheet, on-appliance verification steps, rollback plan. |
| `review/recommendation.md` | Go, go with conditions, or no-go, in one page: the blocking findings, the conditions, and the residual risks HH accepts. |

Finish every phase before writing the recommendation. If a phase is blocked (no GPU, no
container runtime, no network), say so in the baseline and in the recommendation, and list what
must be verified on the appliance itself.

## 10. Rules

- Do not change code, configuration, or documentation in `projects/` unless the user asks. If
  asked to fix something, follow `projects/aideway/AGENTS.md` (write the failing test first, no
  new third-party dependencies without consent, no coauthor lines, commit message rules).
- Never contact HH systems. DNS lookups of public records are the limit. Do not connect to
  `*.hhsys.org` hosts, the relay, the share, or the appliance.
- Never create, paste, or synthesize anything that looks like a real patient record with real
  identifiers. Test material is synthetic and marked as such.
- Do not put secrets, keys, passwords, or `.env` contents in the review files. Reference them by
  variable name.
- Log what was not reviewed as explicitly as what was. Scaling down scope is the user's call.
- Prefer the cold, exact statement over the reassuring one. No praise, no superlatives.
