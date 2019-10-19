CREATE TABLE user (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  roll_number TEXT,
  branch TEXT,
  semester INTEGER,
  cgpi REAL
);