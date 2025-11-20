IF OBJECT_ID('dbo.Prices', 'U') IS NOT NULL DROP TABLE dbo.Prices;
IF OBJECT_ID('dbo.Products', 'U') IS NOT NULL DROP TABLE dbo.Products;
IF OBJECT_ID('dbo.Supermarkets', 'U') IS NOT NULL DROP TABLE dbo.Supermarkets;

-- Products table
CREATE TABLE Products (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    category VARCHAR(255) NULL
);

-- Supermarkets table
CREATE TABLE Supermarkets (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    city VARCHAR(255) NOT NULL
);

-- Prices table
CREATE TABLE Prices (
    id INT IDENTITY(1,1) PRIMARY KEY,
    product_id INT NOT NULL,
    store_id INT NOT NULL,
    price DECIMAL(6,2) NOT NULL,

    CONSTRAINT FK_Prices_Product
        FOREIGN KEY (product_id)
        REFERENCES Products(id)
        ON DELETE CASCADE,

    CONSTRAINT FK_Prices_Store
        FOREIGN KEY (store_id)
        REFERENCES Supermarkets(id)
        ON DELETE CASCADE,

    CONSTRAINT CHK_Prices_Price_Positive
        CHECK (price >= 0.01),

    CONSTRAINT UQ_Prices_Product_Store
        UNIQUE (product_id, store_id)
);

CREATE INDEX IX_Prices_ProductId_StoreId ON Prices(product_id, store_id);
