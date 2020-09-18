import os
import argparse
import random
import matplotlib.pyplot as plt
from copy import deepcopy

from uniswap import Uniswap


def get_PATH(path):
    PATH = (path or 'plots/uniswap') + '/'
    os.makedirs(PATH, exist_ok=True)
    return PATH


def Swap_k_Curve(args, pool, display=False):
    tmp_pool = deepcopy(pool)

    ks, ETHs, ERC20s = [], [], []
    ks.append(tmp_pool.k)

    """Txs"""
    for _ in range(1000):  # 1000 Rounds
        if random.random() < 0.5:
            tmp_pool.ETH_to_ERC20(105)
        else:
            tmp_pool.ERC20_to_ETH_exact(105)

        ks.append(tmp_pool.k)
        ETHs.append(tmp_pool.ETH)
        ERC20s.append(tmp_pool.ERC20)

    print(">>> after 1000 txs.")
    tmp_pool.print_pool_state(bool_LT=True)

    """Plot"""
    # k_Curve
    fig, ax1 = plt.subplots()
    ln1 = ax1.plot(ks, 'c-', label='k')
    ax1.set_xlabel('transaction')
    ax1.set_ylim((1998.9e11, 2001.6e11))
    ax1.set_ylabel('k')  # , color='c')
    # ax1.tick_params('y', colors='c')

    plt.legend()

    if display:
        plt.show()
    else:
        figure = plt.gcf()  # get current figure
        figure.set_size_inches(8, 6)
        plt.savefig(get_PATH(args.path) + 'Swap_k_Curve.png', format='png', dpi=300)

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
    ax1.legend(lns, labs, loc='upper left')

    if display:
        plt.show()
    else:
        figure = plt.gcf()  # get current figure
        figure.set_size_inches(8, 6)
        plt.savefig(get_PATH(args.path) + 'Swap_ETHNERC20_Curve.png', format='png', dpi=300)


def ETH2ERC20_Swap_Curve(args, pool, display=False):
    delta_ETHs = range(1, 1000000, 1000)
    amount_ERC20s = []
    for delta_ETH in delta_ETHs:
        delta_ERC20 = pool.ETH_to_ERC20(delta_ETH, bool_update=False)
        amount_ERC20s.append(delta_ERC20 / delta_ETH)  # amount of ERC20 per 1 ETH

    # Plot
    fig, ax1 = plt.subplots()

    ln1 = ax1.plot([1, 1000000], [200, 200], 'r-', label='original')  # straight line
    ax1.set_xlabel('ETH')
    ax1.set_ylabel('ERC20', color='r')
    ax1.set_ylim((95, 205))
    ax1.tick_params('y', colors='r')

    ax2 = ax1.twinx()
    ln2 = ax2.plot(delta_ETHs, amount_ERC20s, 'b-', label='uniswap')
    ax2.set_ylabel('ERC20', color='b')
    ax2.set_ylim((95, 205))
    ax2.tick_params('y', colors='b')

    lns = ln1 + ln2
    labs = [ln.get_label() for ln in lns]
    ax1.legend(lns, labs)

    if display:
        plt.show()
    else:
        figure = plt.gcf()  # get current figure
        figure.set_size_inches(8, 6)
        plt.savefig(get_PATH(args.path) + 'ETH2ERC20_Swap_Curve.png', format='png', dpi=300)


