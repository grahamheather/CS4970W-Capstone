/*******************************************************************************
 * Database character set: latin1
 * Server version: 5.5
 * Server version build: 5.5.5-10.1.34-MariaDB
 ******************************************************************************/

/*******************************************************************************
 * Selected metadata objects
 * -------------------------
 * Extracted at 3/12/2019 10:11:55 PM
 ******************************************************************************/

/*******************************************************************************
 * Tables
 * ------
 * Extracted at 3/12/2019 10:11:55 PM
 ******************************************************************************/

CREATE TABLE devices (
  device_id        Binary(16) NOT NULL,
  device_id_text   VarChar(36) AS (INSERT ( INSERT ( INSERT ( INSERT ( HEX ( device_id ) , 9 , 0 , '-' ) , 14 , 0 , '-' ) , 19 , 0 , '-' ) , 24 , 0 , '-' )) VIRTUAL CHARACTER SET latin1 COLLATE latin1_swedish_ci,
  handle           NVarChar(50) COLLATE utf8_general_ci NOT NULL,
  created_date     DateTime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_date_iso VarChar(21) AS (DATE_FORMAT ( created_date , '%Y-%m-%dT%TZ' )) VIRTUAL CHARACTER SET latin1 COLLATE latin1_swedish_ci,
  description      NVarChar(100) COLLATE utf8_general_ci,
  location         NVarChar(50) COLLATE utf8_general_ci,
  ip_address       Integer(10) UNSIGNED,
  ip_address_text  VarChar(15) AS (INET_NTOA ( ip_address )) VIRTUAL CHARACTER SET latin1 COLLATE latin1_swedish_ci,
  settings_id      Binary(16),
  settings_id_text VarChar(36) AS (INSERT ( INSERT ( INSERT ( INSERT ( HEX ( settings_id ) , 9 , 0 , '-' ) , 14 , 0 , '-' ) , 19 , 0 , '-' ) , 24 , 0 , '-' )) VIRTUAL CHARACTER SET latin1 COLLATE latin1_swedish_ci, 
  PRIMARY KEY (
      device_id
  )
) ENGINE=InnoDB ROW_FORMAT=COMPACT DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci;
ALTER TABLE devices COMMENT = '';
CREATE TABLE device_settings (
  settings_id      Binary(16) NOT NULL,
  settings_id_text VarChar(36) AS (INSERT ( INSERT ( INSERT ( INSERT ( HEX ( settings_id ) , 9 , 0 , '-' ) , 14 , 0 , '-' ) , 19 , 0 , '-' ) , 24 , 0 , '-' )) VIRTUAL CHARACTER SET latin1 COLLATE latin1_swedish_ci,
  device_id        Binary(16) NOT NULL,
  device_id_text   VarChar(36) AS (INSERT ( INSERT ( INSERT ( INSERT ( HEX ( device_id ) , 9 , 0 , '-' ) , 14 , 0 , '-' ) , 19 , 0 , '-' ) , 24 , 0 , '-' )) VIRTUAL CHARACTER SET latin1 COLLATE latin1_swedish_ci,
  created_date     DateTime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_date_iso VarChar(21) AS (DATE_FORMAT ( created_date , '%Y-%m-%dT%TZ' )) VIRTUAL CHARACTER SET latin1 COLLATE latin1_swedish_ci,
  json_settings    VarChar(65399) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL DEFAULT '{}', 
  PRIMARY KEY (
      settings_id
  )
) ENGINE=InnoDB ROW_FORMAT=COMPACT DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci;
ALTER TABLE device_settings COMMENT = '';
CREATE TABLE recordings (
  recording_id       Binary(16) NOT NULL,
  recording_id_text  VarChar(36) AS (INSERT ( INSERT ( INSERT ( INSERT ( HEX ( recording_id ) , 9 , 0 , '-' ) , 14 , 0 , '-' ) , 19 , 0 , '-' ) , 24 , 0 , '-' )) VIRTUAL CHARACTER SET latin1 COLLATE latin1_swedish_ci,
  device_id          Binary(16),
  device_id_text     VarChar(36) AS (INSERT ( INSERT ( INSERT ( INSERT ( HEX ( device_id ) , 9 , 0 , '-' ) , 14 , 0 , '-' ) , 19 , 0 , '-' ) , 24 , 0 , '-' )) VIRTUAL CHARACTER SET latin1 COLLATE latin1_swedish_ci,
  speaker_id         Binary(16),
  speaker_id_text    VarChar(36) AS (INSERT ( INSERT ( INSERT ( INSERT ( HEX ( speaker_id ) , 9 , 0 , '-' ) , 14 , 0 , '-' ) , 19 , 0 , '-' ) , 24 , 0 , '-' )) VIRTUAL CHARACTER SET latin1 COLLATE latin1_swedish_ci,
  settings_id        Binary(16),
  settings_id_text   VarChar(36) AS (INSERT ( INSERT ( INSERT ( INSERT ( HEX ( settings_id ) , 9 , 0 , '-' ) , 14 , 0 , '-' ) , 19 , 0 , '-' ) , 24 , 0 , '-' )) VIRTUAL CHARACTER SET latin1 COLLATE latin1_swedish_ci,
  recording_time     DateTime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  recording_time_iso VarChar(21) AS (DATE_FORMAT ( recording_time , '%Y-%m-%dT%TZ' )) VIRTUAL CHARACTER SET latin1 COLLATE latin1_swedish_ci,
  json_data          VarChar(65293) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL DEFAULT '{}', 
  PRIMARY KEY (
      recording_id
  )
) ENGINE=InnoDB ROW_FORMAT=COMPACT DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci;
ALTER TABLE recordings COMMENT = '';
CREATE TABLE speakers (
  speaker_id       Binary(16) NOT NULL,
  speaker_id_text  VarChar(36) AS (INSERT ( INSERT ( INSERT ( INSERT ( HEX ( speaker_id ) , 9 , 0 , '-' ) , 14 , 0 , '-' ) , 19 , 0 , '-' ) , 24 , 0 , '-' )) VIRTUAL CHARACTER SET latin1 COLLATE latin1_swedish_ci,
  device_id        Binary(16),
  device_id_text   VarChar(36) AS (INSERT ( INSERT ( INSERT ( INSERT ( HEX ( device_id ) , 9 , 0 , '-' ) , 14 , 0 , '-' ) , 19 , 0 , '-' ) , 24 , 0 , '-' )) VIRTUAL CHARACTER SET latin1 COLLATE latin1_swedish_ci,
  created_date     DateTime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_date_iso VarChar(21) AS (DATE_FORMAT ( created_date , '%Y-%m-%dT%TZ' )) VIRTUAL CHARACTER SET latin1 COLLATE latin1_swedish_ci,
  json_data        VarChar(65399) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL DEFAULT '{}', 
  PRIMARY KEY (
      speaker_id
  )
) ENGINE=InnoDB ROW_FORMAT=COMPACT DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci;
ALTER TABLE speakers COMMENT = '';
/*******************************************************************************
 * Tables
 * ------
 * Extracted at 3/12/2019 10:11:56 PM
 ******************************************************************************/

