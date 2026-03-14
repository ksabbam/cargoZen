-- =============================================================
-- CargoZen Seed Data
-- =============================================================
USE DATABASE CARGOZEN_DB;

-- AUTH Schema seed data
USE SCHEMA AUTH;

-- Roles
INSERT INTO ROLES (ROLE_NAME, DESCRIPTION, IS_ACTIVE) VALUES
('ADMIN', 'System Administrator', TRUE),
('MANAGER', 'Operations Manager', TRUE),
('OPERATOR', 'Data Entry Operator', TRUE),
('VIEWER', 'Read-Only Viewer', TRUE);

-- Users  (default password for all = Admin@123, bcrypt-hashed)
INSERT INTO USERS (USERNAME, EMAIL, PASSWORD_HASH, FULL_NAME, ROLE_ID, IS_ACTIVE) VALUES
('admin',    'admin@cargozen.com',    '$2b$12$m.y.1P6OCN0HzuydOdTaduJbETnH81zC/elrd1iQ2Lb2mDcQgzxmq', 'System Administrator', 1, TRUE),
('manager',  'manager@cargozen.com',  '$2b$12$m.y.1P6OCN0HzuydOdTaduJbETnH81zC/elrd1iQ2Lb2mDcQgzxmq', 'Operations Manager',   2, TRUE),
('operator', 'operator@cargozen.com', '$2b$12$m.y.1P6OCN0HzuydOdTaduJbETnH81zC/elrd1iQ2Lb2mDcQgzxmq', 'Data Operator',        3, TRUE);

-- Role Permissions
INSERT INTO ROLE_PERMISSIONS (ROLE_ID, MODULE, CAN_VIEW, CAN_CREATE, CAN_EDIT, CAN_DELETE) VALUES
(1, 'DASHBOARD',      TRUE, TRUE, TRUE, TRUE),
(1, 'ADMINISTRATION', TRUE, TRUE, TRUE, TRUE),
(1, 'TRANSACTIONS',   TRUE, TRUE, TRUE, TRUE),
(1, 'REPORTS',        TRUE, TRUE, TRUE, TRUE),
(2, 'DASHBOARD',      TRUE, TRUE, TRUE, FALSE),
(2, 'ADMINISTRATION', TRUE, TRUE, TRUE, FALSE),
(2, 'TRANSACTIONS',   TRUE, TRUE, TRUE, FALSE),
(2, 'REPORTS',        TRUE, TRUE, FALSE, FALSE),
(3, 'DASHBOARD',      TRUE, FALSE, FALSE, FALSE),
(3, 'TRANSACTIONS',   TRUE, TRUE,  TRUE,  FALSE),
(3, 'REPORTS',        TRUE, FALSE, FALSE, FALSE),
(4, 'DASHBOARD',      TRUE, FALSE, FALSE, FALSE),
(4, 'REPORTS',        TRUE, FALSE, FALSE, FALSE);

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

-- System Settings (VARIANT column requires INSERT..SELECT with PARSE_JSON)
INSERT INTO SYSTEM_SETTINGS (SETTING_KEY, SETTING_VALUE, SETTING_GROUP, DATA_TYPE, DESCRIPTION)
SELECT 'company_name', PARSE_JSON('"CargoZen Logistics LLC"'), 'GENERAL', 'STRING', 'Company name'
UNION ALL SELECT 'base_currency', PARSE_JSON('"USD"'), 'FINANCE', 'STRING', 'Base currency code'
UNION ALL SELECT 'date_format', PARSE_JSON('"DD/MM/YYYY"'), 'GENERAL', 'STRING', 'Date display format'
UNION ALL SELECT 'fiscal_year_start', PARSE_JSON('"01"'), 'FINANCE', 'STRING', 'Fiscal year start month (01-12)'
UNION ALL SELECT 'auto_approve_orgs', PARSE_JSON('false'), 'ADMIN', 'BOOLEAN', 'Auto-approve new organizations'
UNION ALL SELECT 'session_timeout_mins', PARSE_JSON('60'), 'SECURITY', 'NUMBER', 'Session timeout in minutes'
UNION ALL SELECT 'max_login_attempts', PARSE_JSON('5'), 'SECURITY', 'NUMBER', 'Maximum failed login attempts'
UNION ALL SELECT 'job_no_prefix', PARSE_JSON('"IMP-"'), 'TRANSACTIONS', 'STRING', 'Import job number prefix'
UNION ALL SELECT 'payment_no_prefix', PARSE_JSON('"PAY-"'), 'TRANSACTIONS', 'STRING', 'Payment number prefix'
UNION ALL SELECT 'receipt_no_prefix', PARSE_JSON('"RCP-"'), 'TRANSACTIONS', 'STRING', 'Receipt number prefix';

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
