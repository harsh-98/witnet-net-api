<!-- https://www.digitalocean.com/community/tutorials/how-to-install-nginx-on-ubuntu-18-04 -->
<!-- https://stackoverflow.com/questions/24861311/forwarding-port-80-to-8080-using-nginx -->

# Installing nginx

Port forwarding:

/etc/nginx/nginx.conf

```
map $http_upgrade $connection_upgrade {
default upgrade;
'' close;
}
```

```
server {
    listen 80;
    server_name witnet.live;

    location / {
        proxy_set_header   X-Forwarded-For $remote_addr;
        proxy_set_header   Host $http_host;
        proxy_pass         "http://127.0.0.1:3000";
    }
    location /primus {
        # Backend nodejs server
        proxy_pass          http://127.0.0.1:3000;
        proxy_http_version  1.1;
        proxy_set_header    Upgrade     $http_upgrade;
        proxy_set_header    Connection  $connection_upgrade;
    }
}
```

Serving the files from the file system:

```
server {
        listen 80;
        listen [::]:80;

        root /home/debian;
        index index.html index.htm index.nginx-debian.html;

        server_name witnet.live;

        location / {
                try_files $uri $uri/ =404;
        }
}
```

```
sudo ln -s /etc/nginx/sites-available/witnet.live.conf /etc/nginx/sites-enabled/
sudo sytemctl restart nginx
```

```
sudo certbot --nginx -d witnet.live -d www.witnet.live
```

## Reference:

- https://www.digitalocean.com/community/tutorials/how-to-install-nginx-on-ubuntu-18-04
- https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-16-04
