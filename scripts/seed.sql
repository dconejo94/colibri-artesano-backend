-- ============================================================================
-- Colibrí Artesano — Seed Data
-- ============================================================================
-- Local development / integration data, consistent with the variant-centric
-- model: every product has at least one variant (the sellable unit that carries
-- stock and price), and images belong to variants (not products). Products have
-- no stock column — the product total is derived from its variants.
--
-- Test accounts (password for ALL: "password123"):
--   Vendor 1 : daniel@colibri.dev          store "Artesanías Chorotega"     (admin + vendor)
--   Vendor 2 : maria@artesana.cr           store "Tejidos de María"
--   Vendor 3 : camila@siraki.cr            store "Colectivo Sirakí"
--   Vendor 4 : marta@tallerguaitil.cr      store "Taller Guaitil"
--   Vendor 5 : rodrigo.mata@pintor.cr      store "Rodrigo Mata Arte"
--   Vendor 6 : esteban@cuerosdelvalle.cr   store "Cueros del Valle"
--   Vendor 7 : luis@maderasnativas.cr      store "Maderas Nativas CR"
--   Buyer  1 : ana.compradora@gmail.com
--   Buyer  2 : bruno@comprador.cr
--   Buyer  3 : sofia.jimenez@hotmail.com
-- ============================================================================

BEGIN;

-- ── Users (7 vendors + 3 buyers) ──────────────────────────────────────────────
-- password_hash is bcrypt for "password123" (same hash reused; bcrypt salts it).

INSERT INTO users (id, email, password_hash, is_admin, name, phone, address, bio, role) VALUES
  ('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'daniel@colibri.dev',       '$2b$12$8sboH57GwUBjk2DveqvctOp2swBjAf2au3oYWRK4HOz8V0M/fJkVa', true,
   'Daniel Conejo',  '+506 8888-0001', 'San José, Costa Rica', 'Artesano ceramista y administrador.', 'vendor'),
  ('b1ffcd00-ad1c-4ff9-cc7e-7cc0ce491b22', 'maria@artesana.cr',        '$2b$12$8sboH57GwUBjk2DveqvctOp2swBjAf2au3oYWRK4HOz8V0M/fJkVa', false,
   'María Solís',    '+506 8888-0002', 'Sarchí, Alajuela',     'Tejedora de textiles artesanales.',   'vendor'),
  ('c1111111-0000-0000-0000-000000000001', 'camila@siraki.cr',         '$2b$12$8sboH57GwUBjk2DveqvctOp2swBjAf2au3oYWRK4HOz8V0M/fJkVa', false,
   'Camila Rojas',   '+506 8888-0003', 'Pérez Zeledón, San José', 'Tejedora del Pacífico Sur, tinte natural y telar de cintura.', 'vendor'),
  ('c2222222-0000-0000-0000-000000000001', 'marta@tallerguaitil.cr',   '$2b$12$8sboH57GwUBjk2DveqvctOp2swBjAf2au3oYWRK4HOz8V0M/fJkVa', false,
   'Marta Obando',   '+506 8888-0004', 'Guaitil, Guanacaste',  'Ceramista del taller comunitario de Guaitil.', 'vendor'),
  ('c3333333-0000-0000-0000-000000000001', 'rodrigo.mata@pintor.cr',   '$2b$12$8sboH57GwUBjk2DveqvctOp2swBjAf2au3oYWRK4HOz8V0M/fJkVa', false,
   'Rodrigo Mata',   '+506 8888-0005', 'Escazú, San José',     'Pintor costarricense inspirado en la flora y fauna tropical.', 'vendor'),
  ('c4444444-0000-0000-0000-000000000001', 'esteban@cuerosdelvalle.cr','$2b$12$8sboH57GwUBjk2DveqvctOp2swBjAf2au3oYWRK4HOz8V0M/fJkVa', false,
   'Esteban Vargas', '+506 8888-0008', 'Valle Central, Heredia', 'Marroquinero, trabaja cuero curtido naturalmente.', 'vendor'),
  ('c5555555-0000-0000-0000-000000000001', 'luis@maderasnativas.cr',   '$2b$12$8sboH57GwUBjk2DveqvctOp2swBjAf2au3oYWRK4HOz8V0M/fJkVa', false,
   'Luis Fernández', '+506 8888-0009', 'Sarchí, Alajuela',     'Ebanista, talla maderas costarricenses de rescate.', 'vendor'),
  ('f5ddab44-eb5a-8dd3-aab1-baa4ac835f66', 'ana.compradora@gmail.com', '$2b$12$8sboH57GwUBjk2DveqvctOp2swBjAf2au3oYWRK4HOz8V0M/fJkVa', false,
   'Ana Rodríguez',  '+506 8888-0006', 'Cartago, Costa Rica',  'Apasionada por la artesanía.',        'buyer'),
  ('a7777777-0000-0000-0000-000000000001', 'bruno@comprador.cr',       '$2b$12$8sboH57GwUBjk2DveqvctOp2swBjAf2au3oYWRK4HOz8V0M/fJkVa', false,
   'Bruno Méndez',   '+506 8888-0007', 'Liberia, Guanacaste',  'Coleccionista de cerámica.',          'buyer'),
  ('c6666666-0000-0000-0000-000000000001', 'sofia.jimenez@hotmail.com','$2b$12$8sboH57GwUBjk2DveqvctOp2swBjAf2au3oYWRK4HOz8V0M/fJkVa', false,
   'Sofía Jiménez',  '+506 8888-0010', 'Heredia, Costa Rica',  'Le encanta apoyar a artesanos locales.', 'buyer')
