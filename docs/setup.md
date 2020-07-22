## Network Dashboard Setup

### Frontend

```
git clone https://github.com/harsh-98/eth-netstats
npm install
npm i -g grunt
grunt
```

##### Configure Secrets

Either export `WS_SECRET`:

```
export WS_SECRET="secret1|secret2"
```

or

```
create a file `ws_secret.json` with `['secret1', 'secret2']`.
```

##### Configuring trusted or banned nodes

```
edit `lib/utils/config.json` add `trusted ip` or `banned ip`.
```

### Backend

Edit create and edit `api.toml` to configure backend.

```
cp api.sample.toml api.toml
```

```
git clone https://github.com/harsh-98/witnet-net-api
pip install pipenv
pipenv install
python main.py
```

# Enabling https

Using: httpd/apache

```
/usr/sbin/setsebool -P httpd_can_network_connect 1 #httpd/apache for port forwarding for an application
```

- httpd:
  mod_proxy_wstunnel.so mod_proxy mod_proxy_http in /etc/httpd/conf.modules.d/00-base.conf
- apache:

```
sudo a2enmod mod_proxy
sudo a2enmod mod_proxy_http
sudo a2enmod  mod_proxy_wstunnel
```

Config:

```
<VirtualHost *:80>
  #ProxyPreserveHost On
  ProxyRequests On
  ServerName www.witnet.live
  ServerAlias witnet.live
  ProxyPass / http://127.0.0.1:3000/
  ProxyPassReverse / http://127.0.0.1:3000/
RewriteEngine on
RewriteCond %{HTTP:UPGRADE} ^WebSocket$ [NC]
RewriteCond %{HTTP:CONNECTION} ^Upgrade$ [NC]
RewriteRule .* ws://localhost:3000%{REQUEST_URI} [P]
</VirtualHost>
```

Reference:

- https://devops.ionos.com/tutorials/install-and-configure-mod_rewrite-for-apache-on-centos-7/
- https://stackoverflow.com/questions/17334319/setting-up-a-websocket-on-apache

## On mac os sierra or above

Set below to allow the code to fork the main process, with multiprocessing.

```
export  OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
```

## Debugging close_wait sockets

Mac OS:

```
netstat -np tcp -f inet
```

n is for using number ip and not resolving the ips.
p for protocol.
f for the address family.

Linux :

```
netstat -apnt | grep :21337
```

a for active
n for not resolving ips.
t for tcp.
p for proess details
