from math import floor, ceil  # for quantization
from pprint import pprint


class Uniswap:  # between Eth and ERC20
    def __init__(self,
                 address,
                 amount_ETH,   # ex) (1.) * n
                 amount_ERC20,    # ex) (200. ~= 199.5) * n
                 init_LT,
                 fee=0.003      # 0.3%
                 ):

        self.ETH, self.ERC20, self.LT = amount_ETH, amount_ERC20, init_LT
        self.k = self.ETH * self.ERC20  # constant product
        self.fee = fee

        self.LT_holders = {}
        self.LT_holders[address] = init_LT

    def _update(self, ETH_prime, ERC20_prime, LT_prime=None):
        if LT_prime is not None:
            self.LT = LT_prime
        self.ETH, self.ERC20 = ETH_prime, ERC20_prime
        self.k = self.ETH * self.ERC20

    def update_fee(self, new_fee):
        self.fee = new_fee

    """Swap Protocol"""

    def _get_input_price(self, delta_X, X, Y, bool_fee=True):
        # Validity check
        if (X == 0) or (Y == 0):
            raise Exception("invalid X: {} or Y: {}".format(X, Y))

        alpha = float(delta_X / X)
        gamma = (1. - self.fee) if bool_fee else (1.)

        delta_Y = floor(alpha * gamma / (1. + alpha * gamma) * Y)

        # Validity check
        if delta_Y >= Y:
            raise Exception("invalid delta_Y. {} >= {}".format(delta_Y, Y))

        return delta_Y

    def _get_output_price(self, delta_Y, Y, X, bool_fee=True):
        # Validity check
        if (X == 0) or (Y == 0):
            raise Exception("invalid X: {} or Y: {}".format(X, Y))
        if delta_Y >= Y:
            raise Exception("invalid delta_Y. {} >= {}".format(delta_Y, Y))

        beta = float(delta_Y / Y)
        gamma = (1. - self.fee) if bool_fee else (1.)

        delta_X = floor(beta / ((1. - beta) * gamma) * X) + 1
        return delta_X

    def ETH_to_ERC20(self, delta_ETH, bool_fee=True, bool_update=True):
        ETH_prime = self.ETH + delta_ETH
        delta_ERC20 = self._get_input_price(delta_ETH, self.ETH, self.ERC20, bool_fee=bool_fee)

        if bool_update:
            ERC20_prime = self.ERC20 - delta_ERC20
            self._update(ETH_prime, ERC20_prime)  # Pool update
        return delta_ERC20

    def ETH_to_ERC20_exact(self, delta_ERC20, bool_fee=True, bool_update=True):
        delta_ETH = self._get_output_price(delta_ERC20, self.ERC20, self.ETH, bool_fee=bool_fee)
        ETH_prime = self.ETH + delta_ETH

        if bool_update:
            ERC20_prime = self.ERC20 - delta_ERC20
            self._update(ETH_prime, ERC20_prime)  # Pool update
        return delta_ETH

    def ERC20_to_ETH(self, delta_ERC20, bool_fee=True, bool_update=True):
        ERC20_prime = self.ERC20 + delta_ERC20
        delta_ETH = self._get_input_price(delta_ERC20, self.ERC20, self.ETH, bool_fee=bool_fee)

        if bool_update:
            ETH_prime = self.ETH - delta_ETH
            self._update(ETH_prime, ERC20_prime)  # Pool update
        return delta_ETH

    def ERC20_to_ETH_exact(self, delta_ETH, bool_fee=True, bool_update=True):
        delta_ERC20 = self._get_output_price(delta_ETH, self.ETH, self.ERC20, bool_fee=bool_fee)
        ERC20_prime = self.ERC20 + delta_ERC20

        if bool_update:
            ETH_prime = self.ETH - delta_ETH
            self._update(ETH_prime, ERC20_prime)  # Pool update
        return delta_ERC20

    """Liquidity Protocol"""

    def required_ERC20_for_liquidity(self, delta_ETH):
        alpha = float(delta_ETH / self.ETH)

        ERC20_prime = floor((1. + alpha) * self.ERC20) + 1
        return ERC20_prime - self.ERC20

    def join(self, address, delta_ETH, delta_ERC20, bool_update=True):
        # delta_ERC20 validity check
        current_required_ERC20_for_liquidity = self.required_ERC20_for_liquidity(delta_ETH)
        if current_required_ERC20_for_liquidity != delta_ERC20:
            raise Exception("invalid delta_ERC20. Require {} ERC20 but input is {}".format(
                current_required_ERC20_for_liquidity, delta_ERC20))

        delta_LT = self._mint(delta_ETH, delta_ERC20, bool_update=bool_update)
        if address in self.LT_holders.keys():
            self.LT_holders[address] += delta_LT
        else:
            self.LT_holders[address] = delta_LT

        return delta_LT

    def out(self, address, delta_LT, bool_update=True):
        # Ownership validity check
        if address not in self.LT_holders.keys():
            raise Exception("invalid address")

        # delta_LT validity check
        if self.LT_holders[address] < delta_LT:
            raise Exception("invalid delta_LT. Have to be under {} LT but input is {}".format(
                self.LT_holders[address], delta_LT))

        delta_ETH, delta_ERC20 = self._burn(delta_LT, bool_update=bool_update)
        self.LT_holders[address] -= delta_LT
        if self.LT_holders[address] == 0:
            del self.LT_holders[address]

        return delta_ETH, delta_ERC20

    def _mint(self, delta_ETH, delta_ERC20, bool_update=True):  # add_liquidity
        alpha = float(delta_ETH / self.ETH)

        ETH_prime = self.ETH + delta_ETH
        ERC20_prime = floor((1. + alpha) * self.ERC20) + 1
        LT_prime = floor((1. + alpha) * self.LT)
        delta_LT = LT_prime - self.LT

        if bool_update:
            self._update(ETH_prime, ERC20_prime, LT_prime)  # Pool update
        return delta_LT

    def _burn(self, delta_LT, bool_update=True):  # remove_liquidity
        alpha = float(delta_LT / self.LT)

        ETH_prime = ceil((1. - alpha) * self.ETH)
        ERC20_prime = ceil((1. - alpha) * self.ERC20)
        LT_prime = self.LT - delta_LT
        delta_ETH = self.ETH - ETH_prime
        delta_ERC20 = self.ERC20 - ERC20_prime

        if bool_update:
            self._update(ETH_prime, ERC20_prime, LT_prime)  # burn LT
        return delta_ETH, delta_ERC20

    """Logging"""

    def print_pool_state(self, bool_LT=False):
        print("ETH\t\tERC20\t\tk\t\tLT")
        print("{}\t\t{}\t{}\t{}".format(
            self.ETH, self.ERC20, self.k, self.LT))
        if bool_LT:
            pprint(self.LT_holders)
        print('\n')


if __name__ == "__main__":
    import random

    random.seed(12345)

    """init"""
    us = Uniswap('-1', 100000, 20000000, 1000000)  # 1:200
    us.print_pool_state(bool_LT=True)

    """Providing Liquidity"""
    print(us.join('0', 2000, 400001))
    us.print_pool_state(bool_LT=True)

    """Txs"""
    for _ in range(1000000):
        if random.random() < 0.5:
            us.ETH_to_ERC20(2)
        else:
            us.ERC20_to_ETH_exact(2)
    us.print_pool_state(bool_LT=False)

    """Removing Liquidity"""
    print(us.out('0', 20000))  # The LT holder takes extra fees
    us.print_pool_state(bool_LT=True)
