INSERT INTO users (id, username, first_name, nickname, major, points)
VALUES (694245594, 'admin', 'Alireza', 'Admin', 'تجربی', 0)
ON CONFLICT (id) DO NOTHING;
