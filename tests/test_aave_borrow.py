from sre_constants import SUCCESS
from scripts.aave_borrow import approve_erc20_tokens, get_asset_price, get_lending_pool
from scripts.helpful_scripts import get_account
from brownie import network, config, accounts


def test_get_asset_price():
    asset_price = get_asset_price(config["networks"][network.show_active()]["dai_eth_price_feed"])
    assert asset_price>0

def test_get_lending_pool():
    lending_pool = get_lending_pool()
    assert lending_pool is not None

def test_approve_erc20():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    lending_pool = get_lending_pool()
    amount = 10**17
    tx = approve_erc20_tokens(amount, lending_pool.address, erc20_address, account)
    tx.wait(1)
    assert tx is not True