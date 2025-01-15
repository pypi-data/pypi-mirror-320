import requests
import json
from interfaces import TransactionDetails, OrderData, UserOperationStruct, CreateAccountResponse, GasResponse, ComputeQuoteResponse, GetBalanceResponse, SubmitTransactionResponse, BuildUserOpResponse
from typing import List, Optional, Dict, Any

BASE_URL = "https://hyperapp.in"

class Enclave:
    def __init__(self, API_KEY: str):
        self.API_KEY = API_KEY

    def check_user_name(self, username: str) -> Dict[str, Any]:
        resp = requests.get(
            f"{BASE_URL}/api/user/check-username?username={username}",
            headers={
                'Authorization': self.API_KEY,
                'Content-Type': 'application/json'
            }
        )
        return resp.json()

    def create_smart_account(self, eoa_address: str) -> CreateAccountResponse:
        try:
            response = requests.post(
                f"{BASE_URL}/smart-account/create",
                headers={
                    'Authorization': self.API_KEY,
                    'Content-Type': 'application/json'
                },
                data=json.dumps({'eoaAddress': eoa_address})
            )
            return CreateAccountResponse(**response.json())  # Use Pydantic model
        except Exception as error:
            print("Error creating smart account:", error)
            raise error

    def build_transaction(self, transaction_details: List[TransactionDetails], network: int, wallet_address: str, order_data: Optional[OrderData] = None, paymaster_data: Optional[str] = None, sign_mode: str = 'P256') -> BuildUserOpResponse:
        try:
            response = requests.post(
                f"{BASE_URL}/smart-account/transaction/build",
                headers={
                    'Authorization': self.API_KEY,
                    'Content-Type': 'application/json'
                },
                data=json.dumps({
                    'transactionDetails': transaction_details,
                    'network': network,
                    'walletAddress': wallet_address,
                    'orderData': order_data,
                    'paymasterData': paymaster_data,
                    'signMode': sign_mode
                })
            )
            return BuildUserOpResponse(**response.json())  # Use Pydantic model
        except Exception as error:
            print("Error building transaction:", error)
            raise error

    def delegate_action(self, transaction_details: List[TransactionDetails], network: int, wallet_address: str, order_data: Optional[OrderData] = None, paymaster_data: Optional[str] = None) -> SubmitTransactionResponse:
        try:
            response = requests.post(
                f"{BASE_URL}/smart-account/delegate-action",
                headers={
                    'Authorization': self.API_KEY,
                    'Content-Type': 'application/json'
                },
                data=json.dumps({
                    'transactionDetails': transaction_details,
                    'network': network,
                    'walletAddress': wallet_address,
                    'orderData': order_data,
                    'paymasterData': paymaster_data
                })
            )
            return response.json()
        except Exception as error:
            print("Error building transaction:", error)
            raise error

    def submit_transaction(self, signature: str, user_op: UserOperationStruct, network: int, wallet_address: str, signature_type: str) -> SubmitTransactionResponse:
        try:
            response = requests.post(
                f"{BASE_URL}/smart-account/transaction/submit",
                headers={
                    'Authorization': self.API_KEY,
                    'Content-Type': 'application/json'
                },
                data=json.dumps({
                    'signature': signature,
                    'userOp': user_op,
                    'walletAddress': wallet_address,
                    'network': network,
                    'signatureType': signature_type
                })
            )
            return response.json()
        except Exception as error:
            print("Error submitting transaction:", error)
            raise error

    def calculate_gas_fees(self, transaction_details: List[TransactionDetails], network: str, wallet_address: str, order_data: Optional[OrderData] = None) -> GasResponse:
        try:
            response = requests.post(
                f"{BASE_URL}/smart-account/transaction/gas-fees",
                headers={
                    'Authorization': self.API_KEY,
                    'Content-Type': 'application/json'
                },
                data=json.dumps({
                    'transactionDetails': transaction_details,
                    'network': network,
                    'walletAddress': wallet_address,
                    'orderData': order_data
                })
            )
            return response.json()
        except Exception as error:
            print("Error calculating gas fees:", error)
            raise error

    def compute_quote(self, wallet_address: str, output_network: str, amount: float, type: str, limit: int = None) -> ComputeQuoteResponse:
        try:
            response = requests.post(
                f"{BASE_URL}/v3/smartbalance/getquote",
                headers={
                    'Authorization': self.API_KEY,
                    'Content-Type': 'application/json'
                },
                data=json.dumps({
                    'walletAddress': wallet_address,
                    'outputNetwork': output_network,
                    'amount': amount,
                    'type': type,
                    'limit': limit
                }) if limit else json.dumps({
                    'walletAddress': wallet_address,
                    'outputNetwork': output_network,
                    'amount': amount,
                    'type': type
                })
            )
            return response.json()
        except Exception as error:
            print("Error computing quote:", error)
            raise error

    def get_smart_balance(self, wallet_address: str) -> GetBalanceResponse:
        try:
            response = requests.get(
                f"{BASE_URL}/v3/smartbalance/getbalance?walletAddress={wallet_address}",
                headers={
                    'Authorization': self.API_KEY,
                    'Content-Type': 'application/json'
                }
            )
            data = response.json()
            return data
        except Exception as error:
            print("Error getting smart balance:", error)
            raise error

    def enable_session_key(self, wallet_address: str, session_key: str, valid_after: int, valid_until: int, network: str) -> BuildUserOpResponse:
        try:
            response = requests.post(
                f"{BASE_URL}/smart-account/session-key/enable",
                headers={
                    'Authorization': self.API_KEY,
                    'Content-Type': 'application/json'
                },
                data=json.dumps({
                    'sessionKey': session_key,
                    'walletAddress': wallet_address,
                    'validAfter': valid_after,
                    'validUntil': valid_until,
                    'network': network
                })
            )
            return response.json()
        except Exception as error:
            print("Error enabling session key:", error)
            raise error

    def disable_session_key(self, wallet_address: str, session_key: str, network: str) -> BuildUserOpResponse:
        try:
            response = requests.post(
                f"{BASE_URL}/smart-account/session-key/disable",
                headers={
                    'Authorization': self.API_KEY,
                    'Content-Type': 'application/json'
                },
                data=json.dumps({
                    'sessionKey': session_key,
                    'walletAddress': wallet_address,
                    'network': network
                })
            )
            return response.json()
        except Exception as error:
            print("Error disabling session key:", error)
            raise error