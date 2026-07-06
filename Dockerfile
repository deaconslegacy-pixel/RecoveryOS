FROM node:20-bullseye AS frontend-builder
WORKDIR /build
COPY frontend/package.json frontend/package-lock.json* ./
COPY frontend/ ./frontend/
WORKDIR /build/frontend
RUN npm ci --legacy-peer-deps || npm ci
RUN npm run build

FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV GUNICORN_CMD_ARGS="--log-level=info"

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY . .

# Copy built frontend from previous stage
COPY --from=frontend-builder /build/frontend/dist /app/frontend_dist

# Create a non-root user and ensure app directory ownership
RUN addgroup --system app \
	&& adduser --system --ingroup app --home /app --shell /usr/sbin/nologin app \
	&& chown -R app:app /app

# Run as non-root user
USER app

EXPOSE 8000

CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "app.main:app", "--bind", "0.0.0.0:8000"]

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
	CMD python -c "import urllib.request,sys; code=urllib.request.urlopen('http://127.0.0.1:8000/health').getcode(); sys.exit(0 if code==200 else 1)" || exit 1
