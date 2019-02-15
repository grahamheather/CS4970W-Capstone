/*******************************************************************************
 * Database character set: latin1
 * Server version: 5.5
 * Server version build: 5.5.5-10.1.34-MariaDB
 ******************************************************************************/

/*******************************************************************************
 * Selected metadata objects
 * -------------------------
 * Extracted at 2/14/2019 11:20:26 PM
 ******************************************************************************/

/*******************************************************************************
 * Stored Functions
 * ----------------
 * Extracted at 2/14/2019 11:20:26 PM
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
CREATE FUNCTION f_generate_binary_uuid(uuid_string NVarChar(36))
  RETURNS Binary(16)
  DETERMINISTIC
  NO SQL
  SQL SECURITY INVOKER
begin
  RETURN UNHEX(REPLACE(uuid_string,'-',''));
end
/
