
--)Deletes previous data stuff for a safe rerun and shi
DELETE FROM Prices;
DELETE FROM Products;
DELETE FROM Supermarkets;

--) We inserting 3 supermarkets for now
INSERT INTO Supermarkets (name, city) VALUES
  ('Carrefour',  'Madrid'),
  ('Mercadona',  'Madrid'),
  ('Dia',        'Madrid');

--) Inserting bout 15 products
INSERT INTO Products (name, category) VALUES
  ('Milk 1L',              'Dairy'),
  ('Eggs 12-pack',         'Dairy'),
  ('White Bread',          'Bakery'),
  ('Wholegrain Bread',     'Bakery'),
  ('Bananas 1kg',          'Produce'),
  ('Apples 1kg',           'Produce'),
  ('Chicken Breast 1kg',   'Meat'),
  ('Ground Beef 500g',     'Meat'),
  ('Rice 1kg',             'Grains'),
  ('Pasta 500g',           'Grains'),
  ('Olive Oil 1L',         'Pantry'),
  ('Tomato Sauce 500g',    'Pantry'),
  ('Yogurt Natural 4x125g','Dairy'),
  ('Corn Flakes 375g',     'Cereal'),
  ('Coffee Ground 250g',   'Drinks');

--) Inserting prices
INSERT INTO Prices (product_id, store_id, price) VALUES
  ((SELECT id FROM Products WHERE name = 'Milk 1L'),
   (SELECT id FROM Supermarkets WHERE name = 'Carrefour' AND city = 'Madrid'), 0.89),
  ((SELECT id FROM Products WHERE name = 'Milk 1L'),
   (SELECT id FROM Supermarkets WHERE name = 'Mercadona' AND city = 'Madrid'), 0.85),
  ((SELECT id FROM Products WHERE name = 'Milk 1L'),
   (SELECT id FROM Supermarkets WHERE name = 'Dia'       AND city = 'Madrid'), 0.79),

  ((SELECT id FROM Products WHERE name = 'Eggs 12-pack'),
   (SELECT id FROM Supermarkets WHERE name = 'Carrefour' AND city = 'Madrid'), 2.10),
  ((SELECT id FROM Products WHERE name = 'Eggs 12-pack'),
   (SELECT id FROM Supermarkets WHERE name = 'Mercadona' AND city = 'Madrid'), 1.95),
  ((SELECT id FROM Products WHERE name = 'Eggs 12-pack'),
   (SELECT id FROM Supermarkets WHERE name = 'Dia'       AND city = 'Madrid'), 1.99),

  ((SELECT id FROM Products WHERE name = 'White Bread'),
   (SELECT id FROM Supermarkets WHERE name = 'Carrefour' AND city = 'Madrid'), 1.20),
  ((SELECT id FROM Products WHERE name = 'White Bread'),
   (SELECT id FROM Supermarkets WHERE name = 'Mercadona' AND city = 'Madrid'), 0.99),
  ((SELECT id FROM Products WHERE name = 'White Bread'),
   (SELECT id FROM Supermarkets WHERE name = 'Dia'       AND city = 'Madrid'), 0.89),

  ((SELECT id FROM Products WHERE name = 'Wholegrain Bread'),
   (SELECT id FROM Supermarkets WHERE name = 'Carrefour' AND city = 'Madrid'), 1.35),
  ((SELECT id FROM Products WHERE name = 'Wholegrain Bread'),
   (SELECT id FROM Supermarkets WHERE name = 'Mercadona' AND city = 'Madrid'), 1.19),
  ((SELECT id FROM Products WHERE name = 'Wholegrain Bread'),
   (SELECT id FROM Supermarkets WHERE name = 'Dia'       AND city = 'Madrid'), 1.10),

  ((SELECT id FROM Products WHERE name = 'Bananas 1kg'),
   (SELECT id FROM Supermarkets WHERE name = 'Carrefour' AND city = 'Madrid'), 1.49),
  ((SELECT id FROM Products WHERE name = 'Bananas 1kg'),
   (SELECT id FROM Supermarkets WHERE name = 'Mercadona' AND city = 'Madrid'), 1.39),
  ((SELECT id FROM Products WHERE name = 'Bananas 1kg'),
   (SELECT id FROM Supermarkets WHERE name = 'Dia'       AND city = 'Madrid'), 1.29),

  ((SELECT id FROM Products WHERE name = 'Apples 1kg'),
   (SELECT id FROM Supermarkets WHERE name = 'Carrefour' AND city = 'Madrid'), 2.10),
  ((SELECT id FROM Products WHERE name = 'Apples 1kg'),
   (SELECT id FROM Supermarkets WHERE name = 'Mercadona' AND city = 'Madrid'), 1.95),
  ((SELECT id FROM Products WHERE name = 'Apples 1kg'),
   (SELECT id FROM Supermarkets WHERE name = 'Dia'       AND city = 'Madrid'), 1.85),

  ((SELECT id FROM Products WHERE name = 'Chicken Breast 1kg'),
   (SELECT id FROM Supermarkets WHERE name = 'Carrefour' AND city = 'Madrid'), 6.99),
  ((SELECT id FROM Products WHERE name = 'Chicken Breast 1kg'),
   (SELECT id FROM Supermarkets WHERE name = 'Mercadona' AND city = 'Madrid'), 6.49),
  ((SELECT id FROM Products WHERE name = 'Chicken Breast 1kg'),
   (SELECT id FROM Supermarkets WHERE name = 'Dia'       AND city = 'Madrid'), 6.29),

  ((SELECT id FROM Products WHERE name = 'Ground Beef 500g'),
   (SELECT id FROM Supermarkets WHERE name = 'Carrefour' AND city = 'Madrid'), 4.50),
  ((SELECT id FROM Products WHERE name = 'Ground Beef 500g'),
   (SELECT id FROM Supermarkets WHERE name = 'Mercadona' AND city = 'Madrid'), 4.20),
  ((SELECT id FROM Products WHERE name = 'Ground Beef 500g'),
   (SELECT id FROM Supermarkets WHERE name = 'Dia'       AND city = 'Madrid'), 3.99),

  ((SELECT id FROM Products WHERE name = 'Rice 1kg'),
   (SELECT id FROM Supermarkets WHERE name = 'Carrefour' AND city = 'Madrid'), 1.35),
  ((SELECT id FROM Products WHERE name = 'Rice 1kg'),
   (SELECT id FROM Supermarkets WHERE name = 'Mercadona' AND city = 'Madrid'), 1.25),
  ((SELECT id FROM Products WHERE name = 'Rice 1kg'),
   (SELECT id FROM Supermarkets WHERE name = 'Dia'       AND city = 'Madrid'), 1.15),

  ((SELECT id FROM Products WHERE name = 'Pasta 500g'),
   (SELECT id FROM Supermarkets WHERE name = 'Carrefour' AND city = 'Madrid'), 1.00),
  ((SELECT id FROM Products WHERE name = 'Pasta 500g'),
   (SELECT id FROM Supermarkets WHERE name = 'Mercadona' AND city = 'Madrid'), 0.95),
  ((SELECT id FROM Products WHERE name = 'Pasta 500g'),
   (SELECT id FROM Supermarkets WHERE name = 'Dia'       AND city = 'Madrid'), 0.89),

  ((SELECT id FROM Products WHERE name = 'Olive Oil 1L'),
   (SELECT id FROM Supermarkets WHERE name = 'Carrefour' AND city = 'Madrid'), 6.50),
  ((SELECT id FROM Products WHERE name = 'Olive Oil 1L'),
   (SELECT id FROM Supermarkets WHERE name = 'Mercadona' AND city = 'Madrid'), 6.20),
  ((SELECT id FROM Products WHERE name = 'Olive Oil 1L'),
   (SELECT id FROM Supermarkets WHERE name = 'Dia'       AND city = 'Madrid'), 5.99),

  ((SELECT id FROM Products WHERE name = 'Tomato Sauce 500g'),
   (SELECT id FROM Supermarkets WHERE name = 'Carrefour' AND city = 'Madrid'), 1.80),
  ((SELECT id FROM Products WHERE name = 'Tomato Sauce 500g'),
   (SELECT id FROM Supermarkets WHERE name = 'Mercadona' AND city = 'Madrid'), 1.60),
  ((SELECT id FROM Products WHERE name = 'Tomato Sauce 500g'),
   (SELECT id FROM Supermarkets WHERE name = 'Dia'       AND city = 'Madrid'), 1.55),

  ((SELECT id FROM Products WHERE name = 'Yogurt Natural 4x125g'),
   (SELECT id FROM Supermarkets WHERE name = 'Carrefour' AND city = 'Madrid'), 1.75),
  ((SELECT id FROM Products WHERE name = 'Yogurt Natural 4x125g'),
   (SELECT id FROM Supermarkets WHERE name = 'Mercadona' AND city = 'Madrid'), 1.55),
  ((SELECT id FROM Products WHERE name = 'Yogurt Natural 4x125g'),
   (SELECT id FROM Supermarkets WHERE name = 'Dia'       AND city = 'Madrid'), 1.45),

  ((SELECT id FROM Products WHERE name = 'Corn Flakes 375g'),
   (SELECT id FROM Supermarkets WHERE name = 'Carrefour' AND city = 'Madrid'), 2.50),
  ((SELECT id FROM Products WHERE name = 'Corn Flakes 375g'),
   (SELECT id FROM Supermarkets WHERE name = 'Mercadona' AND city = 'Madrid'), 2.30),
  ((SELECT id FROM Products WHERE name = 'Corn Flakes 375g'),
   (SELECT id FROM Supermarkets WHERE name = 'Dia'       AND city = 'Madrid'), 2.10),

  ((SELECT id FROM Products WHERE name = 'Coffee Ground 250g'),
   (SELECT id FROM Supermarkets WHERE name = 'Carrefour' AND city = 'Madrid'), 3.90),
  ((SELECT id FROM Products WHERE name = 'Coffee Ground 250g'),
   (SELECT id FROM Supermarkets WHERE name = 'Mercadona' AND city = 'Madrid'), 3.70),
  ((SELECT id FROM Products WHERE name = 'Coffee Ground 250g'),
   (SELECT id FROM Supermarkets WHERE name = 'Dia'       AND city = 'Madrid'), 3.50);
