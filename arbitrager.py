from math import floor, sqrt


class Arbitrager:
    def __init__(self,
                 balance_ERC20,
                 oracle_ratio):

        self.balance_ERC20 = balance_ERC20      # total value (ETH + ERC20)  # [ERC20]
        self.oracle_ratio = oracle_ratio    # ERC20 / ETH

        """Params"""
        self.tx_fee = {
            "ETH2ERC20": 46000,
            "ERC202ETH": 60000,
            "default": 21000}

    def update(self, oracle_ratio):
        self.oracle_ratio = oracle_ratio

    """Balance"""

    def get_balance_ETH(self):
        return self.balance_ERC20 / self.oracle_ratio

    def get_balance_ERC20(self):
        return self.balance_ERC20

    def update_balance_ETH(self, amount_ETH):
        if self.balance_ERC20 + (amount_ETH * self.oracle_ratio) >= 0:
            self.balance_ERC20 += amount_ETH * self.oracle_ratio
        else:
            raise Exception("invalid amount.")

    def update_balance_ERC20(self, amount_ERC20):
        if self.balance_ERC20 + amount_ERC20 >= 0:
            self.balance_ERC20 += amount_ERC20
        else:
            raise Exception("invalid amount.")

    """Arbitraging"""

    # TODO: sell (liquidity providing)

    # def _sell_ETH(self, pool):
    #     pass

    # def _sell_ERC20(self, pool):
    #     pass

    def _best_number(self, X, Y, fee, unit):
        gamma = (1. - fee)
        N = floor(  # TODO: floor or ceil
            (sqrt(Y) * sqrt(gamma) * sqrt(X) / sqrt(unit) - X) / (gamma))
        return N

    def _buy_ETH(self, pool):
        # Calculating the best N_ERC20 which maximize `gain`
        N_ERC20 = self._best_number(pool.ERC20, pool.ETH, pool.fee, (1. / self.oracle_ratio))

        # Buy ETH
        delta_ETH = pool.ERC20_to_ETH(N_ERC20, bool_update=False)
        gain = delta_ETH * self.oracle_ratio - N_ERC20 - self.tx_fee["ERC202ETH"]  # profit - loss - fee

        if gain <= 0:
            pass
        else:
            self.update_balance_ERC20(gain)
            pool.ERC20_to_ETH(N_ERC20, bool_update=True)

        return gain

    def _buy_ERC20(self, pool):
        # Calculating the best N_ETH which maximize `gain`
        N_ETH = self._best_number(pool.ETH, pool.ERC20, pool.fee, self.oracle_ratio)

        # Buy ERC20
        delta_ERC20 = pool.ETH_to_ERC20(N_ETH, bool_update=False)
        gain = delta_ERC20 - N_ETH * self.oracle_ratio - self.tx_fee["ETH2ERC20"]  # profit - loss - fee

        if gain <= 0:
            pass
        else:
            self.update_balance_ERC20(gain)
            pool.ETH_to_ERC20(N_ETH, bool_update=True)

        return gain

    def arbitrage(self, pool):
        current_ETH, current_ERC20 = pool.ETH, pool.ERC20
        pool_ratio = float(current_ERC20 / current_ETH)

        if pool_ratio > self.oracle_ratio:
            # self._sell_ETH(pool)
            return self._buy_ERC20(pool)

        elif pool_ratio < self.oracle_ratio:
            # self._sell_ERC20(pool)
            return self._buy_ETH(pool)


if __name__ == "__main__":
    from uniswap import Uniswap

    import random
    import matplotlib.pyplot as plt

    random.seed(12345)

    # Arbitrager
    arbitrager = Arbitrager(1000000000, 200.)
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
            us.ETH_to_ERC20(1000)
        else:
            us.ERC20_to_ETH_exact(1000)

        # print(us.ETH, '\t', us.ERC20, '\t', float(us.ERC20 / us.ETH), '\t', arbitrager.balance_ERC20)
        arbitrager.arbitrage(us)
        # print(us.ETH, '\t', us.ERC20, '\t', float(us.ERC20 / us.ETH), '\t', arbitrager.balance_ERC20)
        # print()
        balances.append(arbitrager.balance_ERC20)

    # us.print_pool_state(bool_LT=False)

    """Removing Liquidity"""
    us.out('0', 20000)  # The LT holder takes extra fees
    us.print_pool_state(bool_LT=True)

    """Plot"""
    plt.plot(balances)
    plt.xlabel('round')
    plt.ylabel('balance')
    plt.show()
