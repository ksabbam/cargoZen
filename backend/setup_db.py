"""
Setup CargoZen database on Supabase (PostgreSQL).
Creates all tables in the public schema and seeds initial data.
"""
import psycopg2
import psycopg2.extras
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set in .env")
    exit(1)

print(f"Connecting to database...")
conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = False
cur = conn.cursor()


def run(sql, label=None):
    try:
        cur.execute(sql)
        tag = label or sql.strip()[:60]
        print(f"  OK: {tag}")
        return True
    except Exception as e:
        tag = label or sql.strip()[:60]
        print(f"  FAIL: {tag}")
        print(f"        {str(e)[:150]}")
        conn.rollback()
        return False


# ===================== SCHEMA =====================
print("\n=== Creating tables ===\n")

run("""
CREATE TABLE IF NOT EXISTS roles (
    role_id         SERIAL PRIMARY KEY,
    role_name       VARCHAR(50)  NOT NULL UNIQUE,
    description     VARCHAR(255),
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
)""", "CREATE roles")

run("""
CREATE TABLE IF NOT EXISTS users (
    user_id         SERIAL PRIMARY KEY,
    username        VARCHAR(100) NOT NULL UNIQUE,
    email           VARCHAR(255) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    full_name       VARCHAR(255),
    role_id         INTEGER REFERENCES roles(role_id),
    is_active       BOOLEAN DEFAULT TRUE,
    last_login      TIMESTAMP,
    refresh_token   VARCHAR(500),
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
)""", "CREATE users")

run("""
CREATE TABLE IF NOT EXISTS role_permissions (
    perm_id         SERIAL PRIMARY KEY,
    role_id         INTEGER REFERENCES roles(role_id),
    module          VARCHAR(100) NOT NULL,
    can_view        BOOLEAN DEFAULT FALSE,
    can_create      BOOLEAN DEFAULT FALSE,
    can_edit        BOOLEAN DEFAULT FALSE,
    can_delete      BOOLEAN DEFAULT FALSE,
    can_export      BOOLEAN DEFAULT FALSE,
    can_approve     BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP DEFAULT NOW()
)""", "CREATE role_permissions")

run("""
CREATE TABLE IF NOT EXISTS user_column_prefs (
    pref_id         SERIAL PRIMARY KEY,
    user_id         INTEGER REFERENCES users(user_id),
    module_key      VARCHAR(100) NOT NULL,
    column_config   JSONB,
    updated_at      TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, module_key)
)""", "CREATE user_column_prefs")

run("""
CREATE TABLE IF NOT EXISTS token_blacklist (
    id              SERIAL PRIMARY KEY,
    token_jti       VARCHAR(255) NOT NULL UNIQUE,
    expires_at      TIMESTAMP NOT NULL,
    created_at      TIMESTAMP DEFAULT NOW()
)""", "CREATE token_blacklist")

run("""
CREATE TABLE IF NOT EXISTS organization_groups (
    group_id        SERIAL PRIMARY KEY,
    group_code      VARCHAR(50)  NOT NULL UNIQUE,
    group_name      VARCHAR(255) NOT NULL,
    group_type      VARCHAR(100),
    description     VARCHAR(500),
    is_active       BOOLEAN DEFAULT TRUE,
    created_by      INTEGER,
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
)""", "CREATE organization_groups")

run("""
CREATE TABLE IF NOT EXISTS organizations (
    org_id              SERIAL PRIMARY KEY,
    org_code            VARCHAR(50)  NOT NULL UNIQUE,
    org_name            VARCHAR(255) NOT NULL,
    org_short_name      VARCHAR(100),
    group_id            INTEGER REFERENCES organization_groups(group_id),
    org_type            VARCHAR(100),
    is_customer         BOOLEAN DEFAULT FALSE,
    is_vendor           BOOLEAN DEFAULT FALSE,
    is_agent            BOOLEAN DEFAULT FALSE,
    is_carrier          BOOLEAN DEFAULT FALSE,
    address_line1       VARCHAR(500),
    address_line2       VARCHAR(500),
    city                VARCHAR(100),
    state               VARCHAR(100),
    country             VARCHAR(100),
    postal_code         VARCHAR(20),
    phone               VARCHAR(50),
    email               VARCHAR(255),
    website             VARCHAR(255),
    tax_id              VARCHAR(100),
    credit_limit        NUMERIC(18,2),
    credit_days         INTEGER,
    currency            VARCHAR(10) DEFAULT 'USD',
    approval_status     VARCHAR(20) DEFAULT 'PENDING',
    approval_date       TIMESTAMP,
    approved_by         INTEGER,
    is_active           BOOLEAN DEFAULT TRUE,
    created_by          INTEGER,
    created_at          TIMESTAMP DEFAULT NOW(),
    updated_at          TIMESTAMP DEFAULT NOW()
)""", "CREATE organizations")

