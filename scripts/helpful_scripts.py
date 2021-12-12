from brownie import (
    accounts,
    network,
    config,
    Contract,
    MockV3Aggregator,
    VRFCoordinatorMock,
    LinkToken,
    interface,
)

FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]


def get_account(index=None, id=None):
    # different ways of getting account (see # see PatrickCollins/brownie/scripts/)
    # 1. accounts[0]
    # 2. accounts.add("env")
    # 3. accounts.load("id")
    if index:
        return accounts[index]
    if id:
        # most secure way
        # this account will be used if in the deploy function, `account = get_account(id="MyMetaMask")`
        # see PatrickCollins/brownie/scripts/deploy_Brownie_native_account.py
        # have "MyMetaMask" (my MetaMask Rinkeby acc1)
        # password: usual
        return accounts.load(id)
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]
    return accounts.add(config["wallets"]["from_key"])
    # .env file: export PRIVATE_KEY=b9e.... (my MetaMask Rinkeby acc1)
    # brownie-config.yaml file: dotenv: .env  wallets: from_key: ${PRIVATE_KEY}


contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}


def get_contract(contract_name):
    """This function will grab the contract addresses from the brownie config
    if defined, otherwise, it will deploy a mock version of that contract, and
    return that mock contract.
        Args:
            contract_name (string)
        Returns:
            brownie.network.contract.ProjectContract: The most recently deployed
            version of this contract.(e.g. Mock3Aggregator[-1])
    """
    contract_type = contract_to_mock[contract_name]
    # let's check do we even need to deploy on Mock
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:  # if the contract has not be deployed
            # = MockV3Aggregator.length <=0
            deploy_mocks()
        contract = contract_type[-1]
        # = same as MockV3Aggregator[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        # address
        # ABI
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
        # MockV3Aggregator.abi
    return contract


DECIMALS = 8
INITIAL_VALUE = 200000000000

# compare this to what we did in brownie FundMe
def deploy_mocks(decimals=DECIMALS, initial_value=INITIAL_VALUE):
    account = get_account()
    MockV3Aggregator.deploy(decimals, initial_value, {"from": account})
    link_token = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(link_token.address, {"from": account})
    print("Deployed!")


def fund_with_link(
    contract_address, account=None, link_token=None, amount=100000000000000000
):  # 0.1 LINK
    account = (
        account if account else get_account()
    )  # if account is provided in function call then use it, otherwise ...
    link_token = link_token if link_token else get_contract("link_token")

    # method 1 - use LinkToken contract we have in contract/test
    tx = link_token.transfer(contract_address, amount, {"from": account})

    # method 2 - use interface in interfaces folder
    # link_token_contract = interface.LinkTokenInterface(link_token.address)
    # tx = link_token_contract.transfer(contract_address, amount, {"from": account})

    tx.wait(1)
    print("Fund contract!")
    return tx
