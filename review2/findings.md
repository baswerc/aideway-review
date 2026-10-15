# Second review findings

Review date: 2026-10-15. Source baseline and test limits are in [00-baseline.md](00-baseline.md). Findings are sorted by HH pilot severity; IDs remain stable. Prior findings are rechecked individually in [prior-findings-status.md](prior-findings-status.md); overlapping issues are consolidated here. This is 36 decision-relevant findings, not the count of all source-history items.

| Severity | Count |
|---|---:|
| CRITICAL | 5 |
| HIGH | 22 |
| MEDIUM | 6 |
| LOW | 3 |
| **Total** | **36** |

Confirmed means established by source/locked-library inspection or a retained probe; it does not mean a live HH failure was observed. Tests: covered means a relevant behavior/probe/check was executed; it does not mean a fix exists. Tests: none means the specific failure scenario lacks an executed regression, even where surrounding suites pass. Every appliance-only limitation remains open.

### [CRITICAL] R2-06 — Failed restore can destroy the current database
- Phase: 1
- Location: `projects/harness/lib/backup.sh:519`; `projects/harness/lib/backup.sh:542`
- Defect: The pre-restore snapshot omits the database before `pg_restore --clean --create --exit-on-error` drops and rebuilds it.
- Scenario: An installer attempts rollback; restore fails after dropping the live database because of disk, schema or dump incompatibility. The saved configuration/key snapshot cannot recover the displaced database.
- Fix: Restore into an isolated database and validate before switching; retain and verify a separate current database backup before any destructive restore.
- Confidence: confirmed
- Tests: none
- Test evidence: No targeted execution for real interrupted PostgreSQL restore; harness tests mock the client.
- Prior: harness issue 6, open; elevated for the HH rollback/data-loss scenario under instructions section 8.

### [CRITICAL] R2-11 — Relay failure locks out MFA users and can roll back its own alert
- Phase: 2
- Location: `projects/aideway/backend/src/main/kotlin/org/aideway/io/session/SessionRoutes.kt:40`; `projects/aideway/backend/src/main/kotlin/org/aideway/system/SystemManager.kt:74`; `projects/aideway/backend/src/main/kotlin/org/aideway/alert/AlertGateway.kt:70`
- Defect: MFA sends synchronously inside the request transaction; a non-HTTP SMTP exception rolls back both the challenge and the attempted delivery-failure alert.
- Scenario: With MFA enabled and the only relay unavailable, login returns a server error and no token; the in-app alert recommended by the guide may not survive. Existing sessions and authenticated host access are separate recovery paths.
- Fix: Persist failure evidence outside the failed transaction, return an actionable safe error, and rehearse the documented MFA_ENABLED=false host override followed by immediate restoration after relay repair. Do not rely on an in-app page to recover a locked-out operator.
- Confidence: confirmed
- Tests: none
- Test evidence: No targeted execution for the full HTTP/real-relay failure path; exact Keep v1.0.15 interceptor bytecode and current call chain verified
- Prior: first review P2-01, open; recovery is documented in the harness README, so it is not correct to claim no break-glass mechanism exists

### [CRITICAL] R2-18 — Unreadable and image-only PDFs can reach inference as empty text
- Phase: 4
- Location: `projects/aideway/backend/src/main/kotlin/org/aideway/document/pdf/PdfBuilder.kt:48`; `projects/aideway/backend/src/main/kotlin/org/aideway/workflow/nodes/types/transform/markdown/FileMarkdownConverter.kt:36`
- Defect: OCR requires a readable configured tessdata directory, but shipped settings do not supply it and conversion accepts empty extraction.
- Scenario: A scanned report with a significant finding converts to zero characters and is sent toward analysis. A model response of unexpected_result=false then follows the silent branch; no readability gate forces human review. The local probe proves empty extraction, not a measured model false-negative rate.
- Fix: Configure and verify OCR, reject empty/insufficient extraction, and route unsupported/encrypted/oversized/unreadable input to an explicit review queue; test image-only and mixed-page reports on the release image.
- Confidence: confirmed
- Tests: covered
- Test evidence: Executed evidence/ClinicalProbe.java and clinical-probes.log: synthetic image-only and zero-byte PDFs both produce zero characters
- Prior: first review phase 4 OCR finding, open

### [CRITICAL] R2-19 — Analysis accepts incomplete JSON objects as successful clinical output
- Phase: 4
- Location: `projects/aideway/backend/src/main/kotlin/org/aideway/workflow/nodes/types/transform/analyze/file/AnalyzeFileNodeType.kt:116`; `projects/aideway/backend/dev/src/main/kotlin/org/aideway/dev/DevWorkflowSeeder.kt:903`
- Defect: Response handling checks JSON syntax/object shape but does not enforce the configured response schema or reject nonterminal finish reasons before publishing.
- Scenario: The model supplies {} with STOP or MAX_TOKENS; the production response handler returns Success in both probes. Missing/invalid decision fields must not be treated as a negative result by the graph or allowed to fail silently on its parallel dataset branch. Provider-side constrained decoding is not an application validation gate.
- Fix: Validate every required field/type/range against the pinned schema, require an acceptable completion reason, and route invalid output to review before any filter or dataset side effect.
- Confidence: confirmed
- Tests: covered
- Test evidence: Executed evidence/ClinicalProbe.java and clinical-probes.log; no live-model E2E claim
- Prior: first review phase 4 schema-validation finding, open