run("""
CREATE TABLE IF NOT EXISTS airlines (
    airline_id      SERIAL PRIMARY KEY,
    airline_code    VARCHAR(20)  NOT NULL UNIQUE,
    iata_code       VARCHAR(10),
    icao_code       VARCHAR(10),
    airline_name    VARCHAR(255) NOT NULL,
    country         VARCHAR(100),
    headquarters    VARCHAR(255),
    phone           VARCHAR(50),
    email           VARCHAR(255),
    alliance        VARCHAR(100),
    is_active       BOOLEAN DEFAULT TRUE,
    created_by      INTEGER,
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
)""", "CREATE airlines")

run("""
CREATE TABLE IF NOT EXISTS shipping_lines (
    line_id         SERIAL PRIMARY KEY,
    line_code       VARCHAR(50)  NOT NULL UNIQUE,
    scac_code       VARCHAR(10),
    line_name       VARCHAR(255) NOT NULL,
    country         VARCHAR(100),
    headquarters    VARCHAR(255),
    phone           VARCHAR(50),
    email           VARCHAR(255),
    website         VARCHAR(255),
    is_active       BOOLEAN DEFAULT TRUE,
    created_by      INTEGER,
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
)""", "CREATE shipping_lines")

run("""
CREATE TABLE IF NOT EXISTS accounts (
    account_id      SERIAL PRIMARY KEY,
    account_code    VARCHAR(50)  NOT NULL UNIQUE,
    account_name    VARCHAR(255) NOT NULL,
    account_type    VARCHAR(50)  NOT NULL,
    account_subtype VARCHAR(100),
    parent_account_id INTEGER REFERENCES accounts(account_id),
    description     VARCHAR(500),
    is_control      BOOLEAN DEFAULT FALSE,
    opening_balance NUMERIC(18,2) DEFAULT 0,
    currency        VARCHAR(10) DEFAULT 'USD',
    is_active       BOOLEAN DEFAULT TRUE,
    created_by      INTEGER,
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
)""", "CREATE accounts")

run("""
CREATE TABLE IF NOT EXISTS charge_master (
    charge_id       SERIAL PRIMARY KEY,
    charge_code     VARCHAR(50)  NOT NULL UNIQUE,
    charge_name     VARCHAR(255) NOT NULL,
    charge_type     VARCHAR(100),
    charge_category VARCHAR(100),
    applicable_for  VARCHAR(50),
    gl_account_id   INTEGER REFERENCES accounts(account_id),
    tax_code        VARCHAR(50),
    is_taxable      BOOLEAN DEFAULT FALSE,
    unit_type       VARCHAR(50),
    is_active       BOOLEAN DEFAULT TRUE,
    created_by      INTEGER,
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
)""", "CREATE charge_master")

run("""
CREATE TABLE IF NOT EXISTS default_charges (
    default_id      SERIAL PRIMARY KEY,
    charge_id       INTEGER REFERENCES charge_master(charge_id),
    job_type        VARCHAR(50),
    transport_mode  VARCHAR(50),
    amount          NUMERIC(18,2),
    currency        VARCHAR(10) DEFAULT 'USD',
    is_active       BOOLEAN DEFAULT TRUE,
    created_by      INTEGER,
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
)""", "CREATE default_charges")

run("""
CREATE TABLE IF NOT EXISTS business_dimensions (
    dim_id          SERIAL PRIMARY KEY,
    dim_code        VARCHAR(50)  NOT NULL UNIQUE,
    dim_name        VARCHAR(255) NOT NULL,
    dim_type        VARCHAR(100),
    parent_dim_id   INTEGER REFERENCES business_dimensions(dim_id),
    is_active       BOOLEAN DEFAULT TRUE,
    created_by      INTEGER,
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
)""", "CREATE business_dimensions")

run("""
CREATE TABLE IF NOT EXISTS commodities (
    commodity_id    SERIAL PRIMARY KEY,
    commodity_code  VARCHAR(50)  NOT NULL UNIQUE,
    commodity_name  VARCHAR(255) NOT NULL,
    hs_code         VARCHAR(20),
    commodity_group VARCHAR(100),
    is_dangerous    BOOLEAN DEFAULT FALSE,
    dangerous_class VARCHAR(50),
    un_number       VARCHAR(20),
    description     VARCHAR(500),
    is_active       BOOLEAN DEFAULT TRUE,
    created_by      INTEGER,
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
)""", "CREATE commodities")

