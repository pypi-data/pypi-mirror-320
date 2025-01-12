from solders.pubkey import Pubkey

from ....account import SolanaAccount
from ....asset import SolanaToken, Token
from ....chain import Chain, SolanaChain
from ....chain_client import SolanaClient
from ....transaction import SolanaTransaction
from ...types import OrderFunding
from .anchor import instructions
from .anchor.types import PlaceOrderParams
from .anchor.instructions import PlaceOrderAccounts
from .anchor.instructions.place_order import PlaceOrderArgs


async def create_place_order_transaction[
    SrcChainType: SolanaChain,
    DestChainType: Chain,
](
    *,
    src_client: SolanaClient[SrcChainType],
    src_token: SolanaToken[SrcChainType],
    dest_token: Token[DestChainType],
    order_book_address: str,
    order_funding: OrderFunding,
    signer: SolanaAccount[SrcChainType],
) -> SolanaTransaction[SrcChainType]:
    raise NotImplementedError("Solana non-CCTP trades not yet implemented")

    token_account = src_token.associated_token_account(signer.keypair.pubkey())

    # accounts = PlaceOrderAccounts(
    #     authority=self.ctx.get_public_address(),
    #     oapp=self.__get_tristero_oapp(),
    #     admin_panel=self.__get_admin_panel(),
    #     token_mint=order_funding.bond_token_address,
    #     token_account=token_account,
    #     match_account=self.__get_trade_match_pda(),
    #     staking_account=self.__get_staking_panel(),
    #     order=self.__get_order_pda(),
    # )

    # instruction = instructions.place_order(
    #     args=PlaceOrderArgs(
    #         params=PlaceOrderParams(
    #             order_funding.src_amount_in,
    #             order_funding.src_amount_in,
    #             list(bytes.fromhex(order_dir.dst_token_address)),
    #             order_funding.dst_amount_out,
    #             order_dir.dst_lzc,
    #         )
    #     ),
    #     accounts=accounts,
    # )

    return await SolanaTransaction.create(
        src_client,
        (instruction,),
        (signer,),
    )
