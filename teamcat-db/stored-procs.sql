/*******************************************************************************
 * Database character set: latin1
 * Server version: 5.5
 * Server version build: 5.5.5-10.1.34-MariaDB
 ******************************************************************************/

/*******************************************************************************
 * Selected metadata objects
 * -------------------------
 * Extracted at 2/14/2019 11:19:20 PM
 ******************************************************************************/

/*******************************************************************************
 * Stored Procedures
 * -----------------
 * Extracted at 2/14/2019 11:19:20 PM
 ******************************************************************************/

CREATE PROCEDURE p_delete_device(device_id NVarChar(36))
  NO SQL
  SQL SECURITY INVOKER
begin

DELETE FROM devices
WHERE device_id = f_generate_binary_uuid(device_id);

end
/
CREATE PROCEDURE p_delete_recording(recording_id NVarChar(36))
  NO SQL
  SQL SECURITY INVOKER
begin

DELETE FROM recordings
WHERE recording_id = f_generate_binary_uuid(recording_id);

end
/
CREATE PROCEDURE p_delete_speaker(speaker_id NVarChar(36))
  NO SQL
  SQL SECURITY INVOKER
begin

DELETE FROM speakers
WHERE speaker_id = f_generate_binary_uuid(speaker_id);

end
/
CREATE PROCEDURE p_get_device(device_id NVarChar(36))
  NO SQL
  SQL SECURITY INVOKER
begin

SELECT (device_id_text, handle, created_date, description, location, ip_address_text) FROM devices
WHERE device_id = f_generate_binary_uuid(device_id);

end
/
CREATE PROCEDURE p_get_device_by_date(after_date DateTime, before_date DateTime)
  NO SQL
  SQL SECURITY INVOKER
begin

SELECT (device_id_text, handle, created_date, description, location, ip_address_text) FROM devices
WHERE created_date >= COALESCE(after_date, 0) AND
      created_date <= COALESCE(before_date, NOW());

end
/
CREATE PROCEDURE p_get_device_by_handle(handle NVarChar(50))
  NO SQL
  SQL SECURITY INVOKER
begin

SELECT (device_id_text, handle, created_date, description, location, ip_address_text) FROM devices
WHERE handle LIKE CONCAT_WS(handle, '%', '%');

end
/
CREATE PROCEDURE p_get_device_settings(device_id NVarChar(36))
  NO SQL
  SQL SECURITY INVOKER
begin

SELECT (device_id_text, last_modified, json_settings) FROM device_settings
WHERE device_id = f_generate_binary_uuid(device_id);

end
/
CREATE PROCEDURE p_get_device_settings_by_date(after_date DateTime, before_date DateTime)
  NO SQL
  SQL SECURITY INVOKER
begin

SELECT (device_id_text, last_modified, json_settings) FROM device_settings
WHERE last_modified >= COALESCE(after_date, 0) AND
      last_modified <= COALESCE(before_date, NOW());

end
/
CREATE PROCEDURE p_get_recordings(recording_id NVarChar(36))
  NO SQL
  SQL SECURITY INVOKER
begin

SELECT (recording_id_text, device_id_text, speaker_id_text, recording_time, json_data) FROM recordings
WHERE recording_id = f_generate_binary_uuid(recording_id);

end
/
CREATE PROCEDURE p_get_recordings_by_date(after_date DateTime, before_date DateTime)
  NO SQL
  SQL SECURITY INVOKER
begin

SELECT (recording_id_text, device_id_text, speaker_id_text, recording_time, json_data) FROM recordings
WHERE recording_time  >= COALESCE(after_date, 0) AND
      recording_time <= COALESCE(before_date, NOW());

end
/
CREATE PROCEDURE p_get_recordings_by_device(device_id NVarChar(36))
  NO SQL
  SQL SECURITY INVOKER
begin

SELECT (recording_id_text, device_id_text, speaker_id_text, recording_time, json_data) FROM recordings
WHERE device_id = f_generate_binary_uuid(device_id);

end
/
CREATE PROCEDURE p_get_recordings_by_speaker(speaker_id NVarChar(36))
  NO SQL
  SQL SECURITY INVOKER
begin

SELECT (recording_id_text, device_id_text, speaker_id_text, recording_time, json_data) FROM recordings
WHERE speaker_id = f_generate_binary_uuid(speaker_id);

