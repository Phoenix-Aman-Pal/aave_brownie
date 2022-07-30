from brownie import config, network, accounts, interface
from scripts.helpful_scripts import get_account
from scripts.get_weth import get_weth
from web3 import Web3

# 0.01
AMOUNT = Web3.toWei(1, "ether")


def main():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    if network.show_active() in ["mainnet-fork"]:
        get_weth()
    # ABI
    # Address
    lending_pool = get_lending_pool()
    # Now we need to approve the contract
    approve_erc20_tokens(AMOUNT, lending_pool.address, erc20_address, account)
    # Now its time to deposit
    print("Depositing !!!")
    tx = lending_pool.deposit(
        erc20_address, AMOUNT, account.address, 0, {"from": account}
    )
    tx.wait(1)
    print("Deposited !!!")
    borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)
    print("Lets borrow !!!")
    # Dai in terms of eth
    dai_eth_price = get_asset_price(
        config["networks"][network.show_active()]["dai_eth_price_feed"]
    )
    # Borrowable eth to dai
    dai_amount_to_borrow = borrowable_eth / dai_eth_price * 0.95
    print(f"We are borrowing {dai_amount_to_borrow} DAI !!!")
    # Time to borrow
    dai_address = config["networks"][network.show_active()]["dai_token"]
    borrow_tx = lending_pool.borrow(
        dai_address,
        Web3.toWei(dai_amount_to_borrow, "ether"),
        1,
        0,
        account.address,
        {"from": account},
    )
    borrow_tx.wait(1)
    print("We borrowed some DAI !!!")
    get_borrowable_data(lending_pool, account)
    repay_all(Web3.toWei(dai_amount_to_borrow, "ether"), lending_pool, account)
    get_borrowable_data(lending_pool, account)
    print("We just deposited, borrowed, repayed with aave, brownie, chainlink !!!")

def repay_all(amount, lending_pool, account):
    approve_erc20_tokens(amount, lending_pool, config["networks"][network.show_active()]["dai_token"], account)
    repay_tx = lending_pool.repay(config["networks"][network.show_active()]["dai_token"], amount, 1, account.address, {"from":account})
    repay_tx.wait(1)
    print("Repayed !!!")


def get_borrowable_data(lending_pool, account):
    (
        totalCollateralETH,
        totalDebtETH,
        availableBorrowsETH,
        currentLiquidationThreshold,
        ltv,
        healthFactor,
    ) = lending_pool.getUserAccountData(account.address)

    totalCollateralETH = Web3.fromWei(totalCollateralETH, "ether")
    totalDebtETH = Web3.fromWei(totalDebtETH, "ether")
    availableBorrowsETH = Web3.fromWei(availableBorrowsETH, "ether")
    print(f"You have {totalCollateralETH} worth of Eth deposited !!!")
    print(f"You have {totalDebtETH} worth of Eth borrowed !!!")
    print(f"You can borrow {availableBorrowsETH} worth of Eth !!!")
    return (float(availableBorrowsETH), float(totalDebtETH))


def get_asset_price(price_feed_address):
    # ABI
    # Address
    dai_eth_price_feed = interface.AggregatorV3Interface(price_feed_address)
    latest_price = dai_eth_price_feed.latestRoundData()[1]
    converted_latest_price = Web3.fromWei(latest_price, "ether")
    print(f"Latest dai/eth price is {converted_latest_price}")
    return float(converted_latest_price)


def approve_erc20_tokens(amount, spender, erc20_address, account):
    print("Approving ERC20 token !!!")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {"from": account})
    tx.wait(1)
    print("Approved !!!")
    return tx


def get_lending_pool():
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )
    lending_pool_address = lending_pool_addresses_provider.getLendingPool()
    # Now we got address of pool. Now we have to get the ABI
    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool
