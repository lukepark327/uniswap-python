from math import floor, sqrt


class Arbitrager:
    def __init__(self,
                 balance_ERC20,
                 oracle_ratio):

        self.balance_ERC20 = balance_ERC20  # total value (Eth + ERC20)  # [ERC20]
        self.oracle_ratio = oracle_ratio    # ERC20 / Eth

        """Params"""
        self.tx_fee = {
            "Eth_to_ERC20": 46000,
            "ERC20_to_Eth": 60000,
            "default": 21000}

    def update(self, oracle_ratio):
        self.oracle_ratio = oracle_ratio

    """Balance"""

    def get_balance_Eth(self):
        return self.balance_ERC20 / self.oracle_ratio

    def get_balance_ERC20(self):
        return self.balance_ERC20

    def update_balance_Eth(self, amount_Eth):
        if self.balance_ERC20 + (amount_Eth * self.oracle_ratio) >= 0:
            self.balance_ERC20 += amount_Eth * self.oracle_ratio
        else:
            raise Exception("invalid amount.")

    def update_balance_ERC20(self, amount_ERC20):
        if self.balance_ERC20 + amount_ERC20 >= 0:
            self.balance_ERC20 += amount_ERC20
        else:
            raise Exception("invalid amount.")

    """Arbitraging"""

    # TODO: sell (liquidity providing)

    # def _sell_Eth(self, pool):
    #     pass

    # def _sell_ERC20(self, pool):
    #     pass

    def _best_number(self, X, Y, fee, unit):
        gamma = (1. - fee)
        N = floor(  # TODO: floor or ceil
            (sqrt(Y) * sqrt(gamma) * sqrt(X) / sqrt(unit) - X) / (gamma))
        return N

    def _buy_Eth(self, pool):
        # Calculating the best N_ERC20 which maximize `gain`
        N_ERC20 = self._best_number(pool.ERC20, pool.Eth, pool.fee, (1. / self.oracle_ratio))

        # Buy Eth
        delta_Eth = pool.ERC20_to_Eth(N_ERC20, bool_update=False)
        gain = delta_Eth * self.oracle_ratio - N_ERC20 - self.tx_fee["ERC20_to_Eth"]  # profit - loss - fee

        if gain <= 0:
            pass
        else:
            self.update_balance_ERC20(gain)
            pool.ERC20_to_Eth(N_ERC20, bool_update=True)

    def _buy_ERC20(self, pool):
        # Calculating the best N_Eth which maximize `gain`
        N_Eth = self._best_number(pool.Eth, pool.ERC20, pool.fee, self.oracle_ratio)

        # Buy ERC20
        delta_ERC20 = pool.Eth_to_ERC20(N_Eth, bool_update=False)
        gain = delta_ERC20 - N_Eth * self.oracle_ratio - self.tx_fee["Eth_to_ERC20"]  # profit - loss - fee

        if gain <= 0:
            pass
        else:
            self.update_balance_ERC20(gain)
            pool.Eth_to_ERC20(N_Eth, bool_update=True)

    def arbitrage(self, pool):
        current_Eth, current_ERC20 = pool.Eth, pool.ERC20
        pool_ratio = float(current_ERC20 / current_Eth)

        if pool_ratio > self.oracle_ratio:
            # self._sell_Eth(pool)
            self._buy_ERC20(pool)

        elif pool_ratio < self.oracle_ratio:
            # self._sell_ERC20(pool)
            self._buy_Eth(pool)


if __name__ == "__main__":
    from uniswap import Uniswap

    import random
    import matplotlib.pyplot as plt

    # Arbitrager
    arbitrager = Arbitrager(1000000000, 200)
    balances = []

    """init"""
    us = Uniswap('-1', 100000, 20000000, 1000000)  # 1:200
    us.print_pool_state(bool_LT=True)

    """Providing Liquidity"""
    us.join('0', 2000, 400001)
    us.print_pool_state(bool_LT=True)

    """Txs"""
    for _ in range(1000):
        if random.random() < 0.5:
            us.Eth_to_ERC20(1000)
        else:
            us.ERC20_to_Eth_exact(1000)

        # print(us.Eth, '\t', us.ERC20, '\t', float(us.ERC20 / us.Eth), '\t', arbitrager.balance_ERC20)
        arbitrager.arbitrage(us)
        # print(us.Eth, '\t', us.ERC20, '\t', float(us.ERC20 / us.Eth), '\t', arbitrager.balance_ERC20)
        # print()
        balances.append(arbitrager.balance_ERC20)

    # us.print_pool_state(bool_LT=False)

    """Removing Liquidity"""
    us.out('0', 20000)  # The LT holder takes extra fees
    us.print_pool_state(bool_LT=True)

    """Plot"""
    plt.plot(balances)
    plt.show()
