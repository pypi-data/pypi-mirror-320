import os
from web3 import Web3
from app import Enclave

from dotenv import load_dotenv
load_dotenv()

if __name__ == "__main__":    
    # Create a new instance of Web3 Optimism
    w3 = Web3(Web3.HTTPProvider(
        f"https://opt-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY_KEY')}"))

    # Create a new instance of Enclave
    client = Enclave(os.getenv("ENCLAVE_KEY"))

    # Generate a new Ethereum account
    eoa = w3.eth.account.from_key(os.getenv("PRIVATE_KEY"))

    # Display the account address and private key
    print("Address:", eoa.address)
    # DANGER: print("Private Key:", eoa._private_key.hex())

    # Create Enclave Smart Contract Wallet
    account = client.create_smart_account(eoa.address)
    print("Smart account created:", account.wallet.scw_address)

    # Get balance for Enclave Account
    balance = client.get_smart_balance(account.wallet.scw_address)
    print('Smart Account Balance:', balance['netBalance'])

    # Assuming you have already initialized the Enclave instance as shown above
    network = 10
    amount = 0.1 * 1e6  # Amount to compute the quote for
    limit = 0.099 * 1e6  # Amount to compute the quote for
    quote_type = 'AMOUNT_IN' 

    # User is willing to spend at 0.1 USDC from their balance and wants at least 0.099 USDC on OP Mainnet
    quote = client.compute_quote(account.wallet.scw_address, network, amount, quote_type,)
    print('Quote computed:', quote)

    # Define the transaction details
    usdc_on_optimism = '0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85' 

    # Define the recipient address and amount to transfer
    recipient_address = '0x4E2ef45077FB15Ef5f0FfF9E86B38991aA4bAe5C'  # Replace with the recipient's address
    credit_amount = int(quote['total_credit']) + int(quote['userWithdrawal'])

    # Debugging information
    print("Recipient Address:", recipient_address)
    print("Amount to transfer:", credit_amount)

    # Create the call data for the ERC20 transfer using Web3.py
    usdc_contract = w3.eth.contract(address=usdc_on_optimism, abi=[{
        'constant': False,
        'inputs': [
            {'name': 'to', 'type': 'address'},
            {'name': 'amount', 'type': 'uint256'}
        ],
        'name': 'transfer',
        'outputs': [{'name': '', 'type': 'bool'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function'
    }])
    encoded_data = usdc_contract.encode_abi(
        "transfer",
        args=[
            Web3.to_checksum_address(recipient_address),
            credit_amount
        ]
    )

    transaction_details = [{
        'encodedData': encoded_data, 
        'targetContractAddress': usdc_on_optimism,
        'value': 0  # Assuming no ETH is being transferred, only USDC
    }]

    # Define the order data - Describes how much the user wants to spend from their chain-abstracted balances
    order_data = {
        'amount': str(int(amount)),  # Amount of USDC required for the transfer 
        'type': 'AMOUNT_IN'
    }

    # Build the transaction
    built_txn = client.build_transaction(
        transaction_details,
        10,  # Target network
        account.wallet.scw_address,  # User's smart account address
        order_data,
        None,
        1  # Sign mode (Pass SignMode.SimpleSessionKey for sessionKey transaction)
    )

    print('Transaction built successfully')

    from eth_account.messages import encode_defunct
    # Sign the message
    print("Msgtosign:", built_txn.message_to_sign)
    print("Msgtosign v2:", encode_defunct(hexstr=built_txn.message_to_sign))
    # print("Msgtosign in bytes:", w3.to_bytes(built_txn.message_to_sign.encode('utf-8')))
    signature = eoa.sign_message(encode_defunct(hexstr=built_txn.message_to_sign))
    print("Signature 1:", signature)
    print("Signature 2:", signature.signature.hex())

    # Verify the signature
    message = encode_defunct(hexstr=built_txn.message_to_sign)
    recovered_address = w3.eth.account.recover_message(message, signature=signature.signature)
    is_valid = recovered_address.lower() == eoa.address.lower()
    print("Signature verification:", "Valid" if is_valid else "Invalid")
    print("Recovered address:", recovered_address)

    user_op_serializable = {k: (v.hex() if isinstance(v, bytes) else v) for k, v in built_txn.user_op.model_dump().items()}


    # Submit the transaction
    response = client.submit_transaction(
        "0x" + signature.signature.hex(),
        user_op_serializable,
        10,  # Target network
        account.wallet.scw_address,
        1  # Signature type (Pass SignMode.SimpleSessionKey if the signature is being generated from a sessionKey instead of the user's default EOA)
    )

    print('Transaction submitted successfully:', response)
