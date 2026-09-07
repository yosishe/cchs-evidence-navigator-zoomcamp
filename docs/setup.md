# Setup, operation and clean reproduction

## What has actually run

The primary submission-candidate route is native Mac Ollama with the pinned
`gemma3:12b` model and explicit JSONL storage. [The final native demonstration](../reports/final/native-bound-flow.json)
used the shipped app configuration, three publications and 377 windows. It
produced one useful source-backed EXA-01 answer and one correct ABS-01 abstention,
downloaded six matching JSON/CSV files, saved two linked QA ratings and retained
all four records through a native application stop/restart. The six charts were
inspected before and after restart. There were exactly two generation attempts,
no retries, no final-set inference, no installs and no asset downloads.

Observed generation/validation durations were 148.8 and 51.0 seconds, respectively;
these are operational observations, not a latency promise. The server actually
allocated 4,096 context tokens. Its 131,072-token architecture capacity is a
different value. Existing Python 3.12.14 dependencies and the existing pinned
MiniLM cache were reused. The encoder check found 377 inputs and zero truncations.
[Setup evidence](../reports/final/native-setup.json), [runtime preflight](../reports/final/native-preflight.json).

The [historical Phi3 Compose rehearsal](../reports/container-rehearsal.json)
proved build, initialization, 172 Linux checks, one abstention, downloads,
feedback and PostgreSQL persistence; two answerable calls timed out. Gemma was
not run inside Compose. No model weights or Docker resources were changed for
this final route. A fresh public-clone smoke check follows publication and is
kept outside the commit it identifies; it reuses dependencies/assets and does
not prove a new installation or answer-quality result.

## Native local development

Prerequisites: Python 3.12 or later within the declared `<3.15` range, `uv`, and a
running local Ollama server. Use the pinned locks, not a manually assembled package
set. Install/download only with the machine owner's required authorization.

```bash
uv sync --frozen --extra vectors
uv run python -m navigator ingest
uv run python -m navigator prepare-encoder --allow-download
uv run python tools/prepare_compose_model.py --allow-download
uv run python -m navigator check-runtime
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 ENABLE_PAID_LLM=0 TELEMETRY_BACKEND=jsonl NAVIGATOR_TRAFFIC_ORIGIN=qa uv run streamlit run app.py --server.port 8601 --server.fileWatcherType none --browser.gatherUsageStats false
```

The explicit model-setup command reads `configs/app.json`. It verifies already
installed weights; if absent and downloads are allowed, it prepares that configured
model tag and records its resolved digest. When `model_digest` is specified, a
different installed digest fails; the approved Gemma exception also enforces its
recorded digest. The shipped Gemma configuration pins its exact digest in `configs/app.json`.
A mismatched digest fails setup. The app itself never downloads.

Default endpoint: `http://localhost:11434/v1/`. The local route needs no commercial
key. `ENABLE_PAID_LLM=0` prevents the optional legacy commercial route; no fallback
connects the local route to it. Start in **Evidence preview** to check ingestion,
then choose **LLM answer** for real local generation. `NAVIGATOR_TRAFFIC_ORIGIN=qa`
marks a demonstration as test activity instead of real researcher feedback.

The selected config governs model, digest, prompt, retrieval, output budget and
timeout. `NAVIGATOR_CONFIG` can select a separately declared experiment config.
Leave `NAVIGATOR_REQUEST_TIMEOUT` unset to preserve the fingerprinted value. A
different override invalidates selected evidence. No unmeasured response-time
target is claimed.

## Repeat the native demonstration and restart check

For a reviewer demonstration, use a separate runtime directory and the same
existing encoder cache. This creates data under the selected runtime only.
Clear `NAVIGATOR_CONFIG` and `NAVIGATOR_REQUEST_TIMEOUT` overrides first.

```bash
unset NAVIGATOR_CONFIG NAVIGATOR_REQUEST_TIMEOUT
export NAVIGATOR_RUNTIME="$PWD/runtime/reviewer-demo"
export NAVIGATOR_MODEL_CACHE="$PWD/runtime/models"
export TELEMETRY_BACKEND=jsonl NAVIGATOR_TRAFFIC_ORIGIN=qa ENABLE_PAID_LLM=0
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
uv run python -m navigator ingest
uv run python -m navigator prepare-encoder
uv run python -m navigator check-runtime
uv run streamlit run app.py --server.port 8601 --server.fileWatcherType none --browser.gatherUsageStats false
```

