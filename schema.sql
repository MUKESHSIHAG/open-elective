CREATE TABLE IF NOT EXISTS users (
  id TEXT NOT NULL,
  name TEXT NOT NULL,
  email TEXT UNIQUE PRIMARY KEY,
  roll_number TEXT,
  branch TEXT,
  branch_code TEXT,
  semester INTEGER,
  cgpi REAL
);
CREATE TABLE IF NOT EXISTS preferences (
    roll_number TEXT,
    scode TEXT,
    preference INTEGER,
    CHECK (preference > 0),
    UNIQUE (roll_number,scode),
    UNIQUE (roll_number,preference)
);
CREATE TABLE IF NOT EXISTS course (
    scode TEXT,
    sname TEXT,
    PRIMARY KEY (scode)
);
CREATE TABLE IF NOT EXISTS alloted (
    roll_number TEXT,
    scode TEXT,
    PRIMARY KEY (roll_number)
);
INSERT INTO course VALUES
('CEO-325', 'FINITE ELEMENT METHOD'),
('EEO-325', 'OPTIMIZATION TECHNIQUES'),
('MEO-325', 'MODELING AND SIMULATION'),
('ECO-325(a)', 'MEMS & SENSOR DESIGN'),
('ECO-325(b)', 'TELECOMMUNICATION SYSTEMS'),
('CSO-324', 'COMPUTER GRAPHICS'),
('CHO-326(b)', 'ENGINEERING OPTIMIZATION'),
('HUO-325', 'DYNAMICS OF BEHAVIORAL SCIENCES IN INDUSTRY'),
('CMO-329', 'BIONANOTECHNOLOGY'),
('MAO-325(b)', 'STATISTICAL TESTING & QUALITY CONTROL');