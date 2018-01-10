# Initial queries
INSERT INTO hf_interest (name, image, typ, description, updated_at, created_at, notification_type) VALUES ('Pokemon Go', 'interest/Pokemongo.png', 'game', 'Get notified when you are close to nearby pokestops.', '2016-07-19 11:33:03.709694', '2016-07-19 11:33:04.000000', '0');

INSERT INTO hf_interest (name, image, typ, description, updated_at, created_at, notification_type) VALUES ('Hifi', 'interest/hifi.png', 'Main', 'Get updates from Hifi.', '2016-08-03 09:57:11.382322', '2016-08-03 10:47:48.000000', '1');

INSERT INTO hf_interestdata (guid, name, lat, lng, image, message, updated_at, created_at, interest_id, distance) VALUES ('0', 'Hifi', 0, 0, 'attachments/t08-17_085405idac688aa3edcdb01.jpg', 'Location + Message = Hifi. ? Let it be a location triggered reminder, message, restaurant review, task or even a scavenger. Simply use your imagination and we are excited to see how you guys use Hifi.', '2016-08-03 12:15:09.953610', '2016-08-03 12:14:40.000000', 2, 11600000);

INSERT INTO hf_interestdata (guid, name, lat, lng, image, message, updated_at, created_at, interest_id, distance) VALUES ('1', 'Hifi', 0, 0, '', 'Welcome to Hifi! Go out and tie messages to places for friends or yourself. Reach the location and get notified.', '2016-08-03 12:17:44.291163', '2016-08-03 12:17:41.000000', 2, 11600000);

# Other useful queries

UPDATE hf_hifipost SET colour = elt(floor(rand()*9) + 1, 'F44336', 'E91E63', '9C27B0', '673AB7', '3F51B5', '2196F3', '03A9F4', '00BCD4', '009688');