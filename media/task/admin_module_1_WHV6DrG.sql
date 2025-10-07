-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Nov 25, 2024 at 12:42 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `facility_management`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin_module`
--

CREATE TABLE `admin_module` (
  `id` bigint(20) NOT NULL,
  `name` varchar(150) NOT NULL,
  `sort_order_no` int(11) NOT NULL,
  `is_vendor` int(11) DEFAULT NULL,
  `is_active` int(11) NOT NULL,
  `status` int(11) NOT NULL,
  `created_on` datetime(6) NOT NULL,
  `updated_on` datetime(6) NOT NULL,
  `created_by` int(11) NOT NULL,
  `updated_by` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;

--
-- Dumping data for table `admin_module`
--

INSERT INTO `admin_module` (`id`, `name`, `sort_order_no`, `is_vendor`, `is_active`, `status`, `created_on`, `updated_on`, `created_by`, `updated_by`) VALUES
(1, 'Masters/Company', 1, 1, 1, 1, '2024-11-25 15:02:48.000000', '2024-11-25 15:02:49.000000', 0, 0),
(2, 'Masters/Employee', 2, 1, 1, 1, '2024-11-25 15:02:48.000000', '2024-11-25 15:02:48.000000', 0, 0),
(3, 'Masters/Category', 3, 0, 1, 1, '2024-11-25 15:02:48.000000', '2024-11-25 15:02:48.000000', 0, 0),
(4, 'Masters/Brand', 4, 0, 1, 1, '2024-11-25 15:04:10.000000', '2024-11-25 15:02:48.000000', 0, 0),
(5, 'Masters/User Privilege', 5, 1, 1, 1, '2024-11-25 15:04:40.000000', '2024-11-25 15:04:41.000000', 0, 0),
(6, 'Masters/Holidays', 6, 0, 1, 1, '2024-11-25 15:05:08.000000', '2024-11-25 15:05:09.000000', 0, 0),
(7, 'Service Frequency', 7, 0, 1, 1, '2024-11-25 15:05:40.000000', '2024-11-25 15:05:40.000000', 0, 0),
(8, 'Asset Library', 8, 0, 1, 1, '2024-11-25 15:06:09.000000', '2024-11-25 15:02:48.000000', 0, 0),
(9, 'Customer', 9, 0, 1, 1, '2024-11-25 15:06:29.000000', '2024-11-25 15:06:30.000000', 0, 0),
(10, 'Vendors', 10, 0, 1, 1, '2024-11-25 15:06:50.000000', '2024-11-25 15:02:48.000000', 0, 0),
(11, 'Projects', 11, 1, 1, 1, '2024-11-25 15:02:48.000000', '2024-11-25 15:02:48.000000', 0, 0),
(12, 'Assets', 12, 1, 1, 1, '2024-11-25 15:07:38.000000', '2024-11-25 15:07:39.000000', 0, 0),
(13, 'Bulk Upload - Assets', 13, 0, 1, 1, '2024-11-25 15:08:18.000000', '2024-11-25 15:08:19.000000', 0, 0),
(14, 'Move Assets', 14, 1, 1, 1, '2024-11-25 15:08:42.000000', '2024-11-25 15:08:43.000000', 0, 0),
(15, 'Complaints', 15, 1, 1, 1, '2024-11-25 15:02:48.000000', '2024-11-25 15:02:48.000000', 0, 0),
(16, 'Appointments', 16, 1, 1, 1, '2024-11-25 15:02:48.000000', '2024-11-25 15:02:48.000000', 0, 0),
(17, 'File Attachments - Appointments', 17, 1, 1, 1, '2024-11-25 15:10:34.000000', '2024-11-25 15:10:35.000000', 0, 0),
(18, 'File Endorsement', 18, 0, 1, 1, '2024-11-25 15:11:06.000000', '2024-11-25 15:11:07.000000', 0, 0),
(19, 'Reopen Appointments', 19, 1, 1, 1, '2024-11-25 15:11:27.000000', '2024-11-25 15:11:28.000000', 0, 0),
(20, 'Transfer Appointments', 20, 1, 1, 1, '2024-11-25 15:11:58.000000', '2024-11-25 15:11:59.000000', 0, 0),
(21, 'Non-Pre Schedule', 21, 1, 1, 1, '2024-11-25 15:02:48.000000', '2024-11-25 15:02:48.000000', 0, 0),
(22, 'QAR Generate', 22, 0, 1, 1, '2024-11-25 15:13:09.000000', '2024-11-25 15:13:10.000000', 0, 0),
(23, 'Calendar', 23, 1, 1, 1, '2024-11-25 15:13:34.000000', '2024-11-25 15:13:35.000000', 0, 0),
(24, 'Monthwise Report', 24, 1, 1, 1, '2024-11-25 15:02:48.000000', '2024-11-25 15:02:48.000000', 0, 0),
(25, 'Outstanding Report', 25, 1, 1, 1, '2024-11-25 15:15:14.000000', '2024-11-25 15:15:16.000000', 0, 0),
(26, 'Completed Report', 26, 1, 1, 1, '2024-11-25 15:16:22.000000', '2024-11-25 15:16:22.000000', 0, 0),
(27, 'Work Hour Report', 27, 1, 1, 1, '2024-11-25 15:02:48.000000', '2024-11-25 15:02:48.000000', 0, 0),
(28, 'KPI Report', 28, 1, 1, 1, '2024-11-25 15:17:17.000000', '2024-11-25 15:17:18.000000', 0, 0),
(29, 'Asset Vendor', 12, 0, 1, 1, '2024-11-25 15:26:21.000000', '2024-11-25 15:26:21.000000', 0, 0);

--
-- Triggers `admin_module`
--
DELIMITER $$
CREATE TRIGGER `trg_modules` AFTER UPDATE ON `admin_module` FOR EACH ROW BEGIN


IF OLD.name<>NEW.name THEN
	insert into audit_trial_modules(tbl_name,tbl_id, column_name, old_value, new_value, is_new, created_on,updated_on,updated_by) values('admin_module',NEW.id,'name',OLD.name,NEW.name,0,OLD.created_on,NOW(),NEW.updated_by);
END IF;	


IF OLD.sort_order_no<>NEW.sort_order_no THEN
	insert into audit_trial_modules(tbl_name,tbl_id, column_name, old_value, new_value, is_new, created_on,updated_on,updated_by) values('admin_module',NEW.id,'sort_order_no',OLD.sort_order_no,NEW.sort_order_no,0,OLD.created_on,NOW(),NEW.updated_by);
END IF;		


IF OLD.is_vendor<>NEW.is_vendor THEN
	insert into audit_trial_modules(tbl_name,tbl_id, column_name, old_value, new_value, is_new, created_on,updated_on,updated_by) values('admin_module',NEW.id,'is_vendor',OLD.is_vendor,NEW.is_vendor,0,OLD.created_on,NOW(),NEW.updated_by);
END IF;		


IF OLD.is_active<>NEW.is_active THEN
	insert into audit_trial_modules(tbl_name,tbl_id, column_name, old_value, new_value, is_new, created_on,updated_on,updated_by) values('admin_module',NEW.id,'is_active',OLD.is_active,NEW.is_active,0,OLD.created_on,NOW(),NEW.updated_by);
END IF;

IF OLD.status<>NEW.status THEN
	insert into audit_trial_modules(tbl_name,tbl_id, column_name, old_value, new_value, is_new, created_on,updated_on,updated_by) values('admin_module',NEW.id,'status',OLD.status,NEW.status,0,OLD.created_on,NOW(),NEW.updated_by);
END IF;

END
$$
DELIMITER ;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `admin_module`
--
ALTER TABLE `admin_module`
  ADD PRIMARY KEY (`id`) USING BTREE;

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `admin_module`
--
ALTER TABLE `admin_module`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=30;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