run("""
CREATE TABLE IF NOT EXISTS system_settings (
    setting_id      SERIAL PRIMARY KEY,
    setting_key     VARCHAR(255) NOT NULL UNIQUE,
    setting_value   JSONB,
    setting_group   VARCHAR(100),
    data_type       VARCHAR(50),
    description     VARCHAR(500),
    is_editable     BOOLEAN DEFAULT TRUE,
    updated_by      INTEGER,
    updated_at      TIMESTAMP DEFAULT NOW()
)""", "CREATE system_settings")

run("""
CREATE TABLE IF NOT EXISTS vendor_contracts (
    contract_id     SERIAL PRIMARY KEY,
    contract_no     VARCHAR(100) NOT NULL UNIQUE,
    vendor_id       INTEGER REFERENCES organizations(org_id),
    contract_type   VARCHAR(100),
    transport_mode  VARCHAR(50),
    start_date      DATE,
    end_date        DATE,
    currency        VARCHAR(10) DEFAULT 'USD',
    remarks         VARCHAR(1000),
    status          VARCHAR(50) DEFAULT 'DRAFT',
    created_by      INTEGER,
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
)""", "CREATE vendor_contracts")

run("""
CREATE TABLE IF NOT EXISTS vendor_contract_rates (
    rate_id         SERIAL PRIMARY KEY,
    contract_id     INTEGER REFERENCES vendor_contracts(contract_id),
    charge_id       INTEGER REFERENCES charge_master(charge_id),
    origin          VARCHAR(100),
    destination     VARCHAR(100),
    rate            NUMERIC(18,4),
    unit            VARCHAR(50),
    min_charge      NUMERIC(18,2),
    valid_from      DATE,
    valid_to        DATE,
    created_at      TIMESTAMP DEFAULT NOW()
)""", "CREATE vendor_contract_rates")

run("""
CREATE TABLE IF NOT EXISTS custom_clearing_setup (
    setup_id            SERIAL PRIMARY KEY,
    clearing_type       VARCHAR(50) NOT NULL,
    port_code           VARCHAR(50),
    port_name           VARCHAR(255),
    customs_authority   VARCHAR(255),
    broker_org_id       INTEGER REFERENCES organizations(org_id),
    procedures          JSONB,
    required_docs       JSONB,
    is_active           BOOLEAN DEFAULT TRUE,
    created_by          INTEGER,
    created_at          TIMESTAMP DEFAULT NOW(),
    updated_at          TIMESTAMP DEFAULT NOW()
)""", "CREATE custom_clearing_setup")

run("""
CREATE TABLE IF NOT EXISTS import_jobs (
    job_id          SERIAL PRIMARY KEY,
    job_no          VARCHAR(100) NOT NULL UNIQUE,
    job_date        DATE NOT NULL,
    transport_mode  VARCHAR(50),
    shipper_id      INTEGER,
    consignee_id    INTEGER,
    carrier_id      INTEGER,
    carrier_type    VARCHAR(20),
    bl_no           VARCHAR(100),
    flight_no       VARCHAR(50),
    vessel_name     VARCHAR(255),
    voyage_no       VARCHAR(50),
    pol             VARCHAR(100),
    pod             VARCHAR(100),
    eta             DATE,
    ata             DATE,
    commodity_id    INTEGER,
    gross_weight    NUMERIC(18,3),
    chargeable_weight NUMERIC(18,3),
    volume_cbm      NUMERIC(18,3),
    packages        INTEGER,
    package_type    VARCHAR(50),
    incoterms       VARCHAR(20),
    freight_currency VARCHAR(10),
    freight_amount  NUMERIC(18,2),
    status          VARCHAR(50) DEFAULT 'OPEN',
    remarks         VARCHAR(1000),
    created_by      INTEGER,
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
)""", "CREATE import_jobs")

run("""
CREATE TABLE IF NOT EXISTS job_charges (
    line_id         SERIAL PRIMARY KEY,
    job_id          INTEGER REFERENCES import_jobs(job_id),
    charge_id       INTEGER,
    charge_name     VARCHAR(255),
    quantity        NUMERIC(18,3) DEFAULT 1,
    unit_type       VARCHAR(50),
    rate            NUMERIC(18,4),
    currency        VARCHAR(10),
    amount          NUMERIC(18,2),
    tax_amount      NUMERIC(18,2) DEFAULT 0,
    total_amount    NUMERIC(18,2),
    vendor_id       INTEGER,
    created_at      TIMESTAMP DEFAULT NOW()
)""", "CREATE job_charges")

