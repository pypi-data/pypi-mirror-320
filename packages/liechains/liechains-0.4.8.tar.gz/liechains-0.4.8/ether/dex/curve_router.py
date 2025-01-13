import json, time

from ether.client import Web3Client
from ether.dex.swap import Swap

curve_router_abi = json.loads(
    '[{"name":"Exchange","inputs":[{"name":"sender","type":"address","indexed":true},{"name":"receiver","type":"address","indexed":true},{"name":"route","type":"address[11]","indexed":false},{"name":"swap_params","type":"uint256[5][5]","indexed":false},{"name":"pools","type":"address[5]","indexed":false},{"name":"in_amount","type":"uint256","indexed":false},{"name":"out_amount","type":"uint256","indexed":false}],"anonymous":false,"type":"event"},{"stateMutability":"payable","type":"fallback"},{"stateMutability":"nonpayable","type":"constructor","inputs":[{"name":"_weth","type":"address"},{"name":"_stable_calc","type":"address"},{"name":"_crypto_calc","type":"address"}],"outputs":[]},{"stateMutability":"payable","type":"function","name":"exchange","inputs":[{"name":"_route","type":"address[11]"},{"name":"_swap_params","type":"uint256[5][5]"},{"name":"_amount","type":"uint256"},{"name":"_min_dy","type":"uint256"}],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"payable","type":"function","name":"exchange","inputs":[{"name":"_route","type":"address[11]"},{"name":"_swap_params","type":"uint256[5][5]"},{"name":"_amount","type":"uint256"},{"name":"_min_dy","type":"uint256"},{"name":"_pools","type":"address[5]"}],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"payable","type":"function","name":"exchange","inputs":[{"name":"_route","type":"address[11]"},{"name":"_swap_params","type":"uint256[5][5]"},{"name":"_amount","type":"uint256"},{"name":"_min_dy","type":"uint256"},{"name":"_pools","type":"address[5]"},{"name":"_receiver","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"view","type":"function","name":"get_dy","inputs":[{"name":"_route","type":"address[11]"},{"name":"_swap_params","type":"uint256[5][5]"},{"name":"_amount","type":"uint256"}],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"view","type":"function","name":"get_dy","inputs":[{"name":"_route","type":"address[11]"},{"name":"_swap_params","type":"uint256[5][5]"},{"name":"_amount","type":"uint256"},{"name":"_pools","type":"address[5]"}],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"view","type":"function","name":"get_dx","inputs":[{"name":"_route","type":"address[11]"},{"name":"_swap_params","type":"uint256[5][5]"},{"name":"_out_amount","type":"uint256"},{"name":"_pools","type":"address[5]"}],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"view","type":"function","name":"get_dx","inputs":[{"name":"_route","type":"address[11]"},{"name":"_swap_params","type":"uint256[5][5]"},{"name":"_out_amount","type":"uint256"},{"name":"_pools","type":"address[5]"},{"name":"_base_pools","type":"address[5]"}],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"view","type":"function","name":"get_dx","inputs":[{"name":"_route","type":"address[11]"},{"name":"_swap_params","type":"uint256[5][5]"},{"name":"_out_amount","type":"uint256"},{"name":"_pools","type":"address[5]"},{"name":"_base_pools","type":"address[5]"},{"name":"_base_tokens","type":"address[5]"}],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"view","type":"function","name":"version","inputs":[],"outputs":[{"name":"","type":"string"}]}]'
)


class CurveRouter(Swap):
    def __init__(self, w3: Web3Client, _route, _params, _pools) -> None:
        self.cli = w3
        self.router = self.cli.eth.contract(
            address="0x16C6521Dff6baB339122a0FE25a9116693265353", abi=curve_router_abi
        )
        self._route = _route
        self._params = _params
        self._pools = _pools
        self.sender = w3.acc.address

    def quote(self, amount_in) -> int:
        """
        根据token和amount_in报价
        各协议各自实现
        """
        out = self.router.functions["get_dy"](
            self._route,self._params, amount_in,self._pools
        ).call()
        return out

    def swap(self, amount_in, min_amount_out):
        """
        执行swap
        """
        out = self.router.functions["exchange"](
            self._route,self._params, amount_in, min_amount_out,self._pools
        ).transact()
        return out
