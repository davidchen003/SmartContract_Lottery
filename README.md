# Into

- User can enter lottery with ETH based on a USD fee
- An admin will choose when the lottery is over (so it's not decentralized)
- The lottery will select a random winner

## Initialize brownie

- `$brownie init`

## Mainnet-fork setup for testing

- Test early and often
- 3 ways to test

  - `mainnet-fork`, which we'll use here
  - `development` with mocks
  - `testnet`

- mainnet-forking

  - first, delete the brownie's built-in mainnet-fork, `$brownie networks delete mainnet-fork`
  - then add our custom mainnet-fork `$brownie networks add development mainnet-fork cmd=ganache-cli host=http://127.0.0.1 fork=my_Alchemy_mainnet_HTTP_address accounts=10 mnemonic=brownie port=8545`

- brownie-config.yaml

  - set up mainnet-fork and `eth_usd_price_feed`

- test
  - `$brownie compile`
  - `$brownie test --network mainnet-fork`

**Commit 1**