run("""
CREATE TABLE IF NOT EXISTS bank_payments (
    payment_id      SERIAL PRIMARY KEY,
    payment_no      VARCHAR(100) NOT NULL UNIQUE,
    payment_date    DATE NOT NULL,
    bank_account_id INTEGER,
    bank_name       VARCHAR(255),
    payee_id        INTEGER,
    payee_name      VARCHAR(255),
    amount          NUMERIC(18,2) NOT NULL,
    currency        VARCHAR(10) DEFAULT 'USD',
    exchange_rate   NUMERIC(18,6) DEFAULT 1,
    base_amount     NUMERIC(18,2),
    payment_method  VARCHAR(50),
    reference_no    VARCHAR(100),
    narration       VARCHAR(1000),
    status          VARCHAR(50) DEFAULT 'DRAFT',
    created_by      INTEGER,
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
)""", "CREATE bank_payments")

run("""
CREATE TABLE IF NOT EXISTS payment_allocations (
    alloc_id        SERIAL PRIMARY KEY,
    payment_id      INTEGER REFERENCES bank_payments(payment_id),
    job_id          INTEGER REFERENCES import_jobs(job_id),
    invoice_ref     VARCHAR(100),
    amount          NUMERIC(18,2),
    created_at      TIMESTAMP DEFAULT NOW()
)""", "CREATE payment_allocations")

run("""
CREATE TABLE IF NOT EXISTS bank_receipts (
    receipt_id      SERIAL PRIMARY KEY,
    receipt_no      VARCHAR(100) NOT NULL UNIQUE,
    receipt_date    DATE NOT NULL,
    bank_account_id INTEGER,
    bank_name       VARCHAR(255),
    payer_id        INTEGER,
    payer_name      VARCHAR(255),
    amount          NUMERIC(18,2) NOT NULL,
    currency        VARCHAR(10) DEFAULT 'USD',
    exchange_rate   NUMERIC(18,6) DEFAULT 1,
    base_amount     NUMERIC(18,2),
    receipt_method  VARCHAR(50),
    reference_no    VARCHAR(100),
    narration       VARCHAR(1000),
    status          VARCHAR(50) DEFAULT 'DRAFT',
    created_by      INTEGER,
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
)""", "CREATE bank_receipts")

run("""
CREATE TABLE IF NOT EXISTS journal_entries (
    entry_id        SERIAL PRIMARY KEY,
    entry_no        VARCHAR(100) NOT NULL UNIQUE,
    entry_date      DATE NOT NULL,
    entry_type      VARCHAR(50),
    description     VARCHAR(500),
    total_debit     NUMERIC(18,2),
    total_credit    NUMERIC(18,2),
    reference_type  VARCHAR(50),
    reference_id    INTEGER,
    status          VARCHAR(50) DEFAULT 'DRAFT',
    reversed_by     INTEGER,
    created_by      INTEGER,
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
)""", "CREATE journal_entries")

run("""
CREATE TABLE IF NOT EXISTS journal_lines (
    line_id         SERIAL PRIMARY KEY,
    entry_id        INTEGER REFERENCES journal_entries(entry_id),
    line_no         INTEGER,
    account_id      INTEGER,
    account_code    VARCHAR(50),
    account_name    VARCHAR(255),
    debit_amount    NUMERIC(18,2) DEFAULT 0,
    credit_amount   NUMERIC(18,2) DEFAULT 0,
    currency        VARCHAR(10) DEFAULT 'USD',
    exchange_rate   NUMERIC(18,6) DEFAULT 1,
    dim_id          INTEGER,
    narration       VARCHAR(500),
    created_at      TIMESTAMP DEFAULT NOW()
)""", "CREATE journal_lines")

run("""
CREATE TABLE IF NOT EXISTS general_debit_notes (
    dn_id           SERIAL PRIMARY KEY,
    dn_no           VARCHAR(100) NOT NULL UNIQUE,
    dn_date         DATE NOT NULL,
    party_id        INTEGER,
    party_name      VARCHAR(255),
    amount          NUMERIC(18,2) NOT NULL,
    currency        VARCHAR(10) DEFAULT 'USD',
    reason          VARCHAR(500),
    job_id          INTEGER REFERENCES import_jobs(job_id),
    status          VARCHAR(50) DEFAULT 'DRAFT',
    created_by      INTEGER,
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
)""", "CREATE general_debit_notes")

