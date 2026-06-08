-- ============================================================================
-- Colibrí Artesano — Seed Data
-- ============================================================================
-- This script populates the database with realistic test data for local
-- development and frontend integration testing.
--
-- YOUR test user (matches OWNER_ID in the mobile app):
--   User ID : a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11
--   Email   : daniel@colibri.dev
--   Store   : Artesanías Chorotega  (ID: 10000000-...)
-- ============================================================================

BEGIN;

-- ── Users ────────────────────────────────────────────────────────────────────

INSERT INTO users (id, email, password_hash, is_admin, name, phone, address, bio) VALUES
  ('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'daniel@colibri.dev',       '$2b$12$placeholder_hash_daniel',   true,
   'Daniel Conejo',   '+506 8888-0001', 'San José, Costa Rica',      'Artesano ceramista y administrador de la plataforma.'),
  ('b1ffcd00-ad1c-4ff9-cc7e-7cc0ce491b22', 'maria@artesana.cr',        '$2b$12$placeholder_hash_maria',    false,
   'María Solís',     '+506 8888-0002', 'Sarchí, Alajuela',          'Tejedora de textiles artesanales con más de 20 años de experiencia.'),
  ('c2aade11-be2d-5aa0-dd8f-8dd1df502c33', 'jose@barro.cr',            '$2b$12$placeholder_hash_jose',     false,
   'José Vargas',     '+506 8888-0003', 'Nicoya, Guanacaste',        'Alfarero especializado en barro negro y técnicas ancestrales chorotega.'),
  ('d3bbef22-cf3e-6bb1-ee9a-9ee2ea613d44', 'lucia@textiles.cr',        '$2b$12$placeholder_hash_lucia',    false,
   'Lucía Jiménez',   '+506 8888-0004', 'Heredia, Costa Rica',       'Bordadora y cestería artesanal con fibras naturales del Valle Central.'),
  ('e4ccfa33-da4f-7cc2-ffa0-aff3fb724e55', 'carlos@madera.cr',         '$2b$12$placeholder_hash_carlos',   false,
   'Carlos Mora',     '+506 8888-0005', 'Ciudad Quesada, San Carlos', 'Tallador en maderas sostenibles del bosque lluvioso costarricense.'),
  ('f5ddab44-eb5a-8dd3-aab1-baa4ac835f66', 'ana.compradora@gmail.com', '$2b$12$placeholder_hash_ana',      false,
   'Ana Rodríguez',   '+506 8888-0006', 'Cartago, Costa Rica',       'Apasionada por el arte y la artesanía costarricense.')
ON CONFLICT (id) DO NOTHING;

-- ── Categories ───────────────────────────────────────────────────────────────

INSERT INTO categories (id, name, slug) VALUES
  ('ca000000-0000-0000-0000-000000000001', 'Cerámica',      'ceramica'),
  ('ca000000-0000-0000-0000-000000000002', 'Textiles',      'textiles'),
  ('ca000000-0000-0000-0000-000000000003', 'Joyería',       'joyeria'),
  ('ca000000-0000-0000-0000-000000000004', 'Madera',        'madera'),
  ('ca000000-0000-0000-0000-000000000005', 'Cuero',         'cuero'),
  ('ca000000-0000-0000-0000-000000000006', 'Pintura',       'pintura'),
  ('ca000000-0000-0000-0000-000000000007', 'Cestería',      'cesteria'),
  ('ca000000-0000-0000-0000-000000000008', 'Piedra',        'piedra')
ON CONFLICT (id) DO NOTHING;

-- ── Stores ───────────────────────────────────────────────────────────────────

