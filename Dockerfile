FROM python:3.13-slim-bookworm

WORKDIR /usr/src/app
COPY . .

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    nano \
    dos2unix \
    curl \
    tzdata && \
    pip install --no-cache-dir -r requirements.txt

ENV TZ=Asia/Jakarta
RUN ln -sf /usr/share/zoneinfo/Asia/Jakarta /etc/localtime && \
    echo "Asia/Jakarta" > /etc/timezone

# RUN python3 manage.py collectstatic --no-input
# RUN python3 manage.py migrate

COPY ./start.sh /start.sh
# RUN dos2unix /start.sh
RUN chmod +x /start.sh

EXPOSE 8042
CMD ["/start.sh"]

