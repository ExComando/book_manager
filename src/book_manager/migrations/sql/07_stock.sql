-- Datos de la tabla stock, generados desde stock.csv
INSERT INTO stock (libro_id, cantidad) VALUES (1, 12) ON CONFLICT DO NOTHING;
INSERT INTO stock (libro_id, cantidad) VALUES (2, 3) ON CONFLICT DO NOTHING;
INSERT INTO stock (libro_id, cantidad) VALUES (3, 25) ON CONFLICT DO NOTHING;
INSERT INTO stock (libro_id, cantidad) VALUES (4, 7) ON CONFLICT DO NOTHING;
INSERT INTO stock (libro_id, cantidad) VALUES (5, 30) ON CONFLICT DO NOTHING;
INSERT INTO stock (libro_id, cantidad) VALUES (6, 4) ON CONFLICT DO NOTHING;
INSERT INTO stock (libro_id, cantidad) VALUES (7, 9) ON CONFLICT DO NOTHING;
INSERT INTO stock (libro_id, cantidad) VALUES (8, 0) ON CONFLICT DO NOTHING;
INSERT INTO stock (libro_id, cantidad) VALUES (9, 15) ON CONFLICT DO NOTHING;
INSERT INTO stock (libro_id, cantidad) VALUES (10, 6) ON CONFLICT DO NOTHING;
INSERT INTO stock (libro_id, cantidad) VALUES (11, 18) ON CONFLICT DO NOTHING;
INSERT INTO stock (libro_id, cantidad) VALUES (12, 2) ON CONFLICT DO NOTHING;