run("""
CREATE TABLE IF NOT EXISTS purchase_bills (
    bill_id         SERIAL PRIMARY KEY,
    bill_no         VARCHAR(100) NOT NULL UNIQUE,
    bill_date       DATE NOT NULL,
    vendor_id       INTEGER,
    vendor_name     VARCHAR(255),
    vendor_invoice_no VARCHAR(100),
    vendor_inv_date DATE,
    amount          NUMERIC(18,2),
    tax_amount      NUMERIC(18,2) DEFAULT 0,
    total_amount    NUMERIC(18,2),
    currency        VARCHAR(10) DEFAULT 'USD',
    due_date        DATE,
    job_id          INTEGER REFERENCES import_jobs(job_id),
    status          VARCHAR(50) DEFAULT 'DRAFT',
    remarks         VARCHAR(1000),
    created_by      INTEGER,
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
)""", "CREATE purchase_bills")

run("""
CREATE TABLE IF NOT EXISTS purchase_bill_lines (
    line_id         SERIAL PRIMARY KEY,
    bill_id         INTEGER REFERENCES purchase_bills(bill_id),
    charge_id       INTEGER,
    charge_name     VARCHAR(255),
    quantity        NUMERIC(18,3) DEFAULT 1,
    unit_rate       NUMERIC(18,4),
    amount          NUMERIC(18,2),
    tax_amount      NUMERIC(18,2) DEFAULT 0,
    gl_account_id   INTEGER,
    created_at      TIMESTAMP DEFAULT NOW()
)""", "CREATE purchase_bill_lines")

run("""
CREATE TABLE IF NOT EXISTS customs_export (
    export_id       SERIAL PRIMARY KEY,
    export_no       VARCHAR(100) NOT NULL UNIQUE,
    export_date     DATE NOT NULL,
    exporter_id     INTEGER,
    exporter_name   VARCHAR(255),
    consignee_id    INTEGER,
    consignee_name  VARCHAR(255),
    commodity_id    INTEGER,
    commodity_desc  VARCHAR(500),
    hs_code         VARCHAR(20),
    country_of_origin VARCHAR(100),
    destination_country VARCHAR(100),
    transport_mode  VARCHAR(50),
    incoterms       VARCHAR(20),
    total_value     NUMERIC(18,2),
    currency        VARCHAR(10) DEFAULT 'USD',
    gross_weight    NUMERIC(18,3),
    net_weight      NUMERIC(18,3),
    packages        INTEGER,
    customs_entry_no VARCHAR(100),
    customs_entry_date DATE,
    status          VARCHAR(50) DEFAULT 'DRAFT',
    remarks         VARCHAR(1000),
    created_by      INTEGER,
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
)""", "CREATE customs_export")

conn.commit()

# ===================== SEED DATA =====================
print("\n=== Seeding data ===\n")

# Generate bcrypt hash for Admin@123
admin_hash = bcrypt.hashpw(b"Admin@123", bcrypt.gensalt(rounds=12)).decode("utf-8")

# Check if roles already exist
cur.execute("SELECT COUNT(*) FROM roles")
role_count = cur.fetchone()[0]

if role_count == 0:
    run("""
    INSERT INTO roles (role_name, description, is_active) VALUES
    ('ADMIN', 'System Administrator', TRUE),
    ('MANAGER', 'Operations Manager', TRUE),
    ('OPERATOR', 'Data Entry Operator', TRUE),
    ('VIEWER', 'Read-Only Viewer', TRUE)
    """, "INSERT roles")

    cur.execute("""
    INSERT INTO users (username, email, password_hash, full_name, role_id, is_active) VALUES
    (%s, %s, %s, %s, 1, TRUE),
    (%s, %s, %s, %s, 2, TRUE),
    (%s, %s, %s, %s, 3, TRUE)
    """, ('admin', 'admin@cargozen.com', admin_hash, 'System Administrator',
          'manager', 'manager@cargozen.com', admin_hash, 'Operations Manager',
          'operator', 'operator@cargozen.com', admin_hash, 'Data Operator'))
    print("  OK: INSERT users")

    run("""
    INSERT INTO role_permissions (role_id, module, can_view, can_create, can_edit, can_delete) VALUES
    (1, 'DASHBOARD', TRUE, TRUE, TRUE, TRUE),
    (1, 'ADMINISTRATION', TRUE, TRUE, TRUE, TRUE),
    (1, 'TRANSACTIONS', TRUE, TRUE, TRUE, TRUE),
    (1, 'REPORTS', TRUE, TRUE, TRUE, TRUE),
    (2, 'DASHBOARD', TRUE, TRUE, TRUE, FALSE),
    (2, 'ADMINISTRATION', TRUE, TRUE, TRUE, FALSE),
    (2, 'TRANSACTIONS', TRUE, TRUE, TRUE, FALSE),
    (2, 'REPORTS', TRUE, TRUE, FALSE, FALSE),
    (3, 'DASHBOARD', TRUE, FALSE, FALSE, FALSE),
    (3, 'TRANSACTIONS', TRUE, TRUE, TRUE, FALSE),
    (3, 'REPORTS', TRUE, FALSE, FALSE, FALSE),
    (4, 'DASHBOARD', TRUE, FALSE, FALSE, FALSE),
    (4, 'REPORTS', TRUE, FALSE, FALSE, FALSE)
    """, "INSERT role_permissions")