ALTER TABLE devices
  CHANGE device_id_text device_id_text   VarChar(36) AS (INSERT ( INSERT ( INSERT ( INSERT ( HEX ( device_id ) , 9 , 0 , '-' ) , 14 , 0 , '-' ) , 19 , 0 , '-' ) , 24 , 0 , '-' )) VIRTUAL CHARACTER SET latin1 COLLATE latin1_swedish_ci, 
  CHANGE created_date_iso created_date_iso VarChar(21) AS (DATE_FORMAT ( created_date , '%Y-%m-%dT%TZ' )) VIRTUAL CHARACTER SET latin1 COLLATE latin1_swedish_ci, 
  CHANGE ip_address_text ip_address_text  VarChar(15) AS (INET_NTOA ( ip_address )) VIRTUAL CHARACTER SET latin1 COLLATE latin1_swedish_ci, 
  CHANGE settings_id_text settings_id_text VarChar(36) AS (INSERT ( INSERT ( INSERT ( INSERT ( HEX ( settings_id ) , 9 , 0 , '-' ) , 14 , 0 , '-' ) , 19 , 0 , '-' ) , 24 , 0 , '-' )) VIRTUAL CHARACTER SET latin1 COLLATE latin1_swedish_ci,
  ENGINE=InnoDB ROW_FORMAT=COMPACT DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci;
