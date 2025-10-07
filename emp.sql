-- --------------------------------------------------------
-- Host:                         69.57.172.213
-- Server version:               8.0.36 - Source distribution
-- Server OS:                    Linux
-- HeidiSQL Version:             12.6.0.6765
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Dumping database structure for ideapro_erp
CREATE DATABASE IF NOT EXISTS `ideapro_erp` /*!40100 DEFAULT CHARACTER SET utf8mb3 */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `ideapro_erp`;

-- Dumping structure for table ideapro_erp.employee
CREATE TABLE IF NOT EXISTS `employee` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `company_id` int DEFAULT NULL,
  `is_admin` int DEFAULT '0',
  `supervisor_id` int DEFAULT '0',
  `employee_code` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `employee_role` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `user_role` varchar(50) COLLATE utf8mb4_general_ci DEFAULT '0',
  `name` varchar(150) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `username` varchar(150) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `finger_print` varchar(150) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `address_line1` varchar(150) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `address_line2` varchar(150) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `password` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `city` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `country` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `postal_code` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `phone` varchar(15) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `mobile` varchar(15) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `email` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `certificate` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `is_scheduler` tinyint(1) unsigned zerofill DEFAULT '0',
  `is_superadmin` tinyint(1) DEFAULT '0',
  `is_technician` tinyint(1) DEFAULT '0',
  `is_supervisor` tinyint(1) unsigned zerofill DEFAULT '0',
  `is_foreigner` tinyint(1) DEFAULT '0',
  `is_gps` tinyint(1) DEFAULT '0',
  `is_photo` tinyint(1) DEFAULT '0',
  `is_qr` tinyint(1) unsigned zerofill DEFAULT '0',
  `is_signature` tinyint(1) DEFAULT '0',
  `vehicle_number` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `color` varchar(7) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `is_active` int DEFAULT NULL,
  `status` int DEFAULT NULL,
  `created_on` datetime(6) DEFAULT NULL,
  `updated_on` datetime(6) DEFAULT NULL,
  `created_by` int DEFAULT NULL,
  `updated_by` int DEFAULT NULL,
  `device_id` varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `fcm_token` varchar(250) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `auth_id` int DEFAULT NULL,
  `ms_token` text COLLATE utf8mb4_general_ci,
  `expires_on` datetime DEFAULT NULL,
  `login_from` varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `id` (`id`,`company_id`,`is_superadmin`,`supervisor_id`,`is_active`,`status`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;

-- Dumping data for table ideapro_erp.employee: ~6 rows (approximately)
INSERT INTO `employee` (`id`, `company_id`, `is_admin`, `supervisor_id`, `employee_code`, `employee_role`, `user_role`, `name`, `username`, `finger_print`, `address_line1`, `address_line2`, `password`, `city`, `country`, `postal_code`, `phone`, `mobile`, `email`, `certificate`, `is_scheduler`, `is_superadmin`, `is_technician`, `is_supervisor`, `is_foreigner`, `is_gps`, `is_photo`, `is_qr`, `is_signature`, `vehicle_number`, `color`, `is_active`, `status`, `created_on`, `updated_on`, `created_by`, `updated_by`, `device_id`, `fcm_token`, `auth_id`, `ms_token`, `expires_on`, `login_from`) VALUES
	(1, 0, 0, 0, NULL, 'superadmin', '0', 'Project manager', 'Project manager', NULL, NULL, NULL, 'e10adc3949ba59abbe56e057f20f883e', 'Tirupur', 'Tirupur', '0', NULL, NULL, 'admin@projectmanager.com', NULL, 0, 1, 0, 0, 0, 0, 0, 0, 0, NULL, NULL, 1, 1, '2024-12-04 13:24:29.000000', '2024-12-04 13:24:30.000000', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
	(2, 1, 1, 0, 'GNP-000001', 'admin', '', 'Genplus Innovations', 'Genplus Innovations', NULL, 'Rp Complex, 11/1, Pudhu Thottam Main street, above State Bank, Town Extn, Tiruppur, Tamil Nadu 641604', 'Rp Complex, 11/1, Pudhu Thottam Main street, above State Bank, Town Extn, Tiruppur, Tamil Nadu 641604', 'e10adc3949ba59abbe56e057f20f883e', 'Tirupur', 'India', 'Tamilnadu', '932147568', '', 'genplusinnovations@gmail.com', '', 0, 0, 0, 1, 0, 0, 0, 0, 0, '', '', 1, 1, '2024-12-04 08:05:54.212405', '2024-12-04 08:05:54.212407', 1, 1, '', '', NULL, '', NULL, ''),
	(3, 1, 0, 2, 'GNP-000002', 'staff', '6', 'Dhivyadharshini', 'Dhivyadharshini', 'dhivya@gmail.com', 'Kangeyam Road, Tirupur', 'Kangeyam Road, Tirupur', 'e10adc3949ba59abbe56e057f20f883e', 'Tirupur', 'India', '0', '9632587417', '9632587415', 'dhivya@gmail.com', '', 0, 0, 0, 0, 0, 0, 0, 0, 0, '', '#cb86f9', 1, 1, '2024-12-04 09:06:52.915249', '2024-12-04 09:06:52.915254', 2, 2, '', '', NULL, '', NULL, ''),
	(4, 1, 0, 2, 'GNP-000003', 'staff', '6', 'Harishini', 'Harishini', 'harishini@gmail.com', 'Kovilvazi, Tirupur', 'Kovilvazi, Tirupur', 'e10adc3949ba59abbe56e057f20f883e', 'Tirupur', 'India', '', '9345756412', '9360208684', 'harishini@gmail.com', '', 0, 0, 0, 0, 0, 0, 0, 0, 0, '', '#56f0fb', 1, 1, '2024-12-04 09:08:54.588396', '2024-12-04 09:08:54.588399', 2, 2, '', '', NULL, '', NULL, ''),
	(5, 1, 0, 2, 'GNP-000004', 'staff', '6', 'Janani', 'Janani', 'janani@gmail.com', 'Veerapandi', 'Veerapandi', 'e10adc3949ba59abbe56e057f20f883e', 'Tirupur', 'India', '', '8521473698', '7412589635', 'janani@gmail.com', '', 0, 0, 0, 0, 0, 0, 0, 0, 0, '', '#000000', 1, 1, '2024-12-04 09:10:23.923171', '2024-12-04 09:10:23.923173', 2, 2, '', '', NULL, '', NULL, ''),
	(6, 2, 1, 0, 'IP-000001', 'admin', '', 'Ragu', 'Ragu', NULL, 'Singapore', 'Singapore', 'e10adc3949ba59abbe56e057f20f883e', 'Singapore', 'Singapore', 'Singapore', '9876543210', '', 'sivaraguram@gmail.com', '', 0, 0, 0, 0, 0, 0, 0, 0, 0, '', '', 1, 1, '2024-12-06 07:17:48.414174', '2024-12-06 07:17:48.414178', 1, 1, '', '', NULL, '', NULL, '');

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
