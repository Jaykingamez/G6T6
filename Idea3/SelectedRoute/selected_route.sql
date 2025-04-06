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
  `UserID` int(11) NOT NULL,
  `RouteName` char (100) NOT NULL,
  PRIMARY KEY (`RouteID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Add some sample data
INSERT INTO `SelectedRoute` (`BusStopCode`, `BusID`,`UserID`, `RouteName`) VALUES
(4121, 147,"3", "From 520817 to SMU SCIS"),
(75209, 46,"3", "From 520817 to SMU SCIS"),
(75089, 293,"3", "From 520717 to Pasir Ris"),
(75209, 46,"3", "From 520717 to Pasir Ris")
;

COMMIT;
