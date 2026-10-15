# Go-live checklist

All boxes remain open: local source/tests are not HH acceptance. Owners must attach dated evidence for the exact release manifest. IDs refer to [findings.md](findings.md); [install-kit.md](install-kit.md) defines the acceptance matrix. An unavailable site check is not a pass.

## TekFive engineering

- [ ] **E01 — Freeze the database baseline and prove upgrades.** Pass the schema guard; migrate a synthetic populated baseline; interrupt/retry and recover without missing records. Preserve before/after counts. R2-35.
- [ ] **E02 — Produce a verifiable release.** Resolve strict dependency verification, build/test all components, triage GHSA matches by use, scan release images/OS/Python, and supply signed image/model/package/guide manifests plus CI and required-check evidence. R2-01/R2-29/R2-36.
- [ ] **E03 — Prove HH provisioning.** Rehearse fresh production setup with named users/roles, exactly one system SMTP service, local vLLM, tiers, published dataset/prompt/workflow revisions, `/mnt/drop` and the approved recipient. Export graph/configuration identity without secrets. R2-17/R2-31.
- [ ] **E04 — Reject invalid analysis input/output.** Test empty/scanned/mixed/encrypted/corrupt/oversized PDFs, `{}`, null/wrong-type decision fields and MAX_TOKENS. Require an explicit failure/review disposition, working OCR, and bounded conversion time/memory. R2-16/R2-18/R2-19.
- [ ] **E05 — Implement clinical uncertainty handling.** Route missing history/CPT, conflicting intent and low-confidence negatives to an approved review queue. Archive version comparisons, false-negative denominators and calibration for the actual model. R2-20/R2-30.
- [ ] **E06 — Enforce required outcomes.** Prove durable result/disposition for every report and both agreed notifications for flagged reports. Test dataset failure, invalid notification urgency, enqueue failure and CONTINUE branches. R2-17/R2-21.
- [ ] **E07 — Make mail failure actionable.** Test outage, recipient 4xx/5xx, partial delivery, restart during send, queued-policy revocation and retry exhaustion. Reauthorize delayed sends and provide independently monitored failure alerts. Distinguish SENT, FAILED and TIMED_OUT. R2-12/R2-13.
- [ ] **E08 — Prove MFA recovery.** Preserve failure evidence outside the failed request transaction; rehearse host recovery after every browser session has expired, then restore MFA and prove fresh sign-in. R2-11.
- [ ] **E09 — Correct harness acceptance.** Fail audit crashes/malformed output; reconcile container/tmpfs checks, `.env` serialization, image tags, TLS trust/hostname verification and disk-encryption criteria. Test punctuation round trips without execution. R2-02/R2-03/R2-07/R2-08/R2-09.
- [ ] **E10 — Make backup/restore safe.** Reject unsupported encryption promises, authenticate on replacement hardware without bypass, restore into an isolated target, and prove failure preserves the current database. R2-04/R2-05/R2-06.
- [ ] **E11 — Reconcile ingestion.** Test absent mounts, startup backlog, oversized files, delete denial, amendments and redelivery; document deletion acknowledgment and implement safe quarantine/replay and report-level idempotency. R2-14/R2-15/R2-16/R2-22.
- [ ] **E12 — Close incident-access and PHI gaps.** Audit/revoke sessions on CLI account changes; run URL/log canaries, delivery-audit and tier tests; prove separate retention/purge policies. R2-25/R2-26/R2-27/R2-28.
- [ ] **E13 — Correct docs and daily UI.** Execute emergency commands against the release, repair links/labels, expose sweep failures and visible execution states, and complete keyboard/zoom/contrast checks. R2-23/R2-24/R2-32/R2-33/R2-34.

## TekFive field install

- [ ] **I01 — Match the manifest.** Record serial, DGX OS/driver/CUDA, image digests, harness/docs hashes, model/prompt/schema hashes and site revision. Neither `latest`, `main` nor model-file presence establishes identity. R2-31/R2-36.
- [ ] **I02 — Inspect physical readiness.** Confirm rack kit receipt/fit, ventilation, power/UPS and connections. The invoice is not a receipt.
- [ ] **I03 — Prove offline completeness.** With external access disabled, verify/install packages, images, models, OCR/NER and share clients. Run doctor/status/audit; retain every failure/skip. R2-07/R2-08/R2-23.
- [ ] **I04 — Verify host protection/custody.** Record effective SSH/root policy, operator GID/access, storage encryption, TPM sealing and recovery rehearsal. Keep secrets out of logs. R2-09/R2-27.
- [ ] **I05 — Verify TLS from HH workstations.** Prove SAN, chain, trust, expiry and redirect using approved tools; assign web and internal-certificate renewal owners. R2-08.
- [ ] **I06 — Rehearse boot/outage recovery.** Verify unit enablement; test normal reboot, maintenance down/reboot, share absent at boot and later recovery, and failed unseal. R2-10/R2-14.
- [ ] **I07 — Measure simultaneous load.** Run vLLM, NER, OCR and PostgreSQL at expected peak volume; record available memory, GPU use, OOM events, queue age and latency. Tune timeouts/concurrency from measurements. R2-07/R2-30/R2-31.
- [ ] **I08 — Complete the synthetic matrix.** Reconcile input IDs to execution/result/queue IDs and mailbox receipt; every failure requires a disposition. Real intake remains disabled until approval. R2-18–R2-22.
- [ ] **I09 — Prove replacement recovery.** Use encrypted media, verify archive authenticity, restore to a separate target and reconcile data/audit chains. Retain a separate pre-change database backup. R2-04–R2-06.
- [ ] **I10 — Demonstrate handoff.** Named staff demonstrate sign-in, queue/alert/sweep inspection, recovery, safe export, retention and backup verification; record escalation contacts/targets. R2-11/R2-13/R2-23/R2-25/R2-32.

