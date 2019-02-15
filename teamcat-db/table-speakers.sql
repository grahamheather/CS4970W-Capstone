CREATE TABLE speakers (
  speaker_id      Binary(16) NOT NULL,
  speaker_id_text VarChar(36) AS (INSERT ( INSERT ( INSERT ( INSERT ( HEX ( speaker_id ) , 9 , 0 , '-' ) , 14 , 0 , '-' ) , 19 , 0 , '-' ) , 24 , 0 , '-' )) VIRTUAL CHARACTER SET latin1 COLLATE latin1_swedish_ci,
  device_id       Binary(16) NOT NULL,
  device_id_text  VarChar(36) AS (INSERT ( INSERT ( INSERT ( INSERT ( HEX ( device_id ) , 9 , 0 , '-' ) , 14 , 0 , '-' ) , 19 , 0 , '-' ) , 24 , 0 , '-' )) VIRTUAL CHARACTER SET latin1 COLLATE latin1_swedish_ci,
  created_date    DateTime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  json_data       VarChar(65420) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL DEFAULT '{}', 
  PRIMARY KEY (
      speaker_id
  )
) ENGINE=InnoDB ROW_FORMAT=COMPACT DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci;
ALTER TABLE speakers COMMENT = '';
ALTER TABLE speakers ADD CONSTRAINT fk_speakers_devices FOREIGN KEY (device_id)
  REFERENCES devices (device_id)
  ON DELETE NO ACTION 
  ON UPDATE NO ACTION;


