CREATE TABLE devices (
  device_id       Binary(16) NOT NULL,
  device_id_text  VarChar(36) AS (INSERT ( INSERT ( INSERT ( INSERT ( HEX ( device_id ) , 9 , 0 , '-' ) , 14 , 0 , '-' ) , 19 , 0 , '-' ) , 24 , 0 , '-' )) VIRTUAL CHARACTER SET latin1 COLLATE latin1_swedish_ci,
  handle          NVarChar(50) COLLATE utf8_general_ci NOT NULL,
  created_date    DateTime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  description     NVarChar(100) COLLATE utf8_general_ci,
  location        NVarChar(50) COLLATE utf8_general_ci,
  ip_address      Integer(10) UNSIGNED,
  ip_address_text VarChar(15) AS (INET_NTOA ( ip_address )) VIRTUAL CHARACTER SET latin1 COLLATE latin1_swedish_ci, 
  PRIMARY KEY (
      device_id
  )
) ENGINE=InnoDB ROW_FORMAT=COMPACT DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci;
ALTER TABLE devices COMMENT = '';

