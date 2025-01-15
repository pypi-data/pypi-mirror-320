from enum import Enum
from typing import Optional, Dict, Any, Union, List
from pydantic import BaseModel, Field

# Define the Wallet model
class Wallet(BaseModel):
    type: Optional[str] = Field(None, alias='type')
    scw_address: str = Field(..., alias='scw_address')
    eoa_address: Optional[str] = Field(None, alias='eoa_address')
    multi_scw: Optional[Any] = Field(None, alias='multi_scw')

class SignMode(Enum):
    P256 = 0
    ECDSA = 1
    MultichainP256 = 2
    MultichainECDSA = 3
    SessionKey = 4
    SimpleSessionKey = 5

class TransactionDetails(BaseModel):
    encoded_data: str = Field(..., alias='encodedData')
    target_contract_address: str = Field(..., alias='targetContractAddress')
    value: Optional[Union[int, float]] = Field(None, alias='value')

class OrderData(BaseModel):
    amount: Union[str, float, int] = Field(..., alias='amount')
    limit: Optional[Union[str, float, int]] = Field(None, alias='limit')
    type: str = Field(..., alias='type')

class UserOperationStruct(BaseModel):
    sender: str = Field(..., alias='sender')
    nonce: Optional[Union[int, None]] = Field(None, alias='nonce')
    init_code: Optional[bytes] = Field(None, alias='initCode')
    call_data: bytes = Field(..., alias='callData')
    call_gas_limit: Optional[Union[int, None]] = Field(None, alias='callGasLimit')
    verification_gas_limit: Union[int, float] = Field(..., alias='verificationGasLimit')
    pre_verification_gas: Union[int, float] = Field(..., alias='preVerificationGas')
    max_fee_per_gas: Optional[Union[int, None]] = Field(None, alias='maxFeePerGas')
    max_priority_fee_per_gas: Optional[Union[int, None]] = Field(None, alias='maxPriorityFeePerGas')
    paymaster_and_data: bytes = Field(..., alias='paymasterAndData')
    signature: bytes = Field(..., alias='signature')

class CreateAccountResponse(BaseModel):
    username: str = Field(..., alias='username')
    verified: bool = Field(..., alias='verified')
    authenticated: Optional[bool] = Field(False, alias='authenticated')
    wallet: Wallet = Field(..., alias='wallet')
    org_id: str = Field(..., alias='orgId')
    added_on: Optional[int] = Field(None, alias='addedOn')
    updated_on: Optional[int] = Field(None, alias='updatedOn')
    version: Optional[int] = Field(None, alias='version')
    metadata: Optional[Any] = Field(None, alias='metadata')

class BuildUserOpResponse(BaseModel):
    user_op: UserOperationStruct = Field(..., alias='userOp')
    message_to_sign: str = Field(..., alias='messageToSign')
    sign_mode: SignMode = Field(..., alias='signMode')

class SubmitTransactionResponse(BaseModel):
    txn_hash: str = Field(..., alias='txnHash')
    block_hash: str = Field(..., alias='blockHash')
    timestamp: int = Field(..., alias='timestamp')

class GasResponse(BaseModel):
    result: Union[int, float] = Field(..., alias='result')

class ComputeQuoteResponse(BaseModel):
    total_withdrawn: str = Field(..., alias='total_withdrawn')
    total_fees: Optional[Union[int, float]] = Field(None, alias='total_fees')
    withdrawals: Optional[Dict[str, Optional[str]]] = Field(None, alias='withdrawals')
    total_credit: Union[int, float] = Field(..., alias='total_credit')
    user_withdrawal: Union[int, float] = Field(..., alias='userWithdrawal')

class GetBalanceResponse(BaseModel):
    gross_balance: str = Field(..., alias='grossBalance')
    net_balance: str = Field(..., alias='netBalance')
    pending_claims: str = Field(..., alias='pendingClaims')
    balance_by_network: List[Dict[str, Union[int, str]]] = Field(..., alias='balanceByNetwork')