end
/
CREATE PROCEDURE p_get_speakers(speaker_id NVarChar(36))
  NO SQL
  SQL SECURITY INVOKER
begin

SELECT (speaker_id_text, device_id_text, created_date, json_data) FROM speakers
WHERE speaker_id = f_generate_binary_uuid(speaker_id);

end
/
CREATE PROCEDURE p_get_speakers_by_date(after_date DateTime, before_date DateTime)
  NO SQL
  SQL SECURITY INVOKER
begin

SELECT (speaker_id_text, device_id_text, created_date, json_data) FROM speakers
WHERE created_date >= COALESCE(after_date, 0) AND
      created_date <= COALESCE(before_date, NOW());

end
/
CREATE PROCEDURE p_get_speakers_by_device(device_id NVarChar(36))
  NO SQL
  SQL SECURITY INVOKER
begin

SELECT (speaker_id_text, device_id_text, created_date, json_data) FROM speakers
WHERE device_id = f_generate_binary_uuid(device_id);

end
/
CREATE PROCEDURE p_insert_device(handle NVarChar(50), description NVarChar(100), location NVarChar(50), ip_address_string NVarChar(15), json_settings VarChar(65472), OUT device_id NVarChar(36))
  NO SQL
  SQL SECURITY INVOKER
begin

DECLARE create_date DATETIME DEFAULT NOW();
DECLARE ip_address INTEGER UNSIGNED DEFAULT INET_ATON(ip_address_string);
DECLARE device_id NVARCHAR(36) DEFAULT UUID();
DECLARE device_id_bin BINARY(16) DEFAULT f_generate_binary_uuid(device_id); 

INSERT INTO devices (device_id, handle, created_date, description, location, ip_address)
VALUES (device_id_bin, handle, create_date, description, location, ip_address);

INSERT INTO device_settings (device_id, last_modified, json_settings)
VALUES (device_id_bin, create_date, COALESCE(json_settings, '{}'));

SELECT device_id;
            
end
/
CREATE PROCEDURE p_insert_recording(device_id Binary(16), speaker_id Binary(16), recording_time DateTime, json_data VarChar(65368), OUT recording_id NVarChar(36))
  NO SQL
  SQL SECURITY INVOKER
begin

DECLARE recording_id BINARY(16) DEFAULT UUID();

INSERT INTO recordings (recording_id, device_id, speaker_id, recording_time, json_data)
VALUES (
       f_generate_binary_uuid(recording_id), 
       device_id, 
       speaker_id, 
       COALESCE(recording_time, NOW()), 
       COALESCE(json_data, '{}')
);

SELECT recording_id;

end
/
CREATE PROCEDURE p_insert_speaker(device_id Binary(16), json_data VarChar(65420), OUT speaker_id NVarChar(36))
  NO SQL
  SQL SECURITY INVOKER
begin

DECLARE create_date DATETIME DEFAULT NOW();
DECLARE speaker_id BINARY(16) DEFAULT UUID();

INSERT INTO speakers (speaker_id, device_id, created_date, json_data)
VALUES (
       f_generate_binary_uuid(speaker_id), 
       device_id, 
       create_date, 
       COALESCE(json_data, '{}')
);

SELECT speaker_id;

end
/
CREATE PROCEDURE p_update_device(device_id NVarChar(36), description NVarChar(100), location NVarChar(50), ip_address_string NVarChar(15))
  NO SQL
  SQL SECURITY INVOKER
begin

UPDATE devices
SET description = COALESCE(description, devices.description), 
    location = COALESCE(location, devices.location), 
    ip_address = COALESCE(INET_ATON(ip_address_string), devices.ip_address)
WHERE device_id = f_generate_binary_uuid(device_id); 

end
/
CREATE PROCEDURE p_update_device_settings(device_id NVarChar(36), json_settings VarChar(65472))
  NO SQL
  SQL SECURITY INVOKER
begin

UPDATE device_settings
SET last_modified = NOW(),
    json_settings = COALESCE(json_settings, '{}')
WHERE device_id = f_generate_binary_uuid(device_id);    
    
end
/
CREATE PROCEDURE p_update_speakers(speaker_id NVarChar(36), json_data NVarChar(65420))
  NO SQL
  SQL SECURITY INVOKER
begin

UPDATE speakers
SET json_data = COALESCE(json_data, '{}')
WHERE speaker_id = f_generate_binary_uuid(speaker_id);

end
/
