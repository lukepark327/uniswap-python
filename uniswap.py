from math import floor, ceil  # for quantization
from pprint import pprint


class Uniswap:  # between Eth and Token
    def __init__(self,
                 address,
                 amount_Eth,
                 amount_ERC20,
                 init_LT,
                 fee=0.003  # 0.3%
                 ):

        self.Eth, self.ERC20, self.LT = amount_Eth, amount_ERC20, init_LT
        self.k = self.Eth * self.ERC20  # constant product
        self.fee = fee

        self.LT_holders = {}
        self.LT_holders[address] = init_LT

    def _update(self, Eth_prime, ERC20_prime, LT_prime=None):
        if LT_prime is not None:
            self.LT = LT_prime
        self.Eth, self.ERC20 = Eth_prime, ERC20_prime
        self.k = self.Eth * self.ERC20

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

    def Eth_to_ERC20(self, delta_Eth, bool_fee=True, bool_update=True):
        Eth_prime = self.Eth + delta_Eth
        delta_ERC20 = self._get_input_price(delta_Eth, self.Eth, self.ERC20, bool_fee=bool_fee)
        ERC20_prime = self.ERC20 - delta_ERC20

        if bool_update:
            self._update(Eth_prime, ERC20_prime)
        return delta_ERC20

    def Eth_to_ERC20_exact(self, delta_ERC20, bool_fee=True, bool_update=True):
        delta_Eth = self._get_output_price(delta_ERC20, self.ERC20, self.Eth, bool_fee=bool_fee)
        Eth_prime = self.Eth + delta_Eth
        ERC20_prime = self.ERC20 - delta_ERC20

        if bool_update:
            self._update(Eth_prime, ERC20_prime)
        return delta_Eth

    def ERC20_to_Eth(self, delta_ERC20, bool_fee=True, bool_update=True):
        ERC20_prime = self.ERC20 + delta_ERC20
        delta_Eth = self._get_input_price(delta_ERC20, self.ERC20, self.Eth, bool_fee=bool_fee)
        Eth_prime = self.Eth - delta_Eth

        if bool_update:
            self._update(Eth_prime, ERC20_prime)
        return delta_Eth

    def ERC20_to_Eth_exact(self, delta_Eth, bool_fee=True, bool_update=True):
        delta_ERC20 = self._get_output_price(delta_Eth, self.Eth, self.ERC20, bool_fee=bool_fee)
        ERC20_prime = self.ERC20 + delta_ERC20
        Eth_prime = self.Eth - delta_Eth

        if bool_update:
            self._update(Eth_prime, ERC20_prime)
        return delta_ERC20

    """Liquidity Protocol"""

    def required_ERC20_for_liquidity(self, delta_Eth):
        alpha = float(delta_Eth / self.Eth)

        ERC20_prime = floor((1. + alpha) * self.ERC20) + 1
        return ERC20_prime - self.ERC20

    def join(self, address, delta_Eth, delta_ERC20):
        # delta_ERC20 validity check
        current_required_ERC20_for_liquidity = self.required_ERC20_for_liquidity(delta_Eth)
        if current_required_ERC20_for_liquidity != delta_ERC20:
            raise Exception("invalid delta_ERC20. Require {} ERC20 but input is {}".format(
                current_required_ERC20_for_liquidity, delta_ERC20))

        delta_LT = self._mint(delta_Eth, delta_ERC20)
        if address in self.LT_holders.keys():
            self.LT_holders[address] += delta_LT
        else:
            self.LT_holders[address] = delta_LT

        return delta_LT

    def out(self, address, delta_LT):
        # Ownership validity check
        if address not in self.LT_holders.keys():
            raise Exception("invalid address")

        # delta_LT validity check
        if self.LT_holders[address] < delta_LT:
            raise Exception("invalid delta_LT. Have to be under {} LT but input is {}".format(
                self.LT_holders[address], delta_LT))

        delta_Eth, delta_ERC20 = self._burn(delta_LT)
        self.LT_holders[address] -= delta_LT
        if self.LT_holders[address] == 0:
            del self.LT_holders[address]

        return delta_Eth, delta_ERC20

    def _mint(self, delta_Eth, delta_ERC20):  # add_liquidity
        alpha = float(delta_Eth / self.Eth)

        Eth_prime = self.Eth + delta_Eth
        ERC20_prime = floor((1. + alpha) * self.ERC20) + 1
        LT_prime = floor((1. + alpha) * self.LT)
        delta_LT = LT_prime - self.LT

        self._update(Eth_prime, ERC20_prime, LT_prime)
        return delta_LT

    def _burn(self, delta_LT):  # remove_liquidity
        alpha = float(delta_LT / self.LT)

        Eth_prime = ceil((1. - alpha) * self.Eth)
        ERC20_prime = ceil((1. - alpha) * self.ERC20)
        LT_prime = self.LT - delta_LT
        delta_Eth = self.Eth - Eth_prime
        delta_ERC20 = self.ERC20 - ERC20_prime

        self._update(Eth_prime, ERC20_prime, LT_prime)
        return delta_Eth, delta_ERC20

    """Logging"""

    def print_pool_state(self, bool_LT=False):
        print("Eth\t\tERC20\t\tk\t\tLT")
        print("{}\t\t{}\t{}\t{}".format(
            self.Eth, self.ERC20, self.k, self.LT))
        if bool_LT:
            pprint(self.LT_holders)
        print('\n')


if __name__ == "__main__":
    import random

    """init"""
    us = Uniswap('-1', 100000, 20000000, 100000)
    us.print_pool_state(bool_LT=True)

    """Providing Liquidity"""
    print(us.join('0', 2000, 400001))
    us.print_pool_state(bool_LT=True)

    """Txs"""
    for _ in range(1000000):
        if random.random() < 0.5:
            us.Eth_to_ERC20(2)
        else:
            us.ERC20_to_Eth_exact(2)
    us.print_pool_state(bool_LT=False)

    """Removing Liquidity"""
    print(us.out('0', 2000))  # The LT holder takes extra fees
    us.print_pool_state(bool_LT=True)
