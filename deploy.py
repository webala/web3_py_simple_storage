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

# Send
transactionHash = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
transactionReceipt = w3.eth.wait_for_transaction_receipt(
    transactionHash
)  # code stops and waits for transaction to go through


# working with the contract -> contract address and contract ABI needed

simple_storage = w3.eth.contract(address=transactionReceipt.contractAddress, abi=abi)
# Call -> Simulate making a call and getting a return value (No state change)
# Transact -> Actually making a state change
print(simple_storage.functions.retrieve().call())  # function doesnt make a state change
store_transaction = simple_storage.functions.store(15).buildTransaction(
    {
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce
        + 1,  # This nonce has alredy been used in buiding the contract transaction hence add 1
    }
)
# txn -> Transaction
signed_store_txn = w3.eth.account.signTransaction(store_transaction, private_key=private_key)
store_txn_hash = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
store_txn_receipt = w3.eth.wait_for_transaction_receipt(store_txn_hash)

print(simple_storage.functions.retrieve().call())  # function doesnt make a state change

