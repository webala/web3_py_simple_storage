import json
import os
from curses.ascii import SI
from solcx import compile_standard
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()


with open("./simpleStorage.sol", "r") as file:
    simple_storage_file = file.read()


# Compile our solidity
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"simpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.8.0",
)

with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)


# Deploy the contract
# get bytecode
bytecode = compiled_sol["contracts"]["simpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# get ABI(Application binary interface)
abi = compiled_sol["contracts"]["simpleStorage.sol"]["SimpleStorage"]["abi"]


# connect to ganache
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
chain_id = 1337
my_address = "0x3dBdE3D9b38d09f4b35f51D3CCd63c59326A10a5"
private_key = os.getenv("PRIVATE_KEY")
print(private_key)

# create the contract in python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)


# get latest transaction
nonce = w3.eth.getTransactionCount(my_address)

# 1. Build a transaction
# 2. Sign a transaction
# 3. Send a transaction


# Build
transaction = SimpleStorage.constructor().buildTransaction(
    {"chainId": chain_id, "from": my_address, "nonce": nonce}
)

# Sign
signed_transaction = w3.eth.account.sign_transaction(
    transaction, private_key=private_key
)
