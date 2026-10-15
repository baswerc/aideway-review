# Second go-live review baseline

Review date 2026-10-15. Scope and severity follow `instructions.md`; the requested output directory is `review2/`. Application, harness, and customer documentation were reviewed without product edits. No HH system was contacted.

| Checkout | Branch | HEAD | Initial tracked/untracked changes |
|---|---|---|---|
| projects/aideway | main | 9e015e0fe15a50a04cf434c5a445798199f52c93 | none |
| projects/harness | main | 5abce3b05b8c74dec60511b9b01929b3d52f8802 | none |
| projects/docs | main | 066268e932e8f4491c8d1cfb17fb6b0ce355fc8a | none |

These are the same source revisions as the first review. `review/` is evidence to challenge and cross-reference, not proof of its conclusions. The existing ignored `related/harness` link is retained.

Environment: Linux x86_64; Java 25.0.4.1; host Node 22.22.1 and npm 9.2.0; Docker daemon 29.1.3. No HH appliance, relay or share is available. GPU/TPM/LUKS and live clinical model evaluation require separate appliance evidence. No patient data is used.

## Versions and artifact identity

| Item | Current source / environment |
|---|---|
| Harness VERSION / IMAGE_TAG_SERVER | `0.1.0-dev` / `0.1.0-dev` |
| Example nginx / postgres / vLLM image override | `latest` for each; not immutable release identity |
| Gradle / Kotlin | 9.5.0 / 2.4.10 |
| Gradle-managed Node / npm | 22.14.0 / 11.14.1; host versions above are separate |
| Java | 25.0.4.1; source targets Java 25 |
| vLLM Dockerfile and release default | `nvcr.io/nvidia/vllm:26.08-py3` |
| Local vLLM build.sh / harness setup default | `nvcr.io/nvidia/vllm:26.05.post1-py3`; these build paths disagree |
| PostgreSQL | major 17 |
| Locked framework jars inspected | RelayKt 1.0.9, Keep 1.0.15, KViaSH 1.0.3, JFK 1.0.4, PolyglotKt 1.0.3 |
| Dependency verification | `org.gradle.dependency.verification=off`; strict override fails |
| Actual HH release/model/site bundle | Not supplied; source checkout is not a signed appliance manifest |

## Execution ledger

Fresh output is retained under `evidence/`. Counts below are per invocation and overlap; do not add focused reruns to the full suite as new tests. A skip is not a pass. No project tests were added or changed.

| Command / check | Result | Evidence |
|---|---|---|
| `./gradlew build --rerun-tasks` | **Exit 1**. Backend 2,806 tests: 2,797 passed, 2 failed, 7 skipped. Both failures are AuditCleanupTest permission assumptions under root. Dev: 31 passed. Backend/dev detekt and generated API verification passed. Distributions built; task failure prevented the full build from finishing. | [gradle-build.log](evidence/gradle-build.log), [initial XML summary](evidence/backend-initial-results.json) |
| Focused AuditCleanupTest + FileTriggerJobDbTest with `setpriv --bounding-set=-dac_override,-dac_read_search` | **40 passed**, zero failures/skips. Reproduces filesystem denial and resolves both initial failures and both permission skips; not an unexplained product failure. | [focused-and-frontend.log](evidence/focused-and-frontend.log) |
| `:frontend:npmTest` | **125 files, 661 tests passed** | same focused log |
| `:frontend:npmLint :frontend:npmBuild --rerun-tasks` | **Passed**, all five Gradle tasks executed; type-check and production build passed. Earlier lint/build invocation was cached and is not used as fresh evidence. | [frontend-build-fresh.log](evidence/frontend-build-fresh.log) |
| `:frontend:npmTestMockups` | **37 passed** | [extended-checks.log](evidence/extended-checks.log) |
| `./run-tests.sh` in harness | **579 bats cases: 568 passed, 11 skipped; 150 Python tests passed** | [harness-tests.log](evidence/harness-tests.log) |
| Corrected AIDEWAY_PROJECT_ROOT; nginx/server TLS bats | **3 passed, 1 skipped** (host nginx absent) | [harness-corrected-path.log](evidence/harness-corrected-path.log) |
| Two harness permission cases with DAC bypass removed | **2 passed**, zero skips | [harness-permission-tests.log](evidence/harness-permission-tests.log) |
| Application `python3 -B -m unittest discover -s scripts -p 'test_*.py'` | **48 cases: 41 passed, 7 skipped** because AIDEWAY_TEST_NGINX was unset | [python-scripts.log](evidence/python-scripts.log) |
| `AIDEWAY_TEST_NGINX=nginx:1.27-alpine python3 -B scripts/test_nginx_redirect.py` | **All 7 passed** using cached Docker image, isolated containers with no network. Covers the previously skipped container cases. | [nginx-container-tests.log](evidence/nginx-container-tests.log) |
| Python NER worker protocol tests | **27 passed**; protocol tests do not load the clinical model | [python-ner-tests.log](evidence/python-ner-tests.log) |
| vLLM build-script Python test | **1 passed** | [vllm-build-tests.log](evidence/vllm-build-tests.log) |
| `:backend:classificationCorpus` | **15 passed**, non-NER PHI detection/redaction/restoration; not pathology sensitivity | [extended-checks.log](evidence/extended-checks.log) |
| `:backend:nerIntegrationTest` | **14 skipped**, missing NER Python/model environment; Gradle success is not test success | same extended log; [test inventory](evidence/test-inventory.json) |
| `:backend:verifyGeneratedApiCommitted` | **Passed** | extended and initial build logs |
| `python3 scripts/check_release_schema.py` | **Exit 1**: V1 imports live models; baseline must be frozen. Working release blocker, R2-35. | [release-schema.log](evidence/release-schema.log) |
| `./gradlew --no-daemon --dependency-verification strict :backend:classes` | **Exit 1**: missing verification for detekt plugin-marker POM 2.0.0-alpha.6 from MavenRepo. R2-01. | [dependency-verification.log](evidence/dependency-verification.log) |
| Production-code PDF/response probes | Image-only and zero-byte PDFs yield empty text; `{}` accepted with STOP and MAX_TOKENS. Synthetic input only. | [ClinicalProbe.java](evidence/ClinicalProbe.java), [clinical-probes.log](evidence/clinical-probes.log) |
| Isolated harness probes | Audit crash masked; shipped flags produce false FAILs; malformed guide command rejected; inert shell substitution evaluated; pandoc absent but bundled HTML installation exists. | [harness-probes.json](evidence/harness-probes.json) |
| Lockfile SCA | 376 Maven coordinates checked, 28 affected coordinates / 82 GHSA records. npm: 19 nodes (2 critical, 14 high, 3 moderate); reachability differs from scanner severity. | [dependency review](evidence/dependency-review.md) |