Open `http://127.0.0.1:8601/`, choose **LLM answer**, and enter one question. Record
its answer ID and status. Download the evidence JSON and available CSVs; compare
their answer/source IDs and original text. Save a clearly labeled QA rating and
open **Monitoring** with origin `qa`. Counts, statuses, durations, passage counts,
ratings and observed tokens must refer to those stored requests.

Stop Streamlit with Ctrl-C, then repeat only its last start command with the
same environment. Do not rerun the question to test persistence. The input form
starts a new session; **Monitoring** reads the existing stored records. Check
`events.jsonl` under the runtime directory for unchanged answer and feedback IDs.
The primary native route uses JSONL, not PostgreSQL. No database migration or
silent database fallback is part of this route. Use origin `user` only for actual
user activity. Results remain pending scientific review.

## Prepare before running software checks

Run the native setup steps above first. The integration suite exercises real
vector retrieval and the UI, so installing Python packages alone is insufficient.
The required MiniLM model/revision is pinned in `configs/app.json`; the weights
are excluded from the submission. An empty cache must show an actionable setup
failure, not silently download assets, switch retrieval methods or skip the test.

If the pinned encoder is already prepared, validate it offline:

```bash
uv run python -m navigator ingest
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 uv run python -m navigator prepare-encoder
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 ENABLE_PAID_LLM=0 uv run python tools/run_checks.py
```

Require `ENCODER_READY` and a zero process exit code before the full suite. If
the encoder is missing, use the explicit `prepare-encoder --allow-download` setup
step above with authorization, then repeat the offline check. A real Ollama model
answer is tested separately; this software suite uses mocks for generation.

<a id="full-compose-route--execution-pending"></a>

## Full Compose route — historical Phi3 rehearsal; Gemma execution unproved

Docker Desktop 4.90.0 has now been installed from the official Apple-silicon image.
The published SHA-256, Docker signing identity and Apple notarization were verified.
The [execution record](../reports/container-rehearsal.json) separates completed
steps from failed or pending checks. Installation and persistence passed; the
answerable model flow did not pass. The legacy section anchor above is retained
so earlier installation links still resolve.

The actual ARM64 [image build](../reports/container-runtime/compose-build.log)
passed with hash-checked dependencies. Fresh in-container ingestion reproduced
the frozen 377-passage corpus, and [encoder preparation](../reports/container-runtime/encoder-preparation.json)
downloaded the pinned revision and encoded every input without truncation.
All [172 software checks passed without skips](../reports/container-runtime/software-checks.json)
inside the new image using that cache offline. These checks use mocked generation
and isolated JSONL test storage; they do not establish an actual model answer or
PostgreSQL persistence by themselves. Separate real browser/SQL evidence below
now establishes a valid abstention, downloads and database retention.
The `docker_available=false` field in that test report
means the Docker CLI is absent inside the application image, not that the host
engine was unavailable.

The installation preflight observed an Apple M3, 24 GiB unified RAM and about
34 GiB free disk. The initial VM is configured for six CPUs, 10 GiB RAM and a
20 GiB disk, within the owner's maximum of 14 GiB RAM, six CPUs and 20 GiB new
container data. These are operational bounds, not measured model requirements.
Recheck capacity before setup. Gemma 3's installed
weights occupy about 8.15 GB; an isolated container model volume can require
another copy, plus images, Python packages and runtime memory. Measure requirements
before allocating resources. CPU inference in Mac containers may be substantially
slower than the native accelerated path. No GPU acceleration in Compose is assumed.
The recorded rehearsal used the earlier Phi3 configuration. The current app
configuration instead binds Gemma, so a new Compose setup would prepare that
larger pinned artifact. That route has not been executed for this candidate. Do not run timed native model
comparisons concurrently. Installer/app files are additional to the container cap.

Docker uses its Personal route without sign-in. Startup at login, Kubernetes,
Docker AI and Docker Model Runner are disabled. The CLI was installed in the user
location. Run these commands from the project directory containing `compose.yaml`.
If a new shell cannot find the CLI or credential helper, use these shell-local
settings:

```bash
export PATH="/Applications/Docker.app/Contents/Resources/bin:$HOME/.docker/bin:$PATH"
export DOCKER_CONTEXT=desktop-linux
docker desktop start
```

No shell startup file needs to change. Any OS password prompt must be completed
by the owner. Do not add an unrelated service, increase limits, or delete files
to resolve a resource shortage.

