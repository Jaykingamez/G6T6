-- phpMyAdmin SQL Dump
-- version 4.7.4
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Mar 15, 2025 at 09:00 AM
-- Server version: 5.7.19
-- PHP Version: 7.1.9

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `transactions`
--
CREATE DATABASE IF NOT EXISTS `transactions` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `transactions`;

-- --------------------------------------------------------

--
-- Table structure for table `transactions`
--

DROP TABLE IF EXISTS `transactions`;
CREATE TABLE IF NOT EXISTS `transactions` (
  `TransactionId` int(11) NOT NULL AUTO_INCREMENT,
  `UserId` int(11) NOT NULL,
  `CardId` int(11) NOT NULL,
  `Amount` decimal(10,2) NOT NULL,
  `PaymentMethod` enum('STRIPE','PAYPAL') DEFAULT NULL,
  `Status` enum('SUCCESS','FAILED','PENDING') NOT NULL DEFAULT 'PENDING',
  `PreviousBalance` decimal(10,2) NOT NULL,
  `NewBalance` decimal(10,2) NOT NULL,
  `PaymentId` int(11) NOT NULL,
  `CreatedAt` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `UpdatedAt` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`TransactionId`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `transactions`
--

INSERT INTO `transactions` (`TransactionId`, `UserId`, `CardId`, `Amount`, `PaymentMethod`, `Status`, `PreviousBalance`, `NewBalance`, `PaymentId`, `CreatedAt`, `UpdatedAt`) VALUES
(1, 1, 1, '10.00', 'STRIPE', 'SUCCESS', '0.00', '10.00', 1, '2025-03-15 09:00:00', '2025-03-15 09:00:00'),
(2, 2, 2, '20.00', 'PAYPAL', 'PENDING', '0.00', '20.00', 2, '2025-03-15 09:00:00', '2025-03-15 09:00:00');

COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
