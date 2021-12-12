# Into

- User can enter lottery with ETH based on a USD fee
- An admin will choose when the lottery is over (so it's not decentralized)
- The lottery will select a random winner

## Initialize brownie

- `$brownie init`

## Mainnet-fork setup

- Test early and often
- 3 ways to test

  - `mainnet-fork`, which we'll use here
  - `development` with mocks
  - `testnet`

- mainnet-forking

  - first, delete the brownie's built-in mainnet-fork, `$brownie networks delete mainnet-fork`
  - then add our custom mainnet-fork `$brownie networks add development mainnet-fork cmd=ganache-cli host=http://127.0.0.1 fork=my_Alchemy_mainnet_HTTP_address accounts=10 mnemonic=brownie port=8545`

- brownie-config.yaml

  - set up mainnet-fork network and its `eth_usd_price_feed`

## Testing

- `tests/test_lottery.py`
- `$brownie compile`
- `$brownie test --network mainnet-fork`

**Commit 1**

# Deployment

## Enums

- to add lottery phases

## import Ownable.sol

- `import "@openzeppelin/contracts/access/Ownable.sol"`
- update brownie-config.yaml accordingly
- `contract Lottery is Ownable {...}` to inherit Ownable's functions
- use modifier `onlyOwner`

## Chainlink VRF (verifiable randomness function)

- the right way to get a random number into a smart contract

- [RandomNumberConsumer.sol](https://docs.chain.link/docs/get-a-random-number/), to experiment (compile/deploy) in Remix

  - before we can call `getRandomNumber` we need to fund the Remix account with LINK token (from our MetaMask account) so it can pay the fee (~0.1LINK)
  - we need to wait a bit before clicking `randomResult` to get the random number, because there are 2 asynchronous transactions: VRF Coordinator calling `getRandomNumber` is paid by us (Remix account) to get the random number, and Chainlink node calling VRF Coordinator function `fulfillRandomness`, which is paid by Chainlink (or rather Chainlink's sponsors).
  - see [Chainlink basic request model](https://docs.chain.link/docs/architecture-request-model/) for the details

- `import "@chainlink/contracts/src/v0.6/VRFConsumerBase.sol";`
- `contract Lottery is VRFConsumerBase {`
- adding `VRFConsumerBase(_vrfCoordinator, _link)` to constructor
- add `fee`: LINK token needed to pay for the random number requst. Since it may change from blockchain to blockchain, put it in the contructor
- add `keyhash`: a unique way to identify Chainlink VRF node

## getting accounts

- see `PatrickCollins/brownie/scripts` for different ways of getting accounts
- `scripts/helpful_scripts.py`
- `.env` copied from **brownie** repository
- `brownie-config.yaml` add wallets (as in brownie repository)

## get contract

- see [github smartcontractkit/chainlink-mix](https://github.com/smartcontractkit/chainlink-mix/blob/master/scripts/helpful_scripts.py) for more of get_contract() function
- `get_contract()` helpful_scripts.py
- `contract_to_mock` map
  - `"eth_usd_price_feed": MockV3Aggregator` means contract "eth_usd_price_feed" needs to deploy on MockV3Aggregator
  - `"vrf_coordinator": VRFCoordinatorMock`
  - `"link_token": LinkToken`
- `deploy_mock()` similar to what we did in brownie FundMe, but more contracts

## contracts/test, add

- `contracts/testVRFCoordinatorMock.sol` copied from [Chainlink] (https://github.com/smartcontractkit/chainlink/blob/develop/contracts/src/v0.6/tests/VRFCoordinatorMock.sol), but changed two `import "@chainlink ...` lines
- `MockV3Aggregator.sol`, copied from [Chainlink](https://github.com/smartcontractkit/chainlink/blob/develop/contracts/src/v0.6/tests/MockV3Aggregator.sol)
- `LinkToken.sol`

## deploy_lottery.py

- `__init__.py` so python recognize packages
- `scripts/deploy_lottery.py`
- `brownie-config`, add
  - default nextork
  - rinkeby: vrf_coordinator
  - rinkeby: eth_usd_price_feed
  - link_token address from [chainlink](https://docs.chain.link/docs/link-token-contracts/)
  - (Rinkeby) keyhash and fee (0.1LINK) in both development and Rinkeby networks, from [chainlink](https://docs.chain.link/docs/vrf-contracts/)

## deployment

- `$brownie run scripts/deploy_lottery.py`
- we'll see
  - Ganache spins up
  - MockV3Aggregator deployed
  - LinkToken deployed
  - VRFCoordinatorMock deployed
  - Lottery deployed
- we are confident we can deploy this to testnet, but let's do some interaction with the contracts first.

**Commit 2**
