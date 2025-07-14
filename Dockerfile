FROM python:3.10.12-slim-bullseye

WORKDIR /app
COPY . /app 

RUN apt-get update && apt-get install -y \
    nano \
    tzdata && \
    pip install --no-cache-dir -r requirements.txt

ENV TZ=Asia/Jakarta
RUN ln -sf /usr/share/zoneinfo/Asia/Jakarta /etc/localtime && \
    echo "Asia/Jakarta" > /etc/timezone

RUN python3 manage.py collectstatic --no-input
RUN python3 manage.py migrate

COPY ./start.sh /start.sh

EXPOSE 8042
CMD ["/start.sh"]

