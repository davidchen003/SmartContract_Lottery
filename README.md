[Course TOC, code, resources, etc](https://github.com/smartcontractkit/full-blockchain-solidity-course-py/blob/main/README.md#lesson-7-smartcontract-lottery)

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

## Python Lottery Scripts/Functions

- start_lottery()
- enter_lottery()
- end_lottery()
  - need fund the contract with LINK token because we need to get the random number
  - since it's a common function, create `fund_with_link()` in helpful_script
    - method 1, use LinkToken we have in contracts/test folder
    - method 2, use `LinkTokenInterface.sol` in interfaces folder, copied from [chainlink](https://github.com/smartcontractkit/chainlink-mix/blob/master/interfaces/LinkTokenInterface.sol), which will compiled down to a way that brownie knows how to interact with

## Interact with contract

- `$brownie run scripts/deploy_lottery.py`, will only get "0x0000000000000000000000000000000000000000 is the new winner", because there is no Chainlink node on Ganache

**Commit 3**

# Testing

- Unit tests: a way of testing the smallest pieces of code in an isolated instance, done in development network
- integration tests: a way of testing across multiple complex systems, done on testnet
- typically people add `unit` and `integration` folders under tests folder, but since we only have one file under each, we'll just use script names to differentiate one from another `test_lottery_unit.py` and `test_lottery_integration.py`

## Unit tests, on Ganache

- `$brownie test -k test_get_entrance_fee`

  - before adding `if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:`, pass
  - after, skipped

- add

  - `test_cant_enter_unless_started()`
  - `test_can_start_and_enter_lottery()`
  - `test_can_end_lottery()`
  - `test_can_pick_winner_correctly()`
    - we need to test the `fulfillRandomness()` in endLottery, and everything in it.
    - in `VRFCoordinatorMock`, `callBackWithRandomness()` calls `rawFulfillRandomness`, which eventually calls `fulfillRandomness()`
    - we have to pretend to be a chainlink node to call `callBackWithRandomness()`, which returns the random number and the address of the contract to return the random number to, but also have to pass the requestId of the original call.
    - however, the `endLottery`, which has the requestId, doesn't return anything. In order to get that info, we need to use **Event**

- **Events** and logs

  - Event is a piece of data executed/stored in the blockchain but are not accessible by any contract. you can kinda of think of them as the print statement of blockchain.
  - add `event RequestedRandomness(bytes32 requestId);` and `emit RequestedRandomness(requestId);` in `endLottry()` of Lottery.sol
  - use it in test script, `request_id = transaction.events["RequestedRandomness"]["requestId"]`, to get the `requestId`.
  - with this requestID, we can pretend to be a chainlink node and use this `callBackWithRandomness()` to dummy getting back a random number from chainlink node.

- do unit test one by one
  - `$brownie test -k test_can_pick_winner_correctly`
  - etc.

**Commit 4**

## Integration test and deployment, on Rinkeby

- `test_lottery_integration.py`
- make sure `dotenv: .env` in brownie-config.yaml
- make sure you have LINK token in MetaMask account
- `$brownie test -k test_can_pick_winner --network rinkeby -s` (`-s` so to have detailed brownie printout)

**Errors**

- unit test `test_can_pick_winner_correctly` pass, but `$brownie run scripts/deploy_lottery.py` has printout `0x0000000000000000000000000000000000000000 is the new winner!`!
- integration test `$brownie test -k test_can_pick_winner --network rinkeby -s` fail
  - assert lottery.recentWinner() == account
  - AssertionError: assert '0x0000000000...0000000000000' == <LocalAccount...FAF140824B0d'>
  - seems responsed way more than 60seconds! maybe that's the reason?
- **deployment to Rinkeby** `$brownie run scripts/deploy_lottery.py --network rinkeby`
  - terminal printout `0x0000000000000000000000000000000000000000 is the new winner!` however
  - checking the deployed contract (0x92697A4dbA8e35302Fe0e5d2a854158515E94B18) at Rinkeby etherscan -> Contract -> Read Contract -> recentWinner, we'll see the correct winner account

**Commit 5**
