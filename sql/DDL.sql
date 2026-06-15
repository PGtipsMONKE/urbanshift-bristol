CREATE TABLE customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_name VARCHAR(250),
    customer_size VARCHAR(50),
    city VARCHAR(100),
    signup_date DATE,
    account_manager VARCHAR(255),
    industry VARCHAR(100),
    payment_terms_days INT

);

CREATE TABLE couriers (
    courier_id VARCHAR(50) PRIMARY KEY,
    hire_date DATE,
    employment_type VARCHAR(50),
    city VARCHAR(100),
    shift_pattern VARCHAR(50)
);

CREATE TABLE deliveries (
    delivery_id VARCHAR(50) PRIMARY KEY,
    delivery_date DATE, 
    customer_id VARCHAR(50),
    courier_id VARCHAR(50),
    city VARCHAR(100),
    time_taken_minutes INT,
    delivery_status VARCHAR(50),
    revenue_gdp DECIMAL(10,2),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (courier_id) REFERENCES couriers(courier_id)

);


CREATE TABLE incidents (
    incident_id VARCHAR(50) PRIMARY KEY,
    delivery_id VARCHAR(50),
    incident_date DATE,
    incident_type VARCHAR(100),
    resolution_status VARCHAR(100),
    FOREIGN KEY (delivery_id) REFERENCES deliveries(delivery_id)
);