The image uses separate hashed CPU-only locks for Linux ARM64 and AMD64, with
PyTorch 2.14.0+cpu from its official CPU wheel host. The original cross-platform
lock also pulled CUDA runtime packages on Linux; those are unnecessary for this
CPU route. All other resolved versions remain constrained by `uv.lock`. See
[the lock preparation evidence](../reports/release-migration/container-lock-arm64.json)
and [regeneration tool](../tools/resolve_container_locks.py). Resolution may download
wheel archives for metadata; it is not installation or a demonstrated build.
The Dockerfile chooses the lock using BuildKit's target architecture and requires
hash verification. Native macOS continues to use the original frozen `uv.lock`.

Prepare a local `.env` from `.env.example` only if it does not already exist; never
overwrite existing credentials. Set a unique local `POSTGRES_PASSWORD`, an available
`NAVIGATOR_APP_PORT`, and `NAVIGATOR_TRAFFIC_ORIGIN=qa` for the rehearsal. Keep the
timeout blank unless an explicit, reevaluated config requires another value.
On the installation host, `.env` also sets
`COMPOSE_PROJECT_NAME=cchs-zoomcamp-rehearsal`. Those settings refer to the historical Phi3 rehearsal. Do not rerun setup against
those preserved volumes as if they proved the new Gemma configuration. A different Compose project name creates separate
volumes and may consume another copy of the models; check capacity first.

The macOS audit found a Docker helper registered even with `AutoStart=false`.
Docker's separate App Background Activity switch was turned off in System
Settings; Docker was absent from the Open at Login list. No other application's
background settings were changed. Start Docker manually for this local route.

After setup/download authorization:

```bash
docker compose config --quiet
docker compose build
docker compose up -d
docker compose ps --all
docker compose logs --no-color model-init ingest encoder-init app
```

The services are Ollama, config-driven model initialization, PostgreSQL, dlt
ingestion, encoder initialization and Streamlit. Initialization must finish
successfully before the app starts. Normal inference is local-only. `model_weights`,
`artifacts` and `database` are persistent named volumes. Do not run `down -v` as
part of a restart test: that would destroy the evidence you intend to preserve.

