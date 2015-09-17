CREATE DEFINER=`blackbox`@`%` PROCEDURE `aggregated_data_export`(IN symbol       INT(10),
                                          IN period       INT(10),
                                          IN start_date   INT(10),
                                          IN end_date     INT(10))
BEGIN
INSERT INTO data_1h SELECT round(timestamp DIV period) * period AS timestamp,
  CAST(SUBSTRING_INDEX(GROUP_CONCAT(CAST((bid + offer) / 2.0 AS CHAR) ORDER BY timestamp), ',', 1 ) AS DECIMAL(16, 8)) AS open,
  MAX((bid + offer) / 2.0) AS high,
  MIN((bid + offer) / 2.0) AS low,
  CAST(SUBSTRING_INDEX(GROUP_CONCAT(CAST((bid + offer) / 2.0 AS CHAR) ORDER BY timestamp DESC), ',', 1 ) AS DECIMAL(16, 8)) AS close,
  SUM(volume) AS volume
 FROM tick_data2
 WHERE symbol_id=symbol
  AND timestamp BETWEEN start_date AND end_date
 GROUP BY round(timestamp DIV period)
 ORDER BY timestamp;
END