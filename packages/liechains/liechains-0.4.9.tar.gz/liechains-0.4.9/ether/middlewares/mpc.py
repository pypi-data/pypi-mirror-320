import logging
from typing import Callable
from web3.types import *
from web3.middleware.signing import *
from eth_utils.toolz import (
    compose,
)

import secrets
import hashlib
import hmac
from Crypto.Cipher import AES
from hashlib import sha512
from binascii import unhexlify
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
import requests
import json
from web3 import Web3
from web3.middleware import Middleware
from cobo_waas2.api_client import ApiClient
from cobo_waas2.api import *

"""
todo 集成mpc到python
"""


def mpc_middleware(w3: Web3,pubkey: str) -> Middleware:
    def sign_and_send_raw_middleware(
        make_request: Callable[[RPCEndpoint, Any], Any], w3: "Web3"
    ) -> Callable[[RPCEndpoint, Any], RPCResponse]:
        format_and_fill_tx = compose(
            format_transaction, fill_transaction_defaults(w3), fill_nonce(w3)
        )

        def middleware(method: RPCEndpoint, params: Any) -> RPCResponse:
            if method != "eth_sendTransaction":
                return make_request(method, params)
            else:
                transaction = format_and_fill_tx(params[0])

            if not transaction.get("from"):
                return make_request(method, params)

            fm = transaction['from']
            if 'maxFeePerDataGas' in transaction:
                transaction['type'] = '0x3'
            elif 'maxFeePerGas' in transaction and 'maxPriorityFeePerGas' in transaction:
                transaction['type'] = '0x2'
            elif 'acccessList' in transaction:
                transaction['type'] = '0x1'
            else:
                transaction['type'] = '0x0'
            if 'data' in transaction:
                logging.warning(f"use input instead of data in tx dict: {transaction}")
                transaction['input'] = transaction['data']
                transaction.pop('data')
            
            result = signer.sign_transaction(fm, transaction)
            return make_request(RPCEndpoint("eth_sendRawTransaction"), [result['hex']])

        return middleware

    return sign_and_send_raw_middleware

