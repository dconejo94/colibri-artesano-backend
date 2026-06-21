-- ============================================================================
-- Colibrí Artesano — Seed Data
-- ============================================================================
-- Local development / integration data, consistent with the variant-centric
-- model: every product has at least one variant (the sellable unit that carries
-- stock and price), and images belong to variants (not products). Products have
-- no stock column — the product total is derived from its variants.
--
-- Test accounts (password for ALL: "password123"):
--   Vendor 1 : daniel@colibri.dev          store "Artesanías Chorotega"
--   Vendor 2 : maria@artesana.cr           store "Tejidos de María"
--   Buyer  1 : ana.compradora@gmail.com
--   Buyer  2 : bruno@comprador.cr
-- ============================================================================

BEGIN;

-- ── Users (2 vendors + 2 buyers) ─────────────────────────────────────────────
-- password_hash is bcrypt for "password123" (same hash reused; bcrypt salts it).

INSERT INTO users (id, email, password_hash, is_admin, name, phone, address, bio, role) VALUES
  ('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'daniel@colibri.dev',       '$2b$12$8sboH57GwUBjk2DveqvctOp2swBjAf2au3oYWRK4HOz8V0M/fJkVa', true,
   'Daniel Conejo',  '+506 8888-0001', 'San José, Costa Rica', 'Artesano ceramista y administrador.', 'vendor'),
  ('b1ffcd00-ad1c-4ff9-cc7e-7cc0ce491b22', 'maria@artesana.cr',        '$2b$12$8sboH57GwUBjk2DveqvctOp2swBjAf2au3oYWRK4HOz8V0M/fJkVa', false,
   'María Solís',    '+506 8888-0002', 'Sarchí, Alajuela',     'Tejedora de textiles artesanales.',   'vendor'),
  ('f5ddab44-eb5a-8dd3-aab1-baa4ac835f66', 'ana.compradora@gmail.com', '$2b$12$8sboH57GwUBjk2DveqvctOp2swBjAf2au3oYWRK4HOz8V0M/fJkVa', false,
   'Ana Rodríguez',  '+506 8888-0006', 'Cartago, Costa Rica',  'Apasionada por la artesanía.',        'buyer'),
  ('a7777777-0000-0000-0000-000000000001', 'bruno@comprador.cr',       '$2b$12$8sboH57GwUBjk2DveqvctOp2swBjAf2au3oYWRK4HOz8V0M/fJkVa', false,
   'Bruno Méndez',   '+506 8888-0007', 'Liberia, Guanacaste',  'Coleccionista de cerámica.',          'buyer')
ON CONFLICT (id) DO NOTHING;

-- ── Categories ───────────────────────────────────────────────────────────────

INSERT INTO categories (id, name, slug) VALUES
  ('ca000000-0000-0000-0000-000000000001', 'Cerámica', 'ceramica'),
  ('ca000000-0000-0000-0000-000000000002', 'Textiles', 'textiles'),
  ('ca000000-0000-0000-0000-000000000003', 'Joyería',  'joyeria')
ON CONFLICT (id) DO NOTHING;

-- ── Stores (one per vendor) ──────────────────────────────────────────────────

INSERT INTO stores (id, owner_id, name, description) VALUES
  ('10000000-0000-0000-0000-000000000001', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'Artesanías Chorotega', 'Cerámica y arte precolombino de Guanacaste.'),
  ('10000000-0000-0000-0000-000000000002', 'b1ffcd00-ad1c-4ff9-cc7e-7cc0ce491b22', 'Tejidos de María',     'Textiles tejidos a mano con tintes naturales.')
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
  ('f2000000-0000-0000-0000-000000000010', 'bb000000-0000-0000-0000-000000000005', 'Tamaño', 'Familiar',    0.00,      7)
ON CONFLICT (id) DO NOTHING;

-- ── Variant Images (images belong to variants now) ───────────────────────────
-- Attached to each product's first variant; that is the listing cover.

INSERT INTO product_images (id, variant_id, image_url, is_primary) VALUES
  ('f1000000-0000-0000-0000-000000000001', 'f2000000-0000-0000-0000-000000000001', 'https://picsum.photos/seed/vasija1/600/600', true),
  ('f1000000-0000-0000-0000-000000000002', 'f2000000-0000-0000-0000-000000000001', 'https://picsum.photos/seed/vasija2/600/600', false),
  ('f1000000-0000-0000-0000-000000000003', 'f2000000-0000-0000-0000-000000000022', 'https://picsum.photos/seed/plato1/600/600',  true),
  ('f1000000-0000-0000-0000-000000000006', 'f2000000-0000-0000-0000-000000000004', 'https://picsum.photos/seed/collar1/600/600', true),
  ('f1000000-0000-0000-0000-000000000008', 'f2000000-0000-0000-0000-000000000007', 'https://picsum.photos/seed/rebozo1/600/600', true),
  ('f1000000-0000-0000-0000-000000000009', 'f2000000-0000-0000-0000-000000000023', 'https://picsum.photos/seed/mantel1/600/600', true),
  ('f1000000-0000-0000-0000-000000000012', 'f2000000-0000-0000-0000-000000000009', 'https://picsum.photos/seed/hamaca1/600/600', true),
  ('f1000000-0000-0000-0000-000000000013', 'f2000000-0000-0000-0000-000000000009', 'https://picsum.photos/seed/hamaca2/600/600', false)
ON CONFLICT (id) DO NOTHING;

COMMIT;