INSERT INTO stores (id, owner_id, name, description) VALUES
  ('10000000-0000-0000-0000-000000000001', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'Artesanías Chorotega',     'Cerámica y arte precolombino inspirado en la tradición Chorotega de Guanacaste.'),
  ('10000000-0000-0000-0000-000000000002', 'b1ffcd00-ad1c-4ff9-cc7e-7cc0ce491b22', 'Tejidos de María',         'Textiles artesanales tejidos a mano con tintes naturales del Valle Central.'),
  ('10000000-0000-0000-0000-000000000003', 'c2aade11-be2d-5aa0-dd8f-8dd1df502c33', 'Taller del Barro',         'Piezas funcionales y decorativas de barro rojo y negro hechas con técnicas ancestrales.'),
  ('10000000-0000-0000-0000-000000000004', 'd3bbef22-cf3e-6bb1-ee9a-9ee2ea613d44', 'Hilos de Lucía',           'Bordados, hamacas y bolsos hechos con fibras naturales de la zona de Sarchí.'),
  ('10000000-0000-0000-0000-000000000005', 'e4ccfa33-da4f-7cc2-ffa0-aff3fb724e55', 'Maderas del Bosque',       'Artículos decorativos y utensilios tallados a mano en maderas sostenibles.')
ON CONFLICT (id) DO NOTHING;

-- ── Products ─────────────────────────────────────────────────────────────────
-- Store 1: Artesanías Chorotega (YOUR store — Daniel)

INSERT INTO products (id, store_id, category_id, name, description, base_price) VALUES
  ('aa000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000001', 'ca000000-0000-0000-0000-000000000001', 'Vasija Chorotega Clásica',      'Vasija de cerámica pintada con motivos precolombinos tradicionales.',                  25000.00),
  ('aa000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000001', 'ca000000-0000-0000-0000-000000000001', 'Plato Decorativo Sol',         'Plato de cerámica con diseño solar en colores tierra.',                                18000.00),
  ('aa000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000001', 'ca000000-0000-0000-0000-000000000006', 'Máscara Ceremonial',           'Máscara pintada a mano representando deidades indígenas.',                             35000.00),
  ('aa000000-0000-0000-0000-000000000004', '10000000-0000-0000-0000-000000000001', 'ca000000-0000-0000-0000-000000000003', 'Collar de Jade Artesanal',     'Collar hecho con cuentas de jade y cordón de algodón natural.',                        42000.00),
  ('aa000000-0000-0000-0000-000000000005', '10000000-0000-0000-0000-000000000001', 'ca000000-0000-0000-0000-000000000008', 'Escultura en Piedra Volcánica','Escultura tallada en piedra volcánica con forma de quetzal.',                          55000.00)
ON CONFLICT (id) DO NOTHING;

-- Store 2: Tejidos de María

INSERT INTO products (id, store_id, category_id, name, description, base_price) VALUES
  ('bb000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000002', 'ca000000-0000-0000-0000-000000000002', 'Rebozo Tradicional',           'Rebozo tejido en telar de cintura con tintes de añil.',                                28000.00),
  ('bb000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000002', 'ca000000-0000-0000-0000-000000000002', 'Mantel Bordado Flores',        'Mantel de algodón con bordado floral multicolor.',                                     22000.00),
  ('bb000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000002', 'ca000000-0000-0000-0000-000000000002', 'Bolso Tejido Macramé',         'Bolso de macramé con asas de madera y cierre magnético.',                               15000.00),
  ('bb000000-0000-0000-0000-000000000004', '10000000-0000-0000-0000-000000000002', 'ca000000-0000-0000-0000-000000000005', 'Cinturón de Cuero Trenzado',   'Cinturón artesanal de cuero curtido a mano con hebilla de bronce.',                    12000.00),
  ('bb000000-0000-0000-0000-000000000005', '10000000-0000-0000-0000-000000000002', 'ca000000-0000-0000-0000-000000000002', 'Hamaca Familiar',              'Hamaca doble tejida en algodón orgánico con franjas de colores.',                      65000.00)
ON CONFLICT (id) DO NOTHING;

-- Store 3: Taller del Barro

