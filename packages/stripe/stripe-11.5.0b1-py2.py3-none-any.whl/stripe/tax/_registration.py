# -*- coding: utf-8 -*-
# File generated from our OpenAPI spec
from stripe._createable_api_resource import CreateableAPIResource
from stripe._list_object import ListObject
from stripe._listable_api_resource import ListableAPIResource
from stripe._request_options import RequestOptions
from stripe._stripe_object import StripeObject
from stripe._updateable_api_resource import UpdateableAPIResource
from stripe._util import sanitize_id
from typing import ClassVar, List, Optional, Union, cast
from typing_extensions import Literal, NotRequired, TypedDict, Unpack


class Registration(
    CreateableAPIResource["Registration"],
    ListableAPIResource["Registration"],
    UpdateableAPIResource["Registration"],
):
    """
    A Tax `Registration` lets us know that your business is registered to collect tax on payments within a region, enabling you to [automatically collect tax](https://stripe.com/docs/tax).

    Stripe doesn't register on your behalf with the relevant authorities when you create a Tax `Registration` object. For more information on how to register to collect tax, see [our guide](https://stripe.com/docs/tax/registering).

    Related guide: [Using the Registrations API](https://stripe.com/docs/tax/registrations-api)
    """

    OBJECT_NAME: ClassVar[Literal["tax.registration"]] = "tax.registration"

    class CountryOptions(StripeObject):
        class Ae(StripeObject):
            type: Literal["standard"]
            """
            Type of registration in `country`.
            """

        class Al(StripeObject):
            type: Literal["standard"]
            """
            Type of registration in `country`.
            """

        class Am(StripeObject):
            type: Literal["simplified"]
            """
            Type of registration in `country`.
            """

        class Ao(StripeObject):
            type: Literal["standard"]
            """
            Type of registration in `country`.
            """

        class At(StripeObject):
            class Standard(StripeObject):
                place_of_supply_scheme: Literal["small_seller", "standard"]
                """
                Place of supply scheme used in an EU standard registration.
                """

            standard: Optional[Standard]
            type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
            """
            Type of registration in an EU country.
            """
            _inner_class_types = {"standard": Standard}

        class Au(StripeObject):
            type: Literal["standard"]
            """
            Type of registration in `country`.
            """

        class Ba(StripeObject):
            type: Literal["standard"]
            """
            Type of registration in `country`.
            """

        class Bb(StripeObject):
            type: Literal["standard"]
            """
            Type of registration in `country`.
            """

        class Be(StripeObject):
            class Standard(StripeObject):
                place_of_supply_scheme: Literal["small_seller", "standard"]
                """
                Place of supply scheme used in an EU standard registration.
                """

            standard: Optional[Standard]
            type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
            """
            Type of registration in an EU country.
            """
            _inner_class_types = {"standard": Standard}

        class Bg(StripeObject):
            class Standard(StripeObject):
                place_of_supply_scheme: Literal["small_seller", "standard"]
                """
                Place of supply scheme used in an EU standard registration.
                """

            standard: Optional[Standard]
            type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
            """
            Type of registration in an EU country.
            """
            _inner_class_types = {"standard": Standard}

        class Bh(StripeObject):
            type: Literal["standard"]
            """
            Type of registration in `country`.
            """

        class Bs(StripeObject):
            type: Literal["standard"]
            """
            Type of registration in `country`.
            """

        class By(StripeObject):
            type: Literal["simplified"]
            """
            Type of registration in `country`.
            """

        class Ca(StripeObject):
            class ProvinceStandard(StripeObject):
                province: str
                """
                Two-letter CA province code ([ISO 3166-2](https://en.wikipedia.org/wiki/ISO_3166-2)).
                """

            province_standard: Optional[ProvinceStandard]
            type: Literal["province_standard", "simplified", "standard"]
            """
            Type of registration in Canada.
            """
            _inner_class_types = {"province_standard": ProvinceStandard}

        class Cd(StripeObject):
            type: Literal["standard"]
            """
            Type of registration in `country`.
            """

        class Ch(StripeObject):
            type: Literal["standard"]
            """
            Type of registration in `country`.
            """

        class Cl(StripeObject):
            type: Literal["simplified"]
            """
            Type of registration in `country`.
            """

        class Co(StripeObject):
            type: Literal["simplified"]
            """
            Type of registration in `country`.
            """

        class Cr(StripeObject):
            type: Literal["simplified"]
            """
            Type of registration in `country`.
            """

        class Cy(StripeObject):
            class Standard(StripeObject):
                place_of_supply_scheme: Literal["small_seller", "standard"]
                """
                Place of supply scheme used in an EU standard registration.
                """

            standard: Optional[Standard]
            type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
            """
            Type of registration in an EU country.
            """
            _inner_class_types = {"standard": Standard}

        class Cz(StripeObject):
            class Standard(StripeObject):
                place_of_supply_scheme: Literal["small_seller", "standard"]
                """
                Place of supply scheme used in an EU standard registration.
                """

            standard: Optional[Standard]
            type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
            """
            Type of registration in an EU country.
            """
            _inner_class_types = {"standard": Standard}

        class De(StripeObject):
            class Standard(StripeObject):
                place_of_supply_scheme: Literal["small_seller", "standard"]
                """
                Place of supply scheme used in an EU standard registration.
                """

            standard: Optional[Standard]
            type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
            """
            Type of registration in an EU country.
            """
            _inner_class_types = {"standard": Standard}

        class Dk(StripeObject):
            class Standard(StripeObject):
                place_of_supply_scheme: Literal["small_seller", "standard"]
                """
                Place of supply scheme used in an EU standard registration.
                """

            standard: Optional[Standard]
            type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
            """
            Type of registration in an EU country.
            """
            _inner_class_types = {"standard": Standard}

        class Ec(StripeObject):
            type: Literal["simplified"]
            """
            Type of registration in `country`.
            """

        class Ee(StripeObject):
            class Standard(StripeObject):
                place_of_supply_scheme: Literal["small_seller", "standard"]
                """
                Place of supply scheme used in an EU standard registration.
                """

            standard: Optional[Standard]
            type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
            """
            Type of registration in an EU country.
            """
            _inner_class_types = {"standard": Standard}

        class Eg(StripeObject):
            type: Literal["simplified"]
            """
            Type of registration in `country`.
            """

        class Es(StripeObject):
            class Standard(StripeObject):
                place_of_supply_scheme: Literal["small_seller", "standard"]
                """
                Place of supply scheme used in an EU standard registration.
                """

            standard: Optional[Standard]
            type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
            """
            Type of registration in an EU country.
            """
            _inner_class_types = {"standard": Standard}

        class Fi(StripeObject):
            class Standard(StripeObject):
                place_of_supply_scheme: Literal["small_seller", "standard"]
                """
                Place of supply scheme used in an EU standard registration.
                """

            standard: Optional[Standard]
            type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
            """
            Type of registration in an EU country.
            """
            _inner_class_types = {"standard": Standard}

        class Fr(StripeObject):
            class Standard(StripeObject):
                place_of_supply_scheme: Literal["small_seller", "standard"]
                """
                Place of supply scheme used in an EU standard registration.
                """

            standard: Optional[Standard]
            type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
            """
            Type of registration in an EU country.
            """
            _inner_class_types = {"standard": Standard}

        class Gb(StripeObject):
            type: Literal["standard"]
            """
            Type of registration in `country`.
            """

        class Ge(StripeObject):
            type: Literal["simplified"]
            """
            Type of registration in `country`.
            """

        class Gn(StripeObject):
            type: Literal["standard"]
            """
            Type of registration in `country`.
            """

        class Gr(StripeObject):
            class Standard(StripeObject):
                place_of_supply_scheme: Literal["small_seller", "standard"]
                """
                Place of supply scheme used in an EU standard registration.
                """

            standard: Optional[Standard]
            type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
            """
            Type of registration in an EU country.
            """
            _inner_class_types = {"standard": Standard}

        class Hr(StripeObject):
            class Standard(StripeObject):
                place_of_supply_scheme: Literal["small_seller", "standard"]
                """
                Place of supply scheme used in an EU standard registration.
                """

            standard: Optional[Standard]
            type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
            """
            Type of registration in an EU country.
            """
            _inner_class_types = {"standard": Standard}

        class Hu(StripeObject):
            class Standard(StripeObject):
                place_of_supply_scheme: Literal["small_seller", "standard"]
                """
                Place of supply scheme used in an EU standard registration.
                """

            standard: Optional[Standard]
            type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
            """
            Type of registration in an EU country.
            """
            _inner_class_types = {"standard": Standard}

        class Id(StripeObject):
            type: Literal["simplified"]
            """
            Type of registration in `country`.
            """

        class Ie(StripeObject):
            class Standard(StripeObject):
                place_of_supply_scheme: Literal["small_seller", "standard"]
                """
                Place of supply scheme used in an EU standard registration.
                """

            standard: Optional[Standard]
            type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
            """
            Type of registration in an EU country.
            """
            _inner_class_types = {"standard": Standard}

        class Is(StripeObject):
            type: Literal["standard"]
            """
            Type of registration in `country`.
            """

        class It(StripeObject):
            class Standard(StripeObject):
                place_of_supply_scheme: Literal["small_seller", "standard"]
                """
                Place of supply scheme used in an EU standard registration.
                """

            standard: Optional[Standard]
            type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
            """
            Type of registration in an EU country.
            """
            _inner_class_types = {"standard": Standard}

        class Jp(StripeObject):
            type: Literal["standard"]
            """
            Type of registration in `country`.
            """

        class Ke(StripeObject):
            type: Literal["simplified"]
            """
            Type of registration in `country`.
            """

        class Kh(StripeObject):
            type: Literal["simplified"]
            """
            Type of registration in `country`.
            """

        class Kr(StripeObject):
            type: Literal["simplified"]
            """
            Type of registration in `country`.
            """

        class Kz(StripeObject):
            type: Literal["simplified"]
            """
            Type of registration in `country`.
            """

        class Lt(StripeObject):
            class Standard(StripeObject):
                place_of_supply_scheme: Literal["small_seller", "standard"]
                """
                Place of supply scheme used in an EU standard registration.
                """

            standard: Optional[Standard]
            type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
            """
            Type of registration in an EU country.
            """
            _inner_class_types = {"standard": Standard}

        class Lu(StripeObject):
            class Standard(StripeObject):
                place_of_supply_scheme: Literal["small_seller", "standard"]
                """
                Place of supply scheme used in an EU standard registration.
                """

            standard: Optional[Standard]
            type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
            """
            Type of registration in an EU country.
            """
            _inner_class_types = {"standard": Standard}

        class Lv(StripeObject):
            class Standard(StripeObject):
                place_of_supply_scheme: Literal["small_seller", "standard"]
                """
                Place of supply scheme used in an EU standard registration.
                """

            standard: Optional[Standard]
            type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
            """
            Type of registration in an EU country.
            """
            _inner_class_types = {"standard": Standard}

        class Ma(StripeObject):
            type: Literal["simplified"]
            """
            Type of registration in `country`.
            """

        class Md(StripeObject):
            type: Literal["simplified"]
            """
            Type of registration in `country`.
            """

        class Me(StripeObject):
            type: Literal["standard"]
            """
            Type of registration in `country`.
            """

        class Mk(StripeObject):
            type: Literal["standard"]
            """
            Type of registration in `country`.
            """

        class Mr(StripeObject):
            type: Literal["standard"]
            """
            Type of registration in `country`.
            """

        class Mt(StripeObject):
            class Standard(StripeObject):
                place_of_supply_scheme: Literal["small_seller", "standard"]
                """
                Place of supply scheme used in an EU standard registration.
                """

            standard: Optional[Standard]
            type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
            """
            Type of registration in an EU country.
            """
            _inner_class_types = {"standard": Standard}

        class Mx(StripeObject):
            type: Literal["simplified"]
            """
            Type of registration in `country`.
            """

        class My(StripeObject):
            type: Literal["simplified"]
            """
            Type of registration in `country`.
            """

        class Ng(StripeObject):
            type: Literal["simplified"]
            """
            Type of registration in `country`.
            """

        class Nl(StripeObject):
            class Standard(StripeObject):
                place_of_supply_scheme: Literal["small_seller", "standard"]
                """
                Place of supply scheme used in an EU standard registration.
                """

            standard: Optional[Standard]
            type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
            """
            Type of registration in an EU country.
            """
            _inner_class_types = {"standard": Standard}

        class No(StripeObject):
            type: Literal["standard"]
            """
            Type of registration in `country`.
            """

        class Np(StripeObject):
            type: Literal["simplified"]
            """
            Type of registration in `country`.
            """

        class Nz(StripeObject):
            type: Literal["standard"]
            """
            Type of registration in `country`.
            """

        class Om(StripeObject):
            type: Literal["standard"]
            """
            Type of registration in `country`.
            """

        class Pe(StripeObject):
            type: Literal["simplified"]
            """
            Type of registration in `country`.
            """

        class Pl(StripeObject):
            class Standard(StripeObject):
                place_of_supply_scheme: Literal["small_seller", "standard"]
                """
                Place of supply scheme used in an EU standard registration.
                """

            standard: Optional[Standard]
            type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
            """
            Type of registration in an EU country.
            """
            _inner_class_types = {"standard": Standard}

        class Pt(StripeObject):
            class Standard(StripeObject):
                place_of_supply_scheme: Literal["small_seller", "standard"]
                """
                Place of supply scheme used in an EU standard registration.
                """

            standard: Optional[Standard]
            type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
            """
            Type of registration in an EU country.
            """
            _inner_class_types = {"standard": Standard}

        class Ro(StripeObject):
            class Standard(StripeObject):
                place_of_supply_scheme: Literal["small_seller", "standard"]
                """
                Place of supply scheme used in an EU standard registration.
                """

            standard: Optional[Standard]
            type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
            """
            Type of registration in an EU country.
            """
            _inner_class_types = {"standard": Standard}

        class Rs(StripeObject):
            type: Literal["standard"]
            """
            Type of registration in `country`.
            """

        class Ru(StripeObject):
            type: Literal["simplified"]
            """
            Type of registration in `country`.
            """

        class Sa(StripeObject):
            type: Literal["simplified"]
            """
            Type of registration in `country`.
            """

        class Se(StripeObject):
            class Standard(StripeObject):
                place_of_supply_scheme: Literal["small_seller", "standard"]
                """
                Place of supply scheme used in an EU standard registration.
                """

            standard: Optional[Standard]
            type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
            """
            Type of registration in an EU country.
            """
            _inner_class_types = {"standard": Standard}

        class Sg(StripeObject):
            type: Literal["standard"]
            """
            Type of registration in `country`.
            """

        class Si(StripeObject):
            class Standard(StripeObject):
                place_of_supply_scheme: Literal["small_seller", "standard"]
                """
                Place of supply scheme used in an EU standard registration.
                """

            standard: Optional[Standard]
            type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
            """
            Type of registration in an EU country.
            """
            _inner_class_types = {"standard": Standard}

        class Sk(StripeObject):
            class Standard(StripeObject):
                place_of_supply_scheme: Literal["small_seller", "standard"]
                """
                Place of supply scheme used in an EU standard registration.
                """

            standard: Optional[Standard]
            type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
            """
            Type of registration in an EU country.
            """
            _inner_class_types = {"standard": Standard}

        class Sn(StripeObject):
            type: Literal["simplified"]
            """
            Type of registration in `country`.
            """

        class Sr(StripeObject):
            type: Literal["standard"]
            """
            Type of registration in `country`.
            """

        class Th(StripeObject):
            type: Literal["simplified"]
            """
            Type of registration in `country`.
            """

        class Tj(StripeObject):
            type: Literal["simplified"]
            """
            Type of registration in `country`.
            """

        class Tr(StripeObject):
            type: Literal["simplified"]
            """
            Type of registration in `country`.
            """

        class Tz(StripeObject):
            type: Literal["simplified"]
            """
            Type of registration in `country`.
            """

        class Ug(StripeObject):
            type: Literal["simplified"]
            """
            Type of registration in `country`.
            """

        class Us(StripeObject):
            class LocalAmusementTax(StripeObject):
                jurisdiction: str
                """
                A [FIPS code](https://www.census.gov/library/reference/code-lists/ansi.html) representing the local jurisdiction.
                """

            class LocalLeaseTax(StripeObject):
                jurisdiction: str
                """
                A [FIPS code](https://www.census.gov/library/reference/code-lists/ansi.html) representing the local jurisdiction.
                """

            class StateSalesTax(StripeObject):
                class Election(StripeObject):
                    jurisdiction: Optional[str]
                    """
                    A [FIPS code](https://www.census.gov/library/reference/code-lists/ansi.html) representing the local jurisdiction.
                    """
                    type: Literal[
                        "local_use_tax",
                        "simplified_sellers_use_tax",
                        "single_local_use_tax",
                    ]
                    """
                    The type of the election for the state sales tax registration.
                    """

                elections: Optional[List[Election]]
                """
                Elections for the state sales tax registration.
                """
                _inner_class_types = {"elections": Election}

            local_amusement_tax: Optional[LocalAmusementTax]
            local_lease_tax: Optional[LocalLeaseTax]
            state: str
            """
            Two-letter US state code ([ISO 3166-2](https://en.wikipedia.org/wiki/ISO_3166-2)).
            """
            state_sales_tax: Optional[StateSalesTax]
            type: Literal[
                "local_amusement_tax",
                "local_lease_tax",
                "state_communications_tax",
                "state_retail_delivery_fee",
                "state_sales_tax",
            ]
            """
            Type of registration in the US.
            """
            _inner_class_types = {
                "local_amusement_tax": LocalAmusementTax,
                "local_lease_tax": LocalLeaseTax,
                "state_sales_tax": StateSalesTax,
            }

        class Uy(StripeObject):
            type: Literal["standard"]
            """
            Type of registration in `country`.
            """

        class Uz(StripeObject):
            type: Literal["simplified"]
            """
            Type of registration in `country`.
            """

        class Vn(StripeObject):
            type: Literal["simplified"]
            """
            Type of registration in `country`.
            """

        class Za(StripeObject):
            type: Literal["standard"]
            """
            Type of registration in `country`.
            """

        class Zm(StripeObject):
            type: Literal["simplified"]
            """
            Type of registration in `country`.
            """

        class Zw(StripeObject):
            type: Literal["standard"]
            """
            Type of registration in `country`.
            """

        ae: Optional[Ae]
        al: Optional[Al]
        am: Optional[Am]
        ao: Optional[Ao]
        at: Optional[At]
        au: Optional[Au]
        ba: Optional[Ba]
        bb: Optional[Bb]
        be: Optional[Be]
        bg: Optional[Bg]
        bh: Optional[Bh]
        bs: Optional[Bs]
        by: Optional[By]
        ca: Optional[Ca]
        cd: Optional[Cd]
        ch: Optional[Ch]
        cl: Optional[Cl]
        co: Optional[Co]
        cr: Optional[Cr]
        cy: Optional[Cy]
        cz: Optional[Cz]
        de: Optional[De]
        dk: Optional[Dk]
        ec: Optional[Ec]
        ee: Optional[Ee]
        eg: Optional[Eg]
        es: Optional[Es]
        fi: Optional[Fi]
        fr: Optional[Fr]
        gb: Optional[Gb]
        ge: Optional[Ge]
        gn: Optional[Gn]
        gr: Optional[Gr]
        hr: Optional[Hr]
        hu: Optional[Hu]
        id: Optional[Id]
        ie: Optional[Ie]
        is_: Optional[Is]
        it: Optional[It]
        jp: Optional[Jp]
        ke: Optional[Ke]
        kh: Optional[Kh]
        kr: Optional[Kr]
        kz: Optional[Kz]
        lt: Optional[Lt]
        lu: Optional[Lu]
        lv: Optional[Lv]
        ma: Optional[Ma]
        md: Optional[Md]
        me: Optional[Me]
        mk: Optional[Mk]
        mr: Optional[Mr]
        mt: Optional[Mt]
        mx: Optional[Mx]
        my: Optional[My]
        ng: Optional[Ng]
        nl: Optional[Nl]
        no: Optional[No]
        np: Optional[Np]
        nz: Optional[Nz]
        om: Optional[Om]
        pe: Optional[Pe]
        pl: Optional[Pl]
        pt: Optional[Pt]
        ro: Optional[Ro]
        rs: Optional[Rs]
        ru: Optional[Ru]
        sa: Optional[Sa]
        se: Optional[Se]
        sg: Optional[Sg]
        si: Optional[Si]
        sk: Optional[Sk]
        sn: Optional[Sn]
        sr: Optional[Sr]
        th: Optional[Th]
        tj: Optional[Tj]
        tr: Optional[Tr]
        tz: Optional[Tz]
        ug: Optional[Ug]
        us: Optional[Us]
        uy: Optional[Uy]
        uz: Optional[Uz]
        vn: Optional[Vn]
        za: Optional[Za]
        zm: Optional[Zm]
        zw: Optional[Zw]
        _inner_class_types = {
            "ae": Ae,
            "al": Al,
            "am": Am,
            "ao": Ao,
            "at": At,
            "au": Au,
            "ba": Ba,
            "bb": Bb,
            "be": Be,
            "bg": Bg,
            "bh": Bh,
            "bs": Bs,
            "by": By,
            "ca": Ca,
            "cd": Cd,
            "ch": Ch,
            "cl": Cl,
            "co": Co,
            "cr": Cr,
            "cy": Cy,
            "cz": Cz,
            "de": De,
            "dk": Dk,
            "ec": Ec,
            "ee": Ee,
            "eg": Eg,
            "es": Es,
            "fi": Fi,
            "fr": Fr,
            "gb": Gb,
            "ge": Ge,
            "gn": Gn,
            "gr": Gr,
            "hr": Hr,
            "hu": Hu,
            "id": Id,
            "ie": Ie,
            "is": Is,
            "it": It,
            "jp": Jp,
            "ke": Ke,
            "kh": Kh,
            "kr": Kr,
            "kz": Kz,
            "lt": Lt,
            "lu": Lu,
            "lv": Lv,
            "ma": Ma,
            "md": Md,
            "me": Me,
            "mk": Mk,
            "mr": Mr,
            "mt": Mt,
            "mx": Mx,
            "my": My,
            "ng": Ng,
            "nl": Nl,
            "no": No,
            "np": Np,
            "nz": Nz,
            "om": Om,
            "pe": Pe,
            "pl": Pl,
            "pt": Pt,
            "ro": Ro,
            "rs": Rs,
            "ru": Ru,
            "sa": Sa,
            "se": Se,
            "sg": Sg,
            "si": Si,
            "sk": Sk,
            "sn": Sn,
            "sr": Sr,
            "th": Th,
            "tj": Tj,
            "tr": Tr,
            "tz": Tz,
            "ug": Ug,
            "us": Us,
            "uy": Uy,
            "uz": Uz,
            "vn": Vn,
            "za": Za,
            "zm": Zm,
            "zw": Zw,
        }
        _field_remappings = {"is_": "is"}

    class CreateParams(RequestOptions):
        active_from: Union[Literal["now"], int]
        """
        Time at which the Tax Registration becomes active. It can be either `now` to indicate the current time, or a future timestamp measured in seconds since the Unix epoch.
        """
        country: str
        """
        Two-letter country code ([ISO 3166-1 alpha-2](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2)).
        """
        country_options: "Registration.CreateParamsCountryOptions"
        """
        Specific options for a registration in the specified `country`.
        """
        expand: NotRequired[List[str]]
        """
        Specifies which fields in the response should be expanded.
        """
        expires_at: NotRequired[int]
        """
        If set, the Tax Registration stops being active at this time. If not set, the Tax Registration will be active indefinitely. Timestamp measured in seconds since the Unix epoch.
        """

    _CreateParamsCountryOptionsBase = TypedDict(
        "CreateParamsCountryOptions",
        {"is": NotRequired["Registration.CreateParamsCountryOptionsIs"]},
    )

    class CreateParamsCountryOptions(_CreateParamsCountryOptionsBase):
        ae: NotRequired["Registration.CreateParamsCountryOptionsAe"]
        """
        Options for the registration in AE.
        """
        al: NotRequired["Registration.CreateParamsCountryOptionsAl"]
        """
        Options for the registration in AL.
        """
        am: NotRequired["Registration.CreateParamsCountryOptionsAm"]
        """
        Options for the registration in AM.
        """
        ao: NotRequired["Registration.CreateParamsCountryOptionsAo"]
        """
        Options for the registration in AO.
        """
        at: NotRequired["Registration.CreateParamsCountryOptionsAt"]
        """
        Options for the registration in AT.
        """
        au: NotRequired["Registration.CreateParamsCountryOptionsAu"]
        """
        Options for the registration in AU.
        """
        ba: NotRequired["Registration.CreateParamsCountryOptionsBa"]
        """
        Options for the registration in BA.
        """
        bb: NotRequired["Registration.CreateParamsCountryOptionsBb"]
        """
        Options for the registration in BB.
        """
        be: NotRequired["Registration.CreateParamsCountryOptionsBe"]
        """
        Options for the registration in BE.
        """
        bg: NotRequired["Registration.CreateParamsCountryOptionsBg"]
        """
        Options for the registration in BG.
        """
        bh: NotRequired["Registration.CreateParamsCountryOptionsBh"]
        """
        Options for the registration in BH.
        """
        bs: NotRequired["Registration.CreateParamsCountryOptionsBs"]
        """
        Options for the registration in BS.
        """
        by: NotRequired["Registration.CreateParamsCountryOptionsBy"]
        """
        Options for the registration in BY.
        """
        ca: NotRequired["Registration.CreateParamsCountryOptionsCa"]
        """
        Options for the registration in CA.
        """
        cd: NotRequired["Registration.CreateParamsCountryOptionsCd"]
        """
        Options for the registration in CD.
        """
        ch: NotRequired["Registration.CreateParamsCountryOptionsCh"]
        """
        Options for the registration in CH.
        """
        cl: NotRequired["Registration.CreateParamsCountryOptionsCl"]
        """
        Options for the registration in CL.
        """
        co: NotRequired["Registration.CreateParamsCountryOptionsCo"]
        """
        Options for the registration in CO.
        """
        cr: NotRequired["Registration.CreateParamsCountryOptionsCr"]
        """
        Options for the registration in CR.
        """
        cy: NotRequired["Registration.CreateParamsCountryOptionsCy"]
        """
        Options for the registration in CY.
        """
        cz: NotRequired["Registration.CreateParamsCountryOptionsCz"]
        """
        Options for the registration in CZ.
        """
        de: NotRequired["Registration.CreateParamsCountryOptionsDe"]
        """
        Options for the registration in DE.
        """
        dk: NotRequired["Registration.CreateParamsCountryOptionsDk"]
        """
        Options for the registration in DK.
        """
        ec: NotRequired["Registration.CreateParamsCountryOptionsEc"]
        """
        Options for the registration in EC.
        """
        ee: NotRequired["Registration.CreateParamsCountryOptionsEe"]
        """
        Options for the registration in EE.
        """
        eg: NotRequired["Registration.CreateParamsCountryOptionsEg"]
        """
        Options for the registration in EG.
        """
        es: NotRequired["Registration.CreateParamsCountryOptionsEs"]
        """
        Options for the registration in ES.
        """
        fi: NotRequired["Registration.CreateParamsCountryOptionsFi"]
        """
        Options for the registration in FI.
        """
        fr: NotRequired["Registration.CreateParamsCountryOptionsFr"]
        """
        Options for the registration in FR.
        """
        gb: NotRequired["Registration.CreateParamsCountryOptionsGb"]
        """
        Options for the registration in GB.
        """
        ge: NotRequired["Registration.CreateParamsCountryOptionsGe"]
        """
        Options for the registration in GE.
        """
        gn: NotRequired["Registration.CreateParamsCountryOptionsGn"]
        """
        Options for the registration in GN.
        """
        gr: NotRequired["Registration.CreateParamsCountryOptionsGr"]
        """
        Options for the registration in GR.
        """
        hr: NotRequired["Registration.CreateParamsCountryOptionsHr"]
        """
        Options for the registration in HR.
        """
        hu: NotRequired["Registration.CreateParamsCountryOptionsHu"]
        """
        Options for the registration in HU.
        """
        id: NotRequired["Registration.CreateParamsCountryOptionsId"]
        """
        Options for the registration in ID.
        """
        ie: NotRequired["Registration.CreateParamsCountryOptionsIe"]
        """
        Options for the registration in IE.
        """
        it: NotRequired["Registration.CreateParamsCountryOptionsIt"]
        """
        Options for the registration in IT.
        """
        jp: NotRequired["Registration.CreateParamsCountryOptionsJp"]
        """
        Options for the registration in JP.
        """
        ke: NotRequired["Registration.CreateParamsCountryOptionsKe"]
        """
        Options for the registration in KE.
        """
        kh: NotRequired["Registration.CreateParamsCountryOptionsKh"]
        """
        Options for the registration in KH.
        """
        kr: NotRequired["Registration.CreateParamsCountryOptionsKr"]
        """
        Options for the registration in KR.
        """
        kz: NotRequired["Registration.CreateParamsCountryOptionsKz"]
        """
        Options for the registration in KZ.
        """
        lt: NotRequired["Registration.CreateParamsCountryOptionsLt"]
        """
        Options for the registration in LT.
        """
        lu: NotRequired["Registration.CreateParamsCountryOptionsLu"]
        """
        Options for the registration in LU.
        """
        lv: NotRequired["Registration.CreateParamsCountryOptionsLv"]
        """
        Options for the registration in LV.
        """
        ma: NotRequired["Registration.CreateParamsCountryOptionsMa"]
        """
        Options for the registration in MA.
        """
        md: NotRequired["Registration.CreateParamsCountryOptionsMd"]
        """
        Options for the registration in MD.
        """
        me: NotRequired["Registration.CreateParamsCountryOptionsMe"]
        """
        Options for the registration in ME.
        """
        mk: NotRequired["Registration.CreateParamsCountryOptionsMk"]
        """
        Options for the registration in MK.
        """
        mr: NotRequired["Registration.CreateParamsCountryOptionsMr"]
        """
        Options for the registration in MR.
        """
        mt: NotRequired["Registration.CreateParamsCountryOptionsMt"]
        """
        Options for the registration in MT.
        """
        mx: NotRequired["Registration.CreateParamsCountryOptionsMx"]
        """
        Options for the registration in MX.
        """
        my: NotRequired["Registration.CreateParamsCountryOptionsMy"]
        """
        Options for the registration in MY.
        """
        ng: NotRequired["Registration.CreateParamsCountryOptionsNg"]
        """
        Options for the registration in NG.
        """
        nl: NotRequired["Registration.CreateParamsCountryOptionsNl"]
        """
        Options for the registration in NL.
        """
        no: NotRequired["Registration.CreateParamsCountryOptionsNo"]
        """
        Options for the registration in NO.
        """
        np: NotRequired["Registration.CreateParamsCountryOptionsNp"]
        """
        Options for the registration in NP.
        """
        nz: NotRequired["Registration.CreateParamsCountryOptionsNz"]
        """
        Options for the registration in NZ.
        """
        om: NotRequired["Registration.CreateParamsCountryOptionsOm"]
        """
        Options for the registration in OM.
        """
        pe: NotRequired["Registration.CreateParamsCountryOptionsPe"]
        """
        Options for the registration in PE.
        """
        pl: NotRequired["Registration.CreateParamsCountryOptionsPl"]
        """
        Options for the registration in PL.
        """
        pt: NotRequired["Registration.CreateParamsCountryOptionsPt"]
        """
        Options for the registration in PT.
        """
        ro: NotRequired["Registration.CreateParamsCountryOptionsRo"]
        """
        Options for the registration in RO.
        """
        rs: NotRequired["Registration.CreateParamsCountryOptionsRs"]
        """
        Options for the registration in RS.
        """
        ru: NotRequired["Registration.CreateParamsCountryOptionsRu"]
        """
        Options for the registration in RU.
        """
        sa: NotRequired["Registration.CreateParamsCountryOptionsSa"]
        """
        Options for the registration in SA.
        """
        se: NotRequired["Registration.CreateParamsCountryOptionsSe"]
        """
        Options for the registration in SE.
        """
        sg: NotRequired["Registration.CreateParamsCountryOptionsSg"]
        """
        Options for the registration in SG.
        """
        si: NotRequired["Registration.CreateParamsCountryOptionsSi"]
        """
        Options for the registration in SI.
        """
        sk: NotRequired["Registration.CreateParamsCountryOptionsSk"]
        """
        Options for the registration in SK.
        """
        sn: NotRequired["Registration.CreateParamsCountryOptionsSn"]
        """
        Options for the registration in SN.
        """
        sr: NotRequired["Registration.CreateParamsCountryOptionsSr"]
        """
        Options for the registration in SR.
        """
        th: NotRequired["Registration.CreateParamsCountryOptionsTh"]
        """
        Options for the registration in TH.
        """
        tj: NotRequired["Registration.CreateParamsCountryOptionsTj"]
        """
        Options for the registration in TJ.
        """
        tr: NotRequired["Registration.CreateParamsCountryOptionsTr"]
        """
        Options for the registration in TR.
        """
        tz: NotRequired["Registration.CreateParamsCountryOptionsTz"]
        """
        Options for the registration in TZ.
        """
        ug: NotRequired["Registration.CreateParamsCountryOptionsUg"]
        """
        Options for the registration in UG.
        """
        us: NotRequired["Registration.CreateParamsCountryOptionsUs"]
        """
        Options for the registration in US.
        """
        uy: NotRequired["Registration.CreateParamsCountryOptionsUy"]
        """
        Options for the registration in UY.
        """
        uz: NotRequired["Registration.CreateParamsCountryOptionsUz"]
        """
        Options for the registration in UZ.
        """
        vn: NotRequired["Registration.CreateParamsCountryOptionsVn"]
        """
        Options for the registration in VN.
        """
        za: NotRequired["Registration.CreateParamsCountryOptionsZa"]
        """
        Options for the registration in ZA.
        """
        zm: NotRequired["Registration.CreateParamsCountryOptionsZm"]
        """
        Options for the registration in ZM.
        """
        zw: NotRequired["Registration.CreateParamsCountryOptionsZw"]
        """
        Options for the registration in ZW.
        """

    class CreateParamsCountryOptionsAe(TypedDict):
        type: Literal["standard"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsAl(TypedDict):
        type: Literal["standard"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsAm(TypedDict):
        type: Literal["simplified"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsAo(TypedDict):
        type: Literal["standard"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsAt(TypedDict):
        standard: NotRequired[
            "Registration.CreateParamsCountryOptionsAtStandard"
        ]
        """
        Options for the standard registration.
        """
        type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
        """
        Type of registration to be created in an EU country.
        """

    class CreateParamsCountryOptionsAtStandard(TypedDict):
        place_of_supply_scheme: Literal["small_seller", "standard"]
        """
        Place of supply scheme used in an EU standard registration.
        """

    class CreateParamsCountryOptionsAu(TypedDict):
        type: Literal["standard"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsBa(TypedDict):
        type: Literal["standard"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsBb(TypedDict):
        type: Literal["standard"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsBe(TypedDict):
        standard: NotRequired[
            "Registration.CreateParamsCountryOptionsBeStandard"
        ]
        """
        Options for the standard registration.
        """
        type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
        """
        Type of registration to be created in an EU country.
        """

    class CreateParamsCountryOptionsBeStandard(TypedDict):
        place_of_supply_scheme: Literal["small_seller", "standard"]
        """
        Place of supply scheme used in an EU standard registration.
        """

    class CreateParamsCountryOptionsBg(TypedDict):
        standard: NotRequired[
            "Registration.CreateParamsCountryOptionsBgStandard"
        ]
        """
        Options for the standard registration.
        """
        type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
        """
        Type of registration to be created in an EU country.
        """

    class CreateParamsCountryOptionsBgStandard(TypedDict):
        place_of_supply_scheme: Literal["small_seller", "standard"]
        """
        Place of supply scheme used in an EU standard registration.
        """

    class CreateParamsCountryOptionsBh(TypedDict):
        type: Literal["standard"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsBs(TypedDict):
        type: Literal["standard"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsBy(TypedDict):
        type: Literal["simplified"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsCa(TypedDict):
        province_standard: NotRequired[
            "Registration.CreateParamsCountryOptionsCaProvinceStandard"
        ]
        """
        Options for the provincial tax registration.
        """
        type: Literal["province_standard", "simplified", "standard"]
        """
        Type of registration to be created in Canada.
        """

    class CreateParamsCountryOptionsCaProvinceStandard(TypedDict):
        province: str
        """
        Two-letter CA province code ([ISO 3166-2](https://en.wikipedia.org/wiki/ISO_3166-2)).
        """

    class CreateParamsCountryOptionsCd(TypedDict):
        type: Literal["standard"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsCh(TypedDict):
        type: Literal["standard"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsCl(TypedDict):
        type: Literal["simplified"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsCo(TypedDict):
        type: Literal["simplified"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsCr(TypedDict):
        type: Literal["simplified"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsCy(TypedDict):
        standard: NotRequired[
            "Registration.CreateParamsCountryOptionsCyStandard"
        ]
        """
        Options for the standard registration.
        """
        type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
        """
        Type of registration to be created in an EU country.
        """

    class CreateParamsCountryOptionsCyStandard(TypedDict):
        place_of_supply_scheme: Literal["small_seller", "standard"]
        """
        Place of supply scheme used in an EU standard registration.
        """

    class CreateParamsCountryOptionsCz(TypedDict):
        standard: NotRequired[
            "Registration.CreateParamsCountryOptionsCzStandard"
        ]
        """
        Options for the standard registration.
        """
        type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
        """
        Type of registration to be created in an EU country.
        """

    class CreateParamsCountryOptionsCzStandard(TypedDict):
        place_of_supply_scheme: Literal["small_seller", "standard"]
        """
        Place of supply scheme used in an EU standard registration.
        """

    class CreateParamsCountryOptionsDe(TypedDict):
        standard: NotRequired[
            "Registration.CreateParamsCountryOptionsDeStandard"
        ]
        """
        Options for the standard registration.
        """
        type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
        """
        Type of registration to be created in an EU country.
        """

    class CreateParamsCountryOptionsDeStandard(TypedDict):
        place_of_supply_scheme: Literal["small_seller", "standard"]
        """
        Place of supply scheme used in an EU standard registration.
        """

    class CreateParamsCountryOptionsDk(TypedDict):
        standard: NotRequired[
            "Registration.CreateParamsCountryOptionsDkStandard"
        ]
        """
        Options for the standard registration.
        """
        type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
        """
        Type of registration to be created in an EU country.
        """

    class CreateParamsCountryOptionsDkStandard(TypedDict):
        place_of_supply_scheme: Literal["small_seller", "standard"]
        """
        Place of supply scheme used in an EU standard registration.
        """

    class CreateParamsCountryOptionsEc(TypedDict):
        type: Literal["simplified"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsEe(TypedDict):
        standard: NotRequired[
            "Registration.CreateParamsCountryOptionsEeStandard"
        ]
        """
        Options for the standard registration.
        """
        type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
        """
        Type of registration to be created in an EU country.
        """

    class CreateParamsCountryOptionsEeStandard(TypedDict):
        place_of_supply_scheme: Literal["small_seller", "standard"]
        """
        Place of supply scheme used in an EU standard registration.
        """

    class CreateParamsCountryOptionsEg(TypedDict):
        type: Literal["simplified"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsEs(TypedDict):
        standard: NotRequired[
            "Registration.CreateParamsCountryOptionsEsStandard"
        ]
        """
        Options for the standard registration.
        """
        type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
        """
        Type of registration to be created in an EU country.
        """

    class CreateParamsCountryOptionsEsStandard(TypedDict):
        place_of_supply_scheme: Literal["small_seller", "standard"]
        """
        Place of supply scheme used in an EU standard registration.
        """

    class CreateParamsCountryOptionsFi(TypedDict):
        standard: NotRequired[
            "Registration.CreateParamsCountryOptionsFiStandard"
        ]
        """
        Options for the standard registration.
        """
        type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
        """
        Type of registration to be created in an EU country.
        """

    class CreateParamsCountryOptionsFiStandard(TypedDict):
        place_of_supply_scheme: Literal["small_seller", "standard"]
        """
        Place of supply scheme used in an EU standard registration.
        """

    class CreateParamsCountryOptionsFr(TypedDict):
        standard: NotRequired[
            "Registration.CreateParamsCountryOptionsFrStandard"
        ]
        """
        Options for the standard registration.
        """
        type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
        """
        Type of registration to be created in an EU country.
        """

    class CreateParamsCountryOptionsFrStandard(TypedDict):
        place_of_supply_scheme: Literal["small_seller", "standard"]
        """
        Place of supply scheme used in an EU standard registration.
        """

    class CreateParamsCountryOptionsGb(TypedDict):
        type: Literal["standard"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsGe(TypedDict):
        type: Literal["simplified"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsGn(TypedDict):
        type: Literal["standard"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsGr(TypedDict):
        standard: NotRequired[
            "Registration.CreateParamsCountryOptionsGrStandard"
        ]
        """
        Options for the standard registration.
        """
        type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
        """
        Type of registration to be created in an EU country.
        """

    class CreateParamsCountryOptionsGrStandard(TypedDict):
        place_of_supply_scheme: Literal["small_seller", "standard"]
        """
        Place of supply scheme used in an EU standard registration.
        """

    class CreateParamsCountryOptionsHr(TypedDict):
        standard: NotRequired[
            "Registration.CreateParamsCountryOptionsHrStandard"
        ]
        """
        Options for the standard registration.
        """
        type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
        """
        Type of registration to be created in an EU country.
        """

    class CreateParamsCountryOptionsHrStandard(TypedDict):
        place_of_supply_scheme: Literal["small_seller", "standard"]
        """
        Place of supply scheme used in an EU standard registration.
        """

    class CreateParamsCountryOptionsHu(TypedDict):
        standard: NotRequired[
            "Registration.CreateParamsCountryOptionsHuStandard"
        ]
        """
        Options for the standard registration.
        """
        type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
        """
        Type of registration to be created in an EU country.
        """

    class CreateParamsCountryOptionsHuStandard(TypedDict):
        place_of_supply_scheme: Literal["small_seller", "standard"]
        """
        Place of supply scheme used in an EU standard registration.
        """

    class CreateParamsCountryOptionsId(TypedDict):
        type: Literal["simplified"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsIe(TypedDict):
        standard: NotRequired[
            "Registration.CreateParamsCountryOptionsIeStandard"
        ]
        """
        Options for the standard registration.
        """
        type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
        """
        Type of registration to be created in an EU country.
        """

    class CreateParamsCountryOptionsIeStandard(TypedDict):
        place_of_supply_scheme: Literal["small_seller", "standard"]
        """
        Place of supply scheme used in an EU standard registration.
        """

    class CreateParamsCountryOptionsIs(TypedDict):
        type: Literal["standard"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsIt(TypedDict):
        standard: NotRequired[
            "Registration.CreateParamsCountryOptionsItStandard"
        ]
        """
        Options for the standard registration.
        """
        type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
        """
        Type of registration to be created in an EU country.
        """

    class CreateParamsCountryOptionsItStandard(TypedDict):
        place_of_supply_scheme: Literal["small_seller", "standard"]
        """
        Place of supply scheme used in an EU standard registration.
        """

    class CreateParamsCountryOptionsJp(TypedDict):
        type: Literal["standard"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsKe(TypedDict):
        type: Literal["simplified"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsKh(TypedDict):
        type: Literal["simplified"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsKr(TypedDict):
        type: Literal["simplified"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsKz(TypedDict):
        type: Literal["simplified"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsLt(TypedDict):
        standard: NotRequired[
            "Registration.CreateParamsCountryOptionsLtStandard"
        ]
        """
        Options for the standard registration.
        """
        type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
        """
        Type of registration to be created in an EU country.
        """

    class CreateParamsCountryOptionsLtStandard(TypedDict):
        place_of_supply_scheme: Literal["small_seller", "standard"]
        """
        Place of supply scheme used in an EU standard registration.
        """

    class CreateParamsCountryOptionsLu(TypedDict):
        standard: NotRequired[
            "Registration.CreateParamsCountryOptionsLuStandard"
        ]
        """
        Options for the standard registration.
        """
        type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
        """
        Type of registration to be created in an EU country.
        """

    class CreateParamsCountryOptionsLuStandard(TypedDict):
        place_of_supply_scheme: Literal["small_seller", "standard"]
        """
        Place of supply scheme used in an EU standard registration.
        """

    class CreateParamsCountryOptionsLv(TypedDict):
        standard: NotRequired[
            "Registration.CreateParamsCountryOptionsLvStandard"
        ]
        """
        Options for the standard registration.
        """
        type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
        """
        Type of registration to be created in an EU country.
        """

    class CreateParamsCountryOptionsLvStandard(TypedDict):
        place_of_supply_scheme: Literal["small_seller", "standard"]
        """
        Place of supply scheme used in an EU standard registration.
        """

    class CreateParamsCountryOptionsMa(TypedDict):
        type: Literal["simplified"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsMd(TypedDict):
        type: Literal["simplified"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsMe(TypedDict):
        type: Literal["standard"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsMk(TypedDict):
        type: Literal["standard"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsMr(TypedDict):
        type: Literal["standard"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsMt(TypedDict):
        standard: NotRequired[
            "Registration.CreateParamsCountryOptionsMtStandard"
        ]
        """
        Options for the standard registration.
        """
        type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
        """
        Type of registration to be created in an EU country.
        """

    class CreateParamsCountryOptionsMtStandard(TypedDict):
        place_of_supply_scheme: Literal["small_seller", "standard"]
        """
        Place of supply scheme used in an EU standard registration.
        """

    class CreateParamsCountryOptionsMx(TypedDict):
        type: Literal["simplified"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsMy(TypedDict):
        type: Literal["simplified"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsNg(TypedDict):
        type: Literal["simplified"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsNl(TypedDict):
        standard: NotRequired[
            "Registration.CreateParamsCountryOptionsNlStandard"
        ]
        """
        Options for the standard registration.
        """
        type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
        """
        Type of registration to be created in an EU country.
        """

    class CreateParamsCountryOptionsNlStandard(TypedDict):
        place_of_supply_scheme: Literal["small_seller", "standard"]
        """
        Place of supply scheme used in an EU standard registration.
        """

    class CreateParamsCountryOptionsNo(TypedDict):
        type: Literal["standard"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsNp(TypedDict):
        type: Literal["simplified"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsNz(TypedDict):
        type: Literal["standard"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsOm(TypedDict):
        type: Literal["standard"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsPe(TypedDict):
        type: Literal["simplified"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsPl(TypedDict):
        standard: NotRequired[
            "Registration.CreateParamsCountryOptionsPlStandard"
        ]
        """
        Options for the standard registration.
        """
        type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
        """
        Type of registration to be created in an EU country.
        """

    class CreateParamsCountryOptionsPlStandard(TypedDict):
        place_of_supply_scheme: Literal["small_seller", "standard"]
        """
        Place of supply scheme used in an EU standard registration.
        """

    class CreateParamsCountryOptionsPt(TypedDict):
        standard: NotRequired[
            "Registration.CreateParamsCountryOptionsPtStandard"
        ]
        """
        Options for the standard registration.
        """
        type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
        """
        Type of registration to be created in an EU country.
        """

    class CreateParamsCountryOptionsPtStandard(TypedDict):
        place_of_supply_scheme: Literal["small_seller", "standard"]
        """
        Place of supply scheme used in an EU standard registration.
        """

    class CreateParamsCountryOptionsRo(TypedDict):
        standard: NotRequired[
            "Registration.CreateParamsCountryOptionsRoStandard"
        ]
        """
        Options for the standard registration.
        """
        type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
        """
        Type of registration to be created in an EU country.
        """

    class CreateParamsCountryOptionsRoStandard(TypedDict):
        place_of_supply_scheme: Literal["small_seller", "standard"]
        """
        Place of supply scheme used in an EU standard registration.
        """

    class CreateParamsCountryOptionsRs(TypedDict):
        type: Literal["standard"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsRu(TypedDict):
        type: Literal["simplified"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsSa(TypedDict):
        type: Literal["simplified"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsSe(TypedDict):
        standard: NotRequired[
            "Registration.CreateParamsCountryOptionsSeStandard"
        ]
        """
        Options for the standard registration.
        """
        type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
        """
        Type of registration to be created in an EU country.
        """

    class CreateParamsCountryOptionsSeStandard(TypedDict):
        place_of_supply_scheme: Literal["small_seller", "standard"]
        """
        Place of supply scheme used in an EU standard registration.
        """

    class CreateParamsCountryOptionsSg(TypedDict):
        type: Literal["standard"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsSi(TypedDict):
        standard: NotRequired[
            "Registration.CreateParamsCountryOptionsSiStandard"
        ]
        """
        Options for the standard registration.
        """
        type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
        """
        Type of registration to be created in an EU country.
        """

    class CreateParamsCountryOptionsSiStandard(TypedDict):
        place_of_supply_scheme: Literal["small_seller", "standard"]
        """
        Place of supply scheme used in an EU standard registration.
        """

    class CreateParamsCountryOptionsSk(TypedDict):
        standard: NotRequired[
            "Registration.CreateParamsCountryOptionsSkStandard"
        ]
        """
        Options for the standard registration.
        """
        type: Literal["ioss", "oss_non_union", "oss_union", "standard"]
        """
        Type of registration to be created in an EU country.
        """

    class CreateParamsCountryOptionsSkStandard(TypedDict):
        place_of_supply_scheme: Literal["small_seller", "standard"]
        """
        Place of supply scheme used in an EU standard registration.
        """

    class CreateParamsCountryOptionsSn(TypedDict):
        type: Literal["simplified"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsSr(TypedDict):
        type: Literal["standard"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsTh(TypedDict):
        type: Literal["simplified"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsTj(TypedDict):
        type: Literal["simplified"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsTr(TypedDict):
        type: Literal["simplified"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsTz(TypedDict):
        type: Literal["simplified"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsUg(TypedDict):
        type: Literal["simplified"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsUs(TypedDict):
        local_amusement_tax: NotRequired[
            "Registration.CreateParamsCountryOptionsUsLocalAmusementTax"
        ]
        """
        Options for the local amusement tax registration.
        """
        local_lease_tax: NotRequired[
            "Registration.CreateParamsCountryOptionsUsLocalLeaseTax"
        ]
        """
        Options for the local lease tax registration.
        """
        state: str
        """
        Two-letter US state code ([ISO 3166-2](https://en.wikipedia.org/wiki/ISO_3166-2)).
        """
        state_sales_tax: NotRequired[
            "Registration.CreateParamsCountryOptionsUsStateSalesTax"
        ]
        """
        Options for the state sales tax registration.
        """
        type: Literal[
            "local_amusement_tax",
            "local_lease_tax",
            "state_communications_tax",
            "state_retail_delivery_fee",
            "state_sales_tax",
        ]
        """
        Type of registration to be created in the US.
        """

    class CreateParamsCountryOptionsUsLocalAmusementTax(TypedDict):
        jurisdiction: str
        """
        A [FIPS code](https://www.census.gov/library/reference/code-lists/ansi.html) representing the local jurisdiction. Supported FIPS codes are: `14000` (Chicago), `06613` (Bloomington), `21696` (East Dundee), `24582` (Evanston), and `68081` (Schiller Park).
        """

    class CreateParamsCountryOptionsUsLocalLeaseTax(TypedDict):
        jurisdiction: str
        """
        A [FIPS code](https://www.census.gov/library/reference/code-lists/ansi.html) representing the local jurisdiction. Supported FIPS codes are: `14000` (Chicago).
        """

    class CreateParamsCountryOptionsUsStateSalesTax(TypedDict):
        elections: List[
            "Registration.CreateParamsCountryOptionsUsStateSalesTaxElection"
        ]
        """
        Elections for the state sales tax registration.
        """

    class CreateParamsCountryOptionsUsStateSalesTaxElection(TypedDict):
        jurisdiction: NotRequired[str]
        """
        A [FIPS code](https://www.census.gov/library/reference/code-lists/ansi.html) representing the local jurisdiction. Supported FIPS codes are: `003` (Allegheny County) and `60000` (Philadelphia City).
        """
        type: Literal[
            "local_use_tax",
            "simplified_sellers_use_tax",
            "single_local_use_tax",
        ]
        """
        The type of the election for the state sales tax registration.
        """

    class CreateParamsCountryOptionsUy(TypedDict):
        type: Literal["standard"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsUz(TypedDict):
        type: Literal["simplified"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsVn(TypedDict):
        type: Literal["simplified"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsZa(TypedDict):
        type: Literal["standard"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsZm(TypedDict):
        type: Literal["simplified"]
        """
        Type of registration to be created in `country`.
        """

    class CreateParamsCountryOptionsZw(TypedDict):
        type: Literal["standard"]
        """
        Type of registration to be created in `country`.
        """

    class ListParams(RequestOptions):
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
        starting_after: NotRequired[str]
        """
        A cursor for use in pagination. `starting_after` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with `obj_foo`, your subsequent call can include `starting_after=obj_foo` in order to fetch the next page of the list.
        """
        status: NotRequired[Literal["active", "all", "expired", "scheduled"]]
        """
        The status of the Tax Registration.
        """

    class ModifyParams(RequestOptions):
        active_from: NotRequired["Literal['now']|int"]
        """
        Time at which the registration becomes active. It can be either `now` to indicate the current time, or a timestamp measured in seconds since the Unix epoch.
        """
        expand: NotRequired[List[str]]
        """
        Specifies which fields in the response should be expanded.
        """
        expires_at: NotRequired["Literal['']|Literal['now']|int"]
        """
        If set, the registration stops being active at this time. If not set, the registration will be active indefinitely. It can be either `now` to indicate the current time, or a timestamp measured in seconds since the Unix epoch.
        """

    class RetrieveParams(RequestOptions):
        expand: NotRequired[List[str]]
        """
        Specifies which fields in the response should be expanded.
        """

    active_from: int
    """
    Time at which the registration becomes active. Measured in seconds since the Unix epoch.
    """
    country: str
    """
    Two-letter country code ([ISO 3166-1 alpha-2](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2)).
    """
    country_options: CountryOptions
    created: int
    """
    Time at which the object was created. Measured in seconds since the Unix epoch.
    """
    expires_at: Optional[int]
    """
    If set, the registration stops being active at this time. If not set, the registration will be active indefinitely. Measured in seconds since the Unix epoch.
    """
    id: str
    """
    Unique identifier for the object.
    """
    livemode: bool
    """
    Has the value `true` if the object exists in live mode or the value `false` if the object exists in test mode.
    """
    object: Literal["tax.registration"]
    """
    String representing the object's type. Objects of the same type share the same value.
    """
    status: Literal["active", "expired", "scheduled"]
    """
    The status of the registration. This field is present for convenience and can be deduced from `active_from` and `expires_at`.
    """

    @classmethod
    def create(
        cls, **params: Unpack["Registration.CreateParams"]
    ) -> "Registration":
        """
        Creates a new Tax Registration object.
        """
        return cast(
            "Registration",
            cls._static_request(
                "post",
                cls.class_url(),
                params=params,
            ),
        )

    @classmethod
    async def create_async(
        cls, **params: Unpack["Registration.CreateParams"]
    ) -> "Registration":
        """
        Creates a new Tax Registration object.
        """
        return cast(
            "Registration",
            await cls._static_request_async(
                "post",
                cls.class_url(),
                params=params,
            ),
        )

    @classmethod
    def list(
        cls, **params: Unpack["Registration.ListParams"]
    ) -> ListObject["Registration"]:
        """
        Returns a list of Tax Registration objects.
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
        cls, **params: Unpack["Registration.ListParams"]
    ) -> ListObject["Registration"]:
        """
        Returns a list of Tax Registration objects.
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

    @classmethod
    def modify(
        cls, id: str, **params: Unpack["Registration.ModifyParams"]
    ) -> "Registration":
        """
        Updates an existing Tax Registration object.

        A registration cannot be deleted after it has been created. If you wish to end a registration you may do so by setting expires_at.
        """
        url = "%s/%s" % (cls.class_url(), sanitize_id(id))
        return cast(
            "Registration",
            cls._static_request(
                "post",
                url,
                params=params,
            ),
        )

    @classmethod
    async def modify_async(
        cls, id: str, **params: Unpack["Registration.ModifyParams"]
    ) -> "Registration":
        """
        Updates an existing Tax Registration object.

        A registration cannot be deleted after it has been created. If you wish to end a registration you may do so by setting expires_at.
        """
        url = "%s/%s" % (cls.class_url(), sanitize_id(id))
        return cast(
            "Registration",
            await cls._static_request_async(
                "post",
                url,
                params=params,
            ),
        )

    @classmethod
    def retrieve(
        cls, id: str, **params: Unpack["Registration.RetrieveParams"]
    ) -> "Registration":
        """
        Returns a Tax Registration object.
        """
        instance = cls(id, **params)
        instance.refresh()
        return instance

    @classmethod
    async def retrieve_async(
        cls, id: str, **params: Unpack["Registration.RetrieveParams"]
    ) -> "Registration":
        """
        Returns a Tax Registration object.
        """
        instance = cls(id, **params)
        await instance.refresh_async()
        return instance

    _inner_class_types = {"country_options": CountryOptions}