ALTER TABLE device_settings
  CHANGE settings_id_text settings_id_text VarChar(36) AS (INSERT ( INSERT ( INSERT ( INSERT ( HEX ( settings_id ) , 9 , 0 , '-' ) , 14 , 0 , '-' ) , 19 , 0 , '-' ) , 24 , 0 , '-' )) VIRTUAL CHARACTER SET latin1 COLLATE latin1_swedish_ci, 
  CHANGE device_id_text device_id_text   VarChar(36) AS (INSERT ( INSERT ( INSERT ( INSERT ( HEX ( device_id ) , 9 , 0 , '-' ) , 14 , 0 , '-' ) , 19 , 0 , '-' ) , 24 , 0 , '-' )) VIRTUAL CHARACTER SET latin1 COLLATE latin1_swedish_ci, 
  CHANGE created_date_iso created_date_iso VarChar(21) AS (DATE_FORMAT ( created_date , '%Y-%m-%dT%TZ' )) VIRTUAL CHARACTER SET latin1 COLLATE latin1_swedish_ci,
  ENGINE=InnoDB ROW_FORMAT=COMPACT DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci;
ALTER TABLE recordings
  CHANGE recording_id_text recording_id_text  VarChar(36) AS (INSERT ( INSERT ( INSERT ( INSERT ( HEX ( recording_id ) , 9 , 0 , '-' ) , 14 , 0 , '-' ) , 19 , 0 , '-' ) , 24 , 0 , '-' )) VIRTUAL CHARACTER SET latin1 COLLATE latin1_swedish_ci, 
  CHANGE device_id_text device_id_text     VarChar(36) AS (INSERT ( INSERT ( INSERT ( INSERT ( HEX ( device_id ) , 9 , 0 , '-' ) , 14 , 0 , '-' ) , 19 , 0 , '-' ) , 24 , 0 , '-' )) VIRTUAL CHARACTER SET latin1 COLLATE latin1_swedish_ci, 
  CHANGE speaker_id_text speaker_id_text    VarChar(36) AS (INSERT ( INSERT ( INSERT ( INSERT ( HEX ( speaker_id ) , 9 , 0 , '-' ) , 14 , 0 , '-' ) , 19 , 0 , '-' ) , 24 , 0 , '-' )) VIRTUAL CHARACTER SET latin1 COLLATE latin1_swedish_ci, 
  CHANGE settings_id_text settings_id_text   VarChar(36) AS (INSERT ( INSERT ( INSERT ( INSERT ( HEX ( settings_id ) , 9 , 0 , '-' ) , 14 , 0 , '-' ) , 19 , 0 , '-' ) , 24 , 0 , '-' )) VIRTUAL CHARACTER SET latin1 COLLATE latin1_swedish_ci, 
  CHANGE recording_time_iso recording_time_iso VarChar(21) AS (DATE_FORMAT ( recording_time , '%Y-%m-%dT%TZ' )) VIRTUAL CHARACTER SET latin1 COLLATE latin1_swedish_ci,
  ENGINE=InnoDB ROW_FORMAT=COMPACT DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci;