INSERT INTO products (id, store_id, category_id, name, description, base_price) VALUES
  ('cc000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000003', 'ca000000-0000-0000-0000-000000000001', 'Jarra de Barro Negro',         'Jarra torneada en barro negro con acabado satinado.',                                  20000.00),
  ('cc000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000003', 'ca000000-0000-0000-0000-000000000001', 'Set de Tazas Rústicas',        'Set de 4 tazas de barro rojo esmaltadas para café.',                                   16000.00),
  ('cc000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000003', 'ca000000-0000-0000-0000-000000000001', 'Maceta Decorativa Grande',     'Maceta de barro con diseños geométricos para exteriores.',                              30000.00),
  ('cc000000-0000-0000-0000-000000000004', '10000000-0000-0000-0000-000000000003', 'ca000000-0000-0000-0000-000000000006', 'Mural en Cerámica',            'Panel decorativo de cerámica pintada con escenas de la naturaleza.',                   48000.00),
  ('cc000000-0000-0000-0000-000000000005', '10000000-0000-0000-0000-000000000003', 'ca000000-0000-0000-0000-000000000001', 'Comal Artesanal',              'Comal tradicional de barro para tortillas, cocción lenta.',                            14000.00)
ON CONFLICT (id) DO NOTHING;

-- Store 4: Hilos de Lucía

INSERT INTO products (id, store_id, category_id, name, description, base_price) VALUES
  ('dd000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000004', 'ca000000-0000-0000-0000-000000000002', 'Tapiz de Pared Abstracto',     'Tapiz tejido a mano con lana virgen y diseño abstracto contemporáneo.',                38000.00),
  ('dd000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000004', 'ca000000-0000-0000-0000-000000000007', 'Canasta de Palma Tejida',      'Canasta redonda tejida en palma con tapa y asa.',                                      9500.00),
  ('dd000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000004', 'ca000000-0000-0000-0000-000000000002', 'Cojín Bordado Étnico',         'Cojín decorativo con bordado étnico en colores cálidos.',                              11000.00),
  ('dd000000-0000-0000-0000-000000000004', '10000000-0000-0000-0000-000000000004', 'ca000000-0000-0000-0000-000000000003', 'Pulsera Hilo de Plata',        'Pulsera de plata 925 tejida con hilo de seda natural.',                                19000.00),
  ('dd000000-0000-0000-0000-000000000005', '10000000-0000-0000-0000-000000000004', 'ca000000-0000-0000-0000-000000000002', 'Mochila Wayúu',                'Mochila tejida artesanalmente con diseño geométrico en algodón.',                      32000.00)
ON CONFLICT (id) DO NOTHING;

-- Store 5: Maderas del Bosque

INSERT INTO products (id, store_id, category_id, name, description, base_price) VALUES
  ('ee000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000005', 'ca000000-0000-0000-0000-000000000004', 'Tabla de Cortar Premium',      'Tabla de cocina en madera de guanacaste con acabado de aceite mineral.',               17000.00),
  ('ee000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000005', 'ca000000-0000-0000-0000-000000000004', 'Caja Musical Tallada',         'Caja musical con talla de colibrí en madera de cedro.',                                24000.00),
  ('ee000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000005', 'ca000000-0000-0000-0000-000000000004', 'Marco de Espejo Rústico',      'Marco de espejo tallado en madera reciclada con detalles florales.',                   21000.00),
  ('ee000000-0000-0000-0000-000000000004', '10000000-0000-0000-0000-000000000005', 'ca000000-0000-0000-0000-000000000004', 'Set de Cucharas Artesanales',  'Set de 6 cucharas de cocina talladas en madera de laurel.',                            13000.00),
  ('ee000000-0000-0000-0000-000000000005', '10000000-0000-0000-0000-000000000005', 'ca000000-0000-0000-0000-000000000004', 'Reloj de Pared en Teca',       'Reloj de pared minimalista hecho con madera de teca recuperada.',                      29000.00)
ON CONFLICT (id) DO NOTHING;

-- ── Product Images ───────────────────────────────────────────────────────────
-- Using picsum.photos for realistic placeholder images

