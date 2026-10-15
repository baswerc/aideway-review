# Outstanding site and release facts

These answers were unavailable in the reviewed source. Record non-secret answers/evidence in the installation worksheet; transfer credentials separately through approved channels. No HH system was contacted.

| Owner | Question | Required evidence / consequence |
|---|---|---|
| TekFive release | What exact signed harness package, four image digests, app tag/commit and guide build will be delivered? Which vLLM base (26.08 or 26.05.post1) was tested? | Manifest and CI/factory acceptance; current source is 0.1.0-dev and build paths differ. |
| TekFive release | Where is the signed HH configuration bundle, and how are local users/services and published revisions provisioned? | Fresh-production rehearsal and graph identity; dev seed/import alone is insufficient. |
| TekFive release | What is the frozen database baseline and supported migration/rollback procedure? | Passing schema guard, populated upgrade and interrupted-restore evidence. |
| TekFive model owner | What model repository, immutable revision, quantization, tokenizer/template and complete hashes are approved? Which NER weights and Python/CUDA stack? | Signed manifest and offline comparison on Spark, not an example name or remote hash list. |
| TekFive + HH clinical owner | Is v2 or v3 approved, which schema/reasoning settings apply, and where is the clinical evaluation? | Corpus provenance, false-negative denominator/bounds, calibration, revision comparison and sign-off. |
| TekFive factory | Is the unit enabled; which DGX OS/driver/CUDA/client packages are installed; what OCR/NER/GPU resource peaks were measured? | Factory log plus boot/outage matrix. x86 tests cannot answer. |
| TekFive + HH support | Who owns internal TLS renewal, failed mail/intake, incident response and after-hours recovery? What are response/recovery targets? | Named contacts and rehearsed runbook; SMTP failure also threatens login. |
| HH facilities / installer | Has the rack kit arrived and been fitted with acceptable airflow, power and UPS? | Physical inspection/asset record; invoice is not receipt. |
| HH network | What are static IP/mask/gateway/VLAN, actual MAC, DNS/NTP, SSH source ranges and effective egress rules? | Approved worksheet and container-inclusive connection tests. |
| HH network / PKI | Who issues the web certificate, what chain is trusted, and what temporary-trust/renewal policy applies? | SAN/chain verification from HH workstations and named owner. |
| HH mail | What is the **actual relay FQDN**, port, transport, authentication and IP allowlist? Is the path Exchange on-premises, Exchange Online, Cisco gateway or another relay? | Connector record and actual SMTP test. `smtp.hhsys.org` is an example; public DNS cannot answer this. |
| HH mail / PKI | What are relay SANs/issuer and certificate/key rotation policy? Is CA trust or SPKI pinning required? | Certificate verification and renewal rehearsal, including changed keys. |
| HH mail | Is From/envelope sender `aideway@hhsys.org` authorized? What EHLO, rate, size, MIME and timeout rules apply? | Connector policy/message trace/mailbox receipt, not only Test service success. |
| HH mail / pathology | Who owns `pathology.reports@hhsys.org`, who reads it by shift, are forwarding rules present, and what PHI/retention rules apply? | Membership/forwarding review and response owner; named sign-ins should have private MFA channels. |
| HH file server | What is the **actual SMB UNC or NFS export**, security/encryption mode, principal/export identity, ACL and credential rotation policy? | Server configuration and UID/GID read/rename/delete tests; `//files.hhsys.org/pathology/aideway` is an example. |
| HH file server / installer | How are squash or SMB UID/GID mappings configured, and how will mount credentials/fstab be recovered? | Mount recipe, permissions, offline client packages and protected configuration backup. |
| HH pathology producer | Which system exports PDFs, on what event, with atomic rename or in-place writes? What volume, burst, bytes/pages, scanned/mixed/encrypted proportions? | Producer specification and representative marked synthetic fixtures. |
| HH pathology producer | How are report identity, corrections/addenda, same-name replacement and redelivery represented? How is go-live backlog reconciled? | Non-PHI identifiers, source ledger, idempotency rules and source retention window. |
| HH clinical owner | What defines unexpectedness, who adjudicates disagreement, and what happens with missing history/CPT or insufficient extraction? | Approved review/abstention policy, sensitivity bound and turnaround requirement. |
| HH security | Which named users require Administrator, Security Officer or reader access, and which tiers protect full text/summaries/metadata? | Role/clearance matrix and positive/negative tests; shared login lacks individual attribution. |
| HH security | What storage-encryption scope, per-store retention, log/SIEM destinations, external-service and BAA restrictions are approved? | Deployment-specific risk decision, purge/expiry evidence and effective egress policy. |
| HH security + TekFive | **Who holds the recovery passphrase and state.key**, who holds disk recovery material, where are they escrowed, and how is access/rotation/absence handled? | Separate custody record and timed rehearsal; no secret values in this report. |
| HH release authority | Who authorizes clinical use/accepts residual risks, and what evidence is required before intake? | Named decision owner and dated checklist for the final manifest. |

An absent answer remains an open gate. Installed roles, mail topology and model identity cannot be inferred from guide examples.