else:
    print("  [SKIP] Roles already seeded")

# Check if org groups already exist
cur.execute("SELECT COUNT(*) FROM organization_groups")
if cur.fetchone()[0] == 0:
    run("""
    INSERT INTO organization_groups (group_code, group_name, group_type, is_active) VALUES
    ('LOCAL', 'Local Companies', 'DOMESTIC', TRUE),
    ('INTL', 'International Companies', 'INTERNATIONAL', TRUE),
    ('AGENT', 'Freight Agents', 'AGENT', TRUE),
    ('BANK', 'Banking Partners', 'FINANCIAL', TRUE),
    ('GOVT', 'Government Entities', 'GOVERNMENT', TRUE)
    """, "INSERT organization_groups")

    run("""
    INSERT INTO organizations (org_code, org_name, org_short_name, group_id, is_customer, is_vendor, country, approval_status) VALUES
    ('ORG001', 'Global Traders Ltd', 'GTL', 1, TRUE, FALSE, 'UAE', 'APPROVED'),
    ('ORG002', 'Fast Cargo Services', 'FCS', 3, FALSE, TRUE, 'UAE', 'APPROVED'),
    ('ORG003', 'Emirates Shipping Co', 'ESC', 3, FALSE, TRUE, 'UAE', 'APPROVED'),
    ('ORG004', 'Dubai Customs Broker LLC', 'DCB', 3, FALSE, TRUE, 'UAE', 'APPROVED'),
    ('ORG005', 'Al Noor Logistics', 'ANL', 1, TRUE, FALSE, 'UAE', 'PENDING')
    """, "INSERT organizations")

    run("""
    INSERT INTO airlines (airline_code, iata_code, airline_name, country, is_active) VALUES
    ('EK', 'EK', 'Emirates', 'UAE', TRUE), ('EY', 'EY', 'Etihad Airways', 'UAE', TRUE),
    ('SQ', 'SQ', 'Singapore Airlines', 'Singapore', TRUE), ('QR', 'QR', 'Qatar Airways', 'Qatar', TRUE),
    ('LH', 'LH', 'Lufthansa', 'Germany', TRUE), ('BA', 'BA', 'British Airways', 'UK', TRUE),
    ('AA', 'AA', 'American Airlines', 'USA', TRUE), ('FX', 'FX', 'FedEx', 'USA', TRUE),
    ('5X', '5X', 'UPS Airlines', 'USA', TRUE), ('CV', 'CV', 'Cargolux', 'Luxembourg', TRUE)
    """, "INSERT airlines")

    run("""
    INSERT INTO shipping_lines (line_code, scac_code, line_name, country, is_active) VALUES
    ('MSC', 'MSCU', 'Mediterranean Shipping Company', 'Switzerland', TRUE),
    ('MAERSK', 'MAEU', 'Maersk Line', 'Denmark', TRUE),
    ('CMA', 'CMDU', 'CMA CGM', 'France', TRUE),
    ('COSCO', 'COSU', 'COSCO Shipping Lines', 'China', TRUE),
    ('EVERGREEN', 'EGLV', 'Evergreen Line', 'Taiwan', TRUE),
    ('HAPAG', 'HLCU', 'Hapag-Lloyd', 'Germany', TRUE),
    ('ONE', 'ONEY', 'Ocean Network Express', 'Japan', TRUE),
    ('EMC', 'EMCU', 'Emirates Shipping Line', 'UAE', TRUE)
    """, "INSERT shipping_lines")

    run("""
    INSERT INTO accounts (account_code, account_name, account_type, is_active) VALUES
    ('1000', 'Current Assets', 'ASSET', TRUE), ('1100', 'Cash and Bank', 'ASSET', TRUE),
    ('1101', 'Petty Cash', 'ASSET', TRUE), ('1102', 'Bank - Emirates NBD', 'ASSET', TRUE),
    ('1103', 'Bank - Abu Dhabi Commercial', 'ASSET', TRUE),
    ('1200', 'Accounts Receivable', 'ASSET', TRUE), ('1300', 'Prepaid Expenses', 'ASSET', TRUE),
    ('2000', 'Current Liabilities', 'LIABILITY', TRUE), ('2100', 'Accounts Payable', 'LIABILITY', TRUE),
    ('2200', 'Tax Payable', 'LIABILITY', TRUE), ('3000', 'Equity', 'EQUITY', TRUE),
    ('3100', 'Share Capital', 'EQUITY', TRUE), ('3200', 'Retained Earnings', 'EQUITY', TRUE),
    ('4000', 'Revenue', 'INCOME', TRUE), ('4100', 'Freight Income', 'INCOME', TRUE),
    ('4200', 'Customs Clearance Income', 'INCOME', TRUE), ('4300', 'Handling Income', 'INCOME', TRUE),
    ('5000', 'Operating Expenses', 'EXPENSE', TRUE), ('5100', 'Freight Cost', 'EXPENSE', TRUE),
    ('5200', 'Customs Duty', 'EXPENSE', TRUE), ('5300', 'Port Charges', 'EXPENSE', TRUE),
    ('5400', 'Handling Charges', 'EXPENSE', TRUE), ('6000', 'General & Admin Expenses', 'EXPENSE', TRUE)
    """, "INSERT accounts")

    run("""
    INSERT INTO charge_master (charge_code, charge_name, charge_type, charge_category, applicable_for, is_active) VALUES
    ('OCF', 'Origin Charges', 'FREIGHT', 'ORIGIN', 'BOTH', TRUE),
    ('FCH', 'Freight Charges', 'FREIGHT', 'MAIN', 'BOTH', TRUE),
    ('DCH', 'Destination Charges', 'FREIGHT', 'DESTINATION', 'BOTH', TRUE),
    ('THC', 'Terminal Handling Charges', 'HANDLING', 'LOCAL', 'BOTH', TRUE),
    ('DOC', 'Documentation Fee', 'MISC', 'ADMIN', 'BOTH', TRUE),
    ('CUS', 'Customs Clearance Fee', 'CUSTOMS', 'CUSTOMS', 'IMPORT', TRUE),
    ('DUTY', 'Import Duty', 'CUSTOMS', 'DUTY', 'IMPORT', TRUE),
    ('VAT', 'Value Added Tax', 'TAX', 'TAX', 'BOTH', TRUE),
    ('ISF', 'ISF Filing', 'CUSTOMS', 'CUSTOMS', 'IMPORT', TRUE),
    ('BRK', 'Customs Brokerage', 'CUSTOMS', 'CUSTOMS', 'BOTH', TRUE),
    ('DEL', 'Delivery Charges', 'LOCAL', 'LOCAL', 'IMPORT', TRUE),
    ('STG', 'Storage/Demurrage', 'LOCAL', 'LOCAL', 'BOTH', TRUE)
    """, "INSERT charge_master")

    run("""
    INSERT INTO business_dimensions (dim_code, dim_name, dim_type, is_active) VALUES
    ('HQ', 'Head Office', 'BRANCH', TRUE), ('DXB', 'Dubai Branch', 'BRANCH', TRUE),
    ('AUH', 'Abu Dhabi Branch', 'BRANCH', TRUE), ('AIR', 'Air Freight Division', 'DEPARTMENT', TRUE),
    ('SEA', 'Sea Freight Division', 'DEPARTMENT', TRUE), ('CUS', 'Customs Division', 'DEPARTMENT', TRUE),
    ('OPS', 'Operations', 'COST_CENTER', TRUE), ('FIN', 'Finance', 'COST_CENTER', TRUE)
    """, "INSERT business_dimensions")

    run("""
    INSERT INTO commodities (commodity_code, commodity_name, hs_code, commodity_group, is_dangerous, is_active) VALUES
    ('ELEC', 'Electronics & Gadgets', '8471', 'TECHNOLOGY', FALSE, TRUE),
    ('TXTL', 'Textiles & Garments', '5208', 'TEXTILES', FALSE, TRUE),
    ('FOOD', 'Food & Beverages', '2202', 'FOOD', FALSE, TRUE),
    ('MACH', 'Machinery & Equipment', '8431', 'MACHINERY', FALSE, TRUE),
    ('AUTO', 'Automotive Parts', '8708', 'AUTOMOTIVE', FALSE, TRUE),
    ('CHEM', 'Chemicals', '2901', 'CHEMICALS', TRUE, TRUE),
    ('PHRM', 'Pharmaceuticals', '3004', 'PHARMA', FALSE, TRUE),
    ('FURN', 'Furniture & Fixtures', '9403', 'FURNITURE', FALSE, TRUE),
    ('BOOK', 'Books & Publications', '4901', 'MEDIA', FALSE, TRUE),
    ('JEWL', 'Jewelry & Precious Metals', '7113', 'LUXURY', FALSE, TRUE)
    """, "INSERT commodities")

    run("""
    INSERT INTO system_settings (setting_key, setting_value, setting_group, data_type, description) VALUES
    ('company_name', '"CargoZen Logistics LLC"'::jsonb, 'GENERAL', 'STRING', 'Company name'),
    ('base_currency', '"USD"'::jsonb, 'FINANCE', 'STRING', 'Base currency code'),
    ('date_format', '"DD/MM/YYYY"'::jsonb, 'GENERAL', 'STRING', 'Date display format'),
    ('fiscal_year_start', '"01"'::jsonb, 'FINANCE', 'STRING', 'Fiscal year start month'),
    ('auto_approve_orgs', 'false'::jsonb, 'ADMIN', 'BOOLEAN', 'Auto-approve new organizations'),
    ('session_timeout_mins', '60'::jsonb, 'SECURITY', 'NUMBER', 'Session timeout in minutes'),
    ('max_login_attempts', '5'::jsonb, 'SECURITY', 'NUMBER', 'Maximum failed login attempts'),
    ('job_no_prefix', '"IMP-"'::jsonb, 'TRANSACTIONS', 'STRING', 'Import job number prefix'),
    ('payment_no_prefix', '"PAY-"'::jsonb, 'TRANSACTIONS', 'STRING', 'Payment number prefix'),
    ('receipt_no_prefix', '"RCP-"'::jsonb, 'TRANSACTIONS', 'STRING', 'Receipt number prefix')
    """, "INSERT system_settings")

    run("""
    INSERT INTO default_charges (charge_id, job_type, transport_mode, amount, currency, is_active) VALUES
    (1, 'IMPORT', 'SEA', 250.00, 'USD', TRUE), (2, 'IMPORT', 'SEA', 1800.00, 'USD', TRUE),
    (3, 'IMPORT', 'SEA', 200.00, 'USD', TRUE), (4, 'IMPORT', 'SEA', 350.00, 'USD', TRUE),
    (5, 'IMPORT', 'SEA', 75.00, 'USD', TRUE), (6, 'IMPORT', 'SEA', 450.00, 'USD', TRUE),
    (2, 'IMPORT', 'AIR', 2200.00, 'USD', TRUE), (4, 'IMPORT', 'AIR', 120.00, 'USD', TRUE),
    (5, 'IMPORT', 'AIR', 75.00, 'USD', TRUE), (1, 'EXPORT', 'SEA', 200.00, 'USD', TRUE),
    (2, 'EXPORT', 'SEA', 1500.00, 'USD', TRUE), (5, 'EXPORT', 'SEA', 75.00, 'USD', TRUE)
    """, "INSERT default_charges")

    run("""
    INSERT INTO custom_clearing_setup (clearing_type, port_code, port_name, customs_authority, is_active) VALUES
    ('IMPORT', 'AEJEA', 'Jebel Ali, Dubai', 'Dubai Customs', TRUE),
    ('IMPORT', 'AEDXB', 'Port Rashid, Dubai', 'Dubai Customs', TRUE),
    ('IMPORT', 'AEAUH', 'Khalifa Port, Abu Dhabi', 'Abu Dhabi Customs', TRUE),
    ('IMPORT', 'AESHJ', 'Port Khalid, Sharjah', 'Sharjah Customs', TRUE),
    ('EXPORT', 'AEJEA', 'Jebel Ali, Dubai', 'Dubai Customs', TRUE),
    ('EXPORT', 'AEAUH', 'Khalifa Port, Abu Dhabi', 'Abu Dhabi Customs', TRUE),
    ('IMPORT', 'AEDWC', 'Dubai Airport Cargo', 'Dubai Customs', TRUE),
    ('EXPORT', 'AEDWC', 'Dubai Airport Cargo', 'Dubai Customs', TRUE)
    """, "INSERT custom_clearing_setup")
else:
    print("  [SKIP] Seed data already exists")

conn.commit()

# ===================== VERIFY =====================
print("\n=== Verification ===\n")

cur.execute("SELECT COUNT(*) FROM roles")
print(f"  Roles: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM users")
print(f"  Users: {cur.fetchone()[0]}")

cur.execute("SELECT username, full_name, role_id FROM users")
for row in cur.fetchall():
    print(f"    - {row[0]} ({row[1]}) role_id={row[2]}")

cur.execute("SELECT COUNT(*) FROM organizations")
print(f"  Organizations: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM airlines")
print(f"  Airlines: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM shipping_lines")
print(f"  Shipping Lines: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM charge_master")
print(f"  Charge Master: {cur.fetchone()[0]}")

cur.close()
conn.close()

print("\n=== DONE! Database is ready. ===")
print("Start the backend: cd backend && python -m uvicorn app.main:app --reload")
print("Login: admin / Admin@123\n")
