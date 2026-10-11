-- Datos de la tabla libros, generados desde libros.csv
INSERT INTO libros (id, isbn, titulo, autor, editorial_id, genero_id) VALUES (1, '9789500000017', 'Rayuela', 'Julio Cortázar', 1, 1) ON CONFLICT DO NOTHING;
INSERT INTO libros (id, isbn, titulo, autor, editorial_id, genero_id) VALUES (2, '9789500000024', 'El Aleph', 'Jorge Luis Borges', 8, 2) ON CONFLICT DO NOTHING;
INSERT INTO libros (id, isbn, titulo, autor, editorial_id, genero_id) VALUES (3, '9789500000031', 'Martín Fierro', 'José Hernández', 9, 6) ON CONFLICT DO NOTHING;
INSERT INTO libros (id, isbn, titulo, autor, editorial_id, genero_id) VALUES (4, '9789500000048', 'Sobre héroes y tumbas', 'Ernesto Sábato', 2, 1) ON CONFLICT DO NOTHING;
INSERT INTO libros (id, isbn, titulo, autor, editorial_id, genero_id) VALUES (5, '9789500000055', 'El Principito', 'Antoine de Saint-Exupéry', 3, 4) ON CONFLICT DO NOTHING;
INSERT INTO libros (id, isbn, titulo, autor, editorial_id, genero_id) VALUES (6, '9789500000062', 'Clean Code', 'Robert C. Martin', 10, 5) ON CONFLICT DO NOTHING;
INSERT INTO libros (id, isbn, titulo, autor, editorial_id, genero_id) VALUES (7, '9789500000079', 'Fundación', 'Isaac Asimov', 4, 8) ON CONFLICT DO NOTHING;
INSERT INTO libros (id, isbn, titulo, autor, editorial_id, genero_id) VALUES (8, '9789500000086', 'Los siete locos', 'Roberto Arlt', 7, 1) ON CONFLICT DO NOTHING;
INSERT INTO libros (id, isbn, titulo, autor, editorial_id, genero_id) VALUES (9, '9789500000093', 'Breve historia de los argentinos', 'Félix Luna', 2, 7) ON CONFLICT DO NOTHING;
INSERT INTO libros (id, isbn, titulo, autor, editorial_id, genero_id) VALUES (10, '9789500000109', 'Las venas abiertas de América Latina', 'Eduardo Galeano', 5, 3) ON CONFLICT DO NOTHING;
INSERT INTO libros (id, isbn, titulo, autor, editorial_id, genero_id) VALUES (11, '9789500000116', 'Ficciones', 'Jorge Luis Borges', 6, 2) ON CONFLICT DO NOTHING;
INSERT INTO libros (id, isbn, titulo, autor, editorial_id, genero_id) VALUES (12, '9789500000123', 'El nombre de la rosa', 'Umberto Eco', 10, 10) ON CONFLICT DO NOTHING;
