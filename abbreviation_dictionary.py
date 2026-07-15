"""
===========================================================
Abbreviation Dictionary
D365 Metadata Mapper V4
===========================================================

Enterprise abbreviation dictionary.

Supports metadata coming from:

- D365
- Dynamics AX 2009
- Dynamics AX 2012
- NAV
- Oracle
- SAP
- Salesforce
- Siebel
- SQL Server
- CSV
- Excel
- Legacy ERP
"""

from normalizer import normalize


# ==========================================================
# Enterprise Abbreviation Dictionary
# ==========================================================

ABBREVIATIONS = {

    # ------------------------------------------------------
    # Customer
    # ------------------------------------------------------

    "cust": "customer",
    "custmr": "customer",
    "customer": "customer",
    "client": "customer",
    "cli": "customer",
    "debtor": "customer",

    # ------------------------------------------------------
    # Vendor
    # ------------------------------------------------------

    "vend": "vendor",
    "vendor": "vendor",
    "supplier": "vendor",
    "sup": "vendor",
    "creditor": "vendor",

    # ------------------------------------------------------
    # Employee
    # ------------------------------------------------------

    "emp": "employee",
    "empl": "employee",
    "employee": "employee",

    # ------------------------------------------------------
    # Worker
    # ------------------------------------------------------

    "wrk": "worker",
    "worker": "worker",
    "personnel": "worker",

    # ------------------------------------------------------
    # Organization
    # ------------------------------------------------------

    "org": "organization",
    "organisation": "organization",
    "organization": "organization",
    "company": "organization",

    # ------------------------------------------------------
    # Party
    # ------------------------------------------------------

    "party": "party",
    "ptype": "party type",
    "patype": "party type",

    # ------------------------------------------------------
    # Invoice
    # ------------------------------------------------------

    "inv": "invoice",
    "invoice": "invoice",

    # ------------------------------------------------------
    # Account
    # ------------------------------------------------------

    "acct": "account",
    "acc": "account",
    "account": "account",

    # ------------------------------------------------------
    # Address
    # ------------------------------------------------------

    "addr": "address",
    "address": "address",

    # ------------------------------------------------------
    # Number
    # ------------------------------------------------------

    "num": "number",
    "nbr": "number",
    "numb": "number",
    "no": "number",

    # ------------------------------------------------------
    # Identifier
    # ------------------------------------------------------

    "id": "identifier",
    "code": "code",

    # ------------------------------------------------------
    # Method
    # ------------------------------------------------------

    "mth": "method",
    "mthd": "method",
    "method": "method",

    # ------------------------------------------------------
    # Credit
    # ------------------------------------------------------

    "crd": "credit",
    "credit": "credit",

    # ------------------------------------------------------
    # Quantity
    # ------------------------------------------------------

    "qty": "quantity",

    # ------------------------------------------------------
    # Amount
    # ------------------------------------------------------

    "amt": "amount",

    # ------------------------------------------------------
    # Description
    # ------------------------------------------------------

    "desc": "description",

    # ------------------------------------------------------
    # Date
    # ------------------------------------------------------

    "dt": "date",

    # ------------------------------------------------------
    # Country
    # ------------------------------------------------------

    "cntry": "country",
    "country": "country",

    # ------------------------------------------------------
    # Region
    # ------------------------------------------------------

    "region": "region",

    # ------------------------------------------------------
    # State
    # ------------------------------------------------------

    "st": "state",
    "state": "state",

    # ------------------------------------------------------
    # City
    # ------------------------------------------------------

    "cty": "city",
    "city": "city",
        # ------------------------------------------------------
    # Finance
    # ------------------------------------------------------

    "gl": "general ledger",
    "ledger": "ledger",
    "coa": "chart of accounts",
    "accttype": "account type",
    "acctnum": "account number",
    "glacct": "general ledger account",
    "bal": "balance",
    "curr": "currency",
    "currency": "currency",
    "fx": "exchange",
    "tax": "tax",
    "vat": "vat",

    # ------------------------------------------------------
    # Project
    # ------------------------------------------------------

    "proj": "project",
    "project": "project",
    "projid": "project identifier",
    "projgrp": "project group",
    "contract": "contract",

    # ------------------------------------------------------
    # Inventory
    # ------------------------------------------------------

    "item": "item",
    "itm": "item",
    "product": "product",
    "invent": "inventory",
    "inventory": "inventory",
    "inventdim": "inventory dimension",
    "warehouse": "warehouse",
    "wh": "warehouse",
    "site": "site",
    "location": "location",

    # ------------------------------------------------------
    # Sales
    # ------------------------------------------------------

    "sales": "sales",
    "salesid": "sales order",
    "salesord": "sales order",
    "salesorder": "sales order",
    "quotation": "quotation",
    "quote": "quotation",

    # ------------------------------------------------------
    # Purchase
    # ------------------------------------------------------

    "purch": "purchase",
    "purchase": "purchase",
    "po": "purchase order",
    "purchorder": "purchase order",
    "purchid": "purchase order",

    # ------------------------------------------------------
    # Payment
    # ------------------------------------------------------

    "payment": "payment",
    "pay": "payment",
    "paym": "payment",
    "paymethod": "payment method",
    "paymentmethod": "payment method",

    # ------------------------------------------------------
    # Address
    # ------------------------------------------------------

    "countryregion": "country region",
    "countryregionid": "country region",
    "countryregioniso": "country region iso",
    "countryregionisocode": "country region iso code",
    "postal": "postal",
    "postcode": "postal code",
    "zipcode": "postal code",
    "district": "district",
    "county": "county",
        # ------------------------------------------------------
    # Human Resources
    # ------------------------------------------------------

    "person": "person",
    "resource": "resource",
    "department": "department",
    "dept": "department",
    "manager": "manager",
    "mgr": "manager",
    "position": "position",
    "responsible": "responsible",

    # ------------------------------------------------------
    # Generic
    # ------------------------------------------------------

    "name": "name",
    "type": "type",
    "status": "status",
    "group": "group",
    "line": "line",
    "header": "header",
    "value": "value",
    "display": "display",
    "displayvalue": "display value",
    "chain": "chain"

}


# ==========================================================
# Expand Abbreviation
# ==========================================================

def expand_abbreviation(value):
    """
    Expands a single abbreviation.

    Example:
        emp  -> employee
        inv  -> invoice
        org  -> organization
    """

    value = normalize(value)

    if value == "":
        return ""

    value = value.replace(" ", "")

    return ABBREVIATIONS.get(value, value)