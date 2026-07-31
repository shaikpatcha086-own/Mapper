"""
===========================================================
D365 F&O Cross-Module Field Catalogue
D365 Metadata Mapper V3
===========================================================

Purpose
-------
When a source field cannot be matched to the uploaded
target workbook, this catalogue is searched to suggest
which D365 F&O module / entity the field may belong to.

Structure
---------
Each entry:
    {
        "field"       : D365 technical field name
        "label"       : Business label
        "module"      : D365 module (e.g. Accounts Receivable)
        "entity"      : D365 data entity name
        "description" : Business description
        "concepts"    : list of business concept keywords
    }
===========================================================
"""

D365_MODULE_CATALOGUE = [

    # =========================================================
    # Accounts Receivable (AR)
    # =========================================================

    # --- Customer Master ---
    {
        "field": "CustAccount",
        "label": "Customer Account",
        "module": "Accounts Receivable",
        "entity": "CustCustomerV3Entity",
        "description": "Unique identifier for the customer account",
        "concepts": ["customer", "account", "id", "number", "no"]
    },
    {
        "field": "OrganizationName",
        "label": "Name",
        "module": "Accounts Receivable",
        "entity": "CustCustomerV3Entity",
        "description": "Legal name of the customer organization",
        "concepts": ["name", "company", "organization", "legal", "business"]
    },
    {
        "field": "SearchName",
        "label": "Search Name",
        "module": "Accounts Receivable",
        "entity": "CustCustomerV3Entity",
        "description": "Short name used for searching the customer",
        "concepts": ["search", "name", "short", "alias"]
    },
    {
        "field": "CustGroupId",
        "label": "Customer Group",
        "module": "Accounts Receivable",
        "entity": "CustCustomerV3Entity",
        "description": "Group the customer belongs to for reporting and posting",
        "concepts": ["customer", "group", "segment", "category"]
    },
    {
        "field": "SalesCurrencyCode",
        "label": "Currency",
        "module": "Accounts Receivable",
        "entity": "CustCustomerV3Entity",
        "description": "Default transaction currency for the customer",
        "concepts": ["currency", "sales", "transaction", "code"]
    },
    {
        "field": "PaymTermId",
        "label": "Payment Terms",
        "module": "Accounts Receivable",
        "entity": "CustCustomerV3Entity",
        "description": "Default payment terms agreed with the customer",
        "concepts": ["payment", "terms", "due", "days", "net"]
    },
    {
        "field": "PaymMode",
        "label": "Payment Method",
        "module": "Accounts Receivable",
        "entity": "CustCustomerV3Entity",
        "description": "Default method of payment (bank transfer, cheque, etc.)",
        "concepts": ["payment", "method", "mode", "collection", "type"]
    },
    {
        "field": "Blocked",
        "label": "Blocked",
        "module": "Accounts Receivable",
        "entity": "CustCustomerV3Entity",
        "description": "Indicates whether the customer is blocked for transactions",
        "concepts": ["blocked", "hold", "stop", "credit", "status", "active"]
    },
    {
        "field": "CreditMax",
        "label": "Credit Limit",
        "module": "Accounts Receivable",
        "entity": "CustCustomerV3Entity",
        "description": "Maximum credit amount allowed for the customer",
        "concepts": ["credit", "limit", "amount", "maximum", "cap"]
    },
    {
        "field": "InvoiceAccount",
        "label": "Invoice Account",
        "module": "Accounts Receivable",
        "entity": "CustCustomerV3Entity",
        "description": "Customer account that receives the invoice (if different from delivery)",
        "concepts": ["invoice", "account", "billing", "bill", "to"]
    },
    {
        "field": "ContactPersonId",
        "label": "Contact",
        "module": "Accounts Receivable",
        "entity": "CustCustomerV3Entity",
        "description": "Primary contact person for the customer",
        "concepts": ["contact", "person", "primary", "name"]
    },
    {
        "field": "PrimaryContactPhone",
        "label": "Phone No.",
        "module": "Accounts Receivable",
        "entity": "CustCustomerV3Entity",
        "description": "Primary phone number of the customer",
        "concepts": ["phone", "telephone", "contact", "number", "mobile"]
    },
    {
        "field": "PrimaryContactEmail",
        "label": "Email",
        "module": "Accounts Receivable",
        "entity": "CustCustomerV3Entity",
        "description": "Primary email address of the customer",
        "concepts": ["email", "mail", "contact", "address", "electronic"]
    },
    {
        "field": "PrimaryContactFax",
        "label": "Fax No.",
        "module": "Accounts Receivable",
        "entity": "CustCustomerV3Entity",
        "description": "Primary fax number of the customer",
        "concepts": ["fax", "facsimile", "contact", "number"]
    },
    {
        "field": "SalesPoolId",
        "label": "Sales Pool / Sales District",
        "module": "Accounts Receivable",
        "entity": "CustCustomerV3Entity",
        "description": "Sales territory or district assigned to the customer",
        "concepts": ["sales", "pool", "district", "territory", "region", "area"]
    },
    {
        "field": "SalesTaxGroup",
        "label": "Sales Tax Group",
        "module": "Accounts Receivable",
        "entity": "CustCustomerV3Entity",
        "description": "Tax group applied to sales transactions",
        "concepts": ["tax", "vat", "group", "sales", "gst"]
    },
    {
        "field": "PaymentSchedule",
        "label": "Payment Schedule",
        "module": "Accounts Receivable",
        "entity": "CustCustomerV3Entity",
        "description": "Instalment schedule for customer payments",
        "concepts": ["payment", "schedule", "instalment", "plan"]
    },
    {
        "field": "CashDiscountCode",
        "label": "Cash Discount",
        "module": "Accounts Receivable",
        "entity": "CustCustomerV3Entity",
        "description": "Early payment discount code for the customer",
        "concepts": ["cash", "discount", "early", "payment", "settlement"]
    },
    {
        "field": "InvoiceDiscountCode",
        "label": "Invoice Discount Code",
        "module": "Accounts Receivable",
        "entity": "CustCustomerV3Entity",
        "description": "Discount group code applied to invoices",
        "concepts": ["invoice", "discount", "code", "group", "rebate"]
    },
    {
        "field": "LineDiscountGroupCode",
        "label": "Line Discount Group",
        "module": "Accounts Receivable",
        "entity": "CustCustomerV3Entity",
        "description": "Discount group applied at the sales order line level",
        "concepts": ["line", "discount", "group", "code", "price"]
    },
    {
        "field": "PriceGroupId",
        "label": "Price Group",
        "module": "Accounts Receivable",
        "entity": "CustCustomerV3Entity",
        "description": "Price group used for trade agreements",
        "concepts": ["price", "group", "trade", "agreement", "list"]
    },
    {
        "field": "LanguageId",
        "label": "Language",
        "module": "Accounts Receivable",
        "entity": "CustCustomerV3Entity",
        "description": "Language used for customer documents",
        "concepts": ["language", "locale", "document", "print"]
    },
    {
        "field": "DeliveryModeCode",
        "label": "Delivery Mode",
        "module": "Accounts Receivable",
        "entity": "CustCustomerV3Entity",
        "description": "Default delivery method (road, air, sea, etc.)",
        "concepts": ["delivery", "mode", "shipment", "transport", "method"]
    },
    {
        "field": "DeliveryTermsCode",
        "label": "Delivery Terms",
        "module": "Accounts Receivable",
        "entity": "CustCustomerV3Entity",
        "description": "Incoterms or delivery terms agreed with the customer",
        "concepts": ["delivery", "terms", "incoterms", "conditions", "fob"]
    },
    {
        "field": "ShippingCarrierId",
        "label": "Shipping Agent",
        "module": "Accounts Receivable",
        "entity": "CustCustomerV3Entity",
        "description": "Preferred shipping carrier / freight company",
        "concepts": ["shipping", "carrier", "agent", "freight", "transport", "courier"]
    },
    {
        "field": "ShippingCarrierServiceId",
        "label": "Shipping Agent Service",
        "module": "Accounts Receivable",
        "entity": "CustCustomerV3Entity",
        "description": "Specific service level of the shipping carrier",
        "concepts": ["shipping", "carrier", "service", "agent", "code", "level"]
    },
    {
        "field": "DepositSlip",
        "label": "Deposit Slip",
        "module": "Accounts Receivable",
        "entity": "CustCustomerV3Entity",
        "description": "Indicates if a deposit slip is required for payments",
        "concepts": ["deposit", "slip", "payment", "receipt", "voucher"]
    },
    {
        "field": "InvoiceCopies",
        "label": "Invoice Copies",
        "module": "Accounts Receivable",
        "entity": "CustCustomerV3Entity",
        "description": "Number of invoice copies to be printed for the customer",
        "concepts": ["invoice", "copies", "print", "number", "document"]
    },
    {
        "field": "CollectionLetterCode",
        "label": "Collection Letter Sequence",
        "module": "Accounts Receivable",
        "entity": "CustCustomerV3Entity",
        "description": "Sequence of collection letters sent for overdue amounts",
        "concepts": ["collection", "letter", "dunning", "overdue", "sequence", "inkasso"]
    },
    {
        "field": "CollectionContactId",
        "label": "Collection Agent",
        "module": "Accounts Receivable",
        "entity": "CustCustomerV3Entity",
        "description": "Agent responsible for collections from this customer",
        "concepts": ["collection", "agent", "contact", "responsible", "inkasso"]
    },
    {
        "field": "GroupInvoices",
        "label": "Group Invoices",
        "module": "Accounts Receivable",
        "entity": "CustCustomerV3Entity",
        "description": "Whether to consolidate invoices for this customer",
        "concepts": ["group", "invoice", "consolidate", "merge", "cm", "collection"]
    },
    {
        "field": "LastStatementDate",
        "label": "Last Statement No.",
        "module": "Accounts Receivable",
        "entity": "CustCustomerV3Entity",
        "description": "Date or reference of the last account statement sent",
        "concepts": ["last", "statement", "account", "date", "number", "no"]
    },
    {
        "field": "ExportSaleIndicator",
        "label": "Place of Export",
        "module": "Accounts Receivable",
        "entity": "CustCustomerV3Entity",
        "description": "Indicates if this customer is an export sale destination",
        "concepts": ["export", "place", "sale", "indicator", "foreign"]
    },
    {
        "field": "SkipNationalRegister",
        "label": "Skip National Register",
        "module": "Accounts Receivable",
        "entity": "CustCustomerV3Entity",
        "description": "Flag to exclude customer from national register reporting",
        "concepts": ["skip", "national", "register", "exclude", "report"]
    },
    {
        "field": "DocumentSendingProfile",
        "label": "Document Sending Profile",
        "module": "Accounts Receivable",
        "entity": "CustCustomerV3Entity",
        "description": "Profile controlling how documents are sent to the customer",
        "concepts": ["document", "sending", "profile", "email", "print", "electronic"]
    },

    # =========================================================
    # Supply Chain Management (SCM)
    # =========================================================

    {
        "field": "ItemNumber",
        "label": "Item Number",
        "module": "Supply Chain Management",
        "entity": "EcoResProductEntity",
        "description": "Unique identifier for a product/item in inventory",
        "concepts": ["item", "product", "number", "sku", "code"]
    },
    {
        "field": "ProductName",
        "label": "Product Name",
        "module": "Supply Chain Management",
        "entity": "EcoResProductEntity",
        "description": "Name of the product or item",
        "concepts": ["product", "name", "item", "description", "label"]
    },
    {
        "field": "StorageDimensionGroupName",
        "label": "Storage Dimension Group",
        "module": "Supply Chain Management",
        "entity": "EcoResProductEntity",
        "description": "Dimension group defining warehouse/location tracking",
        "concepts": ["storage", "dimension", "group", "warehouse", "location"]
    },
    {
        "field": "WarehouseId",
        "label": "Warehouse",
        "module": "Supply Chain Management",
        "entity": "InventWarehouseEntity",
        "description": "Warehouse identifier for inventory storage",
        "concepts": ["warehouse", "storage", "location", "site", "stock"]
    },
    {
        "field": "SiteId",
        "label": "Site",
        "module": "Supply Chain Management",
        "entity": "InventSiteEntity",
        "description": "Production or storage site identifier",
        "concepts": ["site", "plant", "location", "facility"]
    },
    {
        "field": "SalesOrderNumber",
        "label": "Sales Order",
        "module": "Supply Chain Management",
        "entity": "SalesOrderHeaderV2Entity",
        "description": "Sales order number",
        "concepts": ["sales", "order", "number", "reference"]
    },
    {
        "field": "PurchaseOrderNumber",
        "label": "Purchase Order",
        "module": "Supply Chain Management",
        "entity": "PurchPurchaseOrderHeaderEntity",
        "description": "Purchase order number",
        "concepts": ["purchase", "order", "number", "po", "procurement"]
    },

    # =========================================================
    # General Ledger (GL)
    # =========================================================

    {
        "field": "MainAccountId",
        "label": "Main Account",
        "module": "General Ledger",
        "entity": "MainAccountEntity",
        "description": "GL main account number",
        "concepts": ["account", "ledger", "general", "main", "gl", "number"]
    },
    {
        "field": "LedgerDimension",
        "label": "Ledger Dimension",
        "module": "General Ledger",
        "entity": "LedgerJournalTransEntity",
        "description": "Full ledger dimension including account and financial dimensions",
        "concepts": ["ledger", "dimension", "account", "financial", "segment"]
    },
    {
        "field": "CurrencyCode",
        "label": "Currency",
        "module": "General Ledger",
        "entity": "CurrencyEntity",
        "description": "ISO currency code",
        "concepts": ["currency", "code", "iso", "money"]
    },
    {
        "field": "ExchangeRate",
        "label": "Exchange Rate",
        "module": "General Ledger",
        "entity": "ExchangeRateEntity",
        "description": "Currency exchange rate",
        "concepts": ["exchange", "rate", "currency", "conversion"]
    },

    # =========================================================
    # Accounts Payable (AP)
    # =========================================================

    {
        "field": "VendAccount",
        "label": "Vendor Account",
        "module": "Accounts Payable",
        "entity": "VendVendorV2Entity",
        "description": "Unique vendor account identifier",
        "concepts": ["vendor", "supplier", "account", "number", "id"]
    },
    {
        "field": "VendGroupId",
        "label": "Vendor Group",
        "module": "Accounts Payable",
        "entity": "VendVendorV2Entity",
        "description": "Group the vendor belongs to",
        "concepts": ["vendor", "supplier", "group", "category"]
    },
    {
        "field": "VendPaymMode",
        "label": "Vendor Payment Method",
        "module": "Accounts Payable",
        "entity": "VendVendorV2Entity",
        "description": "Payment method for vendor payments",
        "concepts": ["payment", "method", "vendor", "mode", "bank"]
    },

    # =========================================================
    # Project Management & Accounting
    # =========================================================

    {
        "field": "ProjectId",
        "label": "Project ID",
        "module": "Project Management & Accounting",
        "entity": "ProjProjectEntity",
        "description": "Unique identifier for a project",
        "concepts": ["project", "id", "number", "code", "reference"]
    },
    {
        "field": "ProjectName",
        "label": "Project Name",
        "module": "Project Management & Accounting",
        "entity": "ProjProjectEntity",
        "description": "Name or title of the project",
        "concepts": ["project", "name", "title", "description"]
    },
    {
        "field": "ProjCategoryId",
        "label": "Project Category",
        "module": "Project Management & Accounting",
        "entity": "ProjCategoryEntity",
        "description": "Category classification for project transactions",
        "concepts": ["project", "category", "type", "classification", "activity"]
    },
    {
        "field": "ProjContractId",
        "label": "Project Contract",
        "module": "Project Management & Accounting",
        "entity": "ProjContractEntity",
        "description": "Contract associated with the project",
        "concepts": ["project", "contract", "agreement", "funding"]
    },

    # =========================================================
    # Human Resources (HR)
    # =========================================================

    {
        "field": "WorkerNumber",
        "label": "Employee Number",
        "module": "Human Resources",
        "entity": "HcmWorkerEntity",
        "description": "Unique employee or worker identifier",
        "concepts": ["worker", "employee", "number", "id", "personnel"]
    },
    {
        "field": "PersonFirstName",
        "label": "First Name",
        "module": "Human Resources",
        "entity": "HcmWorkerEntity",
        "description": "First name of the worker",
        "concepts": ["first", "name", "given", "person", "forename"]
    },
    {
        "field": "PersonLastName",
        "label": "Last Name",
        "module": "Human Resources",
        "entity": "HcmWorkerEntity",
        "description": "Last name or surname of the worker",
        "concepts": ["last", "name", "surname", "family", "person"]
    },
    {
        "field": "PositionId",
        "label": "Position",
        "module": "Human Resources",
        "entity": "HcmPositionEntity",
        "description": "Job position identifier",
        "concepts": ["position", "job", "role", "title", "function"]
    },
    {
        "field": "DepartmentNumber",
        "label": "Department",
        "module": "Human Resources",
        "entity": "OMOperatingUnitEntity",
        "description": "Department the worker belongs to",
        "concepts": ["department", "unit", "division", "team", "org"]
    },

    # =========================================================
    # Fixed Assets
    # =========================================================

    {
        "field": "AssetId",
        "label": "Asset Number",
        "module": "Fixed Assets",
        "entity": "AssetAssetEntity",
        "description": "Unique identifier for a fixed asset",
        "concepts": ["asset", "number", "id", "fixed", "equipment"]
    },
    {
        "field": "AssetGroupId",
        "label": "Asset Group",
        "module": "Fixed Assets",
        "entity": "AssetAssetEntity",
        "description": "Group or category of the fixed asset",
        "concepts": ["asset", "group", "category", "class", "type"]
    },
    {
        "field": "AcquisitionDate",
        "label": "Acquisition Date",
        "module": "Fixed Assets",
        "entity": "AssetAssetEntity",
        "description": "Date the asset was acquired or placed in service",
        "concepts": ["acquisition", "date", "purchase", "placed", "service"]
    },

    # =========================================================
    # Bank & Cash Management
    # =========================================================

    {
        "field": "BankAccountId",
        "label": "Bank Account",
        "module": "Cash & Bank Management",
        "entity": "BankAccountEntity",
        "description": "Company bank account identifier",
        "concepts": ["bank", "account", "id", "number", "iban"]
    },
    {
        "field": "BankIBAN",
        "label": "IBAN",
        "module": "Cash & Bank Management",
        "entity": "BankAccountEntity",
        "description": "International bank account number",
        "concepts": ["iban", "bank", "international", "account", "number"]
    },
    {
        "field": "BankSWIFTNo",
        "label": "SWIFT Code",
        "module": "Cash & Bank Management",
        "entity": "BankAccountEntity",
        "description": "Bank SWIFT/BIC code for international transfers",
        "concepts": ["swift", "bic", "bank", "code", "international", "transfer"]
    },
    {
        "field": "DepositSlipAmount",
        "label": "Deposit Amount",
        "module": "Cash & Bank Management",
        "entity": "BankDepositEntity",
        "description": "Amount on the deposit slip",
        "concepts": ["deposit", "amount", "slip", "cash", "payment"]
    },

]


