CREATE DATABASE aitrading;
USE aitrading;
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone_number VARCHAR(15) NOT NULL,
    date_of_birth DATE NOT NULL,
    pan_tax_id VARCHAR(20) NOT NULL UNIQUE,
    country_address TEXT NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
    
CREATE TABLE stocks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol_image VARCHAR(255),        
    company VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    change_value VARCHAR(10),
    suggestion ENUM('Buy', 'Hold', 'Avoid') DEFAULT 'Hold'
);

INSERT INTO stocks (symbol_image, company, price, change_value, suggestion)
VALUES ('/assets/images/tcs.png', 'Tata Consultancy Services', 3700.00, '+15.00', 'Buy');
