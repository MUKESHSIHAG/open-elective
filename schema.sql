CREATE TABLE user (
  id TEXT NOT NULL,
  name TEXT NOT NULL,
  email TEXT UNIQUE PRIMARY KEY,
  roll_number TEXT,
  branch TEXT,
  branch_code TEXT,
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
CREATE TABLE alloted (
    roll_number TEXT,
    scode TEXT,
    PRIMARY KEY (roll_number)
);
INSERT INTO course VALUES
('PHO-325','NUCLEAR SCIENCE AND ITS APPLICATIONS'),
('PHO-316','QUANTUM MECHANICS & ITS APPLICATIONS'),
('MSO-326(b)','FUEL CELL AND HYDROGEN ENERGY'),
('MSO-326(a)','NANO-MATERIALS & TECHNOLOGY'),
('MSO-317','FUEL CELL & HYDROGEN ENERGY'),
('MEO-325','MODELLING AND SIMULATION'),
('MEO-316','QUALITY ENGINEERING'),
('MAO-325(b)','STATISTICAL TESTING & QUALITY CONTROL'),
('MAO-316(b)','LINEAR ALGEBRA'),
('MAO-316(a)','LINEAR ALGEBRA'),
('HUO-325','DYNAMICS OF BEHAVIORAL SCIENCES IN INDUSTRY'),
('HUO-316(d)','DYNAMICS OF BEHAVIOURAL SCIENCES IN INDUSTRY'),
('HUO-316(a)','INDIAN BUSINESS ENVIRONMENT'),
('ENO-316','RENEWABLE ENERGY RESOURCES'),
('EEO-325(b)','OPTIMIZATION TECHNIQUES'),
('EEO-316(a)','NEURAL NETWORKS AND FUZZY LOGIC'),
('ECO-325(b)','TELECOMMUNICATION SYSTEM'),
('ECO-325(a)','MEMS & SENSOR DESIGN'),
('ECO-325','TELECOMMUNICATION SYSTEM'),
('ECO-316(a)','MEMS & SENSOR DESIGN'),
('CSO-324','COMPUTER GRAPHICS'),
('CSO-316','DATA STRUCTURE'),
('CMO-329','BIO-NANOTECHNOLOGY'),
('CMO-317','ENGINEERING PLASTICS AND SPECIALTY POLYMERS'),
('CHO-326','INDUSTRIAL SAFETY & RISK MANAGEMENT'),
('CHO-316','COMPUTATIONAL FLUID DYNAMICS'),
('CEO-325(a)','CPM & PERT'),
('CEO-316','CPM & PERT'),
('ARO-317','AUTO CAD');