CREATE TABLE recordings (
  recording_id      Binary(16) NOT NULL,
  recording_id_text VarChar(36) AS (INSERT ( INSERT ( INSERT ( INSERT ( HEX ( recording_id ) , 9 , 0 , '-' ) , 14 , 0 , '-' ) , 19 , 0 , '-' ) , 24 , 0 , '-' )) VIRTUAL CHARACTER SET latin1 COLLATE latin1_swedish_ci,
  device_id         Binary(16) NOT NULL,
  device_id_text    VarChar(36) AS (INSERT ( INSERT ( INSERT ( INSERT ( HEX ( device_id ) , 9 , 0 , '-' ) , 14 , 0 , '-' ) , 19 , 0 , '-' ) , 24 , 0 , '-' )) VIRTUAL CHARACTER SET latin1 COLLATE latin1_swedish_ci,
  speaker_id        Binary(16) NOT NULL,
  speaker_id_text   VarChar(36) AS (INSERT ( INSERT ( INSERT ( INSERT ( HEX ( speaker_id ) , 9 , 0 , '-' ) , 14 , 0 , '-' ) , 19 , 0 , '-' ) , 24 , 0 , '-' )) VIRTUAL CHARACTER SET latin1 COLLATE latin1_swedish_ci,
  recording_time    DateTime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  json_data         VarChar(65368) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL DEFAULT '{}', 
  PRIMARY KEY (
      recording_id
  )
) ENGINE=InnoDB ROW_FORMAT=COMPACT DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci;
ALTER TABLE recordings COMMENT = '';
ALTER TABLE recordings ADD CONSTRAINT fk_recordings_devices FOREIGN KEY (device_id)
  REFERENCES devices (device_id)
  ON DELETE NO ACTION 
  ON UPDATE NO ACTION;

ALTER TABLE recordings ADD CONSTRAINT fk_recordings_speakers FOREIGN KEY (speaker_id)
  REFERENCES speakers (speaker_id)
  ON DELETE NO ACTION 
  ON UPDATE NO ACTION;


