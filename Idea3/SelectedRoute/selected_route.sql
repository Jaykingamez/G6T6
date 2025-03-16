-- Create the SelectedRoute database
CREATE DATABASE IF NOT EXISTS `SelectedRoute` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;

-- Use the SelectedRoute database
USE `SelectedRoute`;

-- Create the SelectedRoute table
DROP TABLE IF EXISTS `SelectedRoute`;
CREATE TABLE IF NOT EXISTS `SelectedRoute` (
  `RouteID` int(11) NOT NULL AUTO_INCREMENT,
  `BusStopCode` int(11) NOT NULL,
  `BusID` char(11) NOT NULL,
  PRIMARY KEY (`RouteID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Add some sample data (optional)
INSERT INTO `SelectedRoute` (`BusStopCode`, `BusID`) VALUES
(1001, 501),
(1002, 502),
(1003, 503);

COMMIT;
