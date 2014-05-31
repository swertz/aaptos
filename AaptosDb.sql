DROP TABLE IF EXIST supplyReadings;

CREATE TABLE supplyReadings
(
reading int NOT NULL AUTO_INCREMENT,
reading_time timestamp,
instrument varchar(255) NOT NULL,
voltage float NOT NULL,
current  float NOT NULL
);