ON CONFLICT (id) DO NOTHING;

-- ── Categories ───────────────────────────────────────────────────────────────

INSERT INTO categories (id, name, slug) VALUES
  ('ca000000-0000-0000-0000-000000000001', 'Cerámica', 'ceramica'),
  ('ca000000-0000-0000-0000-000000000002', 'Textiles', 'textiles'),
  ('ca000000-0000-0000-0000-000000000003', 'Joyería',  'joyeria'),
  ('ca000000-0000-0000-0000-000000000004', 'Cuero',    'cuero'),
  ('ca000000-0000-0000-0000-000000000005', 'Madera',   'madera'),
  ('ca000000-0000-0000-0000-000000000006', 'Pinturas', 'pinturas')
ON CONFLICT (id) DO NOTHING;

-- ── Stores (one per vendor) ──────────────────────────────────────────────────

INSERT INTO stores (id, owner_id, name, description) VALUES
  ('10000000-0000-0000-0000-000000000001', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'Artesanías Chorotega', 'Cerámica y arte precolombino de Guanacaste.'),
  ('10000000-0000-0000-0000-000000000002', 'b1ffcd00-ad1c-4ff9-cc7e-7cc0ce491b22', 'Tejidos de María',     'Textiles tejidos a mano con tintes naturales.'),
  ('10000000-0000-0000-0000-000000000003', 'c1111111-0000-0000-0000-000000000001', 'Colectivo Sirakí',     'Colectivo de tejedoras del Pacífico Sur. Tinte natural y telar de cintura.'),
  ('10000000-0000-0000-0000-000000000004', 'c2222222-0000-0000-0000-000000000001', 'Taller Guaitil',       'Taller comunitario en Guaitil dedicado a la cerámica chorotega tradicional.'),
  ('10000000-0000-0000-0000-000000000005', 'c3333333-0000-0000-0000-000000000001', 'Rodrigo Mata Arte',    'Pintura costarricense al óleo, inspirada en flora y fauna tropical.'),
  ('10000000-0000-0000-0000-000000000006', 'c4444444-0000-0000-0000-000000000001', 'Cueros del Valle',     'Marroquinería artesanal en cuero curtido naturalmente.'),
  ('10000000-0000-0000-0000-000000000007', 'c5555555-0000-0000-0000-000000000001', 'Maderas Nativas CR',   'Tallado y ebanistería en maderas costarricenses de rescate.')
ON CONFLICT (id) DO NOTHING;

-- ── Products (no stock column; stock lives on variants) ──────────────────────
-- Store 1: Artesanías Chorotega (Daniel)

INSERT INTO products (id, store_id, category_id, name, description, base_price) VALUES
  ('aa000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000001', 'ca000000-0000-0000-0000-000000000001', 'Vasija Chorotega Clásica', 'Vasija de cerámica con motivos precolombinos.', 25000.00),
  ('aa000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000001', 'ca000000-0000-0000-0000-000000000001', 'Plato Decorativo Sol',     'Plato de cerámica con diseño solar.',          18000.00),
  ('aa000000-0000-0000-0000-000000000004', '10000000-0000-0000-0000-000000000001', 'ca000000-0000-0000-0000-000000000003', 'Collar de Jade Artesanal', 'Collar con cuentas de jade y cordón natural.',  42000.00)
