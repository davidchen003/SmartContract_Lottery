from brownie import Lottery, accounts, config, network
from web3 import Web3


def test_get_entrance_fee():
    account = accounts[0]
    lottery = Lottery.deploy(
        config["networks"][network.show_active()]["eth_usd_price_feed"],
        {"from": account},
    )
    # at current ETH price of $4130, $50 is about 0.0121 ETH, or 12100000000000000 Wei
    # assert lottery.getEntranceFee() > 12000000000000000

    assert lottery.getEntranceFee() > Web3.toWei(0.011, "ether")
    assert lottery.getEntranceFee() < Web3.toWei(0.013, "ether")
