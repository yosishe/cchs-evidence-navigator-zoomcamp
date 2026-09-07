# Approved local container installation and rehearsal

The owner explicitly authorized this scope on 7 September 2026. Installation,
asset setup, the software suite and database persistence have completed. The
[actual rehearsal](../reports/container-rehearsal.json) remains functionally partial:
one valid abstention and two answerable-request timeouts. Authorization is not a
successful quality evaluation.
The fresh preflight observed Apple silicon (arm64), 24 GiB RAM, eight CPUs and
36,482,654,208 free disk bytes (about 34 GiB). Memory pressure reported 49% free;
no Docker installation or native model-comparison process was present.

Start with 10 GiB VM memory and six CPUs, within the authorized ceilings below.
The engine disk limit must be set to 20 GiB before project image/asset setup.
Current `configs/app.json` selects Phi3; Gemma's size below is capacity context,
not permission to change the measured application configuration. The
[setup document](setup.md#observed-container-results-and-next-decision) records
the installed runtime, measured resources, actual results and next decision.

## Concrete action

Download the official Apple-silicon Docker Desktop installer, verify its published
checksum/signature, install it and prepare only this project's Compose stack.
Use its personal/educational-use route; no paid service, cloud deployment,
Kubernetes, login-startup item or model-provider account is part of this action.
Any OS dialog requiring the owner's password remains an owner action.

Initial rehearsal limits: up to **14 GiB VM memory, six CPUs and 20 GiB of new
container data**. These are proposed operational bounds, not measured requirements
or course thresholds. Installer/app files are additional. Recheck capacity first
and stop for review if resources are insufficient; do not delete existing files,
unload unrelated applications or increase the limits silently. Do not overlap
the container rehearsal with timed native-model comparisons.

The full stack includes pinned Python/Ollama/PostgreSQL images, locked Python
dependencies, the pinned MiniLM encoder and the configuration's exact local model.
Gemma 3 12B needs approximately **8.15 GB of weight files** based on its installed
artifact. An isolated volume needs its own copy. Download/setup authorization
must cover those assets; normal inference never downloads or uses a paid fallback.
CPU inference inside the Mac VM may exceed native latency substantially. No GPU
acceleration or successful execution within these limits is promised.

## Verification after installation

Follow [the complete setup/restart procedure](setup.md#full-compose-route--execution-pending).
Record actual disk/memory consumption and image/model digests, build logs, dlt
counts, model output, downloaded bytes, PostgreSQL answer/feedback IDs and retained
rows after restart. A native model server does not substitute for the Compose
Ollama service. A configuration file does not earn execution evidence.

Official references checked for this scope:
[Mac installation and educational-use terms](https://docs.docker.com/desktop/setup/install/mac-install/),
[resource settings](https://docs.docker.com/desktop/settings-and-maintenance/settings/#resources).
The official minimum RAM is a Desktop prerequisite, not this model's requirement.

This scope was approved explicitly in the owner's installation request. It covers
the listed local images, dependencies, encoder and configured model assets.
An OS password prompt still belongs to the owner. Read [the current readiness
report](readiness.md) for the separate quality, publication and submission state.