ON CONFLICT (id) DO NOTHING;

-- Store 2: Tejidos de María

INSERT INTO products (id, store_id, category_id, name, description, base_price) VALUES
  ('bb000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000002', 'ca000000-0000-0000-0000-000000000002', 'Rebozo Tradicional',    'Rebozo tejido en telar de cintura.',     28000.00),
  ('bb000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000002', 'ca000000-0000-0000-0000-000000000002', 'Mantel Bordado Flores', 'Mantel de algodón con bordado floral.',  22000.00),
  ('bb000000-0000-0000-0000-000000000005', '10000000-0000-0000-0000-000000000002', 'ca000000-0000-0000-0000-000000000002', 'Hamaca Familiar',       'Hamaca doble tejida en algodón orgánico.', 65000.00)
ON CONFLICT (id) DO NOTHING;

-- Store 3: Colectivo Sirakí (textiles)

INSERT INTO products (id, store_id, category_id, name, description, base_price) VALUES
  ('c7000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000003', 'ca000000-0000-0000-0000-000000000002', 'Tapiz Pacífico Sur',      'Tapiz tejido a mano con tintes naturales del Pacífico Sur.', 35000.00),
  ('c7000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000003', 'ca000000-0000-0000-0000-000000000002', 'Bolso Tejido a Mano',     'Bolso de algodón tejido en telar de cintura.',               19000.00),
  ('c7000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000003', 'ca000000-0000-0000-0000-000000000002', 'Chal de Algodón Natural', 'Chal liviano teñido con pigmentos vegetales.',                24000.00)
ON CONFLICT (id) DO NOTHING;

-- Store 4: Taller Guaitil (cerámica)

INSERT INTO products (id, store_id, category_id, name, description, base_price) VALUES
  ('c8000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000004', 'ca000000-0000-0000-0000-000000000001', 'Olla de Barro Tradicional', 'Olla de barro cocida a leña, técnica ancestral chorotega.', 21000.00),
  ('c8000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000004', 'ca000000-0000-0000-0000-000000000001', 'Figura Chorotega Decorativa', 'Figura de barro con motivos precolombinos pintados a mano.', 16000.00),
  ('c8000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000004', 'ca000000-0000-0000-0000-000000000001', 'Set de Tazas de Barro', 'Juego de 4 tazas de barro esmaltadas, hechas a mano.', 26000.00)
ON CONFLICT (id) DO NOTHING;

-- Store 5: Rodrigo Mata Arte (pinturas)

INSERT INTO products (id, store_id, category_id, name, description, base_price) VALUES
  ('c9000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000005', 'ca000000-0000-0000-0000-000000000006', 'Óleo Atardecer Tropical', 'Óleo sobre lienzo, paisaje costero al atardecer.', 85000.00),
  ('c9000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000005', 'ca000000-0000-0000-0000-000000000006', 'Cuadro Quetzal en Vuelo', 'Óleo sobre lienzo, quetzal en el bosque nuboso.',   95000.00),
  ('c9000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000005', 'ca000000-0000-0000-0000-000000000006', 'Serie Flora Tropical (mini)', 'Set de 3 mini lienzos de flora tropical costarricense.', 45000.00)
ON CONFLICT (id) DO NOTHING;

-- Store 6: Cueros del Valle (cuero)

INSERT INTO products (id, store_id, category_id, name, description, base_price) VALUES
  ('cb000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000006', 'ca000000-0000-0000-0000-000000000004', 'Bolso de Cuero Artesanal', 'Bolso de cuero curtido naturalmente, costura a mano.', 48000.00),
  ('cb000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000006', 'ca000000-0000-0000-0000-000000000004', 'Cinturón Trenzado',       'Cinturón de cuero trenzado, hebilla artesanal.',        18000.00),
  ('cb000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000006', 'ca000000-0000-0000-0000-000000000004', 'Billetera Minimalista',   'Billetera de cuero delgada, diseño minimalista.',       14000.00)
ON CONFLICT (id) DO NOTHING;

-- Store 7: Maderas Nativas CR (madera)