ALTER TABLE speakers
  CHANGE speaker_id_text speaker_id_text  VarChar(36) AS (INSERT ( INSERT ( INSERT ( INSERT ( HEX ( speaker_id ) , 9 , 0 , '-' ) , 14 , 0 , '-' ) , 19 , 0 , '-' ) , 24 , 0 , '-' )) VIRTUAL CHARACTER SET latin1 COLLATE latin1_swedish_ci, 
  CHANGE device_id_text device_id_text   VarChar(36) AS (INSERT ( INSERT ( INSERT ( INSERT ( HEX ( device_id ) , 9 , 0 , '-' ) , 14 , 0 , '-' ) , 19 , 0 , '-' ) , 24 , 0 , '-' )) VIRTUAL CHARACTER SET latin1 COLLATE latin1_swedish_ci, 
  CHANGE created_date_iso created_date_iso VarChar(21) AS (DATE_FORMAT ( created_date , '%Y-%m-%dT%TZ' )) VIRTUAL CHARACTER SET latin1 COLLATE latin1_swedish_ci,
  ENGINE=InnoDB ROW_FORMAT=COMPACT DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci;
/*******************************************************************************
 * Foreign Key Constraints
 * -----------------------
 * Extracted at 3/12/2019 10:11:56 PM
 ******************************************************************************/

ALTER TABLE devices ADD CONSTRAINT fk_devices_device_settings FOREIGN KEY (settings_id)
  REFERENCES device_settings (settings_id)
  ON DELETE SET NULL 
  ON UPDATE CASCADE;

ALTER TABLE device_settings ADD CONSTRAINT fk_device_settings_devices FOREIGN KEY (device_id)
  REFERENCES devices (device_id)
  ON DELETE CASCADE 
  ON UPDATE CASCADE;

ALTER TABLE recordings ADD CONSTRAINT fk_recordings_devices FOREIGN KEY (device_id)
  REFERENCES devices (device_id)
  ON DELETE SET NULL 
  ON UPDATE CASCADE;

ALTER TABLE recordings ADD CONSTRAINT fk_recordings_device_settings FOREIGN KEY (settings_id)
  REFERENCES device_settings (settings_id)
  ON DELETE SET NULL 
  ON UPDATE CASCADE;

ALTER TABLE recordings ADD CONSTRAINT fk_recordings_speakers FOREIGN KEY (speaker_id)
  REFERENCES speakers (speaker_id)
  ON DELETE SET NULL 
  ON UPDATE CASCADE;

ALTER TABLE speakers ADD CONSTRAINT fk_speakers_devices FOREIGN KEY (device_id)
  REFERENCES devices (device_id)
  ON DELETE SET NULL 
  ON UPDATE CASCADE;

/*******************************************************************************
 * Stored Procedures
 * -----------------
 * Extracted at 3/12/2019 10:11:56 PM
 ******************************************************************************/

CREATE PROCEDURE p_delete_device(device_id VarChar(36))
  NO SQL
  SQL SECURITY INVOKER
begin

DELETE FROM devices
WHERE devices.device_id = f_generate_binary_uuid(device_id);

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
CREATE PROCEDURE p_get_all_devices()
  NO SQL
  SQL SECURITY INVOKER
begin

SELECT d.device_id_text AS device_id, 
       d.handle, 
       d.created_date_iso AS created_date, 
       d.description, 
       d.location, 
       d.ip_address_text AS ip_address,
       s.settings_id_text AS settings_id,
       s.created_date_iso AS settings_created_date,
       s.json_settings 
FROM devices d
LEFT JOIN device_settings s
ON d.settings_id = s.settings_id;

end
/
CREATE PROCEDURE p_get_all_device_settings()
  NO SQL
  SQL SECURITY INVOKER
begin

SELECT settings_id_text AS settings_id, 
       device_id_text AS device_id, 
       created_date_iso AS created_date, 
       json_settings
FROM device_settings;

end
/
CREATE PROCEDURE p_get_all_recordings()
  NO SQL
  SQL SECURITY INVOKER
begin

SELECT recording_id_text AS recording_id, 
       device_id_text AS device_id, 
       speaker_id_text AS speaker_id,
       settings_id_text AS settings_id, 
       recording_time_iso AS recording_time,
       json_data
FROM recordings;

end
/
CREATE PROCEDURE p_get_all_speakers()
  NO SQL
  SQL SECURITY INVOKER
begin

