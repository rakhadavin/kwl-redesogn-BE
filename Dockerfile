FROM python:3.11-slim-bookworm

WORKDIR /usr/src/app
COPY . .

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    nano \
    dos2unix \
    curl \
    tzdata \
    build-essential \
    gcc \
    g++ \
    python3-dev \
    libffi-dev \
    libssl-dev \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    libtiff-dev \
    libwebp-dev \
    libopenjp2-7-dev \
    zlib1g-dev \
    liblcms2-dev \
    libxcb1-dev \
    libpq-dev \
    postgresql-client \
    pkg-config \
    supervisor \
    && pip install --no-cache-dir 'pip==24.0' 'setuptools==65.5.1' wheel \
    && pip install --no-cache-dir --timeout=120 -r requirements.txt \
    && pip install --no-cache-dir --force-reinstall 'setuptools==65.5.1' \
    && apt-get remove -y build-essential gcc g++ python3-dev libffi-dev libssl-dev libpq-dev pkg-config \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p staticfiles media app_logs /var/log/supervisor

ENV TZ=Asia/Jakarta
RUN ln -sf /usr/share/zoneinfo/Asia/Jakarta /etc/localtime && \
    echo "Asia/Jakarta" > /etc/timezone

COPY ./supervisord.conf /usr/src/app/supervisord.conf

COPY ./start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 8042
CMD ["./start.sh"]