INSERT INTO product_images (id, product_id, image_url, is_primary) VALUES
  ('f1000000-0000-0000-0000-000000000001', 'aa000000-0000-0000-0000-000000000001', 'https://picsum.photos/seed/vasija1/600/600',   true),
  ('f1000000-0000-0000-0000-000000000002', 'aa000000-0000-0000-0000-000000000001', 'https://picsum.photos/seed/vasija2/600/600',   false),
  ('f1000000-0000-0000-0000-000000000003', 'aa000000-0000-0000-0000-000000000002', 'https://picsum.photos/seed/plato1/600/600',    true),
  ('f1000000-0000-0000-0000-000000000004', 'aa000000-0000-0000-0000-000000000003', 'https://picsum.photos/seed/mascara1/600/600',  true),
  ('f1000000-0000-0000-0000-000000000005', 'aa000000-0000-0000-0000-000000000003', 'https://picsum.photos/seed/mascara2/600/600',  false),
  ('f1000000-0000-0000-0000-000000000006', 'aa000000-0000-0000-0000-000000000004', 'https://picsum.photos/seed/collar1/600/600',   true),
  ('f1000000-0000-0000-0000-000000000007', 'aa000000-0000-0000-0000-000000000005', 'https://picsum.photos/seed/piedra1/600/600',   true),
  ('f1000000-0000-0000-0000-000000000008', 'bb000000-0000-0000-0000-000000000001', 'https://picsum.photos/seed/rebozo1/600/600',   true),
  ('f1000000-0000-0000-0000-000000000009', 'bb000000-0000-0000-0000-000000000002', 'https://picsum.photos/seed/mantel1/600/600',   true),
  ('f1000000-0000-0000-0000-000000000010', 'bb000000-0000-0000-0000-000000000003', 'https://picsum.photos/seed/bolso1/600/600',    true),
  ('f1000000-0000-0000-0000-000000000011', 'bb000000-0000-0000-0000-000000000004', 'https://picsum.photos/seed/cinturon1/600/600', true),
  ('f1000000-0000-0000-0000-000000000012', 'bb000000-0000-0000-0000-000000000005', 'https://picsum.photos/seed/hamaca1/600/600',   true),
  ('f1000000-0000-0000-0000-000000000013', 'bb000000-0000-0000-0000-000000000005', 'https://picsum.photos/seed/hamaca2/600/600',   false),
  ('f1000000-0000-0000-0000-000000000014', 'cc000000-0000-0000-0000-000000000001', 'https://picsum.photos/seed/jarra1/600/600',    true),
  ('f1000000-0000-0000-0000-000000000015', 'cc000000-0000-0000-0000-000000000002', 'https://picsum.photos/seed/tazas1/600/600',    true),
  ('f1000000-0000-0000-0000-000000000016', 'cc000000-0000-0000-0000-000000000003', 'https://picsum.photos/seed/maceta1/600/600',   true),
  ('f1000000-0000-0000-0000-000000000017', 'cc000000-0000-0000-0000-000000000004', 'https://picsum.photos/seed/mural1/600/600',    true),
  ('f1000000-0000-0000-0000-000000000018', 'cc000000-0000-0000-0000-000000000005', 'https://picsum.photos/seed/comal1/600/600',    true),
  ('f1000000-0000-0000-0000-000000000019', 'dd000000-0000-0000-0000-000000000001', 'https://picsum.photos/seed/tapiz1/600/600',    true),
  ('f1000000-0000-0000-0000-000000000020', 'dd000000-0000-0000-0000-000000000002', 'https://picsum.photos/seed/canasta1/600/600',  true),
  ('f1000000-0000-0000-0000-000000000021', 'dd000000-0000-0000-0000-000000000003', 'https://picsum.photos/seed/cojin1/600/600',    true),
  ('f1000000-0000-0000-0000-000000000022', 'dd000000-0000-0000-0000-000000000004', 'https://picsum.photos/seed/pulsera1/600/600',  true),
  ('f1000000-0000-0000-0000-000000000023', 'dd000000-0000-0000-0000-000000000005', 'https://picsum.photos/seed/mochila1/600/600',  true),
  ('f1000000-0000-0000-0000-000000000024', 'ee000000-0000-0000-0000-000000000001', 'https://picsum.photos/seed/tabla1/600/600',    true),
  ('f1000000-0000-0000-0000-000000000025', 'ee000000-0000-0000-0000-000000000002', 'https://picsum.photos/seed/caja1/600/600',     true),
  ('f1000000-0000-0000-0000-000000000026', 'ee000000-0000-0000-0000-000000000003', 'https://picsum.photos/seed/espejo1/600/600',   true),
  ('f1000000-0000-0000-0000-000000000027', 'ee000000-0000-0000-0000-000000000004', 'https://picsum.photos/seed/cucharas1/600/600', true),
  ('f1000000-0000-0000-0000-000000000028', 'ee000000-0000-0000-0000-000000000005', 'https://picsum.photos/seed/reloj1/600/600',    true)
