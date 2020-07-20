from witnet_lib.utils import AttrDict
from witnet_net_api import cli
a = AttrDict({
    "config": "remote.toml",
})
cli.start(a)
