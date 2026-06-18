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
    revenue_gbp DECIMAL(10,2),
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


CREATE OR REPLACE VIEW urbanshift.vw_customer_delivery_summary AS
SELECT
    -- Customer attributes
    c.customer_id,
    c.customer_name,
    c.customer_size,

    -- Delivery attributes
    d.delivery_id,
    d.city,
    d.delivery_date,
    d.revenue_gbp,

    -- Courier attributes (shift pattern lives here)
    cr.courier_id,
    cr.shift_pattern,
    cr.employment_type,

    -- Incident attributes
    i.incident_id,
    i.incident_type,
    CASE WHEN i.incident_id IS NOT NULL THEN 1 ELSE 0 END AS incident_flag

FROM urbanshift.customers c
JOIN urbanshift.deliveries d
    ON c.customer_id = d.customer_id
JOIN urbanshift.couriers cr
    ON d.courier_id = cr.courier_id
LEFT JOIN urbanshift.incidents i
    ON d.delivery_id = i.delivery_id;
