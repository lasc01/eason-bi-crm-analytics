import psycopg2
import pandas as pd
from datetime import date

# PostgreSQL connection parameters
db_config = {
    "host": "localhost",
    "database": "postgres",
    "user": "postgres",
    "password": "1234",
    "port": "5432"
}

# Connect to the PostgreSQL database
try:
    conn = psycopg2.connect(**db_config)
    print("Connected to PostgreSQL database successfully.")
except Exception as e:
    print("Database connection failed:", e)
    exit()

cur = conn.cursor()

# --- Table Creation Queries ---

table_queries = {
    "cust": """
        CREATE TABLE IF NOT EXISTS cust (
            CustomerID VARCHAR(100) PRIMARY KEY,
            Name VARCHAR(100),
            Email VARCHAR(100),
            Phone VARCHAR(20),
            LoyaltyPoints INT,
            JoinDate DATE
        );
    """,
    "store": """
        CREATE TABLE IF NOT EXISTS store (
            StoreID VARCHAR(100) PRIMARY KEY,
            Location VARCHAR(100),
            Address VARCHAR(100),
            ManagerID VARCHAR(20)
        );
    """,
    "staff": """
        CREATE TABLE IF NOT EXISTS staff (
            StaffID VARCHAR(100) PRIMARY KEY,
            Name VARCHAR(100),
            Role VARCHAR(100),
            StoreID VARCHAR(20),
            ContactInfo VARCHAR(100)
        );
    """,
    "sales": """
        CREATE TABLE IF NOT EXISTS sales (
            SaleID VARCHAR(100) PRIMARY KEY,
            Date DATE,
            StoreID VARCHAR(100),
            StaffID VARCHAR(100),
            CustomerID VARCHAR(100),
            Amount VARCHAR(100)
        );
    """,
    "saleitems": """
        CREATE TABLE IF NOT EXISTS saleitems (
            SaleItemID VARCHAR(100) PRIMARY KEY,
            SaleID VARCHAR(100),
            ProductID VARCHAR(100),
            Quantity VARCHAR(100),
            LineTotal VARCHAR(100)
        );
    """,
    "products": """
        CREATE TABLE IF NOT EXISTS products (
            ProductID VARCHAR(100) PRIMARY KEY,
            ProductName VARCHAR(255),
            Category VARCHAR(100),
            Price VARCHAR(100),
            StockStatus VARCHAR(100),
            Description TEXT
        );
    """,
    "inventory": """
        CREATE TABLE IF NOT EXISTS inventory (
            InventoryID VARCHAR(100) PRIMARY KEY,
            ProductID VARCHAR(100),
            StoreID VARCHAR(100),
            Quantity VARCHAR(100),
            RestockDate DATE
        );
    """
}

# Execute table creation
for table_name, query in table_queries.items():
    cur.execute(query)
    print(f"Table '{table_name}' created or already exists.")
conn.commit()

# --- CSV Import and Insert Operations ---

def insert_data_from_csv(csv_path, insert_query, columns):
    df = pd.read_csv(csv_path)
    
    # Special handling for specific columns
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.date
    if 'JoinDate' in df.columns or 'joindate' in df.columns:
        df['joindate'] = pd.to_datetime(df.get('joindate', df.get('JoinDate')), dayfirst=True).dt.date
    if 'RestockDate' in df.columns:
        df['RestockDate'] = pd.to_datetime(df['RestockDate'], errors='coerce').dt.date

    # Add default email/phone if missing in customer data
    if 'email' not in df.columns and 'name' in df.columns:
        df['email'] = df['name'].apply(lambda x: x.lower().replace(" ", ".") + "@example.com")
    if 'phone' not in df.columns:
        df['phone'] = '0000000000'

    # Prepare data as list of tuples
    data = list(df[columns].itertuples(index=False, name=None))
    
    cur.executemany(insert_query, data)
    conn.commit()
    print(f"Data from '{csv_path}' inserted successfully.")


# --- Insert Statements for Each Table ---

insert_statements = {
    "cust": {
        "csv": "D:\\NCI\\BUSINESS ANALY\\Easton_and_Sons_Customer_Table_with_CUST_Prefix.csv",
        "query": """
            INSERT INTO cust (CustomerID, Name, Email, Phone, LoyaltyPoints, JoinDate)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (CustomerID) DO NOTHING;
        """,
        "columns": ['customerid', 'name', 'email', 'phone', 'loyaltypoints', 'joindate']
    },
    "store": {
        "csv": "D:\\NCI\\BUSINESS ANALY\\Easton_and_Sons_Store_Table.csv",
        "query": """
            INSERT INTO store (StoreID, Location, Address, ManagerID)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (StoreID) DO NOTHING;
        """,
        "columns": ['StoreID', 'Location', 'Address', 'ManagerID']
    },
    "staff": {
        "csv": "D:\\NCI\\BUSINESS ANALY\\Easton_and_Sons_Staff_Table.csv",
        "query": """
            INSERT INTO staff (StaffID, Name, Role, StoreID, ContactInfo)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (StaffID) DO NOTHING;
        """,
        "columns": ['StaffID', 'Name', 'Role', 'StoreID', 'ContactInfo']
    },
    "sales": {
        "csv": "D:\\NCI\\BUSINESS ANALY\\Easton_and_Sons_Sales_Table.csv",
        "query": """
            INSERT INTO sales (SaleID, Date, StoreID, StaffID, CustomerID, Amount)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (SaleID) DO NOTHING;
        """,
        "columns": ['SaleID', 'Date', 'StoreID', 'StaffID', 'CustomerID', 'Amount']
    },
    "saleitems": {
        "csv": "D:\\NCI\\BUSINESS ANALY\\Easton_and_Sons_SaleItem_Table.csv",
        "query": """
            INSERT INTO saleitems (SaleItemID, SaleID, ProductID, Quantity, LineTotal)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (SaleItemID) DO NOTHING;
        """,
        "columns": ['SaleItemID', 'SaleID', 'ProductID', 'Quantity', 'LineTotal']
    },
    "products": {
        "csv": "D:\\NCI\\BUSINESS ANALY\\Easton_and_Sons_Product_Table.csv",
        "query": """
            INSERT INTO products (ProductID, ProductName, Category, Price, StockStatus, Description)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (ProductID) DO NOTHING;
        """,
        "columns": ['ProductID', 'ProductName', 'Category', 'Price', 'StockStatus', 'Description']
    },
    "inventory": {
        "csv": "D:\\NCI\\BUSINESS ANALY\\Easton_and_Sons_Inventory_Table.csv",
        "query": """
            INSERT INTO inventory (InventoryID, ProductID, StoreID, Quantity, RestockDate)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (InventoryID) DO NOTHING;
        """,
        "columns": ['InventoryID', 'ProductID', 'StoreID', 'Quantity', 'RestockDate']
    }
}

# Insert all datasets
for table, config in insert_statements.items():
    insert_data_from_csv(config["csv"], config["query"], config["columns"])

# Close database connection
cur.close()
conn.close()
print("All data inserted and connection closed successfully.")
