# open-sensor-map

Schnittstelle zur Auswertung der Luftdatensensoren und Darstellung der Feinstaubwerte 



## Prerequisite

```
sudo apt install git python3.10 virtualenv nginx-full certbot python3-certbot-nginx
git clone https://github.com/oklabflensburg/open-trees-map.git
cd open-trees-map
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt
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

        proxy_pass http://localhost:5000;
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
