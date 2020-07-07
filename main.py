from witnet_lib.utils import AttrDict
from witnet_net_api import cli
a = AttrDict()
a.update({
    "config": "api.toml",
})

cli.start(a)
