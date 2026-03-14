-- =============================================================
-- CargoZen Seed Data
-- =============================================================
USE DATABASE CARGOZEN_DB;

-- AUTH Schema seed data
USE SCHEMA AUTH;

-- Insert default roles
INSERT INTO ROLES (ROLE_NAME, DESCRIPTION) VALUES
('SUPER_ADMIN', 'Full system access'),
('ADMIN', 'Administrative access'),
('MANAGER', 'Management level access'),
('OPERATOR', 'Day-to-day operations'),
('VIEWER', 'Read-only access');

-- Insert admin user (password: Admin@123 - bcrypt hashed)
-- NOTE: If login fails with 'Invalid credentials', call POST /api/auth/fix-admin-password
-- to regenerate the hash. The hash below may not match your bcrypt library version.
INSERT INTO USERS (USERNAME, EMAIL, PASSWORD_HASH, FULL_NAME, ROLE_ID) VALUES
('admin', 'admin@cargozen.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMUJqSBRIKJHF4QiR3YbXVJnUe', 'System Administrator', 1),
('operator1', 'operator@cargozen.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMUJqSBRIKJHF4QiR3YbXVJnUe', 'John Operator', 4);

-- Insert role permissions
INSERT INTO ROLE_PERMISSIONS (ROLE_ID, MODULE, CAN_VIEW, CAN_CREATE, CAN_EDIT, CAN_DELETE, CAN_EXPORT, CAN_APPROVE)
SELECT 1, MODULE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE
FROM (VALUES
    ('organizations'), ('org_groups'), ('airlines'), ('shipping_lines'),
    ('accounts'), ('charge_master'), ('default_charges'), ('business_dimensions'),
    ('commodities'), ('system_settings'), ('vendor_contracts'), ('custom_clearing'),
    ('import_jobs'), ('bank_payments'), ('bank_receipts'), ('journal_entries'),
    ('debit_notes'), ('purchase_bills'), ('customs_export'), ('reports')
) AS MODULES(MODULE);

-- ADMIN Schema seed data
USE SCHEMA ADMIN;

-- Organization Groups
INSERT INTO ORGANIZATION_GROUPS (GROUP_CODE, GROUP_NAME, GROUP_TYPE, IS_ACTIVE) VALUES
('LOCAL', 'Local Companies', 'DOMESTIC', TRUE),
('INTL', 'International Companies', 'INTERNATIONAL', TRUE),
('AGENT', 'Freight Agents', 'AGENT', TRUE),
('BANK', 'Banking Partners', 'FINANCIAL', TRUE),
('GOVT', 'Government Entities', 'GOVERNMENT', TRUE);

-- Organizations (sample)
INSERT INTO ORGANIZATIONS (ORG_CODE, ORG_NAME, ORG_SHORT_NAME, GROUP_ID, IS_CUSTOMER, IS_VENDOR, COUNTRY, APPROVAL_STATUS) VALUES
('ORG001', 'Global Traders Ltd', 'GTL', 1, TRUE, FALSE, 'UAE', 'APPROVED'),
('ORG002', 'Fast Cargo Services', 'FCS', 3, FALSE, TRUE, 'UAE', 'APPROVED'),
('ORG003', 'Emirates Shipping Co', 'ESC', 3, FALSE, TRUE, 'UAE', 'APPROVED'),
('ORG004', 'Dubai Customs Broker LLC', 'DCB', 3, FALSE, TRUE, 'UAE', 'APPROVED'),
('ORG005', 'Al Noor Logistics', 'ANL', 1, TRUE, FALSE, 'UAE', 'PENDING');

-- Airlines
INSERT INTO AIRLINES (AIRLINE_CODE, IATA_CODE, AIRLINE_NAME, COUNTRY, IS_ACTIVE) VALUES
('EK', 'EK', 'Emirates', 'UAE', TRUE),
('EY', 'EY', 'Etihad Airways', 'UAE', TRUE),
('SQ', 'SQ', 'Singapore Airlines', 'Singapore', TRUE),
('QR', 'QR', 'Qatar Airways', 'Qatar', TRUE),
('LH', 'LH', 'Lufthansa', 'Germany', TRUE),
('BA', 'BA', 'British Airways', 'UK', TRUE),
('AA', 'AA', 'American Airlines', 'USA', TRUE),
('FX', 'FX', 'FedEx', 'USA', TRUE),
('5X', '5X', 'UPS Airlines', 'USA', TRUE),
('CV', 'CV', 'Cargolux', 'Luxembourg', TRUE);