def search_catalogue(source_field, source_description="", top_n=3, threshold=60):
    """
    Search the D365 module catalogue for fields matching a source field.

    Uses concept overlap to find the best D365 module matches.
    Returns top_n results above the threshold score.
    """

    from normalizer import tokenize
    from business_dictionary import expand_tokens
    from rapidfuzz import fuzz

    source_tokens = set(expand_tokens(tokenize(source_field)))
    if source_description:
        source_tokens |= set(expand_tokens(tokenize(source_description)))

    results = []

    for entry in D365_MODULE_CATALOGUE:

        concept_tokens = set(entry["concepts"])

        # Concept overlap score
        overlap = source_tokens.intersection(concept_tokens)
        if overlap:
            overlap_score = len(overlap) / max(len(source_tokens), len(concept_tokens)) * 100
        else:
            overlap_score = 0

        # Fuzzy score on label
        label_score = fuzz.token_set_ratio(
            source_field.lower(),
            entry["label"].lower()
        )

        # Fuzzy score on field name
        field_score = fuzz.token_set_ratio(
            source_field.lower(),
            entry["field"].lower()
        )

        best_score = max(overlap_score, label_score, field_score)

        if best_score >= threshold:
            results.append({
                "d365_field": entry["field"],
                "d365_label": entry["label"],
                "module": entry["module"],
                "entity": entry["entity"],
                "description": entry["description"],
                "score": round(best_score),
            })

    results.sort(key=lambda x: x["score"], reverse=True)

    return results[:top_n]