### [CRITICAL] R2-20 — Low-confidence negative results have no review branch
- Phase: 4
- Location: `projects/aideway/backend/dev/src/main/kotlin/org/aideway/dev/DevWorkflowSeeder.kt:903`; `projects/aideway/prompt/v3/system_prompt.md:90`
- Defect: The graph filters solely on unexpected_result=true and ignores confidence, missing indication and procedure_intent=unknown.
- Scenario: A report lacks ordering history/CPT information; the prompt permits uncertain classification but a low-confidence false result ends notification. The configuration has a silent uncertainty path in a safety-net workflow.
- Fix: Have HH define an abstention/review policy and route missing context, uncertainty and incomplete extraction to it; validate thresholds on held-out reports and preserve the ordinary expected-result path.
- Confidence: confirmed
- Tests: none
- Test evidence: No targeted execution for clinical sensitivity or confidence calibration
- Prior: first review phase 4 uncertainty finding, open

### [HIGH] R2-01 — Dependency verification is disabled in the release build
- Phase: 0
- Location: `projects/aideway/gradle.properties:2`
- Defect: Project-wide `org.gradle.dependency.verification=off` disables verification metadata unless a caller explicitly overrides it.
- Scenario: A release build resolves a modified dependency with the pinned coordinates without enforcing the committed verification hashes.
- Fix: Enable strict verification for release and CI, resolve metadata failures, and retain the successful strict build log.
- Confidence: confirmed
- Tests: covered
- Test evidence: strict override fails on the detekt plugin-marker POM; see evidence/dependency-verification.log.
- Prior: first review P6b-06/P9-04; still open, consolidated here.

### [HIGH] R2-02 — Audit failures can disappear, while correct shipped flags fail the gate
- Phase: 1
- Location: `projects/harness/lib/audit.sh:56`; `projects/harness/audit/checks/50-container-flags.sh:51`; `projects/harness/compose.yaml:37`; `projects/docs/guides/getting-started/05.md:14`
- Defect: The runner discards a crashing check's status, and the container check independently requires read-only roots for nginx and vLLM although Compose does not set them.
- Scenario: An empty-output check exits 42 and `audit --json` exits 0 with no finding; a healthy stack using the declared flags instead produces two `fail` findings, violating the guide's “audit must show no fail finding” rule. The `/tmp/aideway-work` warning is also stale because `/tmp` is tmpfs.
- Fix: Preserve check status, validate JSON/severity and require nonempty applicable results; reconcile each container's approved restrictions with the check and update the acceptance gate.
- Confidence: confirmed
- Tests: covered
- Test evidence: Executed isolated probes in `evidence/harness-probes.json`; no appliance run.
- Prior: harness issues 9 and 18 remain open; first review P1a-08/P1b-05. The first recommendation understated the container result as a warning.

### [HIGH] R2-03 — Configuration values are executed as shell text
- Phase: 1
- Location: `projects/harness/lib/common.sh:100`; `projects/harness/lib/config.sh:191`
- Defect: The CLI writes unquoted values that subsequent commands source as Bash code.
- Scenario: An operator enters a value containing spaces or shell metacharacters; the next privileged CLI invocation changes its meaning, fails, or executes it. The inert review marker was evaluated rather than preserved literally. Operator-group write access is an existing trust boundary, so this is not claimed as an unprivileged remote escalation.
- Fix: Use one non-executable parser/serializer compatible with Compose and reject malformed values; test punctuation round trips.
- Confidence: confirmed
- Tests: covered
- Test evidence: Executed the inert-value probe in `evidence/harness-probes.json` and source tracing.
- Prior: harness issue 2, open.

### [HIGH] R2-04 — Backup archives are plaintext even when encryption is requested
- Phase: 1
- Location: `projects/harness/lib/backup.sh:177`; `projects/harness/lib/backup.sh:237`; `projects/harness/lib/backup.sh:251`
- Defect: `--encrypt-to` warns and continues creating an ordinary compressed archive containing the database, recovery keyset, TLS private keys and runtime secrets.
- Scenario: The installer copies the first backup off the appliance believing the advertised encryption option protected it; archive confidentiality depends entirely on the destination and media controls. HMAC signing supplies no confidentiality.
- Fix: Implement authenticated encryption or fail the unsupported option; explicitly protect backup media and staging, and verify the restore procedure with separate recovery custody.
- Confidence: confirmed
- Tests: none
- Test evidence: No targeted execution for encrypted backup behavior; existing backup tests passed only the implemented plaintext path.
- Prior: harness issue 3, open.

