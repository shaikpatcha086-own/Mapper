"""
===========================================================
Enterprise Alias Dictionary
D365 Metadata Mapper V4
===========================================================

Enterprise business aliases.

This dictionary maps legacy ERP names to the
most common D365 business meaning.

It is checked BEFORE semantic matching.
"""

from normalizer import normalize


ENTERPRISE_ALIASES = {

    # =====================================================
    # Customer
    # =====================================================

    "clientid": [
        "customeraccount",
        "customer",
        "customerid",
        "custaccount"
    ],

    "client": [
        "customer",
        "customeraccount",
        "custaccount"
    ],

    "custid": [
        "customeraccount",
        "customer"
    ],

    "customerid": [
        "customeraccount"
    ],

    "custacct": [
        "customeraccount"
    ],

    "custaccount": [
        "customeraccount"
    ],

    # =====================================================
    # Worker
    # =====================================================

    "workerid": [
        "employeeresponsiblenumber",
        "employee",
        "worker"
    ],

    "worker": [
        "employee",
        "employeeresponsiblenumber"
    ],

    "employeeid": [
        "employeeresponsiblenumber"
    ],

    "empid": [
        "employeeresponsiblenumber"
    ],

    "empnum": [
        "employeeresponsiblenumber"
    ],

    # =====================================================
    # Organization
    # =====================================================

    "org": [
        "organizationname"
    ],

    "organization": [
        "organizationname"
    ],

    # =====================================================
    # Party
    # =====================================================

    "patype": [
        "partytype"
    ],

    "partytype": [
        "partytype"
    ],
    # =====================================================
    # Vendor
    # =====================================================

    "vendorid": [
        "vendoraccount",
        "vendaccount",
        "vendor"
    ],

    "vendor": [
        "vendoraccount",
        "vendaccount"
    ],

    "vendid": [
        "vendoraccount"
    ],

    "vendaccount": [
        "vendoraccount"
    ],

    # =====================================================
    # Project
    # =====================================================

    "projectid": [
        "projectid",
        "project"
    ],

    "projid": [
        "projectid"
    ],

    "project": [
        "projectid"
    ],

    "contractid": [
        "projectcontractid"
    ],

    # =====================================================
    # Sales
    # =====================================================

    "salesid": [
        "salesid",
        "salesordernumber"
    ],

    "salesorder": [
        "salesid"
    ],

    "orderid": [
        "salesid",
        "purchid"
    ],

    # =====================================================
    # Purchase
    # =====================================================

    "purchaseid": [
        "purchid"
    ],

    "purchid": [
        "purchid"
    ],

    "purchaseorder": [
        "purchid"
    ],

    # =====================================================
    # Invoice
    # =====================================================

    "invoiceaccount": [
        "invoiceaccount"
    ],

    "invaccount": [
        "invoiceaccount"
    ],

    "invoiceid": [
        "invoiceid"
    ],

    # =====================================================
    # Address
    # =====================================================

    "address": [
        "postaladdress",
        "address"
    ],

    "country": [
        "countryregionisocode"
    ],

    "countrycode": [
        "countryregionisocode"
    ],

    "zipcode": [
        "zipcode"
    ],

    "postalcode": [
        "zipcode"
    ],

    "city": [
        "city"
    ],

    "state": [
        "state"
    ],

    # =====================================================
    # Contact
    # =====================================================

    "phone": [
        "phonenumber"
    ],

    "telephone": [
        "phonenumber"
    ],

    "email": [
        "email"
    ],

    "contact": [
        "contactpersonid"
    ],
        # =====================================================
    # Finance
    # =====================================================

    "ledger": [
        "ledger",
        "generalledger"
    ],

    "gl": [
        "generalledger"
    ],

    "mainaccount": [
        "mainaccount"
    ],

    "account": [
        "mainaccount",
        "ledgeraccount"
    ],

    "currency": [
        "currencycode"
    ],

    "currencyid": [
        "currencycode"
    ],

    "exchange": [
        "exchangerate"
    ],

    "tax": [
        "taxgroup"
    ],

    "vat": [
        "taxgroup"
    ],

    # =====================================================
    # Inventory
    # =====================================================

    "itemid": [
        "itemnumber",
        "itemid"
    ],

    "item": [
        "itemnumber"
    ],

    "product": [
        "productnumber"
    ],

    "warehouse": [
        "warehouseid"
    ],

    "warehouseid": [
        "warehouseid"
    ],

    "site": [
        "siteid"
    ],

    "location": [
        "warehouselocation"
    ],

    "inventlocation": [
        "warehouseid"
    ],

    # =====================================================
    # Payment
    # =====================================================

    "paymentmethod": [
        "paymentmethod"
    ],

    "paymethod": [
        "paymentmethod"
    ],

    "paymentterms": [
        "paymentterms"
    ],

    "terms": [
        "paymentterms"
    ],

    # =====================================================
    # Financial Dimensions
    # =====================================================

    "dimension": [
        "financialdimension"
    ],

    "defaultdimension": [
        "defaultdimension"
    ],

    "dimensiondisplayvalue": [
        "dimensiondisplayvalue"
    ],

    # =====================================================
    # Legal Entity
    # =====================================================

    "company": [
        "legalentity",
        "company"
    ],

    "companyid": [
        "legalentity"
    ],

    "legalentity": [
        "legalentity"
    ],
      # =====================================================
    # Miscellaneous
    # =====================================================

    "createdby": [
        "createdby"
    ],

    "modifiedby": [
        "modifiedby"
    ],

    "createddatetime": [
        "createddatetime"
    ],

    "modifieddatetime": [
        "modifieddatetime"
    ]

}


# ==========================================================
# Public API
# ==========================================================

def get_aliases(field_name):
    """
    Returns enterprise aliases for a field.
    """

    if not field_name:
        return []

    key = normalize(field_name)

    # Remove spaces from normalized key
    key = key.replace(" ", "")

    return ENTERPRISE_ALIASES.get(key, [])


def is_alias_match(source_field, target_field):
    """
    Returns True if target field matches
    any enterprise alias.
    """

    source = normalize(source_field).replace(" ", "")

    target = normalize(target_field).replace(" ", "")

    aliases = [

        normalize(x).replace(" ", "")

        for x in get_aliases(source_field)

    ]

    print("SOURCE :", source)
    print("TARGET :", target)
    print("ALIASES:", aliases)

    return target in aliases
    """
    Returns True if target field is a known enterprise alias.
    """

    source = normalize(source_field)
    target = normalize(target_field)

    aliases = [
        normalize(x)
        for x in get_aliases(source)
    ]

    return target in aliases


if __name__ == "__main__":

    print(normalize("WorkerId"))
    print(get_aliases("WorkerId"))

    print(normalize("ClientId"))
    print(get_aliases("ClientId"))

    print(is_alias_match(
        "WorkerId",
        "EmployeeResponsibleNumber"
    ))

    print(is_alias_match(
        "ClientId",
        "CustomerAccount"
    ))