def ERC202ETH_Swap_Curve(args, pool, display=False):
    delta_ERC20s = range(1, 200000000, 200000)
    amount_ETHs = []
    for delta_ERC20 in delta_ERC20s:
        delta_ETH = pool.ERC20_to_ETH(delta_ERC20, bool_update=False)
        amount_ETHs.append(delta_ETH / delta_ERC20)  # amount of ERC20 per 1 ETH

    n_err = amount_ETHs.count(0.)

    # Plot
    fig, ax1 = plt.subplots()

    ln1 = ax1.plot([1, 200000000], [0.005, 0.005], 'r-', label='original')  # straight line
    ax1.set_xlabel('ERC20')
    ax1.set_ylabel('ETH', color='r')
    ax1.set_ylim((0.0022, 0.0052))
    ax1.tick_params('y', colors='r')

    ax2 = ax1.twinx()
    ln2 = ax2.plot(delta_ERC20s[n_err:], amount_ETHs[n_err:], 'b-', label='uniswap')
    ax2.set_ylabel('ETH', color='b')
    ax2.set_ylim((0.0022, 0.0052))
    ax2.tick_params('y', colors='b')

    lns = ln1 + ln2
    labs = [ln.get_label() for ln in lns]
    ax1.legend(lns, labs)

    if display:
        plt.show()
    else:
        figure = plt.gcf()  # get current figure
        figure.set_size_inches(8, 6)
        plt.savefig(get_PATH(args.path) + 'ERC202ETH_Swap_Curve.png', format='png', dpi=300)


def LP_k_ETHNERC20_Curve(args, pool, display=False):
    tmp_pool = deepcopy(pool)

    ks, ETHs, ERC20s = [], [], []
    ks.append(tmp_pool.k)

    """Txs"""
    for _ in range(1000):  # 1000 Rounds
        if random.random() < 0.5:
            tmp_pool.ETH_to_ERC20(105)
        else:
            tmp_pool.ERC20_to_ETH_exact(105)

        ks.append(tmp_pool.k)
        ETHs.append(tmp_pool.ETH)
        ERC20s.append(tmp_pool.ERC20)

    print(">>> after 1000 txs.")
    tmp_pool.print_pool_state(bool_LT=True)

    """Providing Lquidity"""
    input_ETH = 200000
    required_ERC20 = tmp_pool.required_ERC20_for_liquidity(input_ETH)
    print(">>> input (ETH, ERC20) = ({}, {})".format(input_ETH, required_ERC20))
    get_LT = tmp_pool.join('0', input_ETH, required_ERC20)
    ks.append(tmp_pool.k)

    print(">>> after LP.")
    tmp_pool.print_pool_state(bool_LT=True)

    """Txs"""
    for _ in range(1000):  # 1000 Rounds
        if random.random() < 0.5:
            tmp_pool.ETH_to_ERC20(105)
        else:
            tmp_pool.ERC20_to_ETH_exact(105)

        ks.append(tmp_pool.k)
        ETHs.append(tmp_pool.ETH)
        ERC20s.append(tmp_pool.ERC20)

    print(">>> after 1000 txs.")
    tmp_pool.print_pool_state(bool_LT=True)

    """Remove Lquidity"""
    withdraw_LT = get_LT
    get_ETH, get_ERC20 = tmp_pool.out('0', withdraw_LT)
    print(">>> output (ETH, ERC20) = ({}, {})".format(get_ETH, get_ERC20))
    ks.append(tmp_pool.k)

    print(">>> after LP remove.")
    tmp_pool.print_pool_state(bool_LT=True)

    """Txs"""
    for _ in range(1000):  # 1000 Rounds
        if random.random() < 0.5:
            tmp_pool.ETH_to_ERC20(105)
        else:
            tmp_pool.ERC20_to_ETH_exact(105)

        ks.append(tmp_pool.k)
        ETHs.append(tmp_pool.ETH)
        ERC20s.append(tmp_pool.ERC20)

    print(">>> after 1000 txs.")
    tmp_pool.print_pool_state(bool_LT=True)

    """Plot"""
    # k_Curve
    fig, ax1 = plt.subplots()
    ln1 = ax1.plot(ks, 'c-', label='k')
    ax1.set_xlabel('transaction')
    ax1.set_ylabel('k')  # , color='c')
    # ax1.tick_params('y', colors='c')

    plt.legend()

    plt.axvline(x=1000, color='gray', linestyle=':', linewidth=2)
    plt.axvline(x=2000, color='gray', linestyle=':', linewidth=2)

    if display:
        plt.show()
    else:
        figure = plt.gcf()  # get current figure
        figure.set_size_inches(8, 6)
        plt.savefig(get_PATH(args.path) + 'LP_k_Curve.png', format='png', dpi=300)

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
    ax1.legend(lns, labs)

    plt.axvline(x=1000, color='gray', linestyle=':', linewidth=2)
    plt.axvline(x=2000, color='gray', linestyle=':', linewidth=2)

    if display:
        plt.show()
    else:
        figure = plt.gcf()  # get current figure
        figure.set_size_inches(8, 6)
        plt.savefig(get_PATH(args.path) + 'LP_ETHNERC20_Curve.png', format='png', dpi=300)


