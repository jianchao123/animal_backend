-- MySQL dump 10.13  Distrib 5.7.16, for Linux (x86_64)
--
-- Host: 127.0.0.1    Database: shopping
-- ------------------------------------------------------
-- Server version	5.7.16-0ubuntu0.16.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `administrator`
--

DROP TABLE IF EXISTS `administrator`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `administrator` (
  `userprofilebasic_ptr_id` int(11) NOT NULL,
  PRIMARY KEY (`userprofilebasic_ptr_id`),
  CONSTRAINT `admini_userprofilebasic_ptr_id_4677ca02_fk_user_profile_basic_id` FOREIGN KEY (`userprofilebasic_ptr_id`) REFERENCES `user_profile_basic` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `administrator`
--

LOCK TABLES `administrator` WRITE;
/*!40000 ALTER TABLE `administrator` DISABLE KEYS */;
/*!40000 ALTER TABLE `administrator` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `agency_record`
--

DROP TABLE IF EXISTS `agency_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `agency_record` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `agency_trade_no` varchar(128) DEFAULT NULL,
  `amounts` decimal(32,16) DEFAULT NULL,
  `units` int(11) DEFAULT NULL,
  `deposit_time` datetime(6) DEFAULT NULL,
  `status` int(11) DEFAULT NULL,
  `remark` varchar(128) DEFAULT NULL,
  `to_recycle_businessman_id` int(11),
  PRIMARY KEY (`id`),
  KEY `agency_record_0b0c6edd` (`to_recycle_businessman_id`),
  CONSTRAINT `d64ce171481abd1665ad8bae1b90bd68` FOREIGN KEY (`to_recycle_businessman_id`) REFERENCES `recycle_businessman` (`userprofilebasic_ptr_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `agency_record`
--

LOCK TABLES `agency_record` WRITE;
/*!40000 ALTER TABLE `agency_record` DISABLE KEYS */;
/*!40000 ALTER TABLE `agency_record` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
INSERT INTO `auth_group` VALUES (2,'回收商'),(3,'玩家'),(1,'管理员');
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissi_permission_id_84c5c92e_fk_auth_permission_id` (`permission_id`),
  CONSTRAINT `auth_group_permissi_permission_id_84c5c92e_fk_auth_permission_id` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=109 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
INSERT INTO `auth_group_permissions` VALUES (1,1,1),(2,1,2),(3,1,3),(4,1,4),(5,1,5),(6,1,6),(7,1,7),(8,1,8),(9,1,9),(10,1,10),(11,1,11),(12,1,12),(13,1,13),(14,1,14),(15,1,15),(16,1,16),(17,1,17),(18,1,18),(19,1,19),(20,1,20),(21,1,21),(22,1,22),(23,1,23),(24,1,24),(25,1,25),(26,1,26),(27,1,27),(28,1,28),(29,1,29),(30,1,30),(31,1,31),(32,1,32),(33,1,33),(34,1,34),(35,1,35),(36,1,36),(37,1,37),(38,1,38),(39,1,39),(40,1,40),(41,1,41),(42,1,42),(43,1,43),(44,1,44),(45,1,45),(46,1,46),(47,1,47),(48,1,48),(49,1,49),(50,1,50),(51,1,51),(52,1,52),(53,1,53),(54,1,54),(55,1,55),(56,1,56),(57,1,57),(58,1,58),(59,1,59),(60,1,60),(61,1,61),(62,1,62),(63,1,63),(64,1,64),(65,1,65),(66,1,66),(67,1,67),(68,1,68),(69,1,69),(70,1,70),(71,1,71),(72,1,72),(73,1,73),(74,1,74),(75,1,75),(76,1,76),(77,1,77),(78,1,78),(79,1,79),(80,1,80),(81,1,81),(82,1,82),(83,1,83),(84,1,84),(85,1,85),(86,1,86),(87,1,87),(88,1,88),(89,1,89),(90,1,90),(91,1,91),(92,1,92),(93,1,93),(94,1,94),(95,1,95),(96,1,96),(97,1,97),(98,1,98),(99,1,99),(100,1,100),(101,1,101),(102,1,102),(103,1,103),(104,1,104),(105,1,105),(106,2,100),(107,2,101),(108,2,102);
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permissi_content_type_id_2f476e4b_fk_django_content_type_id` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=106 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can add permission',2,'add_permission'),(5,'Can change permission',2,'change_permission'),(6,'Can delete permission',2,'delete_permission'),(7,'Can add group',3,'add_group'),(8,'Can change group',3,'change_group'),(9,'Can delete group',3,'delete_group'),(10,'Can add content type',4,'add_contenttype'),(11,'Can change content type',4,'change_contenttype'),(12,'Can delete content type',4,'delete_contenttype'),(13,'Can add session',5,'add_session'),(14,'Can change session',5,'change_session'),(15,'Can delete session',5,'delete_session'),(16,'Can add 赠送记录',6,'add_presentsrecord'),(17,'Can change 赠送记录',6,'change_presentsrecord'),(18,'Can delete 赠送记录',6,'delete_presentsrecord'),(19,'Can add 充值记录',7,'add_depositrecord'),(20,'Can change 充值记录',7,'change_depositrecord'),(21,'Can delete 充值记录',7,'delete_depositrecord'),(22,'Can add 消费记录',8,'add_consumerecord'),(23,'Can change 消费记录',8,'change_consumerecord'),(24,'Can delete 消费记录',8,'delete_consumerecord'),(25,'Can add 奖金记录',9,'add_prizerecord'),(26,'Can change 奖金记录',9,'change_prizerecord'),(27,'Can delete 奖金记录',9,'delete_prizerecord'),(28,'Can add 代理记录',10,'add_agencyrecord'),(29,'Can change 代理记录',10,'change_agencyrecord'),(30,'Can delete 代理记录',10,'delete_agencyrecord'),(31,'Can add 比特币提现记录',11,'add_bitcoinwithdrawrecord'),(32,'Can change 比特币提现记录',11,'change_bitcoinwithdrawrecord'),(33,'Can delete 比特币提现记录',11,'delete_bitcoinwithdrawrecord'),(34,'Can add 卡密库存',12,'add_cardinventories'),(35,'Can change 卡密库存',12,'change_cardinventories'),(36,'Can delete 卡密库存',12,'delete_cardinventories'),(37,'Can add 卡密入库记录表',13,'add_cardentryrecord'),(38,'Can change 卡密入库记录表',13,'change_cardentryrecord'),(39,'Can delete 卡密入库记录表',13,'delete_cardentryrecord'),(40,'Can add 卡密',14,'add_card'),(41,'Can change 卡密',14,'change_card'),(42,'Can delete 卡密',14,'delete_card'),(43,'Can add 卡密出库记录表',15,'add_carddeliveryrecord'),(44,'Can change 卡密出库记录表',15,'change_carddeliveryrecord'),(45,'Can delete 卡密出库记录表',15,'delete_carddeliveryrecord'),(46,'Can add 回收记录',16,'add_recyclerecord'),(47,'Can change 回收记录',16,'change_recyclerecord'),(48,'Can delete 回收记录',16,'delete_recyclerecord'),(49,'Can add 邀请记录',17,'add_inviterecord'),(50,'Can change 邀请记录',17,'change_inviterecord'),(51,'Can delete 邀请记录',17,'delete_inviterecord'),(52,'Can add imgs',18,'add_imgs'),(53,'Can change imgs',18,'change_imgs'),(54,'Can delete imgs',18,'delete_imgs'),(55,'Can add goods deliver record',19,'add_goodsdeliverrecord'),(56,'Can change goods deliver record',19,'change_goodsdeliverrecord'),(57,'Can delete goods deliver record',19,'delete_goodsdeliverrecord'),(58,'Can add 商品类型',20,'add_commoditytype'),(59,'Can change 商品类型',20,'change_commoditytype'),(60,'Can delete 商品类型',20,'delete_commoditytype'),(61,'Can add 进货渠道',21,'add_buychannel'),(62,'Can change 进货渠道',21,'change_buychannel'),(63,'Can delete 进货渠道',21,'delete_buychannel'),(64,'Can add 公告',22,'add_notice'),(65,'Can change 公告',22,'change_notice'),(66,'Can delete 公告',22,'delete_notice'),(67,'Can add banner',23,'add_banner'),(68,'Can change banner',23,'change_banner'),(69,'Can delete banner',23,'delete_banner'),(70,'Can add 用户',24,'add_userprofilebasic'),(71,'Can change 用户',24,'change_userprofilebasic'),(72,'Can delete 用户',24,'delete_userprofilebasic'),(73,'Can add 游戏玩家',25,'add_gameplayer'),(74,'Can change 游戏玩家',25,'change_gameplayer'),(75,'Can delete 游戏玩家',25,'delete_gameplayer'),(76,'Can add 回收商',26,'add_recyclebusinessman'),(77,'Can change 回收商',26,'change_recyclebusinessman'),(78,'Can delete 回收商',26,'delete_recyclebusinessman'),(79,'Can add 管理员',27,'add_administrator'),(80,'Can change 管理员',27,'change_administrator'),(81,'Can delete 管理员',27,'delete_administrator'),(82,'Can add wallet',28,'add_wallet'),(83,'Can change wallet',28,'change_wallet'),(84,'Can delete wallet',28,'delete_wallet'),(85,'Can add 消息',29,'add_messages'),(86,'Can change 消息',29,'change_messages'),(87,'Can delete 消息',29,'delete_messages'),(88,'Can add 商品',30,'add_commodity'),(89,'Can change 商品',30,'change_commodity'),(90,'Can delete 商品',30,'delete_commodity'),(91,'Can add 周期',31,'add_period'),(92,'Can change 周期',31,'change_period'),(93,'Can delete 周期',31,'delete_period'),(94,'Can add 夺宝参与记录表',32,'add_duobaoparticipaterecord'),(95,'Can change 夺宝参与记录表',32,'change_duobaoparticipaterecord'),(96,'Can delete 夺宝参与记录表',32,'delete_duobaoparticipaterecord'),(97,'Can add 夺宝号记录表',33,'add_tokenrecord'),(98,'Can change 夺宝号记录表',33,'change_tokenrecord'),(99,'Can delete 夺宝号记录表',33,'delete_tokenrecord'),(100,'Can add 用户每日数据',34,'add_usereverydayinfo'),(101,'Can change 用户每日数据',34,'change_usereverydayinfo'),(102,'Can delete 用户每日数据',34,'delete_usereverydayinfo'),(103,'Can add recycle statistics',35,'add_recyclestatistics'),(104,'Can change recycle statistics',35,'change_recyclestatistics'),(105,'Can delete recycle statistics',35,'delete_recyclestatistics');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `banner`
--

DROP TABLE IF EXISTS `banner`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `banner` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(54) DEFAULT NULL,
  `image_path` varchar(128) DEFAULT NULL,
  `link` varchar(128) DEFAULT NULL,
  `index` int(11) DEFAULT NULL,
  `status` int(11) DEFAULT NULL,
  `banner_type` int(11) DEFAULT NULL,
  `create_time` datetime(6) DEFAULT NULL,
  `administrator_id` int(11),
  PRIMARY KEY (`id`),
  KEY `banner_a68d6894` (`administrator_id`),
  CONSTRAINT `D42c2d93bf5ac567fbf672dcf05f8a0a` FOREIGN KEY (`administrator_id`) REFERENCES `administrator` (`userprofilebasic_ptr_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `banner`
--

LOCK TABLES `banner` WRITE;
/*!40000 ALTER TABLE `banner` DISABLE KEYS */;
/*!40000 ALTER TABLE `banner` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bitcoin_withdraw_record`
--

DROP TABLE IF EXISTS `bitcoin_withdraw_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bitcoin_withdraw_record` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `bitcoin_trade_no` varchar(128) DEFAULT NULL,
  `transaction_id` varchar(128) DEFAULT NULL,
  `amounts` decimal(32,16) DEFAULT NULL,
  `withdraw_time` datetime(6) DEFAULT NULL,
  `status` int(11) DEFAULT NULL,
  `remark` varchar(128) DEFAULT NULL,
  `to_recycle_businessman_id` int(11),
  PRIMARY KEY (`id`),
  KEY `bitcoin_withdraw_record_0b0c6edd` (`to_recycle_businessman_id`),
  CONSTRAINT `D49cf5aebf158a1d370e305f4b60b38a` FOREIGN KEY (`to_recycle_businessman_id`) REFERENCES `recycle_businessman` (`userprofilebasic_ptr_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bitcoin_withdraw_record`
--

LOCK TABLES `bitcoin_withdraw_record` WRITE;
/*!40000 ALTER TABLE `bitcoin_withdraw_record` DISABLE KEYS */;
/*!40000 ALTER TABLE `bitcoin_withdraw_record` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `buy_channel`
--

DROP TABLE IF EXISTS `buy_channel`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `buy_channel` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `channel_code` varchar(8) DEFAULT NULL,
  `remark` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `buy_channel`
--

LOCK TABLES `buy_channel` WRITE;
/*!40000 ALTER TABLE `buy_channel` DISABLE KEYS */;
/*!40000 ALTER TABLE `buy_channel` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `card`
--

DROP TABLE IF EXISTS `card`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `card` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `card_number` varchar(128) DEFAULT NULL,
  `card_pwd` varchar(128) DEFAULT NULL,
  `card_entry_no_id` int(11),
  `card_inventory_id` int(11),
  PRIMARY KEY (`id`),
  KEY `card_962b9340` (`card_entry_no_id`),
  KEY `card_a3279a2a` (`card_inventory_id`),
  CONSTRAINT `card_card_entry_no_id_926afcb4_fk_card_entry_record_id` FOREIGN KEY (`card_entry_no_id`) REFERENCES `card_entry_record` (`id`),
  CONSTRAINT `card_card_inventory_id_1bcc81b7_fk_card_inventories_id` FOREIGN KEY (`card_inventory_id`) REFERENCES `card_inventories` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `card`
--

LOCK TABLES `card` WRITE;
/*!40000 ALTER TABLE `card` DISABLE KEYS */;
/*!40000 ALTER TABLE `card` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `card_delivery_record`
--

DROP TABLE IF EXISTS `card_delivery_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `card_delivery_record` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `volumes` int(11) DEFAULT NULL,
  `delivery_time` datetime(6) DEFAULT NULL,
  `card_inventory_id` int(11),
  `period_id` int(11),
  `to_player_id` int(11),
  PRIMARY KEY (`id`),
  KEY `card_delivery_record_a3279a2a` (`card_inventory_id`),
  KEY `card_delivery_record_b1efa79f` (`period_id`),
  KEY `card_delivery_record_f0e965c9` (`to_player_id`),
  CONSTRAINT `car_to_player_id_751604b3_fk_game_player_userprofilebasic_ptr_id` FOREIGN KEY (`to_player_id`) REFERENCES `game_player` (`userprofilebasic_ptr_id`),
  CONSTRAINT `card_delivery__card_inventory_id_19fe429a_fk_card_inventories_id` FOREIGN KEY (`card_inventory_id`) REFERENCES `card_inventories` (`id`),
  CONSTRAINT `card_delivery_record_period_id_7cc8d467_fk_period_id` FOREIGN KEY (`period_id`) REFERENCES `period` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `card_delivery_record`
--

LOCK TABLES `card_delivery_record` WRITE;
/*!40000 ALTER TABLE `card_delivery_record` DISABLE KEYS */;
/*!40000 ALTER TABLE `card_delivery_record` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `card_entry_record`
--

DROP TABLE IF EXISTS `card_entry_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `card_entry_record` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `volumes` int(11) DEFAULT NULL,
  `entry_time` datetime(6) DEFAULT NULL,
  `card_inventory_id` int(11),
  `entry_admin_id` int(11),
  PRIMARY KEY (`id`),
  KEY `card_entry_record_a3279a2a` (`card_inventory_id`),
  KEY `card_entry_record_578edc14` (`entry_admin_id`),
  CONSTRAINT `D4ecccf3573254d9c94c1c85e7ca8e32` FOREIGN KEY (`entry_admin_id`) REFERENCES `administrator` (`userprofilebasic_ptr_id`),
  CONSTRAINT `card_entry_rec_card_inventory_id_8be37ae0_fk_card_inventories_id` FOREIGN KEY (`card_inventory_id`) REFERENCES `card_inventories` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `card_entry_record`
--

LOCK TABLES `card_entry_record` WRITE;
/*!40000 ALTER TABLE `card_entry_record` DISABLE KEYS */;
/*!40000 ALTER TABLE `card_entry_record` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `card_inventories`
--

DROP TABLE IF EXISTS `card_inventories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `card_inventories` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(128) DEFAULT NULL,
  `code` varchar(16) DEFAULT NULL,
  `market_price_cny` decimal(32,16) DEFAULT NULL,
  `volumes` int(11) DEFAULT NULL,
  `remaining_volumes` int(11) DEFAULT NULL,
  `warning_volumes` int(11) DEFAULT NULL,
  `today_put_volumes` int(11) DEFAULT NULL,
  `update_time` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `card_inventories`
--

LOCK TABLES `card_inventories` WRITE;
/*!40000 ALTER TABLE `card_inventories` DISABLE KEYS */;
/*!40000 ALTER TABLE `card_inventories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `commodity`
--

DROP TABLE IF EXISTS `commodity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `commodity` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `commodity_name` varchar(32) DEFAULT NULL,
  `reward_type` int(11) DEFAULT NULL,
  `market_price_cny` decimal(32,16) DEFAULT NULL,
  `snatch_treasure_amounts` int(11) DEFAULT NULL,
  `dh_price_cny` decimal(32,16) DEFAULT NULL,
  `is_continue` int(11) DEFAULT NULL,
  `status` int(11) DEFAULT NULL,
  `create_time` datetime(6) NOT NULL,
  `buy_channel_id` int(11) DEFAULT NULL,
  `commodity_type_id` int(11) DEFAULT NULL,
  `create_administrator_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `commodity_buy_channel_id_7b54c3f6_fk_buy_channel_id` (`buy_channel_id`),
  KEY `commodity_commodity_type_id_0315c818_fk_commodity_type_id` (`commodity_type_id`),
  KEY `da4d6368a3bbe5fde1f7187a6f41e14e` (`create_administrator_id`),
  CONSTRAINT `commodity_buy_channel_id_7b54c3f6_fk_buy_channel_id` FOREIGN KEY (`buy_channel_id`) REFERENCES `buy_channel` (`id`),
  CONSTRAINT `commodity_commodity_type_id_0315c818_fk_commodity_type_id` FOREIGN KEY (`commodity_type_id`) REFERENCES `commodity_type` (`id`),
  CONSTRAINT `da4d6368a3bbe5fde1f7187a6f41e14e` FOREIGN KEY (`create_administrator_id`) REFERENCES `administrator` (`userprofilebasic_ptr_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `commodity`
--

LOCK TABLES `commodity` WRITE;
/*!40000 ALTER TABLE `commodity` DISABLE KEYS */;
/*!40000 ALTER TABLE `commodity` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `commodity_type`
--

DROP TABLE IF EXISTS `commodity_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `commodity_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type_name` varchar(32) DEFAULT NULL,
  `type_code` varchar(8) DEFAULT NULL,
  `type_index` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `type_index` (`type_index`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `commodity_type`
--

LOCK TABLES `commodity_type` WRITE;
/*!40000 ALTER TABLE `commodity_type` DISABLE KEYS */;
/*!40000 ALTER TABLE `commodity_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `consume_record`
--

DROP TABLE IF EXISTS `consume_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `consume_record` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `amounts` decimal(32,16) DEFAULT NULL,
  `status` int(11) DEFAULT NULL,
  `consume_time` datetime(6) DEFAULT NULL,
  `participate_id` int(11),
  `period_id` int(11),
  `player_id` int(11),
  PRIMARY KEY (`id`),
  KEY `consume_record_69cd4472` (`participate_id`),
  KEY `consume_record_b1efa79f` (`period_id`),
  KEY `consume_record_afe72417` (`player_id`),
  CONSTRAINT `consum_player_id_74606152_fk_game_player_userprofilebasic_ptr_id` FOREIGN KEY (`player_id`) REFERENCES `game_player` (`userprofilebasic_ptr_id`),
  CONSTRAINT `consume__participate_id_739f20a9_fk_duobao_participate_record_id` FOREIGN KEY (`participate_id`) REFERENCES `duobao_participate_record` (`id`),
  CONSTRAINT `consume_record_period_id_51009f8b_fk_period_id` FOREIGN KEY (`period_id`) REFERENCES `period` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `consume_record`
--

LOCK TABLES `consume_record` WRITE;
/*!40000 ALTER TABLE `consume_record` DISABLE KEYS */;
/*!40000 ALTER TABLE `consume_record` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `deposit_record`
--

DROP TABLE IF EXISTS `deposit_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `deposit_record` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `out_trade_no` varchar(128) DEFAULT NULL,
  `trade_no` varchar(128) DEFAULT NULL,
  `amount` decimal(32,16) DEFAULT NULL,
  `units` int(11) DEFAULT NULL,
  `deposit_type` int(11) DEFAULT NULL,
  `deposit_time` datetime(6) DEFAULT NULL,
  `status` int(11) DEFAULT NULL,
  `remark` varchar(128) DEFAULT NULL,
  `from_recycle_businessman_id` int(11),
  `to_player_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `deposit_record_afd92e7d` (`from_recycle_businessman_id`),
  KEY `deposit_record_f0e965c9` (`to_player_id`),
  CONSTRAINT `D3d4bf0042c165e68e19243fdcfa2a4c` FOREIGN KEY (`from_recycle_businessman_id`) REFERENCES `recycle_businessman` (`userprofilebasic_ptr_id`),
  CONSTRAINT `dep_to_player_id_e64b36aa_fk_game_player_userprofilebasic_ptr_id` FOREIGN KEY (`to_player_id`) REFERENCES `game_player` (`userprofilebasic_ptr_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `deposit_record`
--

LOCK TABLES `deposit_record` WRITE;
/*!40000 ALTER TABLE `deposit_record` DISABLE KEYS */;
/*!40000 ALTER TABLE `deposit_record` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin__content_type_id_c4bce8eb_fk_django_content_type_id` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_user_profile_basic_id` (`user_id`),
  CONSTRAINT `django_admin__content_type_id_c4bce8eb_fk_django_content_type_id` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_user_profile_basic_id` FOREIGN KEY (`user_id`) REFERENCES `user_profile_basic` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
INSERT INTO `django_admin_log` VALUES (1,'2018-10-18 18:41:59.868148','1','管理员',1,'Added.',3,1),(2,'2018-10-18 21:13:20.033390','2','回收商',1,'Added.',3,1),(3,'2018-10-18 21:13:40.289462','3','玩家',1,'Added.',3,1);
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (6,'activitys','presentsrecord'),(1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(4,'contenttypes','contenttype'),(10,'financial','agencyrecord'),(11,'financial','bitcoinwithdrawrecord'),(8,'financial','consumerecord'),(7,'financial','depositrecord'),(9,'financial','prizerecord'),(14,'inventory','card'),(15,'inventory','carddeliveryrecord'),(13,'inventory','cardentryrecord'),(12,'inventory','cardinventories'),(17,'recycle_businessman','inviterecord'),(16,'recycle_businessman','recyclerecord'),(18,'resources','imgs'),(19,'rest','goodsdeliverrecord'),(5,'sessions','session'),(23,'shopping_settings','banner'),(21,'shopping_settings','buychannel'),(20,'shopping_settings','commoditytype'),(22,'shopping_settings','notice'),(27,'shopping_user','administrator'),(25,'shopping_user','gameplayer'),(29,'shopping_user','messages'),(26,'shopping_user','recyclebusinessman'),(24,'shopping_user','userprofilebasic'),(28,'shopping_user','wallet'),(30,'snatch_treasure','commodity'),(32,'snatch_treasure','duobaoparticipaterecord'),(31,'snatch_treasure','period'),(33,'snatch_treasure','tokenrecord'),(35,'statistics','recyclestatistics'),(34,'statistics','usereverydayinfo');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_migrations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2018-10-18 09:50:58.732739'),(2,'contenttypes','0002_remove_content_type_name','2018-10-18 09:50:58.801905'),(3,'auth','0001_initial','2018-10-18 09:50:58.997186'),(4,'auth','0002_alter_permission_name_max_length','2018-10-18 09:50:59.038118'),(5,'auth','0003_alter_user_email_max_length','2018-10-18 09:50:59.058416'),(6,'auth','0004_alter_user_username_opts','2018-10-18 09:50:59.077307'),(7,'auth','0005_alter_user_last_login_null','2018-10-18 09:50:59.098817'),(8,'auth','0006_require_contenttypes_0002','2018-10-18 09:50:59.103741'),(9,'auth','0007_alter_validators_add_error_messages','2018-10-18 09:50:59.126842'),(10,'shopping_user','0001_initial','2018-10-18 09:50:59.710224'),(11,'activitys','0001_initial','2018-10-18 09:50:59.735336'),(12,'activitys','0002_auto_20181018_0755','2018-10-18 09:50:59.934618'),(13,'admin','0001_initial','2018-10-18 09:51:00.052045'),(14,'admin','0002_logentry_remove_auto_add','2018-10-18 09:51:00.108665'),(15,'shopping_settings','0001_initial','2018-10-18 09:51:00.204269'),(16,'snatch_treasure','0001_initial','2018-10-18 09:51:00.960269'),(17,'financial','0001_initial','2018-10-18 09:51:01.084525'),(18,'financial','0002_auto_20181018_0755','2018-10-18 09:51:02.280800'),(19,'inventory','0001_initial','2018-10-18 09:51:02.452989'),(20,'inventory','0002_auto_20181018_0755','2018-10-18 09:51:03.312225'),(21,'recycle_businessman','0001_initial','2018-10-18 09:51:03.366281'),(22,'recycle_businessman','0002_auto_20181018_0755','2018-10-18 09:51:04.126701'),(23,'resources','0001_initial','2018-10-18 09:51:04.156232'),(24,'rest','0001_initial','2018-10-18 09:51:04.191333'),(25,'rest','0002_auto_20181018_0755','2018-10-18 09:51:04.769629'),(26,'sessions','0001_initial','2018-10-18 09:51:04.813963'),(27,'shopping_settings','0002_auto_20181018_0755','2018-10-18 09:51:05.128881'),(28,'statistics','0001_initial','2018-10-18 09:51:05.433241');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_de54fa62` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('bitm8ugaxk4ozkgcc3ll3t73zkg968xh','ZmU4Nzc0ZDI3NGQ2NDgwMjdmNDc3ZWIyNDU4MGYwOGVkYjgzZTQ5OTp7Il9hdXRoX3VzZXJfaGFzaCI6IjkwYWZiMjBjNzU5ZmE0N2YyMjQ4YjQxMzdkNDA5ODBlOWIyMWYwMWQiLCJfYXV0aF91c2VyX2JhY2tlbmQiOiJkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZCIsIl9hdXRoX3VzZXJfaWQiOiIxIn0=','2018-11-01 10:34:03.088413');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `duobao_participate_record`
--

DROP TABLE IF EXISTS `duobao_participate_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `duobao_participate_record` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `participate_amounts` int(11) DEFAULT NULL,
  `time` datetime(6) DEFAULT NULL,
  `period_id` int(11),
  `player_id` int(11),
  PRIMARY KEY (`id`),
  KEY `duobao_participate_record_b1efa79f` (`period_id`),
  KEY `duobao_participate_record_afe72417` (`player_id`),
  CONSTRAINT `duobao_participate_record_period_id_08add5d1_fk_period_id` FOREIGN KEY (`period_id`) REFERENCES `period` (`id`),
  CONSTRAINT `duobao_player_id_494b7b33_fk_game_player_userprofilebasic_ptr_id` FOREIGN KEY (`player_id`) REFERENCES `game_player` (`userprofilebasic_ptr_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `duobao_participate_record`
--

LOCK TABLES `duobao_participate_record` WRITE;
/*!40000 ALTER TABLE `duobao_participate_record` DISABLE KEYS */;
/*!40000 ALTER TABLE `duobao_participate_record` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `game_player`
--

DROP TABLE IF EXISTS `game_player`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `game_player` (
  `userprofilebasic_ptr_id` int(11) NOT NULL,
  `ip` varchar(32) DEFAULT NULL,
  `ip_address` varchar(64) DEFAULT NULL,
  `balance_b` decimal(16,6) DEFAULT NULL,
  `has_been_spending_b` decimal(16,6) DEFAULT NULL,
  `deposit_cny` decimal(16,6) DEFAULT NULL,
  `presents_b` decimal(16,6) DEFAULT NULL,
  `participate_count` int(11) DEFAULT NULL,
  `snatch_treasure_b` decimal(16,6) DEFAULT NULL,
  `market_price_cny` decimal(16,6) DEFAULT NULL,
  PRIMARY KEY (`userprofilebasic_ptr_id`),
  CONSTRAINT `game_p_userprofilebasic_ptr_id_1043643d_fk_user_profile_basic_id` FOREIGN KEY (`userprofilebasic_ptr_id`) REFERENCES `user_profile_basic` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `game_player`
--

LOCK TABLES `game_player` WRITE;
/*!40000 ALTER TABLE `game_player` DISABLE KEYS */;
/*!40000 ALTER TABLE `game_player` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `invite_record`
--

DROP TABLE IF EXISTS `invite_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `invite_record` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `invite_time` datetime(6) DEFAULT NULL,
  `invite_player_id` int(11),
  `recycle_businessman_id` int(11),
  PRIMARY KEY (`id`),
  KEY `invite_record_437770b3` (`invite_player_id`),
  KEY `invite_record_a2a29a5c` (`recycle_businessman_id`),
  CONSTRAINT `D7e52298ec692a86f07a093203f92e8b` FOREIGN KEY (`invite_player_id`) REFERENCES `game_player` (`userprofilebasic_ptr_id`),
  CONSTRAINT `b4b156f81322dc2fb5a3aeb469c5526b` FOREIGN KEY (`recycle_businessman_id`) REFERENCES `recycle_businessman` (`userprofilebasic_ptr_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `invite_record`
--

LOCK TABLES `invite_record` WRITE;
/*!40000 ALTER TABLE `invite_record` DISABLE KEYS */;
/*!40000 ALTER TABLE `invite_record` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `messages`
--

DROP TABLE IF EXISTS `messages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `messages` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(64) DEFAULT NULL,
  `content` varchar(128) DEFAULT NULL,
  `from_user` varchar(32) DEFAULT NULL,
  `status` int(11) DEFAULT NULL,
  `create_time` datetime(6) DEFAULT NULL,
  `to_player_id` int(11),
  PRIMARY KEY (`id`),
  KEY `messages_f0e965c9` (`to_player_id`),
  CONSTRAINT `mes_to_player_id_9323e3a0_fk_game_player_userprofilebasic_ptr_id` FOREIGN KEY (`to_player_id`) REFERENCES `game_player` (`userprofilebasic_ptr_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `messages`
--

LOCK TABLES `messages` WRITE;
/*!40000 ALTER TABLE `messages` DISABLE KEYS */;
/*!40000 ALTER TABLE `messages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notice`
--

DROP TABLE IF EXISTS `notice`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `notice` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(54) DEFAULT NULL,
  `content` longtext,
  `type` int(11) DEFAULT NULL,
  `status` int(11) DEFAULT NULL,
  `index` int(11) DEFAULT NULL,
  `is_notice_businessman` int(11) DEFAULT NULL,
  `create_time` datetime(6) DEFAULT NULL,
  `administrator_id` int(11),
  PRIMARY KEY (`id`),
  KEY `notice_a68d6894` (`administrator_id`),
  CONSTRAINT `d9364a53b839c8bd221ab537930f703d` FOREIGN KEY (`administrator_id`) REFERENCES `administrator` (`userprofilebasic_ptr_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notice`
--

LOCK TABLES `notice` WRITE;
/*!40000 ALTER TABLE `notice` DISABLE KEYS */;
/*!40000 ALTER TABLE `notice` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `period`
--

DROP TABLE IF EXISTS `period`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `period` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `period_no` varchar(16) DEFAULT NULL,
  `target_amounts` int(11) DEFAULT NULL,
  `amounts_prepared` int(11) DEFAULT NULL,
  `rate` int(11) DEFAULT NULL,
  `luck_token` varchar(32) DEFAULT NULL,
  `a_value` int(11) DEFAULT NULL,
  `b_value` int(11) DEFAULT NULL,
  `finish_time` datetime(6) DEFAULT NULL,
  `reward_time` datetime(6) DEFAULT NULL,
  `status` int(11) DEFAULT NULL,
  `create_time` datetime(6) DEFAULT NULL,
  `commodity_id` int(11) DEFAULT NULL,
  `create_administrator_id` int(11) DEFAULT NULL,
  `luck_player_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `period_commodity_id_91cdd1ee_fk_commodity_id` (`commodity_id`),
  KEY `fba4f8d33f6f1eddda9de43a57ac699b` (`create_administrator_id`),
  KEY `p_luck_player_id_c944f935_fk_game_player_userprofilebasic_ptr_id` (`luck_player_id`),
  CONSTRAINT `fba4f8d33f6f1eddda9de43a57ac699b` FOREIGN KEY (`create_administrator_id`) REFERENCES `administrator` (`userprofilebasic_ptr_id`),
  CONSTRAINT `p_luck_player_id_c944f935_fk_game_player_userprofilebasic_ptr_id` FOREIGN KEY (`luck_player_id`) REFERENCES `game_player` (`userprofilebasic_ptr_id`),
  CONSTRAINT `period_commodity_id_91cdd1ee_fk_commodity_id` FOREIGN KEY (`commodity_id`) REFERENCES `commodity` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `period`
--

LOCK TABLES `period` WRITE;
/*!40000 ALTER TABLE `period` DISABLE KEYS */;
/*!40000 ALTER TABLE `period` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `presents_record`
--

DROP TABLE IF EXISTS `presents_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `presents_record` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `amounts` int(11) DEFAULT NULL,
  `presents_type` int(11) DEFAULT NULL,
  `present_time` datetime(6) DEFAULT NULL,
  `msg_content` varchar(256) DEFAULT NULL,
  `remark` varchar(64) DEFAULT NULL,
  `from_administrator_id` int(11),
  `to_player_id` int(11),
  PRIMARY KEY (`id`),
  KEY `presents_record_3567de6b` (`from_administrator_id`),
  KEY `presents_record_f0e965c9` (`to_player_id`),
  CONSTRAINT `e6a360239d3b08cfaa727684d60b2702` FOREIGN KEY (`from_administrator_id`) REFERENCES `administrator` (`userprofilebasic_ptr_id`),
  CONSTRAINT `pre_to_player_id_c5ce7dac_fk_game_player_userprofilebasic_ptr_id` FOREIGN KEY (`to_player_id`) REFERENCES `game_player` (`userprofilebasic_ptr_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `presents_record`
--

LOCK TABLES `presents_record` WRITE;
/*!40000 ALTER TABLE `presents_record` DISABLE KEYS */;
/*!40000 ALTER TABLE `presents_record` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `prize_record`
--

DROP TABLE IF EXISTS `prize_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `prize_record` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `amounts` decimal(32,16) DEFAULT NULL,
  `status` int(11) DEFAULT NULL,
  `prize_time` datetime(6) DEFAULT NULL,
  `participate_id` int(11),
  `period_id` int(11),
  `to_player_id` int(11),
  PRIMARY KEY (`id`),
  KEY `prize_record_69cd4472` (`participate_id`),
  KEY `prize_record_b1efa79f` (`period_id`),
  KEY `prize_record_f0e965c9` (`to_player_id`),
  CONSTRAINT `pri_to_player_id_d5140522_fk_game_player_userprofilebasic_ptr_id` FOREIGN KEY (`to_player_id`) REFERENCES `game_player` (`userprofilebasic_ptr_id`),
  CONSTRAINT `prize_re_participate_id_e15b7a81_fk_duobao_participate_record_id` FOREIGN KEY (`participate_id`) REFERENCES `duobao_participate_record` (`id`),
  CONSTRAINT `prize_record_period_id_28c35140_fk_period_id` FOREIGN KEY (`period_id`) REFERENCES `period` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `prize_record`
--

LOCK TABLES `prize_record` WRITE;
/*!40000 ALTER TABLE `prize_record` DISABLE KEYS */;
/*!40000 ALTER TABLE `prize_record` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recycle_businessman`
--

DROP TABLE IF EXISTS `recycle_businessman`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `recycle_businessman` (
  `userprofilebasic_ptr_id` int(11) NOT NULL,
  `recycle_phone` varchar(16) DEFAULT NULL,
  `is_recycle` int(11) DEFAULT NULL,
  `is_login` int(11) DEFAULT NULL,
  `invite_code` varchar(16) DEFAULT NULL,
  `invite_qr_code` varchar(128) DEFAULT NULL,
  `deposit_back_rate` decimal(16,6) DEFAULT NULL,
  `recycle_back_rate` decimal(16,6) DEFAULT NULL,
  `invite_back_rate` decimal(16,6) DEFAULT NULL,
  `balance_cny` decimal(16,6) DEFAULT NULL,
  PRIMARY KEY (`userprofilebasic_ptr_id`),
  CONSTRAINT `recycl_userprofilebasic_ptr_id_8b62d26a_fk_user_profile_basic_id` FOREIGN KEY (`userprofilebasic_ptr_id`) REFERENCES `user_profile_basic` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recycle_businessman`
--

LOCK TABLES `recycle_businessman` WRITE;
/*!40000 ALTER TABLE `recycle_businessman` DISABLE KEYS */;
/*!40000 ALTER TABLE `recycle_businessman` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recycle_record`
--

DROP TABLE IF EXISTS `recycle_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `recycle_record` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `recycle_trade_no` varchar(128) DEFAULT NULL,
  `recycle_time` datetime(6) DEFAULT NULL,
  `commodity_id` int(11),
  `period_id` int(11),
  `recycle_businessman_id` int(11),
  PRIMARY KEY (`id`),
  KEY `recycle_record_f4491b3f` (`commodity_id`),
  KEY `recycle_record_b1efa79f` (`period_id`),
  KEY `recycle_record_a2a29a5c` (`recycle_businessman_id`),
  CONSTRAINT `D0aa65df4bd86cc48de82e760e0e95d8` FOREIGN KEY (`recycle_businessman_id`) REFERENCES `recycle_businessman` (`userprofilebasic_ptr_id`),
  CONSTRAINT `recycle_record_commodity_id_7045d561_fk_commodity_id` FOREIGN KEY (`commodity_id`) REFERENCES `commodity` (`id`),
  CONSTRAINT `recycle_record_period_id_ac49ff67_fk_period_id` FOREIGN KEY (`period_id`) REFERENCES `period` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recycle_record`
--

LOCK TABLES `recycle_record` WRITE;
/*!40000 ALTER TABLE `recycle_record` DISABLE KEYS */;
/*!40000 ALTER TABLE `recycle_record` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `resources_imgs`
--

DROP TABLE IF EXISTS `resources_imgs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `resources_imgs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `image_path` longtext,
  `resource_type` int(11) DEFAULT NULL,
  `relation_pk` int(11) DEFAULT NULL,
  `info` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `resources_imgs`
--

LOCK TABLES `resources_imgs` WRITE;
/*!40000 ALTER TABLE `resources_imgs` DISABLE KEYS */;
/*!40000 ALTER TABLE `resources_imgs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rest_goodsdeliverrecord`
--

DROP TABLE IF EXISTS `rest_goodsdeliverrecord`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `rest_goodsdeliverrecord` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `recipents_name` varchar(16) DEFAULT NULL,
  `recipents_phone` varchar(16) DEFAULT NULL,
  `recipents_address` varchar(128) DEFAULT NULL,
  `deliver_goods_channel` int(11) DEFAULT NULL,
  `quantity` int(11) DEFAULT NULL,
  `real_price_cny` decimal(32,16) DEFAULT NULL,
  `delivery_expense` decimal(32,16) DEFAULT NULL,
  `express_company` varchar(32) DEFAULT NULL,
  `express_number` varchar(64) DEFAULT NULL,
  `deliver_goods_time` datetime(6) DEFAULT NULL,
  `arrive_time` datetime(6) DEFAULT NULL,
  `status` int(11) DEFAULT NULL,
  `remark` varchar(64) DEFAULT NULL,
  `commodity_id` int(11),
  `period_id` int(11),
  `to_player_id` int(11),
  PRIMARY KEY (`id`),
  KEY `rest_goodsdeliverrecord_f4491b3f` (`commodity_id`),
  KEY `rest_goodsdeliverrecord_b1efa79f` (`period_id`),
  KEY `rest_goodsdeliverrecord_f0e965c9` (`to_player_id`),
  CONSTRAINT `res_to_player_id_4f010689_fk_game_player_userprofilebasic_ptr_id` FOREIGN KEY (`to_player_id`) REFERENCES `game_player` (`userprofilebasic_ptr_id`),
  CONSTRAINT `rest_goodsdeliverrecord_commodity_id_93a01256_fk_commodity_id` FOREIGN KEY (`commodity_id`) REFERENCES `commodity` (`id`),
  CONSTRAINT `rest_goodsdeliverrecord_period_id_2b15a021_fk_period_id` FOREIGN KEY (`period_id`) REFERENCES `period` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rest_goodsdeliverrecord`
--

LOCK TABLES `rest_goodsdeliverrecord` WRITE;
/*!40000 ALTER TABLE `rest_goodsdeliverrecord` DISABLE KEYS */;
/*!40000 ALTER TABLE `rest_goodsdeliverrecord` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `shopping_user_wallet`
--

DROP TABLE IF EXISTS `shopping_user_wallet`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `shopping_user_wallet` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `balance` decimal(16,6) DEFAULT NULL,
  `unit` varchar(16) DEFAULT NULL,
  `last_update_time` datetime(6) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `shopping_user_wallet_user_id_cfe3ab0d_fk_user_profile_basic_id` FOREIGN KEY (`user_id`) REFERENCES `user_profile_basic` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `shopping_user_wallet`
--

LOCK TABLES `shopping_user_wallet` WRITE;
/*!40000 ALTER TABLE `shopping_user_wallet` DISABLE KEYS */;
/*!40000 ALTER TABLE `shopping_user_wallet` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `statistics_recyclestatistics`
--

DROP TABLE IF EXISTS `statistics_recyclestatistics`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `statistics_recyclestatistics` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `today_cny` decimal(16,6) DEFAULT NULL,
  `cur_date` date DEFAULT NULL,
  `recycle_businessman_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ec7b76442932ebc870ef6410a1101e9d` (`recycle_businessman_id`),
  CONSTRAINT `ec7b76442932ebc870ef6410a1101e9d` FOREIGN KEY (`recycle_businessman_id`) REFERENCES `recycle_businessman` (`userprofilebasic_ptr_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `statistics_recyclestatistics`
--

LOCK TABLES `statistics_recyclestatistics` WRITE;
/*!40000 ALTER TABLE `statistics_recyclestatistics` DISABLE KEYS */;
/*!40000 ALTER TABLE `statistics_recyclestatistics` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `token_record`
--

DROP TABLE IF EXISTS `token_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `token_record` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `token_no` varchar(32) DEFAULT NULL,
  `participate_id` int(11) DEFAULT NULL,
  `period_id` int(11) DEFAULT NULL,
  `player_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `token_re_participate_id_cf999e5f_fk_duobao_participate_record_id` (`participate_id`),
  KEY `token_record_period_id_e2ae047e_fk_period_id` (`period_id`),
  KEY `token__player_id_43fc1b45_fk_game_player_userprofilebasic_ptr_id` (`player_id`),
  CONSTRAINT `token__player_id_43fc1b45_fk_game_player_userprofilebasic_ptr_id` FOREIGN KEY (`player_id`) REFERENCES `game_player` (`userprofilebasic_ptr_id`),
  CONSTRAINT `token_re_participate_id_cf999e5f_fk_duobao_participate_record_id` FOREIGN KEY (`participate_id`) REFERENCES `duobao_participate_record` (`id`),
  CONSTRAINT `token_record_period_id_e2ae047e_fk_period_id` FOREIGN KEY (`period_id`) REFERENCES `period` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `token_record`
--

LOCK TABLES `token_record` WRITE;
/*!40000 ALTER TABLE `token_record` DISABLE KEYS */;
/*!40000 ALTER TABLE `token_record` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_everyday_info`
--

DROP TABLE IF EXISTS `user_everyday_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_everyday_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `deposit_cny` decimal(16,6) DEFAULT NULL,
  `bonus` decimal(16,6) DEFAULT NULL,
  `difference` decimal(16,6) DEFAULT NULL,
  `presents_b` decimal(16,6) DEFAULT NULL,
  `cur_date` date DEFAULT NULL,
  `player_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_e_player_id_43682f27_fk_game_player_userprofilebasic_ptr_id` (`player_id`),
  CONSTRAINT `user_e_player_id_43682f27_fk_game_player_userprofilebasic_ptr_id` FOREIGN KEY (`player_id`) REFERENCES `game_player` (`userprofilebasic_ptr_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_everyday_info`
--

LOCK TABLES `user_everyday_info` WRITE;
/*!40000 ALTER TABLE `user_everyday_info` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_everyday_info` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_profile_basic`
--

DROP TABLE IF EXISTS `user_profile_basic`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_profile_basic` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `uid` varchar(16) DEFAULT NULL,
  `first_name` varchar(30) NOT NULL,
  `last_name` varchar(30) NOT NULL,
  `username` varchar(32) DEFAULT NULL,
  `nickname` varchar(32) DEFAULT NULL,
  `sex` int(11) DEFAULT NULL,
  `province` varchar(32) DEFAULT NULL,
  `city` varchar(32) DEFAULT NULL,
  `country` varchar(32) DEFAULT NULL,
  `headimage` varchar(128) DEFAULT NULL,
  `email` varchar(32) DEFAULT NULL,
  `phone` varchar(16) DEFAULT NULL,
  `is_staff` int(11) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  `status` int(11) DEFAULT NULL,
  `create_time` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_profile_basic`
--

LOCK TABLES `user_profile_basic` WRITE;
/*!40000 ALTER TABLE `user_profile_basic` DISABLE KEYS */;
INSERT INTO `user_profile_basic` VALUES (1,'pbkdf2_sha256$24000$2DYlE8ou59Vt$rwhSt9U44RY4ieAPl7z0JKyeTJyc1Aq+RwyxD71+IBs=','2018-10-18 10:34:03.076430',1,'10000001','','',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1095222570@qq.com',NULL,1,1,1,'2018-10-18 10:33:54.736371');
/*!40000 ALTER TABLE `user_profile_basic` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_profile_basic_groups`
--

DROP TABLE IF EXISTS `user_profile_basic_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_profile_basic_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `userprofilebasic_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_profile_basic_groups_userprofilebasic_id_6535eb0f_uniq` (`userprofilebasic_id`,`group_id`),
  KEY `user_profile_basic_groups_group_id_3f3ef759_fk_auth_group_id` (`group_id`),
  CONSTRAINT `user_profi_userprofilebasic_id_10fbf233_fk_user_profile_basic_id` FOREIGN KEY (`userprofilebasic_id`) REFERENCES `user_profile_basic` (`id`),
  CONSTRAINT `user_profile_basic_groups_group_id_3f3ef759_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_profile_basic_groups`
--

LOCK TABLES `user_profile_basic_groups` WRITE;
/*!40000 ALTER TABLE `user_profile_basic_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_profile_basic_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_profile_basic_user_permissions`
--

DROP TABLE IF EXISTS `user_profile_basic_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_profile_basic_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `userprofilebasic_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_profile_basic_user_permis_userprofilebasic_id_648cd819_uniq` (`userprofilebasic_id`,`permission_id`),
  KEY `user_profile_basic__permission_id_6cd61a36_fk_auth_permission_id` (`permission_id`),
  CONSTRAINT `user_profi_userprofilebasic_id_e4ec4a9e_fk_user_profile_basic_id` FOREIGN KEY (`userprofilebasic_id`) REFERENCES `user_profile_basic` (`id`),
  CONSTRAINT `user_profile_basic__permission_id_6cd61a36_fk_auth_permission_id` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_profile_basic_user_permissions`
--

LOCK TABLES `user_profile_basic_user_permissions` WRITE;
/*!40000 ALTER TABLE `user_profile_basic_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_profile_basic_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-10-18 21:14:28