Five deliberately disabled gateway demo tests remain skipped: three SimpleMcpServerTest and two SimpleOpenAiApiServerTest cases. The 14 NER integration cases remain unexecuted. Harness residual skips are five minisign signature tests (tool absent) and one host-native nginx syntax test (nginx absent). Two root permission skips and three application-layout skips were resolved by the focused runs; the separate seven Docker nginx tests passed but do not change the native test's recorded skip. No signature test is counted passed merely because verification code exists.

The two original backend failures are environment-specific and pass with DAC bypass removed. The full aggregate build was not rerun after focused resolution; report it as failed with explained/resolved test causes, not as a green aggregate build. Release-schema and strict dependency failures are still open.

## Phase ledger and limits

All source-review phases were worked in the prescribed sequence; [phase-evidence.md](phase-evidence.md) records detailed answers. Unavailable acceptance evidence remains explicitly blocked below and in the recommendation.

| Phase | Completed here | Unavailable / required elsewhere |
|---|---|---|
| 0 baseline | Commits, versions, builds, test/skip ledger, 294 prior-source item rows | Final released artifact and remote CI/branch-protection evidence |
| 1 install | Harness/Compose/setup/audit/keys/TLS/backup/model/systemd source, bats/Python/probes | DGX ARM64 GPU/TPM/LUKS, factory image, actual boot, offline import, real restore and resource tests |
| 2 mail | Application paths plus exact locked Relay/Keep bytecode | HH relay/auth/certificate/sender/quarantine behavior and mailbox receipt |
| 3 share | Scanner/trigger/deletion/mount/UID/ACL source and DB tests | Real SMB/NFS, squash mapping, disconnect/hard-mount hangs and producer export behavior |
| 4 workflow | Seed/import/graph/classification/decision/retention trace; synthetic production-code probes | Production HH bundle, full GPU graph, all required outcomes and recovery |
| 5 docs | All 13 getting-started steps, linked chapter claims, link check, 11 referenced images visually inspected | Release-matched guide build; linked-guide screenshot recapture/live UI equivalence |
| 6 security | Auth/roles/PHI/encryption/audit/CI/BAA source, prior findings, GHSA-backed lockfile SCA | Effective HH ACLs/services, full runtime canary scan, image/OS/Python SCA, full-history secrets scan |
| 7 model | Prompt/schema/seed comparison, PHI corpus, evaluation-infrastructure review | Actual model manifest, NER/GPU integration, labelled pathology set, clinical accuracy/calibration |
| 8 frontend | Source/components, tests/build/mockups, calculated contrast | Authenticated keyboard/screen-reader/zoom/browser audit; Chromium/Lighthouse unavailable, Playwright not used |
| 9 release | CI/signing/provenance and executed freeze/verification guards | Signed release manifest, migration/rollback tests, factory acceptance |
| 10 readiness | Carry list, non-secret worksheet, owners, acceptance and rollback plan | HH/TekFive answers and recorded on-appliance acceptance |

No complete clinical workflow, GPU performance run, HH connection, live patient-data test or physical appliance test was performed. No clinical sensitivity, HIPAA certification, WCAG conformance, delivery receipt or successful disaster recovery is inferred from unit tests. Docker availability allowed local nginx tests; it did not supply the missing ARM64/GPU deployment. The rack invoice is an order record, not evidence of kit receipt or installed thermal clearance.