def LP_LT_Curve(args, pool, display=False):
    input_ETHs = range(200000, 1000000, 10000)
    LTs = []
    for input_ETH in input_ETHs:
        required_ERC20 = pool.required_ERC20_for_liquidity(input_ETH)
        # print(">>> input (ETH, ERC20) = ({}, {})".format(input_ETH, required_ERC20))
        get_LT = pool.join('0', input_ETH, required_ERC20, bool_update=False)
        LTs.append(get_LT)

    """Plot"""
    fig, ax1 = plt.subplots()
    ln1 = ax1.plot(input_ETHs, LTs, 'b-', label='LT')
    ax1.set_xlabel('ETH')
    ax1.set_ylabel('LT')

    plt.legend()

    if display:
        plt.show()
    else:
        figure = plt.gcf()  # get current figure
        figure.set_size_inches(8, 6)
        plt.savefig(get_PATH(args.path) + 'LP_LT_Curve.png', format='png', dpi=300)


def fee_Gain_Curve(args, pool, display=False):
    fees = range(1, 11)  # n * (1/1000) [%]
    Gains = []
    for fee in fees:
        tmp_pool = deepcopy(pool)  # copy
        fee /= 1000.
        tmp_pool.fee = fee

        """Providing Lquidity"""
        input_ETH = 200000
        required_ERC20 = tmp_pool.required_ERC20_for_liquidity(input_ETH)
        get_LT = tmp_pool.join('0', input_ETH, required_ERC20, bool_update=True)

        """Txs"""
        for i in range(1000):  # 1000 Rounds
            if i % 2 == 0:
                tmp_pool.ETH_to_ERC20(105)
            else:
                tmp_pool.ERC20_to_ETH_exact(105)

        """Remove Lquidity"""
        withdraw_LT = get_LT
        get_ETH, get_ERC20 = tmp_pool.out('0', withdraw_LT)
        # print(">>> output (ETH, ERC20) = ({}, {})".format(get_ETH, get_ERC20))
        Gain = get_ETH * 200 + get_ERC20
        Gains.append(Gain)

    """Plot"""
    fig, ax1 = plt.subplots()
    ln1 = ax1.plot([fee / 1000. for fee in fees], Gains, 'r-', label='ERC20')
    ax1.set_xlabel('fee')
    ax1.set_ylabel('ERC20')

    plt.legend()

    plt.axvline(x=0.003, color='gray', linestyle=':', linewidth=2)

    if display:
        plt.show()
    else:
        figure = plt.gcf()  # get current figure
        figure.set_size_inches(8, 6)
        plt.savefig(get_PATH(args.path) + 'Fee_Gain_Curve.png', format='png', dpi=300)


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

    print(">>> init pool.")
    us.print_pool_state(bool_LT=True)

    """Simulation 1-1) Swap & k"""
    Swap_k_Curve(args, us, display=args.no_save)

    """Simulation 1-2) ETH -> ERC20 Swap Curve"""
    ETH2ERC20_Swap_Curve(args, us, display=args.no_save)

    """Simulation 1-3) ERC20 -> ETH Swap Curve"""
    ERC202ETH_Swap_Curve(args, us, display=args.no_save)

    """Simulation 2-1) Providing Liquidity & k"""
    LP_k_ETHNERC20_Curve(args, us, display=args.no_save)

    """Simulation 2-3) LP & LT"""
    LP_LT_Curve(args, us, display=args.no_save)

    """Simulation 2-3) Fee & LP's Gain"""
    fee_Gain_Curve(args, us, display=args.no_save)