-- Shipping Lines
INSERT INTO SHIPPING_LINES (LINE_CODE, SCAC_CODE, LINE_NAME, COUNTRY, IS_ACTIVE) VALUES
('MSC', 'MSCU', 'Mediterranean Shipping Company', 'Switzerland', TRUE),
('MAERSK', 'MAEU', 'Maersk Line', 'Denmark', TRUE),
('CMA', 'CMDU', 'CMA CGM', 'France', TRUE),
('COSCO', 'COSU', 'COSCO Shipping Lines', 'China', TRUE),
('EVERGREEN', 'EGLV', 'Evergreen Line', 'Taiwan', TRUE),
('HAPAG', 'HLCU', 'Hapag-Lloyd', 'Germany', TRUE),
('ONE', 'ONEY', 'Ocean Network Express', 'Japan', TRUE),
('EMC', 'EMCU', 'Emirates Shipping Line', 'UAE', TRUE);

-- Chart of Accounts
INSERT INTO ACCOUNTS (ACCOUNT_CODE, ACCOUNT_NAME, ACCOUNT_TYPE, IS_ACTIVE) VALUES
('1000', 'Current Assets', 'ASSET', TRUE),
('1100', 'Cash and Bank', 'ASSET', TRUE),
('1101', 'Petty Cash', 'ASSET', TRUE),
('1102', 'Bank - Emirates NBD', 'ASSET', TRUE),
('1103', 'Bank - Abu Dhabi Commercial', 'ASSET', TRUE),
('1200', 'Accounts Receivable', 'ASSET', TRUE),
('1300', 'Prepaid Expenses', 'ASSET', TRUE),
('2000', 'Current Liabilities', 'LIABILITY', TRUE),
('2100', 'Accounts Payable', 'LIABILITY', TRUE),
('2200', 'Tax Payable', 'LIABILITY', TRUE),
('3000', 'Equity', 'EQUITY', TRUE),
('3100', 'Share Capital', 'EQUITY', TRUE),
('3200', 'Retained Earnings', 'EQUITY', TRUE),
('4000', 'Revenue', 'INCOME', TRUE),
('4100', 'Freight Income', 'INCOME', TRUE),
('4200', 'Customs Clearance Income', 'INCOME', TRUE),
('4300', 'Handling Income', 'INCOME', TRUE),
('5000', 'Operating Expenses', 'EXPENSE', TRUE),
('5100', 'Freight Cost', 'EXPENSE', TRUE),
('5200', 'Customs Duty', 'EXPENSE', TRUE),
('5300', 'Port Charges', 'EXPENSE', TRUE),
('5400', 'Handling Charges', 'EXPENSE', TRUE),
('6000', 'General & Admin Expenses', 'EXPENSE', TRUE);

-- Charge Master
INSERT INTO CHARGE_MASTER (CHARGE_CODE, CHARGE_NAME, CHARGE_TYPE, CHARGE_CATEGORY, APPLICABLE_FOR, IS_ACTIVE) VALUES
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
('STG', 'Storage/Demurrage', 'LOCAL', 'LOCAL', 'BOTH', TRUE);

-- Business Dimensions
INSERT INTO BUSINESS_DIMENSIONS (DIM_CODE, DIM_NAME, DIM_TYPE, IS_ACTIVE) VALUES
('HQ', 'Head Office', 'BRANCH', TRUE),
('DXB', 'Dubai Branch', 'BRANCH', TRUE),
('AUH', 'Abu Dhabi Branch', 'BRANCH', TRUE),
('AIR', 'Air Freight Division', 'DEPARTMENT', TRUE),
('SEA', 'Sea Freight Division', 'DEPARTMENT', TRUE),
('CUS', 'Customs Division', 'DEPARTMENT', TRUE),
('OPS', 'Operations', 'COST_CENTER', TRUE),
('FIN', 'Finance', 'COST_CENTER', TRUE);