`OLLAMA_NO_CLOUD=1` disables the server's optional cloud features, following the
[official Ollama setting](https://docs.ollama.com/faq#how-do-i-disable-ollama-cloud-features).
The initial server attempted cloud-model metadata refreshes. After this correction,
the running server reported `Ollama cloud disabled: true`; the same model files
and all three answer/feedback pairs were retained. This is application configuration,
not network-level egress isolation. The app's normal inference does not download
weights or fall back to a paid provider.

Use the actual port configured in `.env`. Submit a real answerable question and an
unanswerable question through the browser. Inspect sources and the generated answer;
download evidence JSON and passages CSV. When validated claims exist, also use
**Export claim review CSV** and **Export tag proposals CSV** when proposals exist;
the comparison table is displayed in the app. Compare the
downloaded file contents with the stored answer and original source spans.
Submit QA feedback, check the matching answer ID, then inspect the monitoring
charts with the QA filter. Restart without deleting volumes:

```bash
docker compose restart db ollama app
docker compose ps --all
```

Verify the previously stored answers/feedback still exist, that the selected model
is usable and that another request traverses the full flow. Record image digests,
model digest, config/code/corpus hashes, commands, timestamps, logs and browser
download receipts. Native model timing and CPU-container timing are separate data.

For a normal shutdown that preserves the data and downloaded assets:

```bash
docker compose stop
docker desktop stop
```

For the next manual session, start Desktop and reuse the same project directory,
`.env` and volumes:

```bash
docker desktop start
docker compose up -d --no-build
docker compose ps --all
```

The initialization services may run again to verify existing artifacts. Do not
remove volumes, substitute a native Ollama server, or choose a different project
name to work around a startup failure. Read the failed service's logs first.

### Observed container results and next decision

The [predeclared browser plan](../reports/container-runtime/browser-rehearsal-plan.json)
made exactly three local provider attempts, with no favorable-result retries.
All used the unchanged Phi3/evidence-first configuration and 120-second timeout.
The [complete flow record](../reports/container-runtime/browser-flow.json) links
the raw output, failed-call receipts, SQL records and browser downloads.

| Case | Actual result | Provider-call duration | Evidence implication |
|---|---|---:|---|
| Gene associated with CCHS, before restart | `APITimeoutError`; no answer displayed | 120.59 s | Failed useful-answer check; failure persisted |
| Iceland 2026 registry patient count | Valid `insufficient_evidence`; no invented count | 42.02 s | Real local-model output and appropriate corpus-limited abstention |
| Same gene question, after restart | `APITimeoutError`; no answer displayed | 120.49 s | Service recovered and recorded the request, but useful generation still failed |

Six actual browser exports total **102,087 bytes**. JSON matched the stored
PostgreSQL payloads; all CSV passage rows matched the frozen source spans and
offsets. [Download receipts](../reports/container-runtime/browser-downloads.json)
retain byte counts and hashes. There were no validated claims, so claim/tag
downloads remain unproved for this container candidate. All six monitoring charts
showed three QA requests, three linked QA ratings, two errors and one abstention.
These ratings are test activity, not researcher satisfaction.

The two answer/feedback pairs existing before the service restart survived with
identical full-payload hashes; see [the SQL comparison](../reports/container-runtime/restart-persistence.json).
A third pair was saved after restart. No volumes were deleted. A later recreation
of only Ollama to disable cloud features also preserved all three pairs.

The [resource record](../reports/container-runtime/resource-summary.json) observed
a peak of approximately **13.76 GiB allocated container disk**, **5.71 GiB guest
memory used excluding available memory**, and at least **10.51 GiB free host disk**
in its samples. The VM was configured for **10 GiB and six CPUs**, with a **20 GiB
active disk**. Sampled peaks are not continuous peak measurements. Installer/app
files add approximately 0.54/2.15 GiB outside the container-data bound. The retained
empty original disk occupies about 11.3 MiB and is included conservatively in the
container allocation total. Its old sparse logical capacity is not the active disk.

Prepared Phi3 files total **2,176,179,769 bytes** including the manifest; its resolved
model-artifact size is **2,176,178,913 bytes**. Every model file passed `sha256sum`.
The pinned encoder cache contains **91,578,606 unique file bytes**, counting symlink
targets once. Image identities, asset sizes and hashes are in
[asset accounting](../reports/container-runtime/asset-accounting.json). Full setup
network-wire bytes were not captured; asset sizes and Docker's cumulative network
counters must not be mislabeled as exact transferred bytes.

The model actually loaded with **4,096 context tokens and zero GPU memory**.
The server reports an architectural capacity of 131,072; that is not the allocated
context. Its logs show `truncated = 0` for these requests. The two timed-out calls
continued decoding after model loads of about 29 and 10 seconds, respectively;
therefore loading alone does not explain the failures. Partial server decoding
counters are diagnostic data, not substitutes for missing provider token usage.

Next, prepare a separately fingerprinted development experiment that measures
complete supported answers, output length, model loading, prompt processing and
generation time together. Compare bounded output/prompt choices while keeping
source support and completeness requirements unchanged. A longer timeout is a
declared experiment, not a silent fix; preloading trades latency for retained
memory and cannot by itself establish answer quality. Do not add memory or change
the selected model on the assumption that it resolves this observed failure.
No such follow-up experiment was run in this installation rehearsal.

At the historical container handover the three runtime services were healthy and the app was available at
`http://127.0.0.1:57894/`. Use the shutdown commands above when finished, then the
manual startup commands for the next session. Keep the existing `.env` and Compose
project name so the prepared assets and database are reused. For the current native submission exception, use [D37](release-decisions.md#d37--submission-candidate-with-an-explicit-quality-exception).
These historical observations do not close Gemma container execution.

## Failure handling

- Missing or mismatched model: fail setup; never silently switch weights/providers.
- Missing encoder: explicit preparation is required; no lexical fallback disguised
  as the selected vector experiment.
- Retrieval or storage outage: show a bounded error and retain failed-attempt
  evidence. Never display an answer as saved if storage failed.
- Invalid citations/schema or truncated output: retain the raw failed attempt,
  display the existing error result and do not retry until a favorable answer occurs.
- Changed source bytes, config or selected-evidence hash: stop and reconcile the
  new version before calling it the evaluated release.

## Reproduction from the public commit

After publication, use the actual full SHA supplied with the release receipt:

```bash
git clone https://github.com/yosishe/cchs-evidence-navigator-zoomcamp.git
cd cchs-evidence-navigator-zoomcamp
git checkout --detach FULL_40_CHARACTER_RELEASE_SHA
```

Replace the placeholder with the real SHA; a branch name is not a fixed version.
Follow the native setup steps above. A new machine requires the declared package
and model setup; the publication smoke check only reuses installed dependencies
and a pinned encoder cache to confirm ingestion from the anonymous public commit.
Its receipt is outside the commit to avoid a self-referential hash. No private
project source, owner path or commercial key is a runtime requirement. Native
Ollama is an explicit prerequisite, not a substitute for the Compose service.
