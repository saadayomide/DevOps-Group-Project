-- Reset tables for repeatable seeding
DELETE FROM Prices;
DELETE FROM Products;
DELETE FROM Supermarkets;

-- Supermarkets
INSERT INTO Supermarkets (name, city) VALUES
  ('Walmart', 'Bentonville'),
  ('Target', 'Minneapolis'),
  ('Costco', 'Issaquah');

-- Products
INSERT INTO Products (name, category) VALUES
  ('milk', 'Dairy'),
  ('eggs', 'Dairy'),
  ('rice', 'Pantry'),
  ('pasta', 'Pantry'),
  ('chicken breast', 'Meat'),
  ('apples', 'Produce'),
  ('bread', 'Bakery'),
  ('cereal', 'Breakfast'),
  ('cheese', 'Dairy'),
  ('ground beef', 'Meat');

-- Prices (one per product-store combo)
INSERT INTO Prices (product_id, store_id, price) VALUES
  ((SELECT id FROM Products WHERE name = 'milk'), (SELECT id FROM Supermarkets WHERE name = 'Walmart'), 1.94),
  ((SELECT id FROM Products WHERE name = 'milk'), (SELECT id FROM Supermarkets WHERE name = 'Target'), 2.15),
  ((SELECT id FROM Products WHERE name = 'milk'), (SELECT id FROM Supermarkets WHERE name = 'Costco'), 1.99),

  ((SELECT id FROM Products WHERE name = 'eggs'), (SELECT id FROM Supermarkets WHERE name = 'Walmart'), 2.59),
  ((SELECT id FROM Products WHERE name = 'eggs'), (SELECT id FROM Supermarkets WHERE name = 'Target'), 2.79),
  ((SELECT id FROM Products WHERE name = 'eggs'), (SELECT id FROM Supermarkets WHERE name = 'Costco'), 2.69),

  ((SELECT id FROM Products WHERE name = 'rice'), (SELECT id FROM Supermarkets WHERE name = 'Walmart'), 5.39),
  ((SELECT id FROM Products WHERE name = 'rice'), (SELECT id FROM Supermarkets WHERE name = 'Target'), 5.19),
  ((SELECT id FROM Products WHERE name = 'rice'), (SELECT id FROM Supermarkets WHERE name = 'Costco'), 4.99),

  ((SELECT id FROM Products WHERE name = 'pasta'), (SELECT id FROM Supermarkets WHERE name = 'Walmart'), 1.49),
  ((SELECT id FROM Products WHERE name = 'pasta'), (SELECT id FROM Supermarkets WHERE name = 'Target'), 1.69),
  ((SELECT id FROM Products WHERE name = 'pasta'), (SELECT id FROM Supermarkets WHERE name = 'Costco'), 1.39),

  ((SELECT id FROM Products WHERE name = 'chicken breast'), (SELECT id FROM Supermarkets WHERE name = 'Walmart'), 8.49),
  ((SELECT id FROM Products WHERE name = 'chicken breast'), (SELECT id FROM Supermarkets WHERE name = 'Target'), 8.99),
  ((SELECT id FROM Products WHERE name = 'chicken breast'), (SELECT id FROM Supermarkets WHERE name = 'Costco'), 8.19),

  ((SELECT id FROM Products WHERE name = 'apples'), (SELECT id FROM Supermarkets WHERE name = 'Walmart'), 3.19),
  ((SELECT id FROM Products WHERE name = 'apples'), (SELECT id FROM Supermarkets WHERE name = 'Target'), 3.39),
  ((SELECT id FROM Products WHERE name = 'apples'), (SELECT id FROM Supermarkets WHERE name = 'Costco'), 3.09),

  ((SELECT id FROM Products WHERE name = 'bread'), (SELECT id FROM Supermarkets WHERE name = 'Walmart'), 2.49),
  ((SELECT id FROM Products WHERE name = 'bread'), (SELECT id FROM Supermarkets WHERE name = 'Target'), 2.69),
  ((SELECT id FROM Products WHERE name = 'bread'), (SELECT id FROM Supermarkets WHERE name = 'Costco'), 2.19),

  ((SELECT id FROM Products WHERE name = 'cereal'), (SELECT id FROM Supermarkets WHERE name = 'Walmart'), 4.39),
  ((SELECT id FROM Products WHERE name = 'cereal'), (SELECT id FROM Supermarkets WHERE name = 'Target'), 4.69),
  ((SELECT id FROM Products WHERE name = 'cereal'), (SELECT id FROM Supermarkets WHERE name = 'Costco'), 4.19),

  ((SELECT id FROM Products WHERE name = 'cheese'), (SELECT id FROM Supermarkets WHERE name = 'Walmart'), 5.59),
  ((SELECT id FROM Products WHERE name = 'cheese'), (SELECT id FROM Supermarkets WHERE name = 'Target'), 5.89),
  ((SELECT id FROM Products WHERE name = 'cheese'), (SELECT id FROM Supermarkets WHERE name = 'Costco'), 5.39),

  ((SELECT id FROM Products WHERE name = 'ground beef'), (SELECT id FROM Supermarkets WHERE name = 'Walmart'), 7.99),
  ((SELECT id FROM Products WHERE name = 'ground beef'), (SELECT id FROM Supermarkets WHERE name = 'Target'), 8.29),
  ((SELECT id FROM Products WHERE name = 'ground beef'), (SELECT id FROM Supermarkets WHERE name = 'Costco'), 7.79);
