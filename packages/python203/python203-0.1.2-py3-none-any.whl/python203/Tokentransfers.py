from web3 import Web3
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)

# Infura project ID
INFURA_PROJECT_ID = "f6b751d1f86b42f2bd23af09b4547634"
INFURA_URL = f"https://sepolia.infura.io/v3/{INFURA_PROJECT_ID}"

# Initialize Web3
web3 = Web3(Web3.HTTPProvider(INFURA_URL))

# Check connection
if web3.is_connected():
    logging.info("Connected to the Sepolia testnet via Infura.")
else:
    logging.error("Failed to connect to the Sepolia testnet.")
    exit()

# Contract details
CONTRACT_ADDRESS = web3.to_checksum_address("0xA0f0a2D53b3476c50F2Cf24307F8a1Cd3c758254")
CONTRACT_ABI = json.loads('''
[
    {
        "inputs": [{"internalType": "address","name": "initialOwner","type": "address"}],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "inputs": [{"internalType": "address","name": "to","type": "address"},{"internalType": "uint256","name": "amount","type": "uint256"}],
        "name": "transfer",
        "outputs": [{"internalType": "bool","name": "","type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "address","name": "account","type": "address"}],
        "name": "balanceOf",
        "outputs": [{"internalType": "uint256","name": "","type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "name",
        "outputs": [{"internalType": "string","name": "","type": "string"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "symbol",
        "outputs": [{"internalType": "string","name": "","type": "string"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"internalType": "uint256","name": "","type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]
''')

# Initialize contract
contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)


class TokenTransfer:
    def __init__(self, private_key: str, sender_address: str):
        """
        Initialize the TokenTransfer class.

        Args:
            private_key (str): The private key of the sender's wallet.
            sender_address (str): The sender's wallet address.
        """
        self.private_key = private_key
        self.sender_address = web3.to_checksum_address(sender_address)

    def get_balance(self, address: str):
        """
        Get the token balance of a given address.

        Args:
            address (str): The wallet address.

        Returns:
            float: The token balance in ether units.
        """
        address = web3.to_checksum_address(address)
        balance = contract.functions.balanceOf(address).call()
        return web3.from_wei(balance, 'ether')

    def transfer_tokens_from_rating(self, user_address: str, rating: float):
        """
        Transfer tokens to a user based on the backtest rating.

        Args:
            user_address (str): The address of the receiver.
            rating (float): The backtest rating to convert to token amount.
        """
        try:
            # Convert rating to token units
            user_address = web3.to_checksum_address(user_address)
            token_amount = web3.to_wei(rating, 'ether')

            # Log balances before the transaction
            sender_balance = self.get_balance(self.sender_address)
            recipient_balance = self.get_balance(user_address)

            logging.info(f"Sender Balance Before: {sender_balance} tokens")
            logging.info(f"Recipient Balance Before: {recipient_balance} tokens")

            # Build the transaction
            transaction = contract.functions.transfer(user_address, token_amount).build_transaction({
                'from': self.sender_address,
                'gas': 200000,
                'gasPrice': web3.to_wei('50', 'gwei'),
                'nonce': web3.eth.get_transaction_count(self.sender_address)
            })

            # Sign the transaction
            signed_tx = web3.eth.account.sign_transaction(transaction, private_key=self.private_key)

            # Send the raw transaction
            tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)

            logging.info(f"Transaction sent. TX hash: {web3.to_hex(tx_hash)}")

            # Wait for receipt
            receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            logging.info(f"Transaction confirmed. Receipt: {receipt}")

            # Log balances after the transaction
            sender_balance = self.get_balance(self.sender_address)
            recipient_balance = self.get_balance(user_address)
            total_supply = web3.from_wei(contract.functions.totalSupply().call(), 'ether')

            logging.info(f"Sender Balance After: {sender_balance} tokens")
            logging.info(f"Recipient Balance After: {recipient_balance} tokens")
            logging.info(f"Total Supply: {total_supply} tokens")

        except Exception as e:
            logging.error(f"Error transferring tokens: {e}")
            raise
