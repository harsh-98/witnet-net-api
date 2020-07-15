import platform
from witnet_net_api import __version__
from jsonschema import Draft4Validator, validators, exceptions
from .logger import log
import sys

# https://stackoverflow.com/questions/41290777/trying-to-make-json-schema-validator-in-python-to-set-default-values
# https://python-jsonschema.readthedocs.io/en/latest/faq/#why-doesn-t-my-schema-that-has-a-default-property-actually-set-the-default-on-my-instance


def extend_with_default(validator_class):
    validate_properties = validator_class.VALIDATORS["properties"]

    def set_defaults(validator, properties, instance, schema):
        for property_, subschema in properties.items():
            if "default" in subschema and not isinstance(instance, list):
                instance.setdefault(property_, subschema["default"])

        for error in validate_properties(
            validator, properties, instance, schema,
        ):
            yield error

    return validators.extend(
        validator_class, {"properties": set_defaults},
    )


ConfigValidator = extend_with_default(Draft4Validator)

INFO_FORMAT = {
    "name": "",
    "contact": "",
    "coinbase": None,
    "node": "0.9.1",
    "net": None,
    "os": platform.system(),
    "os_v": platform.release(),
    "client": __version__,
    "canUpdateHistory": True,
}

CONFIG = {
    "definitions": {
        "consensus_constants": {
            "type": "object",
            "properties": {
                "genesis_sec": {
                    "type": "number",
                },
                "magic": {
                    "type": "number",
                },
                "sender_addr": {
                    "type": "string",
                },
                "time_per_epoch": {
                    "type": "number",
                    "default": 45
                },
            },
            "required": [
                "genesis_sec",
                "magic",
                "sender_addr",
            ],
        },
        "node": {
            "type": "object",
            "properties": {
                "p2p_addr": {
                    "type": "string"
                },
                "id": {
                    "type": "string"
                },
                "rpc_addr": {
                    "type": "string",
                    "default": ""
                },
                "contact": {
                    "type": "string"
                },
                "secret": {
                    "type": "string",
                    "default": ""
                },
                "rpc_interval_sec": {
                    "type": "number",
                    "default": 120
                },
            },
            "required": [
                "p2p_addr", "id"
            ]
        }
    },
    "type": "object",
    "properties": {
        "nodes": {
            "type": "array",
            "minItems": 1,
            "items": {
                "$ref": "#/definitions/node"
            }
        },
        "secret": {
            "type": "string",
            "default": ""
        },
        "consensus_constants": {
            "$ref": "#/definitions/consensus_constants"
        },
        "web_addr": {
            "type": "string"
        },
    },
    "required": [
        "nodes",
        "consensus_constants",
        "web_addr",
    ],
}


def validate_config(cfg):
    try:
        ConfigValidator(CONFIG).validate(cfg)
    except exceptions.ValidationError as err:
        log.error(err)
        sys.exit(1)
    return cfg
