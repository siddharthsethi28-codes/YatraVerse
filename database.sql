-- ═══════════════════════════════════════════
--   WanderHub Database Schema (MySQL)
--   Run this file in MySQL Workbench or terminal
-- ═══════════════════════════════════════════

CREATE DATABASE IF NOT EXISTS wanderhub_db;
USE wanderhub_db;

-- ── USERS TABLE (travelers who register on website) ──
CREATE TABLE IF NOT EXISTS users (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    first_name  VARCHAR(100) NOT NULL,
    last_name   VARCHAR(100),
    email       VARCHAR(255) NOT NULL UNIQUE,
    phone       VARCHAR(20),
    city        VARCHAR(100),
    interest    VARCHAR(100),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── AGENCIES TABLE (travel agencies who login to dashboard) ──
CREATE TABLE IF NOT EXISTS agencies (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    agency_name  VARCHAR(255) NOT NULL,
    owner_name   VARCHAR(255) NOT NULL,
    email        VARCHAR(255) NOT NULL UNIQUE,
    phone        VARCHAR(20),
    city         VARCHAR(100),
    password     VARCHAR(255) NOT NULL,
    specialization VARCHAR(100),
    rating       DECIMAL(2,1) DEFAULT 4.5,
    verified     BOOLEAN DEFAULT FALSE,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── TOURS TABLE (tours listed by agencies) ──
CREATE TABLE IF NOT EXISTS tours (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    agency_id   INT NOT NULL,
    name        VARCHAR(255) NOT NULL,
    destination VARCHAR(255) NOT NULL,
    duration    VARCHAR(100) NOT NULL,
    price       DECIMAL(10,2) NOT NULL,
    category    VARCHAR(100) NOT NULL,
    group_size  VARCHAR(100),
    description TEXT,
    highlights  TEXT,
    itinerary   TEXT,
    is_hot      BOOLEAN DEFAULT FALSE,
    rating      DECIMAL(2,1) DEFAULT 4.5,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agency_id) REFERENCES agencies(id) ON DELETE CASCADE
);

-- ── SEARCH HISTORY TABLE (user search tracking) ──
CREATE TABLE IF NOT EXISTS search_history (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    query       VARCHAR(255) NOT NULL,
    searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ── SAMPLE AGENCY DATA ──
INSERT INTO agencies (agency_name, owner_name, email, phone, city, password, specialization, rating, verified)
VALUES
('Raj Voyages',      'Rajesh Sharma', 'raj@voyages.com',           '+91 98001 23456', 'Jaipur',    '$2b$10$hashedpassword1', 'Beach & Heritage Tours', 4.9, TRUE),
('Dream Travels',    'Deepa Nair',    'info@dreamtravels.com',     '+91 87654 32109', 'Kochi',     '$2b$10$hashedpassword2', 'Nature & Hill Stations', 4.8, TRUE),
('Holiday Experts',  'Harish Verma',  'hello@holidayexperts.com',  '+91 76543 21098', 'Delhi',     '$2b$10$hashedpassword3', 'Adventure & Treks',      4.7, TRUE),
('Sunshine Tours',   'Sunita Patel',  'sun@shinetravel.com',       '+91 65432 10987', 'Ahmedabad', '$2b$10$hashedpassword4', 'Budget & Family Tours',  4.6, TRUE);

-- ── SAMPLE TOUR DATA ──
INSERT INTO tours (agency_id, name, destination, duration, price, category, group_size, description, highlights, itinerary, is_hot, rating)
VALUES
(1, 'Goa Beach Holiday',      'Goa',             '5 Days / 4 Nights', 8500,  'Beach',       '2-8 people',  'Experience the best of Goa',          'Hotel,Meals,Beach Activities,Sightseeing,Transfer',        'Day 1: Arrival|Day 2: Water Sports|Day 3: South Goa|Day 4: Spice Farm|Day 5: Departure', TRUE,  4.9),
(3, 'Manali Snow Adventure',  'Manali',          '7 Days / 6 Nights', 12000, 'Hill Station','4-12 people', 'Thrilling Himalayan adventure',       'Hotel+Camps,Breakfast,Rohtang Pass,Rafting,Bonfire',       'Day 1: Arrival|Day 2: Solang Valley|Day 3: Rohtang|Day 4: Hadimba|Day 5: Rafting|Day 6: Kullu|Day 7: Return', FALSE, 4.7),
(1, 'Rajasthan Heritage Trail','Rajasthan',      '6 Days / 5 Nights', 9200,  'Heritage',    '2-10 people', 'Royal Rajasthan journey',             'Heritage Hotel,All Meals,Fort Visits,Desert Safari,Show',  'Day 1: Jaipur|Day 2: Jaipur Sightseeing|Day 3: Jodhpur|Day 4: Jodhpur|Day 5: Udaipur|Day 6: Departure', FALSE, 4.8),
(2, 'Kerala Backwater Bliss', 'Kerala',          '5 Days / 4 Nights', 10500, 'Nature',      '2-6 people',  'Emerald backwaters adventure',        'Houseboat,All Meals,Spice Tour,Elephant,Kathakali',        'Day 1: Kochi|Day 2: Munnar|Day 3: Periyar|Day 4: Houseboat|Day 5: Departure', TRUE,  4.9),
(3, 'Kashmir Valley Dream',   'Kashmir',         '6 Days / 5 Nights', 15000, 'Hill Station','2-8 people',  'Paradise on earth',                   'Houseboat+Hotel,All Meals,Shikara,Cable Car,Pahalgam',     'Day 1: Srinagar|Day 2: Mughal Gardens|Day 3: Gulmarg|Day 4: Pahalgam|Day 5: Sonamarg|Day 6: Departure', TRUE,  4.8),
(4, 'Andaman Island Escape',  'Andaman Islands', '6 Days / 5 Nights', 18000, 'Beach',       '2-8 people',  'Pristine coral reefs and beaches',    'Beach Resort,Breakfast,Scuba Diving,Glass Boat,Jail Tour', 'Day 1: Port Blair|Day 2: Ross Island|Day 3: Havelock|Day 4: Elephant Beach|Day 5: Neil Island|Day 6: Departure', FALSE, 4.7);
