CREATE TABLE user (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  roll_number TEXT,
  branch TEXT,
  semester INTEGER,
  cgpi REAL
);
CREATE TABLE preferences (
    roll_number TEXT,
    scode TEXT,
    preference INTEGER,
    CHECK (preference > 0),
    UNIQUE (roll_number,scode),
    UNIQUE (roll_number,preference)
);
CREATE TABLE course (
    scode TEXT,
    sname TEXT,
    PRIMARY KEY (scode)
);
INSERT INTO course VALUES 
('CSO-316','Data Structure'),
('ECO-316','MEMS and Sensor Design'),
('MEO-316','Robotics'),
('ARO-317','Auto CAD'),
('CHO-316','Computational Fluid Dynamics'),
('CMO-316','Catalysis(Principles and Applications)'),
('EEO-316','Neural Networks and Fuzzy Logic');