### [HIGH] R2-05 — Replacement-device restore can bypass backup authentication
- Phase: 1
- Location: `projects/harness/lib/backup.sh:493`; `projects/harness/docs/manual/09-backups.md:101`
- Defect: `--allow-foreign-state-key` accepts an HMAC mismatch and trusts hashes from the unauthenticated manifest.
- Scenario: During replacement-device recovery an altered archive supplies both replacement payloads and matching hashes; the bypass accepts it. The manual's assurance that integrity checking remains is insufficient to establish authenticity.
- Fix: Bring the separately protected original verification key or use portable signatures; reject mismatched authentication before any restore write.
- Confidence: confirmed
- Tests: covered
- Test evidence: Executed the existing test that explicitly expects foreign-key bypass; this demonstrates behavior, not safety.
- Prior: harness issue 4, open; replacement-device recovery is in scope for HH.

### [HIGH] R2-07 — Default image tags and memory settings do not form a tested appliance configuration
- Phase: 1
- Location: `projects/harness/.env.example:58`; `projects/harness/lib/setup.sh:858`; `projects/harness/compose.yaml:234`; `projects/harness/audit/checks/83-memory-budget.sh:88`
- Defect: Generated configuration selects `latest` overrides that local builds need not create, and the four declared memory caps total 122.25 GiB without a verified Spark budget.
- Scenario: A fresh local-build installation cannot find the configured tags; after tag repair, an appliance with less than 122.25 GiB MemTotal fails its own audit. Caps are not reservations: their sum alone does not prove an OOM. vLLM, NER, PostgreSQL and OS still need a measured shared-memory budget.
- Fix: Publish one exact tag/digest manifest and use it for setup/import; tune the actual model with simultaneous NER and database load and record peak available memory and OOM evidence.
- Confidence: confirmed
- Evidence limits: confirmed for configuration mismatch and arithmetic; physical fit remains unverified.
- Tests: none
- Test evidence: on DGX hardware; existing configuration tests do not establish fit.
- Prior: harness issues 7 and 13, open; signed transfer import updates image tags and can avoid the local-build mismatch.

### [HIGH] R2-08 — TLS test depends on an unbundled image and does not enforce trust or hostname success
- Phase: 1
- Location: `projects/harness/lib/tls.sh:209`; `projects/harness/lib/tls.sh:646`; `projects/docs/guides/getting-started/04.md:40`
- Defect: `tls test` invokes mutable `alpine/openssl`, filters diagnostics, and omits `-verify_return_error` and hostname verification; install checks key match and expiry but not the site SAN or trust chain.
- Scenario: On the offline appliance the helper image is missing, so the documented test fails with its useful error filtered out; if present, a failed certificate verification may still exit successfully. Shell pipefail does propagate a Docker process failure, correcting older “always exits zero” wording.
- Fix: Use a verified local tool, supply the approved CA bundle and explicit hostname/verification flags, preserve diagnostics, and check the HH workstation trust separately.
- Confidence: confirmed
- Tests: none
- Test evidence: against the HH certificate; existing TLS tests cover parse/match/expiry only.
- Prior: harness issues 8 and 12, open residuals; backup now uses a verified-local-image path.

### [HIGH] R2-09 — Disk-encryption acceptance criteria conflict with the delivered guide
- Phase: 1
- Location: `projects/harness/audit/checks/15-disk-encryption.sh:59`; `projects/docs/guides/security/06.md:23`; `projects/docs/guides/getting-started/05.md:14`
- Defect: The audit requires dm-crypt while the security guide calls disk encryption optional and discusses firmware drive locking; its TPM success signal lists devices rather than enrolled LUKS tokens.
- Scenario: An approved unencrypted or firmware-locked appliance fails the getting-started “no fail” gate, or a LUKS volume with no TPM enrollment is reported enrolled merely because a TPM is available. Other secret-bearing paths may reside on different filesystems.
- Fix: Agree and document the actual HH storage requirement; check its mechanism and every sensitive filesystem, and prove reboot/unlock and recovery separately.
- Confidence: confirmed
- Tests: covered
- Test evidence: Executed existing audit tests for the implemented paths; actual disk protection is unverified.
- Prior: harness issue 5 remains open for coverage/enrollment; PostgreSQL's former wrong-path bug is fixed. Actual HH encryption status is unknown.

