import os
import argparse
import random
import matplotlib.pyplot as plt
from copy import deepcopy

from uniswap import Uniswap
from arbitrager import Arbitrager


def get_PATH(path):
    PATH = (path or 'plots/arbitrager') + '/'
    os.makedirs(PATH, exist_ok=True)
    return PATH


def Arbitraging_Curve(args, pool, actor, display=False):
    tmp_pool = deepcopy(pool)

    ks, ETHs, ERC20s, balances, Timings = [], [], [], [], []
    ks.append(tmp_pool.k)
    ETHs.append(tmp_pool.ETH)
    ERC20s.append(tmp_pool.ERC20)
    balances.append(actor.balance_ERC20)

    """Txs"""
    for i in range(10000):  # 1000 Rounds
        if random.random() < 0.5:
            tmp_pool.ETH_to_ERC20(105 * 3)
        else:
            tmp_pool.ERC20_to_ETH_exact(105 * 3)

        ks.append(tmp_pool.k)
        ETHs.append(tmp_pool.ETH)
        ERC20s.append(tmp_pool.ERC20)

        gain = actor.arbitrage(tmp_pool)
        if gain > 0:
            Timings.append(i)

        balances.append(actor.balance_ERC20)

    """Plot"""
    # Balance
    fig, ax1 = plt.subplots()
    ln1 = ax1.plot(balances, 'r-', label='balance')
    ax1.set_xlabel('transaction')
    ax1.set_ylabel('ERC20')  # , color='c')

    plt.legend()

    for i in range(len(Timings)):
        plt.axvline(x=Timings[i], color='gray', linestyle=':', linewidth=2)

    if display:
        plt.show()
    else:
        figure = plt.gcf()  # get current figure
        figure.set_size_inches(8, 6)
        plt.savefig(get_PATH(args.path) + 'balance.png', format='png', dpi=300)

    # k_Curve
    fig, ax1 = plt.subplots()
    ln1 = ax1.plot(ks, 'c-', label='k')
    ax1.set_xlabel('transaction')
    # ax1.set_ylim((1998.9e11, 2001.6e11))
    ax1.set_ylabel('k')  # , color='c')
    # ax1.tick_params('y', colors='c')

    plt.legend(loc='lower right')

    for i in range(len(Timings)):
        plt.axvline(x=Timings[i], color='gray', linestyle=':', linewidth=2)

    if display:
        plt.show()
    else:
        figure = plt.gcf()  # get current figure
        figure.set_size_inches(8, 6)
        plt.savefig(get_PATH(args.path) + 'k_Curve.png', format='png', dpi=300)

    # ETHNERC20_Curve
    fig, ax1 = plt.subplots()

    ln1 = ax1.plot(ETHs, 'b-', label='ETH')
    ax1.set_xlabel('transaction')
    ax1.set_ylabel('ETH', color='b')
    ax1.tick_params('y', colors='b')

    ax2 = ax1.twinx()
    ln2 = ax2.plot(ERC20s, 'r-', label='ERC20')
    ax2.set_ylabel('ERC20', color='r')
    ax2.tick_params('y', colors='r')

    lns = ln1 + ln2
    labs = [ln.get_label() for ln in lns]
    ax1.legend(lns, labs, loc='lower right')

    for i in range(len(Timings)):
        plt.axvline(x=Timings[i], color='gray', linestyle=':', linewidth=2)

    if display:
        plt.show()
    else:
        figure = plt.gcf()  # get current figure
        figure.set_size_inches(8, 6)
        plt.savefig(get_PATH(args.path) + 'ETHNERC20_Curve.png', format='png', dpi=300)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, default=950327)
    parser.add_argument('--path')  # location of log files
    parser.add_argument('--no-save', action='store_true')
    args = parser.parse_args()
    print(args)

    random.seed(args.seed)

    """init"""
    us = Uniswap(address='-1',
                 amount_ETH=1000000,
                 amount_ERC20=200000000,  # ETH:ERC20 = 1:200
                 init_LT=1000000,
                 fee=0.003)
    arbitrager = Arbitrager(1000000000, 200.)  # [ERC20]

    """Simulation)
    # ETH <-> ERC20 & Arbitraging Timing
    # k & Arbitraging Timing
    # Arbitrager's Gain
    """
    Arbitraging_Curve(args, us, arbitrager, display=args.no_save)
