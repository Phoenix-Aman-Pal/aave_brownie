from scripts.helpful_scripts import get_account
from brownie import interface, network, config

def get_weth():
    '''
    Mint WEth by depositing Eth
    '''
    #ABI
    #Address
    account = get_account()
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    tx = weth.deposit({"from": account, "value":1*10**18})
    tx.wait(1)
    print("Recieved 1 WEth !!!")
    return tx

def main():
    get_weth()