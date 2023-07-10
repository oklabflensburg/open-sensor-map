# open-sensor-map

Schnittstelle zur Auswertung der Luftdatensensoren und Darstellung der Feinstaubwerte 



## Prerequisite

```
sudo apt install git python3.10 virtualenv nginx-full certbot python3-certbot-nginx
git clone https://github.com/oklabflensburg/open-trees-map.git
cd open-trees-map
touch .env
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt
```


## Setup Database

```
wget -q https://repos.influxdata.com/influxdata-archive_compat.key
echo '393e8779c89ac8d958f81f942f9ad7fb82a25e133faddaf92e15b16e6ac9ce4c influxdata-archive_compat.key' | sha256sum -c && cat influxdata-archive_compat.key | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/influxdata-archive_compat.gpg > /dev/null
echo 'deb [signed-by=/etc/apt/trusted.gpg.d/influxdata-archive_compat.gpg] https://repos.influxdata.com/debian stable main' | sudo tee /etc/apt/sources.list.d/influxdata.list
sudo apt update
sudo apt upgrade
sudo apt install influxdb2
```

```
sudo systemctl start influxdb
sudo systemctl enable influxdb
```


## Setup Service

```
sudo vim /etc/systemd/system/open-sensor-map-backend.service
```

```
[Unit]
Description=API instance to serve the backend
After=network.target
Requires=postgresql.service

[Service]
Type=simple
User=www-data
Group=www-data
DynamicUser=true

WorkingDirectory=/opt/git/open-sensor-map
PrivateTmp=true

EnvironmentFile=/opt/git/open-sensor-map/.env
ExecStart=/opt/git/open-sensor-map/venv/bin/uvicorn \
        --proxy-headers \
        --forwarded-allow-ips='*' \
        --workers=4 \
        --port=8000 \
        main:app

ExecReload=/bin/kill -HUP ${MAINPID}
RestartSec=1
Restart=always

[Install]
WantedBy=multi-user.target
```


## Start Service

```
sudo systemctl start open-sensor-map-backend.service
sudo systemctl status open-sensor-map-backend.service 
sudo systemctl enable open-sensor-map-backend.service
```


## Setup Server

Setup backend webserver configuration for nginx

```
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name api.open-sensor-map.com;

    charset uft-8;

    add_header Content-Security-Policy "default-src 'self'; script-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; font-src 'self'; worker-src 'none'; object-src 'none'";

    root /opt/git/open-sensor-map;

    location / {
        if ($request_method = 'OPTIONS') {
            add_header 'Access-Control-Allow-Origin' '*';
            #
            # Om nom nom cookies
            #
            add_header 'Access-Control-Allow-Credentials' 'true';
            add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';

            #
            # Custom headers and headers various browsers *should* be OK with but aren't
            #
            add_header 'Access-Control-Allow-Headers' 'DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type';

            #
            # Tell client that this pre-flight info is valid for 20 days
            #
            add_header 'Access-Control-Max-Age' 1728000;
            add_header 'Content-Type' 'text/plain charset=UTF-8';
            add_header 'Content-Length' 0;
            return 204;
        }

        if ($request_method = 'POST') {
            add_header 'Access-Control-Allow-Origin' '*';
            add_header 'Access-Control-Allow-Credentials' 'true';
            add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
            add_header 'Access-Control-Allow-Headers' 'DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type';
        }

        if ($request_method = 'GET') {
            add_header 'Access-Control-Allow-Origin' '*';
            add_header 'Access-Control-Allow-Credentials' 'true';
            add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
            add_header 'Access-Control-Allow-Headers' 'DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type';
        }

        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;

        proxy_buffering on;
        proxy_cache_valid 200 5m;
        proxy_cache_use_stale error timeout invalid_header updating http_500 http_502 http_503 http_504;
        proxy_cache_bypass $http_cache_control;
        add_header X-Proxy-Cache $upstream_cache_status;
        add_header Strict-Transport-Security "max-age=15768000; includeSubDomains; preload" always;
    }

    ssl_certificate /etc/letsencrypt/live/open-sensor-map.de/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/open-sensor-map.de/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
}
```


## Setup Certificates

```
sudo nginx -t
sudo certbot
sudo systemctl reload nginx.service
```


## Start Application

```
uvicorn main:app --reload
```

```
INFO:     Will watch for changes in these directories: ['/opt/git/open-sensor-map']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [11954] using StatReload
INFO:     Started server process [11956]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
{'esp8266id': '15221686', 'software_version': 'NRZ-2020-133', 'sensordatavalues': [{'value_type': 'SDS_P1', 'value': '6.18'}, {'value_type': 'SDS_P2', 'value': '1.67'}, {'value_type': 'BME280_temperature', 'value': '15.13'}, {'value_type': 'BME280_pressure', 'value': '101313.66'}, {'value_type': 'BME280_humidity', 'value': '74.93'}, {'value_type': 'samples', 'value': '5033673'}, {'value_type': 'min_micro', 'value': '28'}, {'value_type': 'max_micro', 'value': '20050'}, {'value_type': 'interval', 'value': '145000'}, {'value_type': 'signal', 'value': '-51'}]}
INFO:     127.0.0.1:39326 - "POST /data/ HTTP/1.1" 200 OK
```