INSERT INTO products (id, store_id, category_id, name, description, base_price) VALUES
  ('cd000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000007', 'ca000000-0000-0000-0000-000000000005', 'Tabla de Picar Guanacaste', 'Tabla de picar en madera de guanacaste maciza.',   17000.00),
  ('cd000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000007', 'ca000000-0000-0000-0000-000000000005', 'Set de Cucharas de Madera', 'Juego de 4 cucharas talladas a mano.',              12000.00),
  ('cd000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000007', 'ca000000-0000-0000-0000-000000000005', 'Lámpara Tallada',           'Lámpara de mesa con base de madera tallada a mano.', 32000.00)
ON CONFLICT (id) DO NOTHING;

-- ── Product Variants (every product has >= 1) ────────────────────────────────
-- Single-option products get one "Único" variant so they stay sellable.

INSERT INTO product_variants (id, product_id, name, value, price_modifier, stock_quantity) VALUES
  -- Vasija (3 sizes)
  ('f2000000-0000-0000-0000-000000000001', 'aa000000-0000-0000-0000-000000000001', 'Tamaño', 'Pequeña (15cm)', -5000.00, 12),
  ('f2000000-0000-0000-0000-000000000002', 'aa000000-0000-0000-0000-000000000001', 'Tamaño', 'Mediana (25cm)',  0.00,     8),
  ('f2000000-0000-0000-0000-000000000003', 'aa000000-0000-0000-0000-000000000001', 'Tamaño', 'Grande (35cm)',   10000.00, 4),
  -- Plato (single)
  ('f2000000-0000-0000-0000-000000000022', 'aa000000-0000-0000-0000-000000000002', 'Default', 'Único', 0.00, 10),
  -- Collar (2 lengths)
  ('f2000000-0000-0000-0000-000000000004', 'aa000000-0000-0000-0000-000000000004', 'Largo', 'Gargantilla', -8000.00, 6),
  ('f2000000-0000-0000-0000-000000000005', 'aa000000-0000-0000-0000-000000000004', 'Largo', 'Estándar',     0.00,    10),
  -- Rebozo (2 colors)
  ('f2000000-0000-0000-0000-000000000007', 'bb000000-0000-0000-0000-000000000001', 'Color', 'Añil',      0.00,    15),
  ('f2000000-0000-0000-0000-000000000008', 'bb000000-0000-0000-0000-000000000001', 'Color', 'Terracota', 2000.00, 10),
  -- Mantel (single)
  ('f2000000-0000-0000-0000-000000000023', 'bb000000-0000-0000-0000-000000000002', 'Default', 'Único', 0.00, 7),
  -- Hamaca (2 sizes)
  ('f2000000-0000-0000-0000-000000000009', 'bb000000-0000-0000-0000-000000000005', 'Tamaño', 'Individual', -15000.00, 20),
  ('f2000000-0000-0000-0000-000000000010', 'bb000000-0000-0000-0000-000000000005', 'Tamaño', 'Familiar',    0.00,      7),

  -- Tapiz Pacífico Sur (2 colores)
  ('f3000000-0000-0000-0000-000000000001', 'c7000000-0000-0000-0000-000000000001', 'Color', 'Añil',      0.00,    9),
  ('f3000000-0000-0000-0000-000000000002', 'c7000000-0000-0000-0000-000000000001', 'Color', 'Terracota', 3000.00, 6),
  -- Bolso Tejido a Mano (2 tamaños)
  ('f3000000-0000-0000-0000-000000000003', 'c7000000-0000-0000-0000-000000000002', 'Tamaño', 'Pequeño', -3000.00, 14),
  ('f3000000-0000-0000-0000-000000000004', 'c7000000-0000-0000-0000-000000000002', 'Tamaño', 'Grande',   0.00,    8),
  -- Chal de Algodón Natural (único)
  ('f3000000-0000-0000-0000-000000000005', 'c7000000-0000-0000-0000-000000000003', 'Default', 'Único', 0.00, 11),

  -- Olla de Barro Tradicional (2 tamaños)
  ('f3000000-0000-0000-0000-000000000006', 'c8000000-0000-0000-0000-000000000001', 'Tamaño', 'Mediana', 0.00,     10),
  ('f3000000-0000-0000-0000-000000000007', 'c8000000-0000-0000-0000-000000000001', 'Tamaño', 'Grande',  6000.00,  5),
  -- Figura Chorotega Decorativa (única)
  ('f3000000-0000-0000-0000-000000000008', 'c8000000-0000-0000-0000-000000000002', 'Default', 'Único', 0.00, 13),
  -- Set de Tazas de Barro (único)
  ('f3000000-0000-0000-0000-000000000009', 'c8000000-0000-0000-0000-000000000003', 'Default', 'Único', 0.00, 9),

  -- Óleo Atardecer Tropical (2 formatos)
  ('f3000000-0000-0000-0000-000000000010', 'c9000000-0000-0000-0000-000000000001', 'Formato', '40x60 cm', 0.00,      3),
  ('f3000000-0000-0000-0000-000000000011', 'c9000000-0000-0000-0000-000000000001', 'Formato', '60x90 cm', 35000.00, 2),
  -- Cuadro Quetzal en Vuelo (único, obra original)
  ('f3000000-0000-0000-0000-000000000012', 'c9000000-0000-0000-0000-000000000002', 'Default', 'Original', 0.00, 1),
  -- Serie Flora Tropical mini (único)
  ('f3000000-0000-0000-0000-000000000013', 'c9000000-0000-0000-0000-000000000003', 'Default', 'Único', 0.00, 4),

  -- Bolso de Cuero Artesanal (2 colores)
  ('f3000000-0000-0000-0000-000000000014', 'cb000000-0000-0000-0000-000000000001', 'Color', 'Café',  0.00,    7),
  ('f3000000-0000-0000-0000-000000000015', 'cb000000-0000-0000-0000-000000000001', 'Color', 'Negro', 2000.00, 9),
  -- Cinturón Trenzado (3 tallas)
  ('f3000000-0000-0000-0000-000000000016', 'cb000000-0000-0000-0000-000000000002', 'Talla', 'S', 0.00, 8),
  ('f3000000-0000-0000-0000-000000000017', 'cb000000-0000-0000-0000-000000000002', 'Talla', 'M', 0.00, 12),
  ('f3000000-0000-0000-0000-000000000018', 'cb000000-0000-0000-0000-000000000002', 'Talla', 'L', 0.00, 6),
  -- Billetera Minimalista (única)
  ('f3000000-0000-0000-0000-000000000019', 'cb000000-0000-0000-0000-000000000003', 'Default', 'Único', 0.00, 15),

  -- Tabla de Picar Guanacaste (única)
  ('f3000000-0000-0000-0000-000000000020', 'cd000000-0000-0000-0000-000000000001', 'Default', 'Único', 0.00, 10),
  -- Set de Cucharas de Madera (único)
  ('f3000000-0000-0000-0000-000000000021', 'cd000000-0000-0000-0000-000000000002', 'Default', 'Único', 0.00, 16),
  -- Lámpara Tallada (2 acabados)
  ('f3000000-0000-0000-0000-000000000022', 'cd000000-0000-0000-0000-000000000003', 'Acabado', 'Natural', 0.00,     5),
  ('f3000000-0000-0000-0000-000000000023', 'cd000000-0000-0000-0000-000000000003', 'Acabado', 'Oscuro',  1500.00,  5)
