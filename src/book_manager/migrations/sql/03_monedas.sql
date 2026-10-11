-- Datos de la tabla monedas, generados desde monedas.csv
INSERT INTO monedas (id, codigo, nombre, simbolo) VALUES (1, 'ARS', 'Peso argentino', '$') ON CONFLICT DO NOTHING;
INSERT INTO monedas (id, codigo, nombre, simbolo) VALUES (2, 'USD', 'Dólar estadounidense', 'US$') ON CONFLICT DO NOTHING;
INSERT INTO monedas (id, codigo, nombre, simbolo) VALUES (3, 'EUR', 'Euro', '€') ON CONFLICT DO NOTHING;
INSERT INTO monedas (id, codigo, nombre, simbolo) VALUES (4, 'BRL', 'Real brasileño', 'R$') ON CONFLICT DO NOTHING;
INSERT INTO monedas (id, codigo, nombre, simbolo) VALUES (5, 'CLP', 'Peso chileno', 'CLP$') ON CONFLICT DO NOTHING;
INSERT INTO monedas (id, codigo, nombre, simbolo) VALUES (6, 'UYU', 'Peso uruguayo', '$U') ON CONFLICT DO NOTHING;
INSERT INTO monedas (id, codigo, nombre, simbolo) VALUES (7, 'GBP', 'Libra esterlina', '£') ON CONFLICT DO NOTHING;
INSERT INTO monedas (id, codigo, nombre, simbolo) VALUES (8, 'CHF', 'Franco suizo', 'CHF') ON CONFLICT DO NOTHING;
INSERT INTO monedas (id, codigo, nombre, simbolo) VALUES (9, 'JPY', 'Yen japonés', '¥') ON CONFLICT DO NOTHING;
INSERT INTO monedas (id, codigo, nombre, simbolo) VALUES (10, 'MXN', 'Peso mexicano', 'MX$') ON CONFLICT DO NOTHING;