### [HIGH] R2-10 — Share-mount dependency can prevent automatic startup after maintenance
- Phase: 1
- Location: `projects/harness/systemd/aideway-harness.service:7`; `projects/harness/scripts/install-to-host.sh:108`; `projects/docs/guides/getting-started/08.md:149`; `projects/docs/guides/getting-started/11.md:65`
- Defect: The unit requires the report mount, has no restart policy, and the getting-started procedure does not verify that the unit is enabled before promising automatic recovery.
- Scenario: Follow the documented maintenance `aideway down`, reboot while the file server is unavailable, and the required mount fails. The stopped stack cannot deliver the in-app directory alert promised by the guide; recovery needs an explicit service start after the mount works. Docker's independent `unless-stopped` behavior makes other reboot sequences deployment-dependent.
- Fix: Verify enablement in factory acceptance and on site; separate application availability from share readiness or implement/test a deliberate retry/recovery policy. Test both outage-at-boot and outage-after-start.
- Confidence: confirmed
- Evidence limits: confirmed for unit/guide mismatch; full boot behavior must be reproduced on the appliance.
- Tests: none
- Test evidence: No targeted execution for a real boot with a failed remote mount.
- Prior: first review P3-02/P1a-03; retained with a narrower, concrete shutdown sequence. The old Compose-override defect (harness issue 10) is fixed.

### [HIGH] R2-12 — Queued email does not recheck service authorization at dispatch
- Phase: 2
- Location: `projects/aideway/backend/src/main/kotlin/org/aideway/service/types/notification/email/ServiceRegistrationResolver.kt:17`
- Defect: The queued resolver reconstructs an endpoint without checking active status, current send tier or the secure-transport policy used by initial client creation.
- Scenario: An HH administrator disables or reclassifies the relay while messages are queued; a later retry still resolves it and can send PHI under changed settings.
- Fix: Persist the queued classification and re-authorize service activity, tier and transport immediately before each send; retain a safe terminal reason.
- Confidence: confirmed
- Tests: none
- Test evidence: No targeted execution for queue-time policy revocation
- Prior: first review phase 2 queue-policy finding, open

### [HIGH] R2-13 — Final workflow email failure produces no application alert
- Phase: 2
- Location: `projects/aideway/backend/src/main/kotlin/org/aideway/service/types/notification/email/EmailClient.kt:23`; `projects/aideway/backend/src/main/kotlin/org/aideway/Application.kt:65`
- Defect: The node queues directly through RelayKt and its terminal delivery job is not wired to the application alert/audit wrapper.
- Scenario: A flagged report completes its graph once mail is queued; recoverable failures can exhaust five attempts, while SendFailedException is immediately nonrecoverable (including recipient deferral) and stale SENDING becomes TIMED_OUT. There is no dedicated Administration > Alerts event to tell HH the result notification never arrived.
- Fix: Register and exercise a terminal-delivery handler that alerts independently of the failed relay, records transmission evidence, and links queue/execution identifiers; make queue acceptance distinct from delivery in the UI. Classify recipient 4xx versus permanent failures and reconcile uncertain sends before any retry.
- Confidence: confirmed
- Tests: none
- Test evidence: exact RelayKt 1.0.9 SmtpProvider/MessageQueueProcessor/SendQueuedMessageJob bytecode establishes failure classes; no real-relay terminal-alert regression test
- Prior: first review phase 2 queue-failure finding and security REVIEW data-audit limit, open

### [HIGH] R2-14 — An absent report mount is accepted as an empty healthy directory
- Phase: 3
- Location: `projects/harness/lib/doctor.sh:1`; `projects/harness/compose.yaml:218`; `projects/aideway/backend/src/main/kotlin/org/aideway/workflow/nodes/types/triggers/file/FileTriggerJob.kt:315`
- Defect: Host preflight and audit do not prove that the expected remote share is mounted, and the bind mount defaults to rprivate.
- Scenario: Start the server against the local placeholder before mounting SMB/NFS: the trigger can sweep an empty directory successfully while new reports arrive on an unseen mount. Mount replacement may also need container recreation.
- Fix: Check mount source/type and a synthetic read/delete probe; recreate the server after mounting as the guide says, and monitor time since the last expected report independently of sweep success.
- Confidence: confirmed
- Tests: none
- Test evidence: source and mount configuration; no real SMB/NFS outage run
- Prior: first review phase 3 missing-mount finding, open

### [HIGH] R2-15 — Delete-after-processing actually deletes after durable launch
- Phase: 3
- Location: `projects/aideway/backend/src/main/kotlin/org/aideway/workflow/nodes/types/triggers/file/FileTriggerJob.kt:501`; `projects/aideway/backend/dev/src/main/kotlin/org/aideway/dev/DevWorkflowSeeder.kt:816`
- Defect: The trigger requests deletion after persisting the launch, before analysis, dataset storage or email delivery succeeds.
- Scenario: A new report launches and disappears from the share, then inference fails. The trigger does not resubmit it; an operator must recover/restart from retained execution input or redeliver from the pathology system. This is not proven loss of the only copy.
- Fix: Document the actual acknowledgment point or delay source deletion until the agreed durable processing milestone; provide a tested quarantine/replay procedure and independent failure monitoring.
- Confidence: confirmed
- Tests: none
- Test evidence: existing file-trigger tests cover launch/deletion; no full clinical failure/recovery test
- Prior: first review phase 3 deletion finding, open with narrower data-loss claim