## HH network

- [ ] **N01 — Supply address/DNS/time details.** Verify fixed IP/gateway/VLAN and name resolution from appliance/workstations; record actual MAC and NTP sources rather than guide examples.
- [ ] **N02 — Prove effective firewall policy.** Test approved HTTPS/SSH sources, Docker isolation and outbound allowlist for mail/share/DNS/NTP/maintenance. Test container traffic as well as host rules. R2-28.
- [ ] **N03 — Supply trust and maintenance dependencies.** Deliver web certificate/chain, workstation trust, renewal owner and approved offline package/update path. Verify reboot-time DNS/NTP. R2-08.

## HH mail

- [ ] **M01 — Approve the connector.** Record real relay FQDN, port, STARTTLS or SSL, authentication/source-IP policy, sender authorization, issuer/SAN and renewal procedure; test actual TLS/CA/pin behavior.
- [ ] **M02 — Prove receipt.** Deliver service test, fresh MFA and flagged synthetic result. Check envelope sender, EHLO, Message-ID/Date, quarantine and mailbox receipt; queue SENT alone is insufficient.
- [ ] **M03 — Approve PHI and forwarding.** Approve reason/summary content, membership, external-forwarding restrictions, retention and shift coverage. No PHI in filenames/subjects. R2-26/R2-27.
- [ ] **M04 — Exercise failure/rotation.** Test credential/certificate changes, outage, 4xx deferral, permanent rejection and backlog; verify independent alert and timely recovery. R2-11–R2-13.

## HH file server

- [ ] **F01 — Supply the share contract.** Confirm actual SMB/NFS endpoint, security/encryption mode, principal/export identity and ACLs. Prove UID 1001 and actual GID can read/rename/delete only the approved folder; test squash mapping.
- [ ] **F02 — Verify mount lifecycle.** Provide client packages, protect credentials root-owned 0600, mount before server recreation, and prove expected source/type inside/outside the container after disconnect and reboot. R2-10/R2-14.
- [ ] **F03 — Account for backlog/rejections.** Test existing files, placeholder directory, large files, delete denial, stale handles and reconnect; supply a source inventory for reconciliation. R2-14–R2-16.

## HH pathology system and clinical owner

- [ ] **P01 — Approve producer behavior.** Document export trigger, atomic rename, non-PHI filename, volume/size/page limits, report/correction identity, source retention and redelivery.
- [ ] **P02 — Approve clinical evaluation.** Name reviewers, truth-set custodian, sensitivity/false-negative bound, abstention rule and response time; sign results for the immutable release. R2-20/R2-30/R2-31.
- [ ] **P03 — Reconcile outcomes.** Test expected abnormal, unexpected, benign, uncertain, multiple specimens and amendments. Input count must equal executions plus explicitly rejected/quarantined items, with a result/disposition for every accepted report. R2-16/R2-18–R2-22.
- [ ] **P04 — Assign daily coverage.** Name mailbox/notification/execution/queue reviewers by shift; define escalation, downtime and periodic false-negative review. Keep the pathology system of record and existing clinical safeguards.

## HH security

- [ ] **S01 — Approve identities/roles.** Assign named users and Administrator/Security Officer/reader access, verify tier/MFA and offboarding; document any time-limited shared-account exception. R2-25/R2-27.
- [ ] **S02 — Approve data flows.** Review actual services/BAAs, cloud egress, mail content, filenames, PHI metadata, audit coverage and log destinations; verify delivery-audit limitations. R2-12/R2-26/R2-28.
- [ ] **S03 — Approve retention/custody.** Set distinct workflow/dataset/audit/log/mailbox/source/backup lifetimes and prove purge/expiry. Assign custodians for recovery passphrase, `state.key` and disk recovery; rehearse access without copying values into reports. R2-04–R2-06/R2-22.
- [ ] **S04 — Sign readiness/residual risk.** Review blocker closure, clinical evaluation and outage/restore evidence for the manifest. Assign owner/deadline for residual LOW/conditional items. Audit exit status alone does not authorize clinical use.