SELECT speaker_id_text AS speaker_id, 
       device_id_text AS device_id, 
       created_date_iso AS created_date, 
       json_data
FROM speakers;

end
/
CREATE PROCEDURE p_get_device(device_id NVarChar(36))
  NO SQL
  SQL SECURITY INVOKER
begin

SELECT d.device_id_text AS device_id, 
       d.handle, 
       d.created_date_iso AS created_date, 
       d.description, 
       d.location, 
       d.ip_address_text AS ip_address,
       s.settings_id_text AS settings_id,
       s.created_date_iso AS settings_created_date,
       s.json_settings 
FROM 
(
     SELECT * 
     FROM devices 
     WHERE devices.device_id = f_generate_binary_uuid(device_id)
) d
LEFT JOIN device_settings s
ON d.settings_id = s.settings_id;

end
/
CREATE PROCEDURE p_get_device_by_date(after_date DateTime, before_date DateTime)
  NO SQL
  SQL SECURITY INVOKER
begin

SELECT d.device_id_text AS device_id, 
       d.handle, 
       d.created_date_iso AS created_date, 
       d.description, 
       d.location, 
       d.ip_address_text AS ip_address,
       s.settings_id_text AS settings_id,
       s.created_date_iso AS settings_created_date,
       s.json_settings 
FROM 
(
     SELECT * 
     FROM devices 
     WHERE created_date >= COALESCE(after_date, 0)
     AND created_date <= COALESCE(before_date, NOW())
) d
LEFT JOIN device_settings s
ON d.settings_id = s.settings_id;

end
/
CREATE PROCEDURE p_get_device_by_handle(handle NVarChar(50))
  NO SQL
  SQL SECURITY INVOKER
begin

SELECT d.device_id_text AS device_id, 
       d.handle, 
       d.created_date_iso AS created_date, 
       d.description, 
       d.location, 
       d.ip_address_text AS ip_address,
       s.settings_id_text AS settings_id,
       s.created_date_iso AS settings_created_date,
       s.json_settings 
FROM 
(
     SELECT * 
     FROM devices 
     WHERE devices.handle 
     LIKE CONCAT_WS(handle, '%', '%')
) d
LEFT JOIN device_settings s
ON d.settings_id = s.settings_id;

end
/
CREATE PROCEDURE p_get_device_settings(settings_id NVarChar(36))
  NO SQL
  SQL SECURITY INVOKER
begin

SELECT settings_id_text AS settings_id,
        device_id_text AS device_id,
        created_date_iso AS created_date, 
       json_settings 
FROM device_settings s
WHERE s.settings_id = f_generate_binary_uuid(settings_id);

end
/
CREATE PROCEDURE p_get_device_settings_by_date(after_date DateTime, before_date DateTime)
  NO SQL
  SQL SECURITY INVOKER
begin

SELECT settings_id_text AS settings_id,
       device_id_text AS device_id,
       created_date_iso AS created_date, 
       json_settings FROM device_settings
WHERE created_date >= COALESCE(after_date, 0) AND
      created_date <= COALESCE(before_date, NOW());

end
/
CREATE PROCEDURE p_get_device_settings_by_device(device_id NVarChar(36))
  NO SQL
  SQL SECURITY INVOKER
begin

SELECT settings_id_text AS settings_id,
        device_id_text AS device_id,
        created_date_iso AS created_date, 
       json_settings 
FROM device_settings s
WHERE s.device_id = f_generate_binary_uuid(device_id);

end
/
CREATE PROCEDURE p_get_recordings(recording_id NVarChar(36))
  NO SQL
  SQL SECURITY INVOKER
begin

SELECT recording_id_text AS recording_id, 
       device_id_text AS device_id, 
       speaker_id_text AS speaker_id,
       settings_id_text AS settings_id, 
       recording_time_iso AS recording_time,
       json_data
FROM recordings r
WHERE r.recording_id = f_generate_binary_uuid(recording_id);

end
/
CREATE PROCEDURE p_get_recordings_by_date(after_date DateTime, before_date DateTime)
  NO SQL
  SQL SECURITY INVOKER