### [HIGH] R2-16 — Oversized reports are marked handled without a failed sweep
- Phase: 3
- Location: `projects/aideway/backend/src/main/kotlin/org/aideway/workflow/nodes/types/triggers/file/FileTriggerJob.kt:340`
- Defect: A file over the configured cap is counted as oversized and recorded without launch, while the sweep can remain SWEPT.
- Scenario: An HH report exceeds the byte limit, remains on the share and receives no execution; staff interpreting successful sweeps as successful ingestion miss it.
- Fix: Expose an actionable per-file rejection/quarantine event with a safe identifier and a queue that reconciles every source report to an execution.
- Confidence: confirmed
- Tests: covered
- Test evidence: source branch covered by file-trigger tests; no clinical reconciliation gate
- Prior: first review phase 3 oversized-report finding, open

### [HIGH] R2-17 — The production HH configuration is not established by the reviewed artifacts
- Phase: 4
- Location: `projects/aideway/backend/dev/src/main/kotlin/org/aideway/dev/DevSeedCatalog.kt:1`; `projects/aideway/backend/dev/src/main/kotlin/org/aideway/dev/DevWorkflowSeeder.kt:800`; `projects/aideway/backend/src/main/kotlin/org/aideway/harness/update/README.md:1`
- Defect: The guide assumes a shipped workflow, service, user, dataset and prompt, but the available seeder is development-only and the offline importer requires existing local users/services and leaves imported definitions in draft.
- Scenario: A production appliance provisioned only by the documented installation steps lacks an evidenced published HH graph. The development graph watches /opt/drop, sends to system@aideway.local, and uses a personal notification node where the guide promises Administration > Alerts. Its fixed urgency CATEGORY_2 is not a current NotificationUrgency enum value (DevWorkflowSeeder.kt:974; notification/NotificationUrgency.kt:16), so that branch also needs correction. No reviewed signed HH manifest resolves these differences.
- Fix: Produce and validate a signed site bundle and explicit provisioning record: local services/users, /mnt/drop, recipient, prompt/schema hashes, published revisions, service bindings, policy tiers, deletion behavior and graph digest. Verify the actual delivered artifact; absence here does not prove it exists nowhere.
- Confidence: confirmed
- Tests: none
- Test evidence: offline-import integration tests pass for their narrower contract; actual HH bundle unavailable
- Prior: instructions section 3 provisioning gap; first review phase 4 finding, open

### [HIGH] R2-21 — Notification and dataset failure policies can leave a completed-looking run incomplete
- Phase: 4
- Location: `projects/aideway/backend/dev/src/main/kotlin/org/aideway/dev/DevWorkflowSeeder.kt:948`; `projects/aideway/backend/dev/src/main/kotlin/org/aideway/dev/DevWorkflowSeeder.kt:1119`
- Defect: Email and dataset nodes use CONTINUE/CONTINUE_WORKFLOW, and recording and decision are parallel branches.
- Scenario: A significant report is flagged but dataset insertion fails, or notification enqueue fails; successful sibling branches do not guarantee the guide promise of a record and both notifications. An execution status alone is insufficient evidence of all outcomes.
- Fix: Require and reconcile durable report record, human-visible alert and delivery outcome; explicitly fail or quarantine missing required outcomes and show branch failures in the daily checklist.
- Confidence: confirmed
- Tests: none
- Test evidence: execution policy tests exist; no asserted HH end-to-end outcome contract
- Prior: first review phase 4 graph failure-policy finding, open

### [HIGH] R2-23 — Recovery runbooks contain commands that the CLI rejects
- Phase: 5
- Location: `projects/harness/docs/manual/11-emergency.md:33`; `projects/harness/docs/manual/11-emergency.md:77`; `projects/docs/guides/getting-started/12.md:61`
- Defect: Emergency backup uses unsupported --label; log collection uses logs --export instead of logs export --out; the decryption troubleshooting command gives several arguments to a single-value --only option.
- Scenario: An installer following incident or decryption recovery instructions stops at argument parsing. The audit command failure was reproduced locally.
- Fix: Replace commands with checked CLI forms; run each audit prefix separately and use aideway logs export --out. Exercise the complete recovery chapter on a disposable appliance.
- Confidence: confirmed
- Tests: covered
- Test evidence: No targeted execution for multi-prefix audit parsing by evidence/harness-probes.json; existing CLI tests pass their supported syntax
- Prior: harness improvements 1/3 and first review documentation findings, open