-- Commodities
INSERT INTO COMMODITIES (COMMODITY_CODE, COMMODITY_NAME, HS_CODE, COMMODITY_GROUP, IS_DANGEROUS, IS_ACTIVE) VALUES
('ELEC', 'Electronics & Gadgets', '8471', 'TECHNOLOGY', FALSE, TRUE),
('TXTL', 'Textiles & Garments', '5208', 'TEXTILES', FALSE, TRUE),
('FOOD', 'Food & Beverages', '2202', 'FOOD', FALSE, TRUE),
('MACH', 'Machinery & Equipment', '8431', 'MACHINERY', FALSE, TRUE),
('AUTO', 'Automotive Parts', '8708', 'AUTOMOTIVE', FALSE, TRUE),
('CHEM', 'Chemicals', '2901', 'CHEMICALS', TRUE, TRUE),
('PHRM', 'Pharmaceuticals', '3004', 'PHARMA', FALSE, TRUE),
('FURN', 'Furniture & Fixtures', '9403', 'FURNITURE', FALSE, TRUE),
('BOOK', 'Books & Publications', '4901', 'MEDIA', FALSE, TRUE),
('JEWL', 'Jewelry & Precious Metals', '7113', 'LUXURY', FALSE, TRUE);

-- System Settings
INSERT INTO SYSTEM_SETTINGS (SETTING_KEY, SETTING_VALUE, SETTING_GROUP, DATA_TYPE, DESCRIPTION) VALUES
('company_name', '"CargoZen Logistics LLC"', 'GENERAL', 'STRING', 'Company name'),
('base_currency', '"USD"', 'FINANCE', 'STRING', 'Base currency code'),
('date_format', '"DD/MM/YYYY"', 'GENERAL', 'STRING', 'Date display format'),
('fiscal_year_start', '"01"', 'FINANCE', 'STRING', 'Fiscal year start month (01-12)'),
('auto_approve_orgs', 'false', 'ADMIN', 'BOOLEAN', 'Auto-approve new organizations'),
('session_timeout_mins', '60', 'SECURITY', 'NUMBER', 'Session timeout in minutes'),
('max_login_attempts', '5', 'SECURITY', 'NUMBER', 'Maximum failed login attempts'),
('job_no_prefix', '"IMP-"', 'TRANSACTIONS', 'STRING', 'Import job number prefix'),
('payment_no_prefix', '"PAY-"', 'TRANSACTIONS', 'STRING', 'Payment number prefix'),
('receipt_no_prefix', '"RCP-"', 'TRANSACTIONS', 'STRING', 'Receipt number prefix');

-- Default Charges (preset charge amounts per job type / mode)
INSERT INTO DEFAULT_CHARGES (CHARGE_ID, JOB_TYPE, TRANSPORT_MODE, AMOUNT, CURRENCY, IS_ACTIVE) VALUES
(1, 'IMPORT', 'SEA', 250.00, 'USD', TRUE),
(2, 'IMPORT', 'SEA', 1800.00, 'USD', TRUE),
(3, 'IMPORT', 'SEA', 200.00, 'USD', TRUE),
(4, 'IMPORT', 'SEA', 350.00, 'USD', TRUE),
(5, 'IMPORT', 'SEA', 75.00, 'USD', TRUE),
(6, 'IMPORT', 'SEA', 450.00, 'USD', TRUE),
(2, 'IMPORT', 'AIR', 2200.00, 'USD', TRUE),
(4, 'IMPORT', 'AIR', 120.00, 'USD', TRUE),
(5, 'IMPORT', 'AIR', 75.00, 'USD', TRUE),
(1, 'EXPORT', 'SEA', 200.00, 'USD', TRUE),
(2, 'EXPORT', 'SEA', 1500.00, 'USD', TRUE),
(5, 'EXPORT', 'SEA', 75.00, 'USD', TRUE);

-- Custom Clearing Setup (port/customs configurations)
INSERT INTO CUSTOM_CLEARING_SETUP (CLEARING_TYPE, PORT_CODE, PORT_NAME, CUSTOMS_AUTHORITY, IS_ACTIVE) VALUES
('IMPORT', 'AEJEA', 'Jebel Ali, Dubai', 'Dubai Customs', TRUE),
('IMPORT', 'AEDXB', 'Port Rashid, Dubai', 'Dubai Customs', TRUE),
('IMPORT', 'AEAUH', 'Khalifa Port, Abu Dhabi', 'Abu Dhabi Customs', TRUE),
('IMPORT', 'AESHJ', 'Port Khalid, Sharjah', 'Sharjah Customs', TRUE),
('EXPORT', 'AEJEA', 'Jebel Ali, Dubai', 'Dubai Customs', TRUE),
('EXPORT', 'AEAUH', 'Khalifa Port, Abu Dhabi', 'Abu Dhabi Customs', TRUE),
('IMPORT', 'AEDWC', 'Dubai Airport Cargo', 'Dubai Customs', TRUE),
('EXPORT', 'AEDWC', 'Dubai Airport Cargo', 'Dubai Customs', TRUE);
