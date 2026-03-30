

CREATE TABLE experiments (
    experiment_id SERIAL PRIMARY KEY,
    name TEXT,
    hypothesis TEXT,
    start_date DATE,
    end_date DATE,
    status TEXT, -- running / completed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



CREATE TABLE users (
    user_id INT PRIMARY KEY,
    signup_date DATE,
    country TEXT,
    platform TEXT, -- iOS / Android / Web
    is_active BOOLEAN
);



CREATE TABLE experiment_assignments (
    assignment_id SERIAL PRIMARY KEY,
    experiment_id INT REFERENCES experiments(experiment_id),
    user_id INT REFERENCES users(user_id),
    variant TEXT, -- control / treatment
    assigned_at TIMESTAMP
);



CREATE TABLE events (
    event_id SERIAL PRIMARY KEY,
    user_id INT,
    event_type TEXT, -- view_product, add_to_cart, checkout_start
    event_timestamp TIMESTAMP,
    session_id TEXT
);



CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    user_id INT,
    order_value NUMERIC,
    order_timestamp TIMESTAMP,
    experiment_id INT,
    variant TEXT
);


CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    user_id INT,
    session_start TIMESTAMP,
    session_end TIMESTAMP
);

