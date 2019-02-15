CREATE TABLE device_settings (
  device_id      Binary(16) NOT NULL,
  device_id_text VarChar(36) AS (INSERT ( INSERT ( INSERT ( INSERT ( HEX ( device_id ) , 9 , 0 , '-' ) , 14 , 0 , '-' ) , 19 , 0 , '-' ) , 24 , 0 , '-' )) VIRTUAL CHARACTER SET latin1 COLLATE latin1_swedish_ci,
  last_modified  DateTime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  json_settings  VarChar(65472) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL DEFAULT '{}', 
  PRIMARY KEY (
      device_id
  )
) ENGINE=InnoDB ROW_FORMAT=COMPACT DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci;
ALTER TABLE device_settings COMMENT = '';
ALTER TABLE device_settings ADD CONSTRAINT fk_device_settings_devices FOREIGN KEY (device_id)
  REFERENCES devices (device_id)
  ON DELETE CASCADE 
  ON UPDATE NO ACTION;