ON CONFLICT (id) DO NOTHING;

-- ── Variant images ────────────────────────────────────────────────────────────
-- Deliberately NOT seeded here. `scripts/seed_images.py` generates a real
-- placeholder image per variant and uploads it to the Azurite blob emulator
-- via the actual upload-url flow, then inserts the resulting product_images
-- rows itself — so every image_url in this dataset is a genuine blob URL,
-- not a hardcoded external link. Run it after this file.

-- ── Events (created by Daniel, the seed admin) ───────────────────────────────
-- Costa Rica does not observe DST, so a fixed -06:00 offset is always correct.

INSERT INTO events (id, title, description, location, event_date, cover_image_url, created_by) VALUES
  ('ee000000-0000-0000-0000-000000000001', 'Feria de Artesanía de Guadalupe',
   'Encuentro de artesanos locales con venta directa, demostraciones de técnicas tradicionales y música en vivo.',
   'Parque Central de Guadalupe, Goicoechea', '2026-08-15 09:00:00-06', 'https://picsum.photos/seed/feria-guadalupe/800/400',
   'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'),
  ('ee000000-0000-0000-0000-000000000002', 'Expo Textiles de Sarchí',
   'Exposición y venta de textiles tejidos a mano, con talleres abiertos al público sobre tinte natural.',
   'Plaza de la Cultura, Sarchí, Alajuela', '2026-09-05 10:00:00-06', 'https://picsum.photos/seed/expo-sarchi/800/400',
   'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'),
  ('ee000000-0000-0000-0000-000000000003', 'Feria Navideña de Artesanos',
   'Feria de fin de año dedicada a piezas artesanales para regalar: cerámica, joyería y textiles.',
   'Antigua Aduana, San José', '2026-12-06 11:00:00-06', 'https://picsum.photos/seed/feria-navidena/800/400',
   'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'),
  ('ee000000-0000-0000-0000-000000000004', 'Mercado de Diseño Costa Rica',
   'Mercado multidisciplinario de diseño y artesanía: pintura, cuero, madera y más, con food trucks y música en vivo.',
   'Antigua Estación al Pacífico, San José', '2026-10-18 10:00:00-06', 'https://picsum.photos/seed/mercado-diseno/800/400',
   'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'),
  ('ee000000-0000-0000-0000-000000000005', 'Festival de Talladores y Ebanistas',
   'Encuentro de talladores y ebanistas costarricenses, con demostraciones en vivo de tallado en madera.',
   'Plaza de la Artesanía, Sarchí, Alajuela', '2026-11-08 09:30:00-06', 'https://picsum.photos/seed/festival-talladores/800/400',
   'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11')
