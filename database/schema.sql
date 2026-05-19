-- SmartPOS Ghana Database Schema
-- Created by ashardrach

-- Business settings
CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY,
    business_name TEXT DEFAULT 'My Business',
    business_address TEXT DEFAULT '',
    business_phone TEXT DEFAULT '',
    business_email TEXT DEFAULT '',
    currency_symbol TEXT DEFAULT 'GHS',
    receipt_footer TEXT DEFAULT 'Thank you for your business!',
    tax_rate REAL DEFAULT 0.0,
    logo_path TEXT DEFAULT '',
    theme TEXT DEFAULT 'dark',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Product categories
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT DEFAULT '',
    created_at TEXT DEFAULT (datetime('now'))
);

-- Products / Inventory
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category_id INTEGER DEFAULT 1,
    barcode TEXT DEFAULT '',
    selling_price REAL NOT NULL DEFAULT 0.0,
    cost_price REAL DEFAULT 0.0,
    stock_quantity INTEGER DEFAULT 0,
    low_stock_threshold INTEGER DEFAULT 5,
    unit TEXT DEFAULT 'piece',
    description TEXT DEFAULT '',
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- Customers
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT DEFAULT '',
    email TEXT DEFAULT '',
    address TEXT DEFAULT '',
    outstanding_debt REAL DEFAULT 0.0,
    total_purchases REAL DEFAULT 0.0,
    notes TEXT DEFAULT '',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Sales header
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER DEFAULT NULL,
    cashier_name TEXT DEFAULT 'Admin',
    subtotal REAL NOT NULL DEFAULT 0.0,
    discount_amount REAL DEFAULT 0.0,
    tax_amount REAL DEFAULT 0.0,
    total_amount REAL NOT NULL DEFAULT 0.0,
    amount_paid REAL DEFAULT 0.0,
    change_amount REAL DEFAULT 0.0,
    payment_method TEXT DEFAULT 'cash',
    momo_reference TEXT DEFAULT '',
    notes TEXT DEFAULT '',
    status TEXT DEFAULT 'completed',
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- Sale line items
CREATE TABLE IF NOT EXISTS sale_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    product_name TEXT NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    unit_price REAL NOT NULL,
    cost_price REAL DEFAULT 0.0,
    subtotal REAL NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (sale_id) REFERENCES sales(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- MoMo transactions
CREATE TABLE IF NOT EXISTS momo_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reference TEXT DEFAULT '',
    amount REAL NOT NULL,
    transaction_type TEXT DEFAULT 'incoming',
    sender_name TEXT DEFAULT '',
    sender_number TEXT DEFAULT '',
    sale_id INTEGER DEFAULT NULL,
    notes TEXT DEFAULT '',
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (sale_id) REFERENCES sales(id)
);

-- Stock movements log
CREATE TABLE IF NOT EXISTS stock_movements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    movement_type TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    previous_stock INTEGER DEFAULT 0,
    new_stock INTEGER DEFAULT 0,
    notes TEXT DEFAULT '',
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Insert default data
INSERT OR IGNORE INTO settings (id, business_name)
VALUES (1, 'My Business');

INSERT OR IGNORE INTO categories (id, name)
VALUES (1, 'General');