begin

SELECT recording_id_text AS recording_id, 
       device_id_text AS device_id, 
       speaker_id_text AS speaker_id,
       settings_id_text AS settings_id, 
       recording_time_iso AS recording_time,
       json_data
FROM recordings r
WHERE r.recording_time >= COALESCE(after_date, 0) AND
      r.recording_time <= COALESCE(before_date, NOW());

end
/
CREATE PROCEDURE p_get_recordings_by_device(device_id NVarChar(36))
  NO SQL
  SQL SECURITY INVOKER
begin

SELECT recording_id_text AS recording_id, 
       device_id_text AS device_id, 
       speaker_id_text AS speaker_id,
       settings_id_text AS settings_id, 
       recording_time_iso AS recording_time,
       json_data
FROM recordings r
WHERE r.device_id = f_generate_binary_uuid(device_id);

end
/
CREATE PROCEDURE p_get_recordings_by_speaker(speaker_id NVarChar(36))
  NO SQL
  SQL SECURITY INVOKER
begin

SELECT recording_id_text AS recording_id, 
       device_id_text AS device_id, 
       speaker_id_text AS speaker_id,
       settings_id_text AS settings_id, 
       recording_time_iso AS recording_time,
       json_data
FROM recordings r
WHERE r.speaker_id = f_generate_binary_uuid(speaker_id);

end
/
CREATE PROCEDURE p_get_speakers(speaker_id NVarChar(36))
  NO SQL
  SQL SECURITY INVOKER
begin

SELECT speaker_id_text AS speaker_id, 
       device_id_text AS device_id, 
       created_date_iso AS created_date, 
       json_data
FROM speakers s
WHERE s.speaker_id = f_generate_binary_uuid(speaker_id);

end
/
CREATE PROCEDURE p_get_speakers_by_date(after_date DateTime, before_date DateTime)
  NO SQL
  SQL SECURITY INVOKER
begin

SELECT speaker_id_text AS speaker_id, 
       device_id_text AS device_id, 
       created_date_iso AS created_date, 
       json_data
FROM speakers s
WHERE s.created_date >= COALESCE(after_date, 0) AND
      s.created_date <= COALESCE(before_date, NOW());

end
/
CREATE PROCEDURE p_get_speakers_by_device(device_id NVarChar(36))
  NO SQL
  SQL SECURITY INVOKER
begin

SELECT speaker_id_text AS speaker_id, 
       device_id_text AS device_id, 
       created_date_iso AS created_date, 
       json_data
FROM speakers s
WHERE s.device_id = f_generate_binary_uuid(device_id);

end
/
CREATE PROCEDURE p_insert_device(handle NVarChar(50), description NVarChar(100), location NVarChar(50), ip_address_string NVarChar(15), json_settings VarChar(65472))
  NO SQL
  SQL SECURITY INVOKER
begin

DECLARE created_date DATETIME DEFAULT NOW();
DECLARE ip_address INTEGER UNSIGNED DEFAULT INET_ATON(ip_address_string);
DECLARE device_id BINARY(16) DEFAULT f_generate_binary_uuid(UUID());
DECLARE settings_id BINARY(16) DEFAULT f_generate_binary_uuid(UUID());

INSERT INTO devices (device_id, handle, created_date, description, location, ip_address)
VALUES (device_id, handle, created_date, description, location, ip_address);

INSERT INTO device_settings (settings_id, device_id, created_date, json_settings)
VALUES (settings_id, device_id, created_date, COALESCE(json_settings, '{}'));

UPDATE devices d
SET d.settings_id = settings_id
WHERE d.device_id = device_id;

SELECT device_id_text AS device_id, 
       settings_id_text AS settings_id,
       created_date_iso AS created_date
FROM devices d
WHERE d.device_id = device_id;
            
end
/
CREATE PROCEDURE p_insert_recording(device_id NVarChar(36), speaker_id NVarChar(36), settings_id NVarChar(36), recording_time DateTime, json_data VarChar(65293))
  NO SQL
  SQL SECURITY INVOKER
