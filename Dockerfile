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
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get remove -y build-essential gcc g++ python3-dev libffi-dev libssl-dev libpq-dev pkg-config \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Reinstall setuptools last to ensure pkg_resources is always available
# (some packages can break it during installation)
RUN pip install --no-cache-dir --force-reinstall 'setuptools>=65.0.0'

RUN mkdir -p staticfiles media app_logs /var/log/supervisor

ENV TZ=Asia/Jakarta
RUN ln -sf /usr/share/zoneinfo/Asia/Jakarta /etc/localtime && \
    echo "Asia/Jakarta" > /etc/timezone

COPY ./supervisord.conf /usr/src/app/supervisord.conf
COPY ./start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 8042
CMD ["/start.sh"]