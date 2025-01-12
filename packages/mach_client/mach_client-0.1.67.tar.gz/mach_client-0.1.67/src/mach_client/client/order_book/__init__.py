from __future__ import annotations
import typing

from eth_typing import ChecksumAddress

from ...account import (
    Account,
    EthereumAccount,
    SolanaAccount,
    TronAccount,
)
from ...asset import SolanaToken, Token
from ...chain import Chain
from ...chain_client import (
    ChainClient,
    EthereumClient,
    SolanaClient,
    TronClient,
)
from ...transaction import Transaction
from ..types import OrderData
from . import ethereum, solana, tron

if typing.TYPE_CHECKING:
    from ... import MachClient


async def create_place_order_transaction[SrcChainType: Chain, DestChainType: Chain](
    *,
    client: MachClient,
    src_client: ChainClient[SrcChainType],
    src_token: Token[SrcChainType],
    dest_token: Token[DestChainType],
    order_data: OrderData,
    signer: Account[SrcChainType],
) -> Transaction[SrcChainType]:
    order_book_address = order_data.contract_address

    match src_client:
        case EthereumClient():
            return await ethereum.create_place_order_transaction(
                src_client=src_client,
                order_book_address=typing.cast(ChecksumAddress, order_book_address),
                order_data=order_data,
                signer=typing.cast(EthereumAccount, signer),
            )

        case SolanaClient():
            return await solana.create_place_order_transaction(
                src_client=src_client,
                src_token=typing.cast(SolanaToken, src_token),
                dest_token=dest_token,
                order_book_address=order_book_address,
                order_funding=order_data.order_funding,
                signer=typing.cast(SolanaAccount, signer),
            )

        case TronClient():
            return await tron.create_place_order_transaction(
                src_client=src_client,
                order_book_address=order_book_address,
                order_data=order_data,
                signer=typing.cast(TronAccount, signer),
            )

        case _:
            raise NotImplementedError(src_client.chain)


__all__ = ["create_place_order_transaction"]
