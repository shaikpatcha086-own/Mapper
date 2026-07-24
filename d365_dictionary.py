"""
===========================================================
D365 Business Dictionary
D365 Finance & Operations Metadata Mapper V3
===========================================================

Purpose
-------
Converts D365 abbreviations and technical field names
into common business concepts for intelligent matching.
"""

from normalizer import normalize

# =========================================================
# D365 Business Dictionary
# =========================================================

D365_DICTIONARY = {

    # -------------------------------------------------
    # Customer
    # -------------------------------------------------

    "cust": "customer",
    "customer": "customer",
    "custaccount": "customer account",
    "customeraccount": "customer account",
    "custgroup": "customer group",
    "customergroup": "customer group",

    # -------------------------------------------------
    # Vendor
    # -------------------------------------------------

    "vend": "vendor",
    "vendor": "vendor",
    "vendaccount": "vendor account",
    "vendoraccount": "vendor account",
    "vendgroup": "vendor group",
    "vendinvoiceaccount": "vendor invoice account",

    # -------------------------------------------------
    # Organization
    # -------------------------------------------------

    "org": "organization",
    "organization": "organization",
    "company": "company",
    "legalentity": "company",
    "dataareaid": "company",

    # -------------------------------------------------
    # Party
    # -------------------------------------------------

    "party": "party",
    "dirparty": "party",
    "partynumber": "party",
    "partyid": "party",
    "ptype": "party type",
    "partytype": "party type",

    # -------------------------------------------------
    # Invoice
    # -------------------------------------------------

    "inv": "invoice",
    "invoice": "invoice",
    "invoiceid": "invoice id",
    "invoiceaccount": "invoice account",
    "invaccount": "invoice account",
    "invoiceorganization": "invoice organization",

    # -------------------------------------------------
    # Account
    # -------------------------------------------------

    "account": "account",
    "accountnum": "account number",
    "accountnumber": "account number",
    "mainaccount": "main account",

    # -------------------------------------------------
    # Ledger
    # -------------------------------------------------

    "ledger": "ledger",
    "ledgerdimension": "ledger dimension",
    "defaultdimension": "financial dimension",
    "financialdimension": "financial dimension",

    # -------------------------------------------------
    # Project
    # -------------------------------------------------

    "proj": "project",
    "project": "project",
    "projectid": "project id",
    "projectgroup": "project group",
    "projectcontract": "project contract",

    # -------------------------------------------------
    # Worker
    # -------------------------------------------------

    "worker": "worker",
    "employee": "worker",
    "personnelnumber": "worker",

    # -------------------------------------------------
    # Address
    # -------------------------------------------------

    "addr": "address",
    "address": "address",
    "street": "street",
    "city": "city",
    "state": "state",
    "province": "state",
    "zipcode": "postal code",
    "postalcode": "postal code",
    "country": "country",

    # -------------------------------------------------
    # Contact
    # -------------------------------------------------

    "email": "email",
    "emailaddress": "email",
    "phone": "phone",
    "telephone": "phone",
    "mobile": "mobile",

    # -------------------------------------------------
    # Warehouse / Inventory
    # -------------------------------------------------

    "warehouse": "warehouse",
    "inventlocation": "warehouse",
    "inventlocationid": "warehouse",
    "inventsite": "site",
    "itemid": "item",
    "itemnumber": "item",

    # -------------------------------------------------
    # Sales
    # -------------------------------------------------

    "salesid": "sales order",
    "salesorder": "sales order",

    # -------------------------------------------------
    # Purchase
    # -------------------------------------------------

    "purchid": "purchase order",
    "purchaseorder": "purchase order",

    # -------------------------------------------------
    # Generic
    # -------------------------------------------------

    "id": "identifier",
    "recid": "record identifier",
    "name": "name",
    "number": "number",
    "code": "code",
    "description": "description",
    "status": "status",
    "type": "type",
    "group": "group",
    "date": "date",
    "amount": "amount",
    "quantity": "quantity",
    "price": "price"
}


# =========================================================
# Get Business Concept
# =========================================================

def get_business_concept(text):
    """
    Converts a D365 field into a business concept.

    Example

    CustAccount
        ->
    customer account

    InvAccount
        ->
    invoice account

    Org
        ->
    organization
    """

    if text is None:
        return ""

    key = normalize(text)

    key = key.replace(" ", "")
    key = key.replace("_", "")
    key = key.replace("-", "")

    return D365_DICTIONARY.get(key, normalize(text))