ON CONFLICT (id) DO NOTHING;

-- ── Product Variants ─────────────────────────────────────────────────────────

INSERT INTO product_variants (id, product_id, name, value, price_modifier, stock_quantity) VALUES
  ('f2000000-0000-0000-0000-000000000001', 'aa000000-0000-0000-0000-000000000001', 'Tamaño', 'Pequeña (15cm)', -5000.00, 12),
  ('f2000000-0000-0000-0000-000000000002', 'aa000000-0000-0000-0000-000000000001', 'Tamaño', 'Mediana (25cm)',  0.00,     8),
  ('f2000000-0000-0000-0000-000000000003', 'aa000000-0000-0000-0000-000000000001', 'Tamaño', 'Grande (35cm)',   10000.00, 4),
  ('f2000000-0000-0000-0000-000000000004', 'aa000000-0000-0000-0000-000000000004', 'Largo',  'Gargantilla',    -8000.00, 6),
  ('f2000000-0000-0000-0000-000000000005', 'aa000000-0000-0000-0000-000000000004', 'Largo',  'Estándar',        0.00,     10),
  ('f2000000-0000-0000-0000-000000000006', 'aa000000-0000-0000-0000-000000000004', 'Largo',  'Extra largo',     5000.00,  3),
  ('f2000000-0000-0000-0000-000000000007', 'bb000000-0000-0000-0000-000000000001', 'Color',  'Añil',     0.00,     15),
  ('f2000000-0000-0000-0000-000000000008', 'bb000000-0000-0000-0000-000000000001', 'Color',  'Terracota', 2000.00, 10),
  ('f2000000-0000-0000-0000-000000000009', 'bb000000-0000-0000-0000-000000000005', 'Tamaño', 'Individual', -15000.00, 20),
  ('f2000000-0000-0000-0000-000000000010', 'bb000000-0000-0000-0000-000000000005', 'Tamaño', 'Familiar',    0.00,     7),
  ('f2000000-0000-0000-0000-000000000011', 'cc000000-0000-0000-0000-000000000002', 'Set', '2 tazas', -6000.00, 15),
  ('f2000000-0000-0000-0000-000000000012', 'cc000000-0000-0000-0000-000000000002', 'Set', '4 tazas',  0.00,    10),
  ('f2000000-0000-0000-0000-000000000013', 'cc000000-0000-0000-0000-000000000002', 'Set', '6 tazas',  8000.00,  5),
  ('f2000000-0000-0000-0000-000000000014', 'dd000000-0000-0000-0000-000000000005', 'Tamaño', 'Pequeña',  -8000.00, 25),
  ('f2000000-0000-0000-0000-000000000015', 'dd000000-0000-0000-0000-000000000005', 'Tamaño', 'Mediana',   0.00,    12),
  ('f2000000-0000-0000-0000-000000000016', 'dd000000-0000-0000-0000-000000000005', 'Tamaño', 'Grande',    12000.00, 6),
  ('f2000000-0000-0000-0000-000000000017', 'ee000000-0000-0000-0000-000000000001', 'Madera', 'Guanacaste', 0.00,    10),
  ('f2000000-0000-0000-0000-000000000018', 'ee000000-0000-0000-0000-000000000001', 'Madera', 'Teca',       3000.00,  5),
  ('f2000000-0000-0000-0000-000000000019', 'ee000000-0000-0000-0000-000000000001', 'Madera', 'Nogal',      5000.00,  3),
  ('f2000000-0000-0000-0000-000000000020', 'ee000000-0000-0000-0000-000000000004', 'Madera', 'Laurel',     0.00,     8),
  ('f2000000-0000-0000-0000-000000000021', 'ee000000-0000-0000-0000-000000000004', 'Madera', 'Cedro',      2000.00,  5)
ON CONFLICT (id) DO NOTHING;

COMMIT;
