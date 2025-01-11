# -*- coding: utf-8 -*-
# File generated from our OpenAPI spec
from stripe._expandable_field import ExpandableField
from stripe._list_object import ListObject
from stripe._listable_api_resource import ListableAPIResource
from stripe._request_options import RequestOptions
from stripe._stripe_object import StripeObject
from typing import ClassVar, List, Optional, Union
from typing_extensions import (
    Literal,
    NotRequired,
    TypedDict,
    Unpack,
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from stripe._account import Account
    from stripe._application import Application
    from stripe._bank_account import BankAccount
    from stripe._card import Card as CardResource
    from stripe._customer import Customer
    from stripe._mandate import Mandate
    from stripe._payment_intent import PaymentIntent
    from stripe._payment_method import PaymentMethod
    from stripe._setup_intent import SetupIntent
    from stripe._source import Source


class SetupAttempt(ListableAPIResource["SetupAttempt"]):
    """
    A SetupAttempt describes one attempted confirmation of a SetupIntent,
    whether that confirmation is successful or unsuccessful. You can use
    SetupAttempts to inspect details of a specific attempt at setting up a
    payment method using a SetupIntent.
    """

    OBJECT_NAME: ClassVar[Literal["setup_attempt"]] = "setup_attempt"

    class PaymentMethodDetails(StripeObject):
        class AcssDebit(StripeObject):
            pass

        class AmazonPay(StripeObject):
            pass

        class AuBecsDebit(StripeObject):
            pass

        class BacsDebit(StripeObject):
            pass

        class Bancontact(StripeObject):
            bank_code: Optional[str]
            """
            Bank code of bank associated with the bank account.
            """
            bank_name: Optional[str]
            """
            Name of the bank associated with the bank account.
            """
            bic: Optional[str]
            """
            Bank Identifier Code of the bank associated with the bank account.
            """
            generated_sepa_debit: Optional[ExpandableField["PaymentMethod"]]
            """
            The ID of the SEPA Direct Debit PaymentMethod which was generated by this SetupAttempt.
            """
            generated_sepa_debit_mandate: Optional[ExpandableField["Mandate"]]
            """
            The mandate for the SEPA Direct Debit PaymentMethod which was generated by this SetupAttempt.
            """
            iban_last4: Optional[str]
            """
            Last four characters of the IBAN.
            """
            preferred_language: Optional[Literal["de", "en", "fr", "nl"]]
            """
            Preferred language of the Bancontact authorization page that the customer is redirected to.
            Can be one of `en`, `de`, `fr`, or `nl`
            """
            verified_name: Optional[str]
            """
            Owner's verified full name. Values are verified or provided by Bancontact directly
            (if supported) at the time of authorization or settlement. They cannot be set or mutated.
            """

        class Boleto(StripeObject):
            pass

        class Card(StripeObject):
            class Checks(StripeObject):
                address_line1_check: Optional[str]
                """
                If a address line1 was provided, results of the check, one of `pass`, `fail`, `unavailable`, or `unchecked`.
                """
                address_postal_code_check: Optional[str]
                """
                If a address postal code was provided, results of the check, one of `pass`, `fail`, `unavailable`, or `unchecked`.
                """
                cvc_check: Optional[str]
                """
                If a CVC was provided, results of the check, one of `pass`, `fail`, `unavailable`, or `unchecked`.
                """

            class ThreeDSecure(StripeObject):
                authentication_flow: Optional[
                    Literal["challenge", "frictionless"]
                ]
                """
                For authenticated transactions: how the customer was authenticated by
                the issuing bank.
                """
                electronic_commerce_indicator: Optional[
                    Literal["01", "02", "05", "06", "07"]
                ]
                """
                The Electronic Commerce Indicator (ECI). A protocol-level field
                indicating what degree of authentication was performed.
                """
                result: Optional[
                    Literal[
                        "attempt_acknowledged",
                        "authenticated",
                        "exempted",
                        "failed",
                        "not_supported",
                        "processing_error",
                    ]
                ]
                """
                Indicates the outcome of 3D Secure authentication.
                """
                result_reason: Optional[
                    Literal[
                        "abandoned",
                        "bypassed",
                        "canceled",
                        "card_not_enrolled",
                        "network_not_supported",
                        "protocol_error",
                        "rejected",
                    ]
                ]
                """
                Additional information about why 3D Secure succeeded or failed based
                on the `result`.
                """
                transaction_id: Optional[str]
                """
                The 3D Secure 1 XID or 3D Secure 2 Directory Server Transaction ID
                (dsTransId) for this payment.
                """
                version: Optional[Literal["1.0.2", "2.1.0", "2.2.0"]]
                """
                The version of 3D Secure that was used.
                """

            class Wallet(StripeObject):
                class ApplePay(StripeObject):
                    pass

                class GooglePay(StripeObject):
                    pass

                apple_pay: Optional[ApplePay]
                google_pay: Optional[GooglePay]
                type: Literal["apple_pay", "google_pay", "link"]
                """
                The type of the card wallet, one of `apple_pay`, `google_pay`, or `link`. An additional hash is included on the Wallet subhash with a name matching this value. It contains additional information specific to the card wallet type.
                """
                _inner_class_types = {
                    "apple_pay": ApplePay,
                    "google_pay": GooglePay,
                }

            brand: Optional[str]
            """
            Card brand. Can be `amex`, `diners`, `discover`, `eftpos_au`, `jcb`, `link`, `mastercard`, `unionpay`, `visa`, or `unknown`.
            """
            checks: Optional[Checks]
            """
            Check results by Card networks on Card address and CVC at the time of authorization
            """
            country: Optional[str]
            """
            Two-letter ISO code representing the country of the card. You could use this attribute to get a sense of the international breakdown of cards you've collected.
            """
            description: Optional[str]
            """
            A high-level description of the type of cards issued in this range. (For internal use only and not typically available in standard API requests.)
            """
            exp_month: Optional[int]
            """
            Two-digit number representing the card's expiration month.
            """
            exp_year: Optional[int]
            """
            Four-digit number representing the card's expiration year.
            """
            fingerprint: Optional[str]
            """
            Uniquely identifies this particular card number. You can use this attribute to check whether two customers who've signed up with you are using the same card number, for example. For payment methods that tokenize card information (Apple Pay, Google Pay), the tokenized number might be provided instead of the underlying card number.

            *As of May 1, 2021, card fingerprint in India for Connect changed to allow two fingerprints for the same card---one for India and one for the rest of the world.*
            """
            funding: Optional[str]
            """
            Card funding type. Can be `credit`, `debit`, `prepaid`, or `unknown`.
            """
            iin: Optional[str]
            """
            Issuer identification number of the card. (For internal use only and not typically available in standard API requests.)
            """
            issuer: Optional[str]
            """
            The name of the card's issuing bank. (For internal use only and not typically available in standard API requests.)
            """
            last4: Optional[str]
            """
            The last four digits of the card.
            """
            network: Optional[str]
            """
            Identifies which network this charge was processed on. Can be `amex`, `cartes_bancaires`, `diners`, `discover`, `eftpos_au`, `interac`, `jcb`, `link`, `mastercard`, `unionpay`, `visa`, or `unknown`.
            """
            three_d_secure: Optional[ThreeDSecure]
            """
            Populated if this authorization used 3D Secure authentication.
            """
            wallet: Optional[Wallet]
            """
            If this Card is part of a card wallet, this contains the details of the card wallet.
            """
            _inner_class_types = {
                "checks": Checks,
                "three_d_secure": ThreeDSecure,
                "wallet": Wallet,
            }

        class CardPresent(StripeObject):
            class Offline(StripeObject):
                stored_at: Optional[int]
                """
                Time at which the payment was collected while offline
                """
                type: Optional[Literal["deferred"]]
                """
                The method used to process this payment method offline. Only deferred is allowed.
                """

            generated_card: Optional[ExpandableField["PaymentMethod"]]
            """
            The ID of the Card PaymentMethod which was generated by this SetupAttempt.
            """
            offline: Optional[Offline]
            """
            Details about payments collected offline.
            """
            _inner_class_types = {"offline": Offline}

        class Cashapp(StripeObject):
            pass

        class IdBankTransfer(StripeObject):
            bank: Optional[Literal["bca", "bni", "bri", "cimb", "permata"]]
            """
            Bank where the account is located.
            """
            bank_code: Optional[str]
            """
            Local bank code of the bank.
            """
            bank_name: Optional[str]
            """
            Name of the bank associated with the bank account.
            """
            display_name: Optional[str]
            """
            Merchant name and billing details name, for the customer to check for the correct merchant when performing the bank transfer.
            """

        class Ideal(StripeObject):
            bank: Optional[
                Literal[
                    "abn_amro",
                    "asn_bank",
                    "bunq",
                    "handelsbanken",
                    "ing",
                    "knab",
                    "moneyou",
                    "n26",
                    "nn",
                    "rabobank",
                    "regiobank",
                    "revolut",
                    "sns_bank",
                    "triodos_bank",
                    "van_lanschot",
                    "yoursafe",
                ]
            ]
            """
            The customer's bank. Can be one of `abn_amro`, `asn_bank`, `bunq`, `handelsbanken`, `ing`, `knab`, `moneyou`, `n26`, `nn`, `rabobank`, `regiobank`, `revolut`, `sns_bank`, `triodos_bank`, `van_lanschot`, or `yoursafe`.
            """
            bic: Optional[
                Literal[
                    "ABNANL2A",
                    "ASNBNL21",
                    "BITSNL2A",
                    "BUNQNL2A",
                    "FVLBNL22",
                    "HANDNL2A",
                    "INGBNL2A",
                    "KNABNL2H",
                    "MOYONL21",
                    "NNBANL2G",
                    "NTSBDEB1",
                    "RABONL2U",
                    "RBRBNL21",
                    "REVOIE23",
                    "REVOLT21",
                    "SNSBNL2A",
                    "TRIONL2U",
                ]
            ]
            """
            The Bank Identifier Code of the customer's bank.
            """
            generated_sepa_debit: Optional[ExpandableField["PaymentMethod"]]
            """
            The ID of the SEPA Direct Debit PaymentMethod which was generated by this SetupAttempt.
            """
            generated_sepa_debit_mandate: Optional[ExpandableField["Mandate"]]
            """
            The mandate for the SEPA Direct Debit PaymentMethod which was generated by this SetupAttempt.
            """
            iban_last4: Optional[str]
            """
            Last four characters of the IBAN.
            """
            verified_name: Optional[str]
            """
            Owner's verified full name. Values are verified or provided by iDEAL directly
            (if supported) at the time of authorization or settlement. They cannot be set or mutated.
            """

        class KakaoPay(StripeObject):
            pass

        class Klarna(StripeObject):
            pass

        class KrCard(StripeObject):
            pass

        class Link(StripeObject):
            pass

        class Paypal(StripeObject):
            pass

        class Payto(StripeObject):
            pass

        class RevolutPay(StripeObject):
            pass

        class SepaDebit(StripeObject):
            pass

        class Sofort(StripeObject):
            bank_code: Optional[str]
            """
            Bank code of bank associated with the bank account.
            """
            bank_name: Optional[str]
            """
            Name of the bank associated with the bank account.
            """
            bic: Optional[str]
            """
            Bank Identifier Code of the bank associated with the bank account.
            """
            generated_sepa_debit: Optional[ExpandableField["PaymentMethod"]]
            """
            The ID of the SEPA Direct Debit PaymentMethod which was generated by this SetupAttempt.
            """
            generated_sepa_debit_mandate: Optional[ExpandableField["Mandate"]]
            """
            The mandate for the SEPA Direct Debit PaymentMethod which was generated by this SetupAttempt.
            """
            iban_last4: Optional[str]
            """
            Last four characters of the IBAN.
            """
            preferred_language: Optional[Literal["de", "en", "fr", "nl"]]
            """
            Preferred language of the Sofort authorization page that the customer is redirected to.
            Can be one of `en`, `de`, `fr`, or `nl`
            """
            verified_name: Optional[str]
            """
            Owner's verified full name. Values are verified or provided by Sofort directly
            (if supported) at the time of authorization or settlement. They cannot be set or mutated.
            """

        class UsBankAccount(StripeObject):
            pass

        acss_debit: Optional[AcssDebit]
        amazon_pay: Optional[AmazonPay]
        au_becs_debit: Optional[AuBecsDebit]
        bacs_debit: Optional[BacsDebit]
        bancontact: Optional[Bancontact]
        boleto: Optional[Boleto]
        card: Optional[Card]
        card_present: Optional[CardPresent]
        cashapp: Optional[Cashapp]
        id_bank_transfer: Optional[IdBankTransfer]
        ideal: Optional[Ideal]
        kakao_pay: Optional[KakaoPay]
        klarna: Optional[Klarna]
        kr_card: Optional[KrCard]
        link: Optional[Link]
        paypal: Optional[Paypal]
        payto: Optional[Payto]
        revolut_pay: Optional[RevolutPay]
        sepa_debit: Optional[SepaDebit]
        sofort: Optional[Sofort]
        type: str
        """
        The type of the payment method used in the SetupIntent (e.g., `card`). An additional hash is included on `payment_method_details` with a name matching this value. It contains confirmation-specific information for the payment method.
        """
        us_bank_account: Optional[UsBankAccount]
        _inner_class_types = {
            "acss_debit": AcssDebit,
            "amazon_pay": AmazonPay,
            "au_becs_debit": AuBecsDebit,
            "bacs_debit": BacsDebit,
            "bancontact": Bancontact,
            "boleto": Boleto,
            "card": Card,
            "card_present": CardPresent,
            "cashapp": Cashapp,
            "id_bank_transfer": IdBankTransfer,
            "ideal": Ideal,
            "kakao_pay": KakaoPay,
            "klarna": Klarna,
            "kr_card": KrCard,
            "link": Link,
            "paypal": Paypal,
            "payto": Payto,
            "revolut_pay": RevolutPay,
            "sepa_debit": SepaDebit,
            "sofort": Sofort,
            "us_bank_account": UsBankAccount,
        }

    class SetupError(StripeObject):
        advice_code: Optional[str]
        """
        For card errors resulting from a card issuer decline, a short string indicating [how to proceed with an error](https://stripe.com/docs/declines#retrying-issuer-declines) if they provide one.
        """
        charge: Optional[str]
        """
        For card errors, the ID of the failed charge.
        """
        code: Optional[
            Literal[
                "account_closed",
                "account_country_invalid_address",
                "account_error_country_change_requires_additional_steps",
                "account_information_mismatch",
                "account_invalid",
                "account_number_invalid",
                "acss_debit_session_incomplete",
                "alipay_upgrade_required",
                "amount_too_large",
                "amount_too_small",
                "api_key_expired",
                "application_fees_not_allowed",
                "authentication_required",
                "balance_insufficient",
                "balance_invalid_parameter",
                "bank_account_bad_routing_numbers",
                "bank_account_declined",
                "bank_account_exists",
                "bank_account_restricted",
                "bank_account_unusable",
                "bank_account_unverified",
                "bank_account_verification_failed",
                "billing_invalid_mandate",
                "bitcoin_upgrade_required",
                "capture_charge_authorization_expired",
                "capture_unauthorized_payment",
                "card_decline_rate_limit_exceeded",
                "card_declined",
                "cardholder_phone_number_required",
                "charge_already_captured",
                "charge_already_refunded",
                "charge_disputed",
                "charge_exceeds_source_limit",
                "charge_exceeds_transaction_limit",
                "charge_expired_for_capture",
                "charge_invalid_parameter",
                "charge_not_refundable",
                "clearing_code_unsupported",
                "country_code_invalid",
                "country_unsupported",
                "coupon_expired",
                "customer_max_payment_methods",
                "customer_max_subscriptions",
                "customer_tax_location_invalid",
                "debit_not_authorized",
                "email_invalid",
                "expired_card",
                "financial_connections_account_inactive",
                "financial_connections_institution_unavailable",
                "financial_connections_no_successful_transaction_refresh",
                "forwarding_api_inactive",
                "forwarding_api_invalid_parameter",
                "forwarding_api_upstream_connection_error",
                "forwarding_api_upstream_connection_timeout",
                "gift_card_balance_insufficient",
                "gift_card_code_exists",
                "gift_card_inactive",
                "idempotency_key_in_use",
                "incorrect_address",
                "incorrect_cvc",
                "incorrect_number",
                "incorrect_zip",
                "instant_payouts_config_disabled",
                "instant_payouts_currency_disabled",
                "instant_payouts_limit_exceeded",
                "instant_payouts_unsupported",
                "insufficient_funds",
                "intent_invalid_state",
                "intent_verification_method_missing",
                "invalid_card_type",
                "invalid_characters",
                "invalid_charge_amount",
                "invalid_cvc",
                "invalid_expiry_month",
                "invalid_expiry_year",
                "invalid_mandate_reference_prefix_format",
                "invalid_number",
                "invalid_source_usage",
                "invalid_tax_location",
                "invoice_no_customer_line_items",
                "invoice_no_payment_method_types",
                "invoice_no_subscription_line_items",
                "invoice_not_editable",
                "invoice_on_behalf_of_not_editable",
                "invoice_payment_intent_requires_action",
                "invoice_upcoming_none",
                "livemode_mismatch",
                "lock_timeout",
                "missing",
                "no_account",
                "not_allowed_on_standard_account",
                "out_of_inventory",
                "ownership_declaration_not_allowed",
                "parameter_invalid_empty",
                "parameter_invalid_integer",
                "parameter_invalid_string_blank",
                "parameter_invalid_string_empty",
                "parameter_missing",
                "parameter_unknown",
                "parameters_exclusive",
                "payment_intent_action_required",
                "payment_intent_authentication_failure",
                "payment_intent_incompatible_payment_method",
                "payment_intent_invalid_parameter",
                "payment_intent_konbini_rejected_confirmation_number",
                "payment_intent_mandate_invalid",
                "payment_intent_payment_attempt_expired",
                "payment_intent_payment_attempt_failed",
                "payment_intent_unexpected_state",
                "payment_method_bank_account_already_verified",
                "payment_method_bank_account_blocked",
                "payment_method_billing_details_address_missing",
                "payment_method_configuration_failures",
                "payment_method_currency_mismatch",
                "payment_method_customer_decline",
                "payment_method_invalid_parameter",
                "payment_method_invalid_parameter_testmode",
                "payment_method_microdeposit_failed",
                "payment_method_microdeposit_verification_amounts_invalid",
                "payment_method_microdeposit_verification_amounts_mismatch",
                "payment_method_microdeposit_verification_attempts_exceeded",
                "payment_method_microdeposit_verification_descriptor_code_mismatch",
                "payment_method_microdeposit_verification_timeout",
                "payment_method_not_available",
                "payment_method_provider_decline",
                "payment_method_provider_timeout",
                "payment_method_unactivated",
                "payment_method_unexpected_state",
                "payment_method_unsupported_type",
                "payout_reconciliation_not_ready",
                "payouts_limit_exceeded",
                "payouts_not_allowed",
                "platform_account_required",
                "platform_api_key_expired",
                "postal_code_invalid",
                "processing_error",
                "product_inactive",
                "progressive_onboarding_limit_exceeded",
                "rate_limit",
                "refer_to_customer",
                "refund_disputed_payment",
                "resource_already_exists",
                "resource_missing",
                "return_intent_already_processed",
                "routing_number_invalid",
                "secret_key_required",
                "sensitive_data_access_expired",
                "sepa_unsupported_account",
                "setup_attempt_failed",
                "setup_intent_authentication_failure",
                "setup_intent_invalid_parameter",
                "setup_intent_mandate_invalid",
                "setup_intent_setup_attempt_expired",
                "setup_intent_unexpected_state",
                "shipping_address_invalid",
                "shipping_calculation_failed",
                "sku_inactive",
                "state_unsupported",
                "status_transition_invalid",
                "stripe_tax_inactive",
                "tax_id_invalid",
                "taxes_calculation_failed",
                "terminal_location_country_unsupported",
                "terminal_reader_busy",
                "terminal_reader_collected_data_invalid",
                "terminal_reader_hardware_fault",
                "terminal_reader_invalid_location_for_activation",
                "terminal_reader_invalid_location_for_payment",
                "terminal_reader_offline",
                "terminal_reader_timeout",
                "testmode_charges_only",
                "tls_version_unsupported",
                "token_already_used",
                "token_card_network_invalid",
                "token_in_use",
                "transfer_source_balance_parameters_mismatch",
                "transfers_not_allowed",
                "url_invalid",
            ]
        ]
        """
        For some errors that could be handled programmatically, a short string indicating the [error code](https://stripe.com/docs/error-codes) reported.
        """
        decline_code: Optional[str]
        """
        For card errors resulting from a card issuer decline, a short string indicating the [card issuer's reason for the decline](https://stripe.com/docs/declines#issuer-declines) if they provide one.
        """
        doc_url: Optional[str]
        """
        A URL to more information about the [error code](https://stripe.com/docs/error-codes) reported.
        """
        message: Optional[str]
        """
        A human-readable message providing more details about the error. For card errors, these messages can be shown to your users.
        """
        network_advice_code: Optional[str]
        """
        For card errors resulting from a card issuer decline, a 2 digit code which indicates the advice given to merchant by the card network on how to proceed with an error.
        """
        network_decline_code: Optional[str]
        """
        For card errors resulting from a card issuer decline, a brand specific 2, 3, or 4 digit code which indicates the reason the authorization failed.
        """
        param: Optional[str]
        """
        If the error is parameter-specific, the parameter related to the error. For example, you can use this to display a message near the correct form field.
        """
        payment_intent: Optional["PaymentIntent"]
        """
        A PaymentIntent guides you through the process of collecting a payment from your customer.
        We recommend that you create exactly one PaymentIntent for each order or
        customer session in your system. You can reference the PaymentIntent later to
        see the history of payment attempts for a particular session.

        A PaymentIntent transitions through
        [multiple statuses](https://stripe.com/docs/payments/intents#intent-statuses)
        throughout its lifetime as it interfaces with Stripe.js to perform
        authentication flows and ultimately creates at most one successful charge.

        Related guide: [Payment Intents API](https://stripe.com/docs/payments/payment-intents)
        """
        payment_method: Optional["PaymentMethod"]
        """
        PaymentMethod objects represent your customer's payment instruments.
        You can use them with [PaymentIntents](https://stripe.com/docs/payments/payment-intents) to collect payments or save them to
        Customer objects to store instrument details for future payments.

        Related guides: [Payment Methods](https://stripe.com/docs/payments/payment-methods) and [More Payment Scenarios](https://stripe.com/docs/payments/more-payment-scenarios).
        """
        payment_method_type: Optional[str]
        """
        If the error is specific to the type of payment method, the payment method type that had a problem. This field is only populated for invoice-related errors.
        """
        request_log_url: Optional[str]
        """
        A URL to the request log entry in your dashboard.
        """
        setup_intent: Optional["SetupIntent"]
        """
        A SetupIntent guides you through the process of setting up and saving a customer's payment credentials for future payments.
        For example, you can use a SetupIntent to set up and save your customer's card without immediately collecting a payment.
        Later, you can use [PaymentIntents](https://stripe.com/docs/api#payment_intents) to drive the payment flow.

        Create a SetupIntent when you're ready to collect your customer's payment credentials.
        Don't maintain long-lived, unconfirmed SetupIntents because they might not be valid.
        The SetupIntent transitions through multiple [statuses](https://docs.stripe.com/payments/intents#intent-statuses) as it guides
        you through the setup process.

        Successful SetupIntents result in payment credentials that are optimized for future payments.
        For example, cardholders in [certain regions](https://stripe.com/guides/strong-customer-authentication) might need to be run through
        [Strong Customer Authentication](https://docs.stripe.com/strong-customer-authentication) during payment method collection
        to streamline later [off-session payments](https://docs.stripe.com/payments/setup-intents).
        If you use the SetupIntent with a [Customer](https://stripe.com/docs/api#setup_intent_object-customer),
        it automatically attaches the resulting payment method to that Customer after successful setup.
        We recommend using SetupIntents or [setup_future_usage](https://stripe.com/docs/api#payment_intent_object-setup_future_usage) on
        PaymentIntents to save payment methods to prevent saving invalid or unoptimized payment methods.

        By using SetupIntents, you can reduce friction for your customers, even as regulations change over time.

        Related guide: [Setup Intents API](https://docs.stripe.com/payments/setup-intents)
        """
        source: Optional[
            Union["Account", "BankAccount", "CardResource", "Source"]
        ]
        type: Literal[
            "api_error",
            "card_error",
            "idempotency_error",
            "invalid_request_error",
        ]
        """
        The type of error returned. One of `api_error`, `card_error`, `idempotency_error`, or `invalid_request_error`
        """

    class ListParams(RequestOptions):
        created: NotRequired["SetupAttempt.ListParamsCreated|int"]
        """
        A filter on the list, based on the object `created` field. The value
        can be a string with an integer Unix timestamp or a
        dictionary with a number of different query options.
        """
        ending_before: NotRequired[str]
        """
        A cursor for use in pagination. `ending_before` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, starting with `obj_bar`, your subsequent call can include `ending_before=obj_bar` in order to fetch the previous page of the list.
        """
        expand: NotRequired[List[str]]
        """
        Specifies which fields in the response should be expanded.
        """
        limit: NotRequired[int]
        """
        A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 10.
        """
        setup_intent: str
        """
        Only return SetupAttempts created by the SetupIntent specified by
        this ID.
        """
        starting_after: NotRequired[str]
        """
        A cursor for use in pagination. `starting_after` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with `obj_foo`, your subsequent call can include `starting_after=obj_foo` in order to fetch the next page of the list.
        """

    class ListParamsCreated(TypedDict):
        gt: NotRequired[int]
        """
        Minimum value to filter by (exclusive)
        """
        gte: NotRequired[int]
        """
        Minimum value to filter by (inclusive)
        """
        lt: NotRequired[int]
        """
        Maximum value to filter by (exclusive)
        """
        lte: NotRequired[int]
        """
        Maximum value to filter by (inclusive)
        """

    application: Optional[ExpandableField["Application"]]
    """
    The value of [application](https://stripe.com/docs/api/setup_intents/object#setup_intent_object-application) on the SetupIntent at the time of this confirmation.
    """
    attach_to_self: Optional[bool]
    """
    If present, the SetupIntent's payment method will be attached to the in-context Stripe Account.

    It can only be used for this Stripe Account's own money movement flows like InboundTransfer and OutboundTransfers. It cannot be set to true when setting up a PaymentMethod for a Customer, and defaults to false when attaching a PaymentMethod to a Customer.
    """
    created: int
    """
    Time at which the object was created. Measured in seconds since the Unix epoch.
    """
    customer: Optional[ExpandableField["Customer"]]
    """
    The value of [customer](https://stripe.com/docs/api/setup_intents/object#setup_intent_object-customer) on the SetupIntent at the time of this confirmation.
    """
    flow_directions: Optional[List[Literal["inbound", "outbound"]]]
    """
    Indicates the directions of money movement for which this payment method is intended to be used.

    Include `inbound` if you intend to use the payment method as the origin to pull funds from. Include `outbound` if you intend to use the payment method as the destination to send funds to. You can include both if you intend to use the payment method for both purposes.
    """
    id: str
    """
    Unique identifier for the object.
    """
    livemode: bool
    """
    Has the value `true` if the object exists in live mode or the value `false` if the object exists in test mode.
    """
    object: Literal["setup_attempt"]
    """
    String representing the object's type. Objects of the same type share the same value.
    """
    on_behalf_of: Optional[ExpandableField["Account"]]
    """
    The value of [on_behalf_of](https://stripe.com/docs/api/setup_intents/object#setup_intent_object-on_behalf_of) on the SetupIntent at the time of this confirmation.
    """
    payment_method: ExpandableField["PaymentMethod"]
    """
    ID of the payment method used with this SetupAttempt.
    """
    payment_method_details: PaymentMethodDetails
    setup_error: Optional[SetupError]
    """
    The error encountered during this attempt to confirm the SetupIntent, if any.
    """
    setup_intent: ExpandableField["SetupIntent"]
    """
    ID of the SetupIntent that this attempt belongs to.
    """
    status: str
    """
    Status of this SetupAttempt, one of `requires_confirmation`, `requires_action`, `processing`, `succeeded`, `failed`, or `abandoned`.
    """
    usage: str
    """
    The value of [usage](https://stripe.com/docs/api/setup_intents/object#setup_intent_object-usage) on the SetupIntent at the time of this confirmation, one of `off_session` or `on_session`.
    """

    @classmethod
    def list(
        cls, **params: Unpack["SetupAttempt.ListParams"]
    ) -> ListObject["SetupAttempt"]:
        """
        Returns a list of SetupAttempts that associate with a provided SetupIntent.
        """
        result = cls._static_request(
            "get",
            cls.class_url(),
            params=params,
        )
        if not isinstance(result, ListObject):
            raise TypeError(
                "Expected list object from API, got %s"
                % (type(result).__name__)
            )

        return result

    @classmethod
    async def list_async(
        cls, **params: Unpack["SetupAttempt.ListParams"]
    ) -> ListObject["SetupAttempt"]:
        """
        Returns a list of SetupAttempts that associate with a provided SetupIntent.
        """
        result = await cls._static_request_async(
            "get",
            cls.class_url(),
            params=params,
        )
        if not isinstance(result, ListObject):
            raise TypeError(
                "Expected list object from API, got %s"
                % (type(result).__name__)
            )

        return result

    _inner_class_types = {
        "payment_method_details": PaymentMethodDetails,
        "setup_error": SetupError,
    }