### [HIGH] R2-25 — Host account changes bypass normal session revocation and audit
- Phase: 6
- Location: `projects/aideway/backend/src/main/kotlin/org/aideway/harness/AdminCli.kt:234`; `projects/aideway/backend/src/main/kotlin/org/aideway/io/session/RequireValidSessionGuard.kt:47`
- Defect: CLI deactivation, password and role changes update rows without the web paths' session-revocation and actor-audit behavior.
- Scenario: During incident recovery the operator changes a password or removes privileges through the documented CLI. An existing access-token session remains usable until normal refresh/expiry or separate revocation, and the application audit lacks the operator mutation.
- Fix: Share the audited account-mutation service between web and CLI; revoke sessions transactionally and record a named operator reason. Until fixed, explicitly revoke sessions through the supported UI as part of recovery.
- Confidence: confirmed
- Tests: none
- Test evidence: normal web revocation is tested; CLI parity is not
- Prior: review.md 2.10 and full-project-review #78, open

### [HIGH] R2-30 — No clinical sensitivity or confidence-calibration evidence accompanies prompt v3
- Phase: 7
- Location: `projects/aideway/prompt/v3/system_prompt.md:73`; `projects/aideway/docs/todo/mvp.md:4`; `projects/aideway/backend/build.gradle.kts:357`
- Defect: The available corpus checks PHI recognition, redaction and restoration, not unexpected pathology outcomes, and no held-out v1/v2/v3 clinical evaluation is recorded.
- Scenario: Unit tests and a passing 15-case classification corpus are used as readiness evidence although the safety-net's false-negative rate, missing-context behavior and confidence calibration remain unknown.
- Fix: Have HH clinical reviewers label an approved evaluation set, freeze model/prompt/schema/OCR settings, measure false negatives and confidence/abstention behavior by subgroup, compare revisions and obtain documented acceptance before enabling real intake.
- Confidence: confirmed
- Evidence limits: confirmed for missing repository evidence; external evidence may exist
- Tests: none
- Test evidence: 15/15 non-NER corpus cases pass; all 14 NER integration tests skip here; no clinical accuracy test run
- Prior: MVP items 1/4 and first review phase 7, open

### [HIGH] R2-31 — Model and prompt identity are not pinned to the clinical configuration
- Phase: 7
- Location: `projects/harness/lib/models.sh:80`; `projects/harness/lib/models.sh:135`; `projects/aideway/backend/src/main/python/ner/models.yaml:4`; `projects/aideway/backend/dev/src/main/resources/seed/pathology-report/system-prompt.md:1`
- Defect: Model verification checks file presence, NER revision/digest fields are empty, and the development prompt resource matches v2 rather than v3.
- Scenario: A rebuild/download from main or a site import changes inference/classification behavior without a stable model manifest; an installer believing the guide's v3 claim may run a different prompt. The exact HH model is not evidenced by this checkout.
- Fix: Approve a model repository commit, quantization, full-file hashes, image digest and tokenizer/chat template; pin NER weights too. Bind prompt/schema hashes and reasoning settings to the published workflow and acceptance results.
- Confidence: confirmed
- Tests: covered
- Test evidence: source/hash comparison retained; no actual Spark model verification
- Prior: harness issue 19 and first review phase 7 pinning finding, open

### [HIGH] R2-35 — Release is blocked by the unfrozen database baseline
- Phase: 9
- Location: `projects/aideway/backend/src/main/kotlin/org/aideway/db/migrations/V1_Init.kt:1`; `projects/aideway/scripts/check_release_schema.py:1`; `projects/aideway/.github/workflows/release.yml:75`
- Defect: The current baseline migration imports live application schema, and the release guard rejects it.
- Scenario: The present checkout cannot pass its own release preparation gate; database recreation during pre-release development is not an acceptable upgrade plan for retained HH records.
- Fix: Freeze the first released schema/seed SQL, establish a versioned migration baseline, and test upgrades plus restore/rollback with representative synthetic records before shipping. Preserve the guard.
- Confidence: confirmed
- Tests: covered
- Test evidence: scripts/check_release_schema.py exits 1; guard regression tests pass
- Prior: full-project-review #68 and first review phase 9 baseline finding, open; the guard is a working protection