ON CONFLICT (id) DO NOTHING;

-- ── Event participants (store participation requests) ────────────────────────
-- Event 1 (Feria Guadalupe): Chorotega, Tejidos María y Taller Guaitil aprobados; Cueros del Valle pendiente.
-- Event 2 (Expo Textiles Sarchí): Tejidos María y Colectivo Sirakí aprobados; Chorotega pendiente.
-- Event 3 (Feria Navideña): sin solicitudes — ejercita el estado vacío.
-- Event 4 (Mercado de Diseño CR): Rodrigo Mata y Cueros del Valle aprobados; Maderas Nativas pendiente.
-- Event 5 (Festival Talladores): Maderas Nativas aprobado; Taller Guaitil pendiente.

INSERT INTO event_participants (id, event_id, store_id, status, requested_by, reviewed_by) VALUES
  ('eb000000-0000-0000-0000-000000000001', 'ee000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000001', 'approved', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'),
  ('eb000000-0000-0000-0000-000000000002', 'ee000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000002', 'approved', 'b1ffcd00-ad1c-4ff9-cc7e-7cc0ce491b22', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'),
  ('eb000000-0000-0000-0000-000000000003', 'ee000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000002', 'approved', 'b1ffcd00-ad1c-4ff9-cc7e-7cc0ce491b22', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'),
  ('eb000000-0000-0000-0000-000000000004', 'ee000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000001', 'pending',  'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', NULL),
  ('eb000000-0000-0000-0000-000000000005', 'ee000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000004', 'approved', 'c2222222-0000-0000-0000-000000000001', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'),
  ('eb000000-0000-0000-0000-000000000006', 'ee000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000006', 'pending',  'c4444444-0000-0000-0000-000000000001', NULL),
  ('eb000000-0000-0000-0000-000000000007', 'ee000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000003', 'approved', 'c1111111-0000-0000-0000-000000000001', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'),
  ('eb000000-0000-0000-0000-000000000008', 'ee000000-0000-0000-0000-000000000004', '10000000-0000-0000-0000-000000000005', 'approved', 'c3333333-0000-0000-0000-000000000001', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'),
  ('eb000000-0000-0000-0000-000000000009', 'ee000000-0000-0000-0000-000000000004', '10000000-0000-0000-0000-000000000006', 'approved', 'c4444444-0000-0000-0000-000000000001', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'),
  ('eb000000-0000-0000-0000-000000000010', 'ee000000-0000-0000-0000-000000000004', '10000000-0000-0000-0000-000000000007', 'pending',  'c5555555-0000-0000-0000-000000000001', NULL),
  ('eb000000-0000-0000-0000-000000000011', 'ee000000-0000-0000-0000-000000000005', '10000000-0000-0000-0000-000000000007', 'approved', 'c5555555-0000-0000-0000-000000000001', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'),
  ('eb000000-0000-0000-0000-000000000012', 'ee000000-0000-0000-0000-000000000005', '10000000-0000-0000-0000-000000000004', 'pending',  'c2222222-0000-0000-0000-000000000001', NULL)
ON CONFLICT (id) DO NOTHING;

COMMIT;
