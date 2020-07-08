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