### [HIGH] R2-36 — Signing does not provide a complete reproducible release acceptance gate
- Phase: 9
- Location: `projects/aideway/.github/workflows/release.yml:33`; `projects/aideway/.github/workflows/release.yml:330`; `projects/harness/lib/models.sh:135`
- Defect: Release bases/actions/installers use mutable references, vulnerability scans are report-only, and no complete tested appliance manifest ties all repos, models, guides and site definitions together.
- Scenario: A signed application image is built from a different base or paired with different model/harness/docs artifacts; signature success alone cannot establish the clinically accepted configuration.
- Fix: Publish a signed manifest of exact commits, image digests, dependencies, model/prompt hashes and guide build; gate unresolved reachable vulnerabilities and archive successful offline factory acceptance plus migration tests.
- Confidence: confirmed
- Tests: none
- Test evidence: CI and signing source reviewed; no final artifact or remote CI run supplied
- Prior: full-project-review #58/#59, harness issue 19 and first review phase 9, open
### [MEDIUM] R2-22 — Replay can repeat clinical side effects and default retention is indefinite
- Phase: 4
- Location: `projects/aideway/backend/src/main/kotlin/org/aideway/workflow/execution/engine/NodeRunner.kt:545`; `projects/aideway/backend/src/main/kotlin/org/aideway/workflow/Workflow.kt:21`
- Defect: At-least-once processing is not paired with report-level idempotency, and workflow/dataset retention require explicit site configuration.
- Scenario: An interrupted or manually restarted execution repeats email or dataset insertion; retained messages, reasoning, records and backups then outlive the intended HH retention period if defaults are accepted.
- Fix: Assign a stable non-PHI report/correction identity and idempotent side-effect keys; document each retention layer and test purge plus backup expiry against HH policy.
- Confidence: confirmed
- Tests: none
- Test evidence: engine replay/retention tests exist; no HH policy or correction reconciliation test
- Prior: workflow-execution-review #10 and first review phase 4 retention finding, open

### [MEDIUM] R2-24 — Customer guides and screenshots do not identify one verified release
- Phase: 5
- Location: `projects/docs/guides/user/16.md:19`; `projects/docs/guides/installation/03.md:6`; `projects/docs/guides/getting-started/13.md:8`
- Defect: Guides retain nonexistent controls, broken chapter links, stale commands/defaults and no complete release identity record.
- Scenario: An operator searches for Require TLS or an editable system sender under Settings, follows one of 24 missing administration links, or compares an unversioned screenshot with a different shipped graph; the handoff cannot establish which images/model/prompt were accepted.
- Fix: Regenerate guides/screenshots from the accepted release and add its digest manifest to Appendix A. Use Secure Connection/Use STARTTLS/Use SSL accurately; sender is operator-managed. Update Create to Save, the local PostgreSQL backup helper, key-pin renewal wording, and abnormal-versus-unexpected notification descriptions. The intended decision axis is unexpectedness; expected abnormal findings are not the same condition.
- Confidence: confirmed
- Tests: covered
- Test evidence: Executed source comparison and evidence/docs-link-check.json; no live UI screenshot equivalence test
- Prior: first review phase 5 drift findings, open

### [MEDIUM] R2-26 — PHI-bearing search and diagnostics can escape the intended data stores
- Phase: 6
- Location: `projects/aideway/frontend/src/features/notifications/NotificationsPage.tsx:66`; `projects/aideway/frontend/src/shared/ui/usePagedQuery.ts:110`; `projects/aideway/backend/src/main/kotlin/org/aideway/workflow/execution/engine/WorkflowExecutionJob.kt:163`
- Defect: Search terms are serialized into browser/API URLs, and generic exception paths retain unredacted causes in operational logs.
- Scenario: A clinician searches a report name or identifier; it persists in history and may reach proxy access logs. A provider exception containing submitted content can also be recorded in job logs/alert stack traces. No real PHI disclosure was observed in this sandbox.
- Fix: Keep sensitive searches in request bodies and memory, redact operational diagnostics at their source, and test canary markers across URLs/logs/exports; apply approved retention to the remaining PHI-bearing stores.
- Confidence: confirmed
- Evidence limits: confirmed for URL behavior; plausible for provider-supplied PHI in generic diagnostics
- Tests: none
- Test evidence: frontend search tests and source paths; no complete log-canary gate
- Prior: full-project-review #10/#34, workflow-execution-review L6, open

### [MEDIUM] R2-27 — Shared sign-in and unchecked MFA configuration weaken handoff controls
- Phase: 6
- Location: `projects/docs/guides/getting-started/05.md:23`; `projects/docs/guides/getting-started/10.md:12`; `projects/aideway/backend/src/main/kotlin/org/aideway/io/session/MfaService.kt:27`
- Defect: The pilot uses a shared mailbox identity, MFA defaults off, and the host audit does not enforce its approved final value or named-user access.
- Scenario: Several staff use the same login and OTP mailbox, so audit records identify the shared account; a missed/malformed enablement value can leave password-only access. Administrator alone also does not grant Security Officer compliance access.
- Fix: Create named accounts with approved roles and private MFA delivery, force password change, verify MFA by a fresh login and negative test, and explicitly assign an audit-review owner with sufficient clearance.
- Confidence: confirmed
- Evidence limits: confirmed for defaults and guide identity; delivered accounts unknown
- Tests: none
- Test evidence: authentication tests pass; no HH identity/role acceptance run
- Prior: review.md 11.5/#39 and first review shared-account finding, open

