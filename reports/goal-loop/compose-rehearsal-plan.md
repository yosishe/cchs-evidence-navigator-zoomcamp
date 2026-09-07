# Prepared local container rehearsal — approval pending

Prepared 6 September 2026. This report specifies the next reproduction check;
it is not an installation receipt or evidence that the stack works. R08/R09 and
the stricter local Goal remain unproven. The application generation configuration
is still a quality candidate, so an infrastructure rehearsal alone cannot finish
the Goal or freeze a submission version.

## Observed prerequisites and remaining uncertainty

- Host reports macOS 26.6.2 and arm64. Docker was absent in the runtime preflight.
- Filesystem check reports approximately 43 GiB available on the project volume.
  This is an observation, not a promised capacity requirement or sufficient-space
  proof. Available memory was not obtained in the sandbox; measure it before setup.
- Existing native apps use ports 8501/8502. Preserve them and native Ollama.
  The new `NAVIGATOR_APP_PORT` option changes only the loopback host port.
- The stack already pins Python, PostgreSQL and Ollama image manifests. It has
  separate dlt ingestion, encoder preparation and course-model initialization.
- `requirements-vectors.lock` includes Linux CUDA/NVIDIA dependencies, although
  this Mac rehearsal cannot assume container GPU acceleration. These may consume
  substantial download/build space. Do not claim a small CPU-only image or alter
  the lock by deleting dependencies. Record actual image sizes; a CPU-specific
  dependency resolution would be a separately checked packaging change.
- The container `model-init` downloads Phi3; `encoder-init` downloads MiniLM at
  the pinned revision. Native caches do not prove fresh named-volume initialization.
  Record the actual Phi3 digest and compare it with the selected model when a
  generation configuration has legitimately been selected.

Docker documents an Apple-silicon installer, current and two prior macOS major
releases, at least 4 GB RAM, and free personal/education use. The installer may
require a local password depending on configuration; its license must be accepted
before use. Those vendor prerequisites are not this stack's measured resource
requirements. [Official Mac installation instructions](https://docs.docker.com/desktop/setup/install/mac-install/).

## Concrete approval scope

Install Docker Desktop for Apple silicon from Docker's official distribution,
verify its published checksum/version and launch it. Download the existing pinned
container images and locked application dependencies, and initialize the taught
Phi3/MiniLM weights in isolated project volumes. No paid services or public
deployment are involved. The owner must handle any password or license interaction
that requires their direct action. No credentials should appear in evidence logs.

Approval has **not** been obtained by writing this report. The user's supplied
AGENTS.md instructions require asking before package installation; the active Goal
also explicitly prohibits unapproved installation/downloads. No automatic approval
review rejection has occurred.

## Rehearsal sequence after approval

1. Recheck Docker, available disk/memory, running services and the Git/config/model
   identity. Preserve current owner changes. Check official installer checksum
   and record the installed Desktop/Engine/Compose versions and architecture.
2. Choose an unused loopback host port (8503 is a proposed value, not verified
   available) and a fresh Compose project name, such as `cchs-goal-rehearsal`.
   If that project already exists, inspect its resources before using it. Never
   reuse unknown data volumes merely to obtain a clean-looking result.
3. Create a separate ignored local environment file, with a generated local
   PostgreSQL password, `NAVIGATOR_TRAFFIC_ORIGIN=qa`, chosen host port and the
   documented timeout. Preserve any existing `.env`. Do not print the password
   or save resolved Compose configuration containing it in the report.
4. Validate Compose interpolation and service dependencies, then build/start the
   **existing full stack** under that project. Capture build, initializer and
   service statuses with timestamps and command exit codes. Use bounded waits;
   a slow but live initialization is not evidence that it has stopped. A dependency
   failure is a failed rehearsal, not permission to remove that service.
5. Prove dlt output feeds the same 377-window corpus and source IDs checked by the
   app; compare corpus/config/model/encoder identities. Confirm serving uses the
   container's Ollama/database/cache and does not depend on native host services.
   Measure CPU/container latency separately from the native results. Do not
   silently change timeout, context length or selected generation configuration.
6. In a real browser, ask a documented development research question, inspect
   every answer statement and citation, download claim and comparison exports,
   and inspect the **downloaded bytes** and answer IDs. Store one QA feedback
   event, then verify the same answer and vote in PostgreSQL and the charts.
   Preserve unsupported outputs as failures; do not retry until a good answer
   appears or label a software-only flow as useful research performance.
7. Restart the app/database/model services within this isolated project without
   deleting volumes. Recheck corpus identity and retained answer/feedback IDs.
   Record counts by traffic origin and chart denominators. Exercise a bounded
   unavailable-model and unavailable-database case, then restore only the scoped
   rehearsal services and verify recovery. Do not touch native services.
8. Preserve logs, output hashes, model identity, actual resource measurements,
   database checks, downloaded files and a source-based answer review. Mark each
   step executed, failed or pending. Teardown, if needed, must preserve volumes;
   never run volume removal or global prune as part of this procedure.

The full selected-version browser and clean-reproduction acceptance must be
repeated after any material generation/runtime change. A preliminary rehearsal
can diagnose infrastructure while quality work continues, but cannot certify a
configuration that has not passed the complete development and final protocol.