begin

DECLARE recording_id BINARY(16) DEFAULT f_generate_binary_uuid(UUID());

INSERT INTO recordings (recording_id, device_id, speaker_id, settings_id, recording_time, json_data)
VALUES (
       recording_id, 
       f_generate_binary_uuid(device_id),
       f_generate_binary_uuid(speaker_id),
       f_generate_binary_uuid(settings_id), 
       COALESCE(recording_time, NOW()), 
       COALESCE(json_data, '{}')       
);

SELECT recording_id_text AS recording_id,
       recording_time_iso AS recording_time
FROM recordings r
WHERE r.recording_id = recording_id;

end
/
CREATE PROCEDURE p_insert_speaker(device_id NVarChar(36), json_data VarChar(65399))
  NO SQL
  SQL SECURITY INVOKER
begin

DECLARE created_date DATETIME DEFAULT NOW();
DECLARE speaker_id BINARY(16) DEFAULT f_generate_binary_uuid(UUID());

INSERT INTO speakers (speaker_id, device_id, created_date, json_data)
VALUES (
       speaker_id, 
       f_generate_binary_uuid(device_id), 
       created_date, 
       COALESCE(json_data, '{}')
);

SELECT speaker_id_text AS speaker_id,
       created_date_iso AS created_date
FROM speakers s
WHERE s.speaker_id = speaker_id;

end
/
CREATE PROCEDURE p_update_device(device_id NVarChar(36), handle NVarChar(50), description NVarChar(100), location NVarChar(50), ip_address VarChar(15))
  NO SQL
  SQL SECURITY INVOKER
begin

UPDATE devices d
SET handle = COALESCE(handle, d.handle),
    description = COALESCE(description, d.description), 
    location = COALESCE(location, d.location), 
    ip_address = COALESCE(INET_ATON(ip_address), d.ip_address)
WHERE d.device_id = f_generate_binary_uuid(device_id);

end
/
CREATE PROCEDURE p_update_device_settings(device_id NVarChar(36), json_settings VarChar(65472))
  NO SQL
  SQL SECURITY INVOKER
begin

DECLARE settings_id_bin BINARY(16) DEFAULT f_generate_binary_uuid(UUID());
DECLARE device_id_bin BINARY(16) DEFAULT f_generate_binary_uuid(device_id);

INSERT INTO device_settings (settings_id, device_id, created_date, json_settings)
VALUES (settings_id_bin, device_id_bin, NOW(), COALESCE(json_settings, '{}'));

UPDATE devices d
SET d.settings_id = settings_id_bin
WHERE d.device_id = device_id_bin;

SELECT settings_id_text AS settings_id,
       created_date_iso AS created_date
FROM device_settings s
WHERE s.settings_id = settings_id_bin;
    
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
/*******************************************************************************
 * Stored Functions
 * ----------------
 * Extracted at 3/12/2019 10:11:57 PM
 ******************************************************************************/

CREATE FUNCTION f_binary_uuid_to_text(uuid_bin Binary(16))
  RETURNS VarChar(36) CHARACTER SET latin1
  DETERMINISTIC
  NO SQL
  SQL SECURITY INVOKER
begin
  RETURN INSERT(INSERT(INSERT(INSERT(HEX(uuid_bin), 9, 0, '-'), 14, 0, '-'), 19, 0, '-'), 24, 0, '-');
end
/
CREATE FUNCTION f_datetime_to_iso_string(input_date DateTime)
  RETURNS DateTime
  DETERMINISTIC
  NO SQL
  SQL SECURITY INVOKER
begin
  RETURN DATE_FORMAT(input_date, '%Y-%m-%dT%TZ');
end
/
CREATE FUNCTION f_generate_binary_uuid(uuid_string NVarChar(36))
  RETURNS Binary(16)
  DETERMINISTIC
  NO SQL
  SQL SECURITY INVOKER
begin
  RETURN UNHEX(REPLACE(uuid_string,'-',''));
end
/
