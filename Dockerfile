ARG PYTHON_VERSION=3.11
ARG ALPINE_VERSION=3.21

# Build stage go
FROM golang:1-alpine AS go-builder
RUN apk add --no-cache build-base

WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=1 go build .

# Build stage python
FROM python:$PYTHON_VERSION-alpine$ALPINE_VERSION AS py-builder
RUN apk add --no-cache build-base jq-dev oniguruma-dev llvm15-dev jpeg-dev zlib-dev autoconf automake libtool git

# Create a virtual environment for a clean install
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV LLVM_CONFIG=/usr/bin/llvm15-config
ENV JQPY_USE_SYSTEM_LIBS=1

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: The Final Image
# Start from a fresh, minimal Alpine image
FROM python:$PYTHON_VERSION-alpine$ALPINE_VERSION

RUN apk add --no-cache jq llvm15-libs zlib jpeg supervisor && \
	mkdir -p /app/cache && \
    mkdir -p /var/log/supervisor && \
    mkdir -p /etc/supervisor/conf.d && \
    chmod -R o+rw /var/log/supervisor && \
    chmod -R o+rw /var/run

# Activate the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Copy your application code
WORKDIR /app

COPY --from=go-builder /app/wttr.in /app/bin/wttr.in
COPY --from=py-builder /opt/venv /opt/venv

COPY ./bin bin
COPY ./lib lib
COPY ./share share
COPY share/docker/supervisord.conf /etc/supervisor/supervisord.conf

ENV WTTR_MYDIR="/app"
ENV WTTR_GEOLITE="/app/GeoLite2-City.mmdb"
ENV WTTR_WEGO="/app/bin/wttr.in"
ENV WTTR_LISTEN_HOST="0.0.0.0"
ENV WTTR_LISTEN_PORT="8002"

EXPOSE 8002

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]
