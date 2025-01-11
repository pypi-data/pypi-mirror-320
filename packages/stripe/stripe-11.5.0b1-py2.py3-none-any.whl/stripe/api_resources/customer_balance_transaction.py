# -*- coding: utf-8 -*-
# File generated from our OpenAPI spec
from typing_extensions import TYPE_CHECKING
from warnings import warn

warn(
    """
    The stripe.api_resources.customer_balance_transaction package is deprecated, please change your
    imports to import from stripe directly.
    From:
      from stripe.api_resources.customer_balance_transaction import CustomerBalanceTransaction
    To:
      from stripe import CustomerBalanceTransaction
    """,
    DeprecationWarning,
    stacklevel=2,
)
if not TYPE_CHECKING:
    from stripe._customer_balance_transaction import (  # noqa
        CustomerBalanceTransaction,
    )