### [MEDIUM] R2-32 — Watched-directory cards can hide a failed sweep
- Phase: 8
- Location: `projects/aideway/frontend/src/features/triggers/WatchedDirectoriesPage.tsx:79`
- Defect: Cards show trigger validation problems and last-sweep time but omit last runtime sweep result.
- Scenario: The directory validates Ready, then reading/deleting files fails. Its card can still look active and recently swept; HH staff following the daily list check miss the runtime failure unless they open details.
- Fix: Show last sweep outcome, rejected-file counts and backlog age on the list and link to the failing execution; update the daily-check wording.
- Confidence: confirmed
- Tests: none
- Test evidence: component source; no browser/live-share run
- Prior: first review phase 8 watched-directory finding, open

### [MEDIUM] R2-33 — Execution status relies on color and small low-contrast badges
- Phase: 8
- Location: `projects/aideway/frontend/src/shared/ui/ExecutionCard.tsx:33`; `projects/aideway/frontend/src/styles/components.css:7171`; `projects/aideway/frontend/src/styles/base.css:112`
- Defect: Execution cards display revision/ID rather than visible status words, and several 11px status color combinations have insufficient text contrast.
- Scenario: A user with reduced color discrimination sees identical ID pills for failed and completed work; tooltip/aria labels do not supply a persistent visible state. Light-theme green/amber and failed red need contrast review.
- Fix: Display status text/icons alongside color, correct theme token contrast, and test keyboard navigation and 200%/400% zoom on all daily pages.
- Confidence: confirmed
- Evidence limits: confirmed for markup/CSS; rendered-browser audit pending
- Tests: covered
- Test evidence: source contrast calculations in evidence/contrast.json; no Lighthouse score claimed
- Prior: first review phase 8 accessibility findings, open

### [LOW] R2-28 — Cloud-service governance is configurable and prompt tests bypass classification
- Phase: 6
- Location: `projects/aideway/backend/src/main/kotlin/org/aideway/service/ServiceTypes.kt:15`; `projects/aideway/backend/src/main/kotlin/org/aideway/service/validation/ServiceValidator.kt:127`; `projects/aideway/backend/src/main/kotlin/org/aideway/intelligence/prompt/PromptTestRunJob.kt:60`
- Defect: Cloud providers remain registrable, missing/pending BAAs are warnings, and prompt/service test input is sent without normal workflow classification.
- Scenario: A future administrator registers a cloud endpoint or tests PHI against a lower-tier service. This is conditional and not established as reachable in the intended local-only HH pilot.
- Fix: Remove/deactivate unapproved services, verify outbound policy, and prohibit PHI in test dialogs until classification/authorization covers them; approve every actual service and BAA relationship.
- Confidence: confirmed
- Evidence limits: confirmed for code paths; no cloud service proven on HH
- Tests: none
- Test evidence: existing warning tests cover UI behavior, not an enforcement gate
- Prior: review.md 5.12/full-project-review #1 and security REVIEW limits, open; LOW under pilot reachability rule

### [LOW] R2-29 — Locked dependencies contain advisories requiring release-specific triage
- Phase: 6
- Location: `projects/aideway/backend/gradle.lockfile:16`; `projects/aideway/frontend/package-lock.json:1`
- Defect: Fresh GHSA-backed scans identify affected locked versions, while exact exploit prerequisites differ from the HH runtime.
- Scenario: Scans report 28 affected Maven coordinates and 19 npm dependency nodes. PDF.js scripting is not instantiated by the current canvas/text viewer and CSP is present; Jackson async/DataInput and Jetty PathMapped prerequisites were not established in the pilot. Scanner severities alone do not prove application compromise.
- Fix: Update affected packages and review the built-image SBOM; document precise runtime reachability and any exceptions. Use evidence/dependency-review.md and retained advisory records, not the first review's unqualified PDF.js/Jackson exploit claims.
- Confidence: confirmed
- Evidence limits: confirmed for version matches; exploitability conditional
- Tests: covered
- Test evidence: fresh npm audit and 376-coordinate OSV/GHSA lookup; no exploit payloads run
- Prior: review.md 11.13/#46 and first review dependency findings, open with corrected reachability

### [LOW] R2-34 — MFA resend copy can claim delivery for an invalid challenge
- Phase: 8
- Location: `projects/aideway/backend/src/main/kotlin/org/aideway/io/session/login/PasswordLoginController.kt:298`; `projects/aideway/frontend/src/features/profile/LoginPage.tsx:167`
- Defect: The endpoint intentionally returns 204 for missing/invalid challenges, and the UI interprets every 204 as a sent code.
- Scenario: An expired or deleted challenge is resent and the user is told a new code was sent; actual SMTP exceptions do propagate and the UI displays an error, correcting the first review's broader failure claim.
- Fix: Use neutral anti-enumeration wording and provide restart-sign-in guidance; preserve a clear error for real delivery failure.
- Confidence: confirmed
- Tests: none
- Test evidence: source/controller contract; login tests pass
- Prior: first review phase 8 resend finding, narrowed

