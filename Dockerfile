FROM python:3.12-slim@sha256:78387bc3881b8273120a12ebe6c1ab22b018ccc2c9adf565ae1ac9b536e184ea
WORKDIR /app
COPY pyproject.toml requirements.lock requirements-container-arm64.lock requirements-container-amd64.lock ./
ARG INSTALL_VECTORS=true
ARG TARGETARCH
# Match the CPU wheel to the container architecture. The Mac-hosted VM has no
# assumed CUDA accelerator; the native/macOS dependency lock is separate.
RUN if [ "$INSTALL_VECTORS" = "true" ]; then \
      case "$TARGETARCH" in arm64|amd64) ;; *) exit 2 ;; esac; \
      pip install --no-cache-dir --require-hashes -r "requirements-container-${TARGETARCH}.lock"; \
    else pip install --no-cache-dir --require-hashes -r requirements.lock; fi
COPY . .
RUN useradd --create-home appuser && mkdir -p /app/runtime && chown -R appuser:appuser /app
USER appuser
EXPOSE 8501
HEALTHCHECK --interval=15s --timeout=5s CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health', timeout=3)"
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true", "--server.fileWatcherType=none", "--browser.gatherUsageStats=false"]
