-- MySQL dump 10.15  Distrib 10.0.13-MariaDB, for Linux (x86_64)
--
-- Host: localhost    Database: newserver
-- ------------------------------------------------------
-- Server version	10.0.13-MariaDB

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
-- Table structure for table `360privilege`
--

DROP TABLE IF EXISTS `360privilege`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `360privilege` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `activityid` int(10) unsigned NOT NULL DEFAULT '0',
  `dailygiftisget` int(10) unsigned NOT NULL DEFAULT '1',
  `privilegegiftstatus` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`characterid`,`activityid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `account`
--

DROP TABLE IF EXISTS `account`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `account` (
  `account` char(255) COLLATE utf8_unicode_ci NOT NULL DEFAULT '0',
  `create_account_time` datetime DEFAULT NULL,
  `gm` int(10) unsigned DEFAULT NULL,
  PRIMARY KEY (`account`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `achievement`
--

DROP TABLE IF EXISTS `achievement`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `achievement` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `achievementstatus` binary(255) DEFAULT NULL,
  `point` int(10) unsigned DEFAULT '0',
  `weardesign` int(10) unsigned DEFAULT '0',
  `moneytotalget` bigint(20) unsigned DEFAULT '0',
  `guilddonationmoney` bigint(20) unsigned DEFAULT '0',
  `combat` int(10) unsigned DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `achievementdesign`
--

DROP TABLE IF EXISTS `achievementdesign`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `achievementdesign` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `designid` int(10) unsigned NOT NULL DEFAULT '0',
  `bforever` int(10) unsigned DEFAULT '0',
  `expiretime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`characterid`,`designid`),
  KEY `character` (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `achievementinfo`
--

DROP TABLE IF EXISTS `achievementinfo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `achievementinfo` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `achievementtype` int(10) unsigned NOT NULL DEFAULT '0',
  `completetimes` int(10) unsigned DEFAULT '0',
  PRIMARY KEY (`characterid`,`achievementtype`),
  KEY `character` (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `activegift`
--

DROP TABLE IF EXISTS `activegift`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `activegift` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `nowcount` int(10) unsigned NOT NULL DEFAULT '0',
  `daygift` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `festivalcount` int(10) unsigned NOT NULL DEFAULT '0',
  `festivalgift` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `activity_auction`
--

DROP TABLE IF EXISTS `activity_auction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `activity_auction` (
  `autoid` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `bopen` int(20) unsigned NOT NULL DEFAULT '0',
  `bigid` int(10) unsigned NOT NULL DEFAULT '0',
  `curactivitydayid` int(10) unsigned NOT NULL DEFAULT '0',
  `endtime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `continueday` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`autoid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `activity_auction_one`
--

DROP TABLE IF EXISTS `activity_auction_one`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `activity_auction_one` (
  `oneid` int(20) unsigned NOT NULL DEFAULT '0',
  `endtime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `auctionthingstatus` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`oneid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `activity_barter`
--

DROP TABLE IF EXISTS `activity_barter`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `activity_barter` (
  `autoid` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `bopen` int(20) unsigned NOT NULL DEFAULT '0',
  `curactivitydayid` int(10) unsigned NOT NULL DEFAULT '0',
  `begintime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`autoid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `activity_catchmonkeyrank`
--

DROP TABLE IF EXISTS `activity_catchmonkeyrank`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `activity_catchmonkeyrank` (
  `activityid` int(20) unsigned NOT NULL DEFAULT '0',
  `endtime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `bprocessreward` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`activityid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `activity_circulamoney`
--

DROP TABLE IF EXISTS `activity_circulamoney`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `activity_circulamoney` (
  `autoid` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `bopen` int(20) unsigned NOT NULL DEFAULT '0',
  `openrefreshtime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `servernum` int(10) unsigned NOT NULL DEFAULT '0',
  `curactivityid` int(10) unsigned NOT NULL DEFAULT '0',
  `endtime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`autoid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `activity_consumegift`
--

DROP TABLE IF EXISTS `activity_consumegift`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `activity_consumegift` (
  `autoid` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `bopen` int(20) unsigned NOT NULL DEFAULT '0',
  `begintime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`autoid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `activity_eightday`
--

DROP TABLE IF EXISTS `activity_eightday`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `activity_eightday` (
  `autoid` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `bopen` int(20) unsigned NOT NULL DEFAULT '0',
  `servernum` int(10) unsigned NOT NULL DEFAULT '0',
  `curactivityid` int(10) unsigned NOT NULL DEFAULT '0',
  `endtime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `topcharacterids` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`autoid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `activity_eightdaygift`
--

DROP TABLE IF EXISTS `activity_eightdaygift`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `activity_eightdaygift` (
  `giftid` int(20) unsigned NOT NULL DEFAULT '0',
  `salenum` int(20) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`giftid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `activity_freebarter`
--

DROP TABLE IF EXISTS `activity_freebarter`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `activity_freebarter` (
  `autoid` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `bopen` int(20) unsigned NOT NULL DEFAULT '0',
  `curactivitydayid` int(10) unsigned NOT NULL DEFAULT '0',
  `begintime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`autoid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `activity_lucktreasure`
--

DROP TABLE IF EXISTS `activity_lucktreasure`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `activity_lucktreasure` (
  `boxlv` int(10) unsigned NOT NULL DEFAULT '0',
  `starttime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `endtime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`boxlv`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `activity_lucktreasure_geter`
--

DROP TABLE IF EXISTS `activity_lucktreasure_geter`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `activity_lucktreasure_geter` (
  `boxlv` int(10) unsigned NOT NULL DEFAULT '0',
  `playername` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`boxlv`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `activity_luckytoken`
--

DROP TABLE IF EXISTS `activity_luckytoken`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `activity_luckytoken` (
  `autoid` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `bopen` int(20) unsigned NOT NULL DEFAULT '0',
  `begintime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`autoid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `activity_rechargegift`
--

DROP TABLE IF EXISTS `activity_rechargegift`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `activity_rechargegift` (
  `autoid` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `bopen` int(20) unsigned NOT NULL DEFAULT '0',
  `servernum` int(10) unsigned NOT NULL DEFAULT '0',
  `curactivitydayid` int(10) unsigned NOT NULL DEFAULT '0',
  `endtime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`autoid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `activity_rechargerank`
--

DROP TABLE IF EXISTS `activity_rechargerank`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `activity_rechargerank` (
  `activityid` int(20) unsigned NOT NULL DEFAULT '0',
  `endtime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `bprocessreward` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`activityid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `activity_upday`
--

DROP TABLE IF EXISTS `activity_upday`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `activity_upday` (
  `autoid` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `bopen` int(20) unsigned NOT NULL DEFAULT '0',
  `servernum` int(10) unsigned NOT NULL DEFAULT '0',
  `curactivityid` int(10) unsigned NOT NULL DEFAULT '0',
  `endtime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`autoid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `activity_vipfeedback`
--

DROP TABLE IF EXISTS `activity_vipfeedback`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `activity_vipfeedback` (
  `servernum` int(10) unsigned NOT NULL DEFAULT '0',
  `dayid` int(10) unsigned NOT NULL DEFAULT '0',
  `endtime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`servernum`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `activitycommon`
--

DROP TABLE IF EXISTS `activitycommon`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `activitycommon` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `answerrewardget` int(10) unsigned DEFAULT NULL,
  `bjoinmelkin` int(10) unsigned DEFAULT NULL,
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `activitypack`
--

DROP TABLE IF EXISTS `activitypack`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `activitypack` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `packtimes` char(255) COLLATE utf8_unicode_ci DEFAULT '',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `aiwanprivilege`
--

DROP TABLE IF EXISTS `aiwanprivilege`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `aiwanprivilege` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `dailyreward` int(10) unsigned NOT NULL DEFAULT '0',
  `servenrefreshtime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `servenrewardstatus` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `antiaddition`
--

DROP TABLE IF EXISTS `antiaddition`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `antiaddition` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `onlinetime` int(10) unsigned DEFAULT NULL,
  `offlinetime` int(10) unsigned DEFAULT NULL,
  `birthday` bigint(10) unsigned DEFAULT NULL,
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `arenacharacter`
--

DROP TABLE IF EXISTS `arenacharacter`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `arenacharacter` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `challengenum` int(10) unsigned DEFAULT NULL,
  `cdtime` bigint(10) unsigned DEFAULT NULL,
  `time_reward_num` int(10) unsigned DEFAULT '0',
  `need_check_cd` int(10) unsigned DEFAULT '0',
  `beat_num` int(10) unsigned DEFAULT '0',
  `can_get_rank_reward` int(10) unsigned DEFAULT '0',
  `reward_rank` int(10) unsigned DEFAULT '0',
  `honor` int(10) unsigned DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `arenahistory`
--

DROP TABLE IF EXISTS `arenahistory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `arenahistory` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `characterid` int(10) unsigned DEFAULT NULL,
  `sourcecharacterid` int(10) unsigned NOT NULL DEFAULT '0',
  `targetcharacterid` int(10) unsigned NOT NULL DEFAULT '0',
  `winnercharacterid` int(10) unsigned NOT NULL DEFAULT '0',
  `old_rank` int(10) unsigned DEFAULT NULL,
  `new_rank` int(10) unsigned DEFAULT NULL,
  `target_name` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `characterid` (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `arenaranking`
--

DROP TABLE IF EXISTS `arenaranking`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `arenaranking` (
  `ranking` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `characterid` int(10) unsigned DEFAULT NULL,
  `robotid` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`ranking`),
  KEY `characterid` (`characterid`)
) ENGINE=MyISAM AUTO_INCREMENT=21621 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `artifact`
--

DROP TABLE IF EXISTS `artifact`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `artifact` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `artifactlevs` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `combat` int(20) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auctiongoods`
--

DROP TABLE IF EXISTS `auctiongoods`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auctiongoods` (
  `id` int(20) unsigned NOT NULL DEFAULT '0',
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `charactername` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `goodstype` int(20) unsigned NOT NULL DEFAULT '0',
  `data` int(20) unsigned NOT NULL DEFAULT '0',
  `mainfilter` int(20) unsigned NOT NULL DEFAULT '0',
  `subfilter` int(20) unsigned NOT NULL DEFAULT '0',
  `quality` int(20) unsigned NOT NULL DEFAULT '0',
  `level` int(20) unsigned NOT NULL DEFAULT '0',
  `selltype` int(20) unsigned NOT NULL DEFAULT '0',
  `price` int(20) unsigned NOT NULL DEFAULT '0',
  `perprice` float unsigned NOT NULL DEFAULT '0',
  `name` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `buylock` int(20) unsigned NOT NULL DEFAULT '0',
  `attributetype` int(20) unsigned NOT NULL DEFAULT '0',
  `num` int(20) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `characterid` (`characterid`),
  KEY `mainfilter` (`mainfilter`),
  KEY `subfilter` (`subfilter`),
  KEY `quality` (`quality`),
  KEY `level` (`level`),
  KEY `name` (`name`),
  KEY `price` (`price`),
  KEY `perprice` (`perprice`),
  KEY `attributetype` (`attributetype`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auctionincome`
--

DROP TABLE IF EXISTS `auctionincome`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auctionincome` (
  `id` int(20) unsigned NOT NULL DEFAULT '0',
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `charactername` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `goodstype` int(20) unsigned NOT NULL DEFAULT '0',
  `data` int(20) unsigned NOT NULL DEFAULT '0',
  `selltype` int(20) unsigned NOT NULL DEFAULT '0',
  `price` int(20) unsigned NOT NULL DEFAULT '0',
  `characterid_buyer` int(20) unsigned NOT NULL DEFAULT '0',
  `buyername` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `time` datetime DEFAULT NULL,
  `openup` int(20) unsigned NOT NULL DEFAULT '0',
  `incometype` int(20) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `characterid` (`characterid`),
  KEY `characterid_buyer` (`characterid_buyer`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `bank`
--

DROP TABLE IF EXISTS `bank`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bank` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `investmentTime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `monthrewardstatus` int(20) unsigned NOT NULL DEFAULT '0',
  `levelinvestmentstatus` int(20) unsigned NOT NULL DEFAULT '0',
  `levelstatus` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `monthitem` int(20) unsigned NOT NULL DEFAULT '0',
  `levelupitem` int(20) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `bankpersonal`
--

DROP TABLE IF EXISTS `bankpersonal`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bankpersonal` (
  `serialnumber` int(10) unsigned NOT NULL DEFAULT '0',
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `time` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `processtype` int(10) unsigned NOT NULL DEFAULT '0',
  `banktype` int(10) unsigned NOT NULL DEFAULT '0',
  `num` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`serialnumber`),
  KEY `character` (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `bankrecord`
--

DROP TABLE IF EXISTS `bankrecord`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bankrecord` (
  `serialnumber` int(10) unsigned NOT NULL DEFAULT '0',
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `name` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `processtype` int(10) unsigned NOT NULL DEFAULT '0',
  `banktype` int(10) unsigned NOT NULL DEFAULT '0',
  `num` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`serialnumber`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `barter`
--

DROP TABLE IF EXISTS `barter`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `barter` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `barterstatus` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `blacker`
--

DROP TABLE IF EXISTS `blacker`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `blacker` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `characterid_target` int(20) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`,`characterid_target`),
  KEY `characterid` (`characterid`),
  KEY `target` (`characterid_target`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `catchmonkeyrankactivityperson`
--

DROP TABLE IF EXISTS `catchmonkeyrankactivityperson`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `catchmonkeyrankactivityperson` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `catchnum` int(10) unsigned NOT NULL DEFAULT '0',
  `catchtime` bigint(19) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cdkey`
--

DROP TABLE IF EXISTS `cdkey`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cdkey` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `cdkey` char(255) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  PRIMARY KEY (`characterid`,`cdkey`),
  KEY `character` (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `character`
--

DROP TABLE IF EXISTS `character`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `character` (
  `characterid` int(20) unsigned NOT NULL AUTO_INCREMENT,
  `account` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `name` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `level` int(10) unsigned DEFAULT NULL,
  `experience` bigint(19) unsigned DEFAULT '0',
  `hp` int(10) unsigned DEFAULT '9999999',
  `maxhp` int(10) unsigned DEFAULT '1000',
  `attack` int(10) unsigned DEFAULT '0',
  `defence` int(10) DEFAULT '0',
  `hit` int(10) DEFAULT '0',
  `dodge` int(10) DEFAULT '0',
  `crit` int(10) DEFAULT '0',
  `toughness` int(10) DEFAULT '0',
  `move_speed_second` int(10) DEFAULT '0',
  `sceneid` int(10) unsigned DEFAULT NULL,
  `posx` float DEFAULT NULL,
  `posy` float DEFAULT NULL,
  `offlinetime` datetime DEFAULT NULL,
  `updatetime` datetime DEFAULT NULL,
  `create_character_time` datetime DEFAULT NULL,
  `combat` int(10) unsigned DEFAULT NULL,
  `sex` int(10) unsigned DEFAULT '0',
  `loginIP` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `logintime` datetime DEFAULT NULL,
  `profession` int(10) unsigned DEFAULT NULL,
  `body_avatar` int(10) unsigned DEFAULT NULL,
  `wing_avatar` int(10) unsigned DEFAULT '0',
  `weapon_avatar` int(10) unsigned DEFAULT NULL,
  `stamp_avatar` int(10) unsigned DEFAULT '0',
  `shield_avatar` int(10) unsigned DEFAULT '0',
  `talisman_avatar` int(10) unsigned DEFAULT '0',
  `ride_avatar` int(10) unsigned DEFAULT '0',
  `serverid` int(10) unsigned NOT NULL DEFAULT '0',
  `super_power` int(10) unsigned DEFAULT '0',
  `vice` int(10) unsigned DEFAULT '0',
  `body_balance` int(10) unsigned DEFAULT '0',
  `unit_power` int(10) unsigned DEFAULT '0',
  `lv_item_use_num` int(10) unsigned DEFAULT '0',
  `vice_remain_time` int(10) unsigned DEFAULT '0',
  `online` int(10) unsigned DEFAULT '0',
  `realm` int(10) unsigned DEFAULT '0',
  `stageid` int(10) unsigned DEFAULT '0',
  `realmcombat` int(10) unsigned DEFAULT '0',
  `levelcombat` int(10) unsigned DEFAULT '0',
  `itemexpid` int(10) unsigned DEFAULT '0',
  `itemexptime` int(10) unsigned DEFAULT '0',
  `levelupitem` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `leveluptime` bigint(10) unsigned DEFAULT '0',
  `luodan` int(10) unsigned DEFAULT '0',
  `realmuptime` bigint(10) unsigned DEFAULT '0',
  `yellow_vip_level` int(10) unsigned DEFAULT NULL,
  `yellow_year_vip_level` int(10) unsigned DEFAULT NULL,
  `yellow_high_vip_level` int(10) unsigned DEFAULT NULL,
  `totalonlinetime` bigint(10) unsigned DEFAULT '0',
  PRIMARY KEY (`characterid`),
  KEY `combat` (`combat`),
  KEY `level` (`level`),
  KEY `account_serverid` (`account`,`serverid`),
  KEY `name` (`name`)
) ENGINE=MyISAM AUTO_INCREMENT=50920 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `characterfashion`
--

DROP TABLE IF EXISTS `characterfashion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `characterfashion` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `fashionid` int(4) unsigned NOT NULL DEFAULT '0',
  `expirytime` bigint(4) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`,`fashionid`),
  KEY `character` (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `characterfashioncombat`
--

DROP TABLE IF EXISTS `characterfashioncombat`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `characterfashioncombat` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `combat` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `characterfashiondress`
--

DROP TABLE IF EXISTS `characterfashiondress`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `characterfashiondress` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `dressfashion` int(4) unsigned NOT NULL DEFAULT '0',
  `combat` int(4) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `characterskill`
--

DROP TABLE IF EXISTS `characterskill`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `characterskill` (
  `characterid` int(20) unsigned NOT NULL AUTO_INCREMENT,
  `base_skill` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `lv_item_use_num` int(10) unsigned DEFAULT '0',
  `skill_breakout` int(10) unsigned DEFAULT '0',
  `skillcombat` int(10) unsigned DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM AUTO_INCREMENT=50920 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `characterstatus`
--

DROP TABLE IF EXISTS `characterstatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `characterstatus` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `statusinfo` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `charactertokenitem`
--

DROP TABLE IF EXISTS `charactertokenitem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `charactertokenitem` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `payemoney` int(10) unsigned NOT NULL DEFAULT '0',
  `buytimes` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `charactertokentask`
--

DROP TABLE IF EXISTS `charactertokentask`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `charactertokentask` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `times` int(10) unsigned NOT NULL DEFAULT '0',
  `monsterid` int(20) unsigned NOT NULL DEFAULT '0',
  `neednum` int(10) unsigned NOT NULL DEFAULT '0',
  `killnum` int(20) unsigned NOT NULL DEFAULT '0',
  `acceptlevel` int(10) unsigned NOT NULL DEFAULT '0',
  `complete` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `charge`
--

DROP TABLE IF EXISTS `charge`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `charge` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `number` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `circulamoney`
--

DROP TABLE IF EXISTS `circulamoney`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `circulamoney` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `rechargenum` int(10) unsigned NOT NULL DEFAULT '0',
  `rewardstatus` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `citywartime`
--

DROP TABLE IF EXISTS `citywartime`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `citywartime` (
  `time` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`time`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `consumegift`
--

DROP TABLE IF EXISTS `consumegift`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `consumegift` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `costemoney` int(20) unsigned NOT NULL DEFAULT '0',
  `rewardstatus` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `exchangestatus` int(20) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `container_gridcd`
--

DROP TABLE IF EXISTS `container_gridcd`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `container_gridcd` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `type` int(4) unsigned NOT NULL DEFAULT '0',
  `cd` int(4) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`,`type`),
  KEY `id_type` (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `containercombat`
--

DROP TABLE IF EXISTS `containercombat`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `containercombat` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `backpackcombat` int(10) unsigned DEFAULT NULL,
  `clothescombat` int(10) unsigned DEFAULT NULL,
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `containers`
--

DROP TABLE IF EXISTS `containers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `containers` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `type` int(4) unsigned NOT NULL DEFAULT '0',
  `size` int(4) unsigned NOT NULL DEFAULT '0',
  `thing` text COLLATE utf8_unicode_ci,
  PRIMARY KEY (`characterid`,`type`),
  KEY `id_type` (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `corona`
--

DROP TABLE IF EXISTS `corona`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `corona` (
  `serialnumber` int(10) unsigned NOT NULL DEFAULT '0',
  `exchangestatus` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`serialnumber`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `coronapersonal`
--

DROP TABLE IF EXISTS `coronapersonal`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `coronapersonal` (
  `serialnumber` int(10) unsigned NOT NULL DEFAULT '0',
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `time` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `lotteryid` int(4) unsigned NOT NULL DEFAULT '0',
  `strenglen` int(4) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`serialnumber`),
  KEY `character` (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `coronarecord`
--

DROP TABLE IF EXISTS `coronarecord`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `coronarecord` (
  `serialnumber` int(10) unsigned NOT NULL DEFAULT '0',
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `name` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `lotteryId` int(4) unsigned NOT NULL DEFAULT '0',
  `strenglen` int(4) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`serialnumber`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `currency`
--

DROP TABLE IF EXISTS `currency`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `currency` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `money` bigint(20) unsigned NOT NULL DEFAULT '0',
  `emoney` bigint(20) unsigned NOT NULL DEFAULT '0',
  `vouchers` bigint(20) unsigned NOT NULL DEFAULT '0',
  `chargeemoney` bigint(20) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`),
  KEY `money` (`money`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dailyrealmbattle`
--

DROP TABLE IF EXISTS `dailyrealmbattle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dailyrealmbattle` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `battletimes` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dbversion`
--

DROP TABLE IF EXISTS `dbversion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dbversion` (
  `version_number` int(11) NOT NULL DEFAULT '0',
  `db_key` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`version_number`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `eightday`
--

DROP TABLE IF EXISTS `eightday`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `eightday` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `rewardstatus` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `giftbuystatus` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `enemies`
--

DROP TABLE IF EXISTS `enemies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `enemies` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `characterid_target` int(20) unsigned NOT NULL DEFAULT '0',
  `record` int(20) NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`,`characterid_target`),
  KEY `characterid` (`characterid`),
  KEY `target` (`characterid_target`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `equipment`
--

DROP TABLE IF EXISTS `equipment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `equipment` (
  `id` int(20) unsigned NOT NULL AUTO_INCREMENT,
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `thingcfgid` int(20) unsigned NOT NULL DEFAULT '0',
  `bind` int(4) unsigned NOT NULL DEFAULT '0',
  `timemode` int(4) NOT NULL DEFAULT '0',
  `expiredTime` bigint(20) unsigned NOT NULL DEFAULT '0',
  `strengthen` int(4) NOT NULL DEFAULT '0',
  `combat` int(4) unsigned NOT NULL DEFAULT '0',
  `realm` int(4) NOT NULL DEFAULT '0',
  `stage` int(4) NOT NULL DEFAULT '0',
  `level` int(4) NOT NULL DEFAULT '0',
  `qualitybless` int(4) NOT NULL DEFAULT '0',
  `leveluptimes` int(4) NOT NULL DEFAULT '0',
  `additional` char(255) COLLATE utf8_unicode_ci DEFAULT '',
  `randomfactor` char(255) COLLATE utf8_unicode_ci DEFAULT '',
  `levelupvalue` int(4) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `id` (`characterid`)
) ENGINE=MyISAM AUTO_INCREMENT=10718453 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `escort`
--

DROP TABLE IF EXISTS `escort`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `escort` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `todayescorttimes` int(10) unsigned DEFAULT '0',
  `todayattacktimes` int(10) unsigned DEFAULT '0',
  `carlev` int(10) unsigned DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `festivalactive`
--

DROP TABLE IF EXISTS `festivalactive`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `festivalactive` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `rewardstatus` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `festivalactivity_active`
--

DROP TABLE IF EXISTS `festivalactivity_active`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `festivalactivity_active` (
  `starttime` char(255) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `endtime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `activitystatus` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`starttime`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `festivalactivity_bisai`
--

DROP TABLE IF EXISTS `festivalactivity_bisai`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `festivalactivity_bisai` (
  `starttime` char(255) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `endtime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `activitystatus` int(10) unsigned NOT NULL DEFAULT '0',
  `bsendrankreward` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`starttime`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `festivalactivity_collect`
--

DROP TABLE IF EXISTS `festivalactivity_collect`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `festivalactivity_collect` (
  `starttime` char(255) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `endtime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `activitystatus` int(10) unsigned NOT NULL DEFAULT '0',
  `buildlv` int(10) unsigned NOT NULL DEFAULT '0',
  `juanstatus` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `buildscore` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`starttime`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `festivalactivity_consume`
--

DROP TABLE IF EXISTS `festivalactivity_consume`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `festivalactivity_consume` (
  `starttime` char(255) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `endtime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `activitystatus` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`starttime`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `festivalactivity_diaoluo`
--

DROP TABLE IF EXISTS `festivalactivity_diaoluo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `festivalactivity_diaoluo` (
  `starttime` char(255) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `endtime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `activitystatus` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`starttime`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `festivalactivity_exchange`
--

DROP TABLE IF EXISTS `festivalactivity_exchange`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `festivalactivity_exchange` (
  `starttime` char(255) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `endtime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `activitystatus` int(10) unsigned NOT NULL DEFAULT '0',
  `exchangestatus` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`starttime`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `festivalactivity_flower`
--

DROP TABLE IF EXISTS `festivalactivity_flower`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `festivalactivity_flower` (
  `starttime` char(255) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `endtime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `activitystatus` int(10) unsigned NOT NULL DEFAULT '0',
  `bprocessreward` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`starttime`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `festivalactivity_online`
--

DROP TABLE IF EXISTS `festivalactivity_online`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `festivalactivity_online` (
  `starttime` char(255) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `endtime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `activitystatus` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`starttime`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `festivalactivity_rechargegift`
--

DROP TABLE IF EXISTS `festivalactivity_rechargegift`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `festivalactivity_rechargegift` (
  `starttime` char(255) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `endtime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `activitystatus` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`starttime`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `festivalbisai`
--

DROP TABLE IF EXISTS `festivalbisai`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `festivalbisai` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `score` int(10) unsigned NOT NULL DEFAULT '0',
  `hadgetrewadid` int(10) unsigned NOT NULL DEFAULT '0',
  `changetime` bigint(20) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `festivalcollect`
--

DROP TABLE IF EXISTS `festivalcollect`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `festivalcollect` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `getbuildlv` int(10) unsigned NOT NULL DEFAULT '0',
  `curscore` int(10) unsigned NOT NULL DEFAULT '0',
  `totalscore` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `festivalconsume`
--

DROP TABLE IF EXISTS `festivalconsume`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `festivalconsume` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `consume` int(20) unsigned NOT NULL DEFAULT '0',
  `rewardstatus` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `festivalexchange`
--

DROP TABLE IF EXISTS `festivalexchange`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `festivalexchange` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `exchangestatus` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `festivalfashionactivity`
--

DROP TABLE IF EXISTS `festivalfashionactivity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `festivalfashionactivity` (
  `starttime` char(255) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `endtime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `activitystatus` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`starttime`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `festivalflower`
--

DROP TABLE IF EXISTS `festivalflower`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `festivalflower` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `serverid` int(10) unsigned NOT NULL DEFAULT '0',
  `sendflower` int(10) unsigned NOT NULL DEFAULT '0',
  `reciveflower` int(10) unsigned NOT NULL DEFAULT '0',
  `askcdendtime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `festivalonline`
--

DROP TABLE IF EXISTS `festivalonline`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `festivalonline` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `onlineseconds` int(10) unsigned NOT NULL DEFAULT '0',
  `rewardstatus` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `festivalrechargegift`
--

DROP TABLE IF EXISTS `festivalrechargegift`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `festivalrechargegift` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `rechargenum` int(20) unsigned NOT NULL DEFAULT '0',
  `rewardstatus` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `firstcharge`
--

DROP TABLE IF EXISTS `firstcharge`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `firstcharge` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `nowtimes` int(10) unsigned DEFAULT NULL,
  `toptimes` int(10) unsigned DEFAULT NULL,
  `recharge` int(10) unsigned DEFAULT NULL,
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `flower`
--

DROP TABLE IF EXISTS `flower`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `flower` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `send` int(10) unsigned NOT NULL DEFAULT '0',
  `recive` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `forbidtalk`
--

DROP TABLE IF EXISTS `forbidtalk`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `forbidtalk` (
  `charactername` char(255) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `time` bigint(20) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`charactername`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `freebarter`
--

DROP TABLE IF EXISTS `freebarter`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `freebarter` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `barterstatus` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `friend`
--

DROP TABLE IF EXISTS `friend`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `friend` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `characterid_target` int(20) unsigned NOT NULL DEFAULT '0',
  `friendliness` int(20) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`,`characterid_target`),
  KEY `characterid` (`characterid`),
  KEY `target` (`characterid_target`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `goddessfigure`
--

DROP TABLE IF EXISTS `goddessfigure`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `goddessfigure` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `realm` int(10) unsigned NOT NULL DEFAULT '0',
  `stageid` int(10) unsigned NOT NULL DEFAULT '0',
  `cdsecond` int(10) unsigned NOT NULL DEFAULT '0',
  `combat` int(10) unsigned NOT NULL DEFAULT '0',
  `goddesstime` bigint(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `guardbattle`
--

DROP TABLE IF EXISTS `guardbattle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `guardbattle` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `topround` int(4) unsigned NOT NULL DEFAULT '0',
  `nowround` int(4) unsigned NOT NULL DEFAULT '0',
  `resettimes` int(10) unsigned NOT NULL DEFAULT '0',
  `roundreward` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `guild`
--

DROP TABLE IF EXISTS `guild`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `guild` (
  `id` int(20) unsigned NOT NULL DEFAULT '0',
  `name` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `level` int(20) unsigned NOT NULL DEFAULT '0',
  `bannerid` int(20) unsigned NOT NULL DEFAULT '0',
  `bannername` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `createtime` datetime DEFAULT NULL,
  `declaretime` datetime DEFAULT NULL,
  `unactive` int(20) unsigned NOT NULL DEFAULT '0',
  `announce` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `autoaccept` int(20) unsigned NOT NULL DEFAULT '0',
  `money` bigint(20) unsigned NOT NULL DEFAULT '0',
  `token` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `taoistlevel` int(20) unsigned NOT NULL DEFAULT '0',
  `petlevel` int(20) unsigned NOT NULL DEFAULT '1',
  `petexp` int(20) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `guildbattle`
--

DROP TABLE IF EXISTS `guildbattle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `guildbattle` (
  `guildid` int(20) unsigned NOT NULL DEFAULT '0',
  `nowbattle` int(20) unsigned NOT NULL DEFAULT '0',
  `deadboss` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `refreshtime` datetime DEFAULT NULL,
  PRIMARY KEY (`guildid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `guildbossreward`
--

DROP TABLE IF EXISTS `guildbossreward`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `guildbossreward` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `reward` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `guildcommon`
--

DROP TABLE IF EXISTS `guildcommon`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `guildcommon` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `acceptinvite` int(20) unsigned NOT NULL DEFAULT '0',
  `story` int(20) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `guildevent`
--

DROP TABLE IF EXISTS `guildevent`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `guildevent` (
  `guildid` int(20) unsigned NOT NULL DEFAULT '0',
  `eventid` int(20) unsigned NOT NULL DEFAULT '0',
  `eventtype` int(20) unsigned NOT NULL DEFAULT '0',
  `time` bigint(20) unsigned NOT NULL DEFAULT '0',
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `rank` int(20) unsigned NOT NULL DEFAULT '0',
  `donatetype` int(20) unsigned NOT NULL DEFAULT '0',
  `donatenum` int(20) unsigned NOT NULL DEFAULT '0',
  `contribute` int(20) unsigned NOT NULL DEFAULT '0',
  `story` int(20) unsigned NOT NULL DEFAULT '0',
  `characterid_target` int(20) unsigned NOT NULL DEFAULT '0',
  `monstertype` int(20) unsigned NOT NULL DEFAULT '0',
  `mapid` int(20) unsigned NOT NULL DEFAULT '0',
  `posx` int(20) unsigned NOT NULL DEFAULT '0',
  `posy` int(20) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`guildid`,`eventid`),
  KEY `guild` (`guildid`),
  KEY `characterid` (`characterid`),
  KEY `target` (`characterid_target`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `guildherocleantime`
--

DROP TABLE IF EXISTS `guildherocleantime`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `guildherocleantime` (
  `guildid` int(10) unsigned NOT NULL DEFAULT '0',
  `battleid` int(10) unsigned NOT NULL DEFAULT '0',
  `charactername` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `cleantime` int(4) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`guildid`,`battleid`),
  KEY `guild` (`guildid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `guildhostility`
--

DROP TABLE IF EXISTS `guildhostility`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `guildhostility` (
  `guildid` int(20) unsigned NOT NULL DEFAULT '0',
  `hostilityid` int(20) unsigned NOT NULL DEFAULT '0',
  `time` bigint(20) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`guildid`,`hostilityid`),
  KEY `guild` (`guildid`),
  KEY `hostility` (`hostilityid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `guildmember`
--

DROP TABLE IF EXISTS `guildmember`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `guildmember` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `guildid` int(20) unsigned NOT NULL DEFAULT '0',
  `rank` int(20) unsigned NOT NULL DEFAULT '0',
  `jointime` datetime DEFAULT NULL,
  `contribution` int(20) unsigned NOT NULL DEFAULT '0',
  `donatemoney` bigint(20) unsigned NOT NULL DEFAULT '0',
  `donatetoken` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`characterid`),
  KEY `guild` (`guildid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `guildpaytoken`
--

DROP TABLE IF EXISTS `guildpaytoken`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `guildpaytoken` (
  `guildid` int(20) unsigned NOT NULL DEFAULT '0',
  `pay` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`guildid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `guildpet`
--

DROP TABLE IF EXISTS `guildpet`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `guildpet` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `feedcount` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `guildquest`
--

DROP TABLE IF EXISTS `guildquest`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `guildquest` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `taskid` int(20) unsigned NOT NULL DEFAULT '0',
  `progress` int(4) unsigned NOT NULL DEFAULT '0',
  `acceptlevel` int(4) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `guildskill`
--

DROP TABLE IF EXISTS `guildskill`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `guildskill` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `skilllevel` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `combat` int(20) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `heaven`
--

DROP TABLE IF EXISTS `heaven`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `heaven` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `activestatus` int(20) unsigned NOT NULL DEFAULT '0',
  `wearheavenid` int(20) unsigned NOT NULL DEFAULT '0',
  `onlinetime` int(20) unsigned NOT NULL DEFAULT '0',
  `logindays` int(20) unsigned NOT NULL DEFAULT '0',
  `specialskillstatus` int(20) unsigned NOT NULL DEFAULT '0',
  `heavenbar` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `combat` int(20) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `heavenimprove`
--

DROP TABLE IF EXISTS `heavenimprove`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `heavenimprove` (
  `id` int(20) unsigned NOT NULL AUTO_INCREMENT,
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `heavenid` int(20) unsigned NOT NULL DEFAULT '0',
  `attributedata` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `hasunsave` int(20) unsigned NOT NULL DEFAULT '0',
  `unsaveattribute` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `character` (`characterid`),
  KEY `heavenitem` (`characterid`,`heavenid`)
) ENGINE=MyISAM AUTO_INCREMENT=37034 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `herobattle`
--

DROP TABLE IF EXISTS `herobattle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `herobattle` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `nowbattle` int(4) unsigned NOT NULL DEFAULT '0',
  `topbattle` int(4) unsigned NOT NULL DEFAULT '0',
  `helptimes` int(4) unsigned NOT NULL DEFAULT '0',
  `behelptimes` int(4) unsigned NOT NULL DEFAULT '0',
  `resettimes` int(4) unsigned NOT NULL DEFAULT '0',
  `rewardbattle` int(4) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `herocleantime`
--

DROP TABLE IF EXISTS `herocleantime`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `herocleantime` (
  `battleid` int(10) unsigned NOT NULL DEFAULT '0',
  `charactername` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `cleantime` int(4) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`battleid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hook`
--

DROP TABLE IF EXISTS `hook`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hook` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `hookconfig` text COLLATE utf8_unicode_ci,
  `normalquickbar` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `musequickbar` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `forbidbusiness` int(4) unsigned NOT NULL DEFAULT '0',
  `forbidaddtoguild` int(4) unsigned NOT NULL DEFAULT '0',
  `forbidaddteam` int(4) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `horse`
--

DROP TABLE IF EXISTS `horse`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `horse` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `ride` int(4) unsigned NOT NULL DEFAULT '0',
  `steplev` int(4) unsigned NOT NULL DEFAULT '0',
  `potentialnum` int(4) unsigned NOT NULL DEFAULT '0',
  `illusionnum` int(4) unsigned NOT NULL DEFAULT '0',
  `bless` int(4) unsigned NOT NULL DEFAULT '0',
  `countdown` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `skillslot` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `curchoosehorseid` int(4) unsigned NOT NULL DEFAULT '0',
  `advancedtimes` int(4) unsigned NOT NULL DEFAULT '0',
  `critsymbolvalue` int(4) unsigned NOT NULL DEFAULT '0',
  `critsymbolendtime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `combat` int(4) unsigned NOT NULL DEFAULT '0',
  `leveluptime` bigint(4) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `horseitem`
--

DROP TABLE IF EXISTS `horseitem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `horseitem` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `horseid` int(4) unsigned NOT NULL DEFAULT '0',
  `bforever` int(4) unsigned NOT NULL DEFAULT '0',
  `expiretime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`characterid`,`horseid`),
  KEY `character` (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `item`
--

DROP TABLE IF EXISTS `item`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `item` (
  `id` int(20) unsigned NOT NULL AUTO_INCREMENT,
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `thingcfgid` int(20) unsigned NOT NULL DEFAULT '0',
  `bind` int(4) unsigned NOT NULL DEFAULT '0',
  `timemode` int(4) NOT NULL DEFAULT '0',
  `expiredTime` bigint(20) unsigned NOT NULL DEFAULT '0',
  `overlap` int(4) unsigned NOT NULL DEFAULT '0',
  `cd` int(4) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `id` (`characterid`)
) ENGINE=MyISAM AUTO_INCREMENT=10718467 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `joyportpaybackactivitypersonal`
--

DROP TABLE IF EXISTS `joyportpaybackactivitypersonal`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `joyportpaybackactivitypersonal` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `costemoney` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `jsxfactivity`
--

DROP TABLE IF EXISTS `jsxfactivity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `jsxfactivity` (
  `activitystatus` int(10) unsigned NOT NULL DEFAULT '0',
  `winguildid` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`activitystatus`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `jsxfactivitypersonal`
--

DROP TABLE IF EXISTS `jsxfactivitypersonal`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `jsxfactivitypersonal` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `playerstatus` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `jyactivity`
--

DROP TABLE IF EXISTS `jyactivity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `jyactivity` (
  `activitystatus` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`activitystatus`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `jyactivitypersonal`
--

DROP TABLE IF EXISTS `jyactivitypersonal`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `jyactivitypersonal` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `playerstatus` int(10) unsigned NOT NULL DEFAULT '0',
  `playerrank` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `lockaccount`
--

DROP TABLE IF EXISTS `lockaccount`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `lockaccount` (
  `account` char(255) COLLATE utf8_unicode_ci NOT NULL DEFAULT '0',
  `locktime` bigint(20) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`account`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `lockip`
--

DROP TABLE IF EXISTS `lockip`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `lockip` (
  `ip` char(255) COLLATE utf8_unicode_ci NOT NULL DEFAULT '0',
  PRIMARY KEY (`ip`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `lucktreasureperson`
--

DROP TABLE IF EXISTS `lucktreasureperson`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `lucktreasureperson` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `buystatus` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `luckyquest`
--

DROP TABLE IF EXISTS `luckyquest`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `luckyquest` (
  `id` int(20) unsigned NOT NULL DEFAULT '0',
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `taskid` int(20) unsigned NOT NULL DEFAULT '0',
  `progress` int(4) unsigned NOT NULL DEFAULT '0',
  `acceptlevel` int(4) unsigned NOT NULL DEFAULT '0',
  `quality` int(20) unsigned NOT NULL DEFAULT '0',
  `additional` float DEFAULT NULL,
  `things` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `character` (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `luckytoken`
--

DROP TABLE IF EXISTS `luckytoken`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `luckytoken` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `rechargenum` int(20) unsigned NOT NULL DEFAULT '0',
  `rewardstatus` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `maid`
--

DROP TABLE IF EXISTS `maid`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `maid` (
  `characterid` int(10) NOT NULL,
  `maidid` int(10) NOT NULL,
  `theterm` bigint(20) NOT NULL DEFAULT '0',
  `maidskill` char(255) COLLATE utf8_unicode_ci DEFAULT '',
  `hp` int(10) unsigned NOT NULL DEFAULT '0',
  `realm` int(10) NOT NULL DEFAULT '0',
  `stageid` int(10) NOT NULL DEFAULT '0',
  `bless` int(4) unsigned NOT NULL DEFAULT '0',
  `countdown` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `advancedtimes` int(4) unsigned NOT NULL DEFAULT '0',
  `appendage` smallint(2) NOT NULL DEFAULT '0',
  `appendagecdendtime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `dannum` int(10) NOT NULL DEFAULT '0',
  `revive_time` int(11) NOT NULL DEFAULT '0',
  `fitcdendtime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `critsymbolvalue` int(4) unsigned NOT NULL DEFAULT '0',
  `critsymbolendtime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `combat` int(4) unsigned NOT NULL DEFAULT '0',
  `leveluptime` bigint(4) unsigned NOT NULL DEFAULT '0',
  `fashionid` int(4) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`,`maidid`),
  KEY `character` (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `maidfashion`
--

DROP TABLE IF EXISTS `maidfashion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `maidfashion` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `fashionid` int(4) unsigned NOT NULL DEFAULT '0',
  `bforever` int(4) unsigned NOT NULL DEFAULT '0',
  `expiretime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`characterid`,`fashionid`),
  KEY `character` (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `mail`
--

DROP TABLE IF EXISTS `mail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `mail` (
  `id` int(20) unsigned NOT NULL DEFAULT '0',
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `money` int(20) unsigned NOT NULL DEFAULT '0',
  `emoney` int(20) unsigned NOT NULL DEFAULT '0',
  `vouchers` int(20) unsigned NOT NULL DEFAULT '0',
  `content` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `things` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `chargenum` int(20) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `characterid` (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `maincityguild`
--

DROP TABLE IF EXISTS `maincityguild`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `maincityguild` (
  `sceneid` int(10) unsigned NOT NULL DEFAULT '0',
  `guildid` int(10) unsigned DEFAULT NULL,
  `occupytime` bigint(10) unsigned DEFAULT NULL,
  `official` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `refreshtime` bigint(10) unsigned DEFAULT NULL,
  PRIMARY KEY (`sceneid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `maketeam`
--

DROP TABLE IF EXISTS `maketeam`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `maketeam` (
  `characterid` int(10) NOT NULL,
  `groupid` int(10) NOT NULL,
  `autoinviteintogroup` smallint(2) NOT NULL DEFAULT '0',
  `autoqueryintogroup` smallint(2) NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`),
  KEY `character` (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `metals`
--

DROP TABLE IF EXISTS `metals`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `metals` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `grownvalue` int(10) unsigned NOT NULL DEFAULT '0',
  `growntimes` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `combat` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `microclientreward`
--

DROP TABLE IF EXISTS `microclientreward`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `microclientreward` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `receive` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `monthsign`
--

DROP TABLE IF EXISTS `monthsign`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `monthsign` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `dailysignstatus` int(4) unsigned NOT NULL DEFAULT '0',
  `totalsignstatus` int(4) unsigned NOT NULL DEFAULT '0',
  `resigntimes` int(4) unsigned NOT NULL DEFAULT '0',
  `totalsignnum` int(4) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `monthsignsystem`
--

DROP TABLE IF EXISTS `monthsignsystem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `monthsignsystem` (
  `resettime` char(255) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  PRIMARY KEY (`resettime`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `multipleexp`
--

DROP TABLE IF EXISTS `multipleexp`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `multipleexp` (
  `autoid` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `multipleexp` int(10) unsigned NOT NULL DEFAULT '0',
  `starttime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `endtime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `buffdesc` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`autoid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `muse`
--

DROP TABLE IF EXISTS `muse`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `muse` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `musetype` int(4) unsigned NOT NULL DEFAULT '0',
  `realm` int(4) unsigned NOT NULL DEFAULT '0',
  `stageid` int(4) unsigned NOT NULL DEFAULT '0',
  `bless` int(4) unsigned NOT NULL DEFAULT '0',
  `countdown` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `musecdendtime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `advancedtimes` int(4) unsigned NOT NULL DEFAULT '0',
  `potentialnum` int(4) unsigned NOT NULL DEFAULT '0',
  `illusionnum` int(4) unsigned NOT NULL DEFAULT '0',
  `critsymbolvalue` int(4) unsigned NOT NULL DEFAULT '0',
  `critsymbolendtime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `combat` int(4) unsigned NOT NULL DEFAULT '0',
  `leveluptime` bigint(4) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `newguild`
--

DROP TABLE IF EXISTS `newguild`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `newguild` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `completenewguildids` binary(255) DEFAULT NULL,
  `newguildrecord` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `newguildgift`
--

DROP TABLE IF EXISTS `newguildgift`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `newguildgift` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `hadgetlevel` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `noviceprocess`
--

DROP TABLE IF EXISTS `noviceprocess`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `noviceprocess` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `completetask` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `onlineactivityperson`
--

DROP TABLE IF EXISTS `onlineactivityperson`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `onlineactivityperson` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `onlinetime` int(10) unsigned NOT NULL DEFAULT '0',
  `rewardstatus` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `onlinereward`
--

DROP TABLE IF EXISTS `onlinereward`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `onlinereward` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `onlinetime` int(4) unsigned NOT NULL DEFAULT '0',
  `rewardstatus` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `overload`
--

DROP TABLE IF EXISTS `overload`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `overload` (
  `battleid` int(10) unsigned NOT NULL DEFAULT '0',
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `usetime` int(4) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`battleid`),
  KEY `character` (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `overloadreward`
--

DROP TABLE IF EXISTS `overloadreward`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `overloadreward` (
  `time` bigint(4) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`time`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `plotbattle`
--

DROP TABLE IF EXISTS `plotbattle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `plotbattle` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `topbattle` int(4) unsigned NOT NULL DEFAULT '0',
  `battletimes` text COLLATE utf8_unicode_ci,
  `cleantime` text COLLATE utf8_unicode_ci,
  `raidsbattle` int(10) unsigned NOT NULL DEFAULT '0',
  `raidstime` int(4) unsigned NOT NULL DEFAULT '0',
  `autoraids` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `plotquest`
--

DROP TABLE IF EXISTS `plotquest`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `plotquest` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `taskid` int(20) unsigned NOT NULL DEFAULT '0',
  `progress` int(4) unsigned NOT NULL DEFAULT '0',
  `taskflag` int(4) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`,`taskid`),
  KEY `character` (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `precinctlevel`
--

DROP TABLE IF EXISTS `precinctlevel`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `precinctlevel` (
  `level` int(20) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`level`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `precinctwarrank`
--

DROP TABLE IF EXISTS `precinctwarrank`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `precinctwarrank` (
  `rank` int(20) unsigned NOT NULL DEFAULT '0',
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `name` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `score` int(10) unsigned NOT NULL DEFAULT '0',
  `guildname` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`rank`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `prizebox`
--

DROP TABLE IF EXISTS `prizebox`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `prizebox` (
  `id` int(10) unsigned NOT NULL DEFAULT '0',
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `battletype` int(10) unsigned NOT NULL DEFAULT '0',
  `battleid` int(10) unsigned NOT NULL DEFAULT '0',
  `money` int(10) unsigned NOT NULL DEFAULT '0',
  `emoney` int(10) unsigned NOT NULL DEFAULT '0',
  `exp` int(10) unsigned NOT NULL DEFAULT '0',
  `unitpower` int(10) unsigned NOT NULL DEFAULT '0',
  `vouchers` int(10) unsigned NOT NULL DEFAULT '0',
  `story` int(10) unsigned NOT NULL DEFAULT '0',
  `thing` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `time` bigint(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `character` (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `puppet`
--

DROP TABLE IF EXISTS `puppet`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `puppet` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `realm` int(4) unsigned NOT NULL DEFAULT '0',
  `stageid` int(4) unsigned NOT NULL DEFAULT '0',
  `potentialnum` int(4) unsigned NOT NULL DEFAULT '0',
  `illusionnum` int(4) unsigned NOT NULL DEFAULT '0',
  `bless` int(4) unsigned NOT NULL DEFAULT '0',
  `countdown` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `skillslot` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `advancedtimes` int(4) unsigned NOT NULL DEFAULT '0',
  `critsymbolvalue` int(4) unsigned NOT NULL DEFAULT '0',
  `critsymbolendtime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `combat` int(4) unsigned NOT NULL DEFAULT '0',
  `leveluptime` bigint(4) unsigned NOT NULL DEFAULT '0',
  `fashionid` int(4) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `puppetfashion`
--

DROP TABLE IF EXISTS `puppetfashion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `puppetfashion` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `fashionid` int(4) unsigned NOT NULL DEFAULT '0',
  `bforever` int(4) unsigned NOT NULL DEFAULT '0',
  `expiretime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`characterid`,`fashionid`),
  KEY `character` (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `puppetqihun`
--

DROP TABLE IF EXISTS `puppetqihun`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `puppetqihun` (
  `qihunid` int(4) unsigned NOT NULL DEFAULT '0',
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `cfgid` int(4) unsigned NOT NULL DEFAULT '0',
  `level` int(4) unsigned NOT NULL DEFAULT '0',
  `exp` int(4) unsigned NOT NULL DEFAULT '0',
  `block` int(4) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`qihunid`),
  KEY `character` (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `puppetqihuncharacter`
--

DROP TABLE IF EXISTS `puppetqihuncharacter`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `puppetqihuncharacter` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `drawlevel` int(4) unsigned NOT NULL DEFAULT '0',
  `qihunslot` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `qihunbag` text COLLATE utf8_unicode_ci,
  `perfectid` int(20) unsigned NOT NULL DEFAULT '0',
  `perfectcount` int(20) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `quenchingjd`
--

DROP TABLE IF EXISTS `quenchingjd`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `quenchingjd` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `growntimes` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `combat` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `questtimes`
--

DROP TABLE IF EXISTS `questtimes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `questtimes` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `type` int(4) unsigned NOT NULL DEFAULT '0',
  `times` int(4) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`,`type`),
  KEY `userId` (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `rankactivity`
--

DROP TABLE IF EXISTS `rankactivity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `rankactivity` (
  `ranktype` int(10) unsigned NOT NULL DEFAULT '0',
  `rank` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `startday` int(10) unsigned NOT NULL DEFAULT '0',
  `starttime` bigint(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`ranktype`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `realmbattle`
--

DROP TABLE IF EXISTS `realmbattle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `realmbattle` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `battletimes` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `realmtask`
--

DROP TABLE IF EXISTS `realmtask`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `realmtask` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `taskid` int(10) unsigned NOT NULL DEFAULT '0',
  `taskflag` int(20) unsigned NOT NULL DEFAULT '0',
  `groupid` int(10) unsigned NOT NULL DEFAULT '0',
  `reward` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `rechargegift`
--

DROP TABLE IF EXISTS `rechargegift`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `rechargegift` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `rechargenum` int(20) unsigned NOT NULL DEFAULT '0',
  `rewardstatus` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `rechargemonster`
--

DROP TABLE IF EXISTS `rechargemonster`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `rechargemonster` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `getrewardstatus` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `rechargerankactivityperson`
--

DROP TABLE IF EXISTS `rechargerankactivityperson`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `rechargerankactivityperson` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `chargenum` int(10) unsigned NOT NULL DEFAULT '0',
  `chargetime` bigint(19) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `rechargeturn`
--

DROP TABLE IF EXISTS `rechargeturn`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `rechargeturn` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `countid` int(10) unsigned NOT NULL DEFAULT '0',
  `hadgetturnid` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `recoupaccount`
--

DROP TABLE IF EXISTS `recoupaccount`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `recoupaccount` (
  `account` char(255) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `emoney` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`account`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `refine`
--

DROP TABLE IF EXISTS `refine`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `refine` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `realm` int(4) unsigned NOT NULL DEFAULT '0',
  `stageid` int(4) unsigned NOT NULL DEFAULT '0',
  `potentialnum` int(4) unsigned NOT NULL DEFAULT '0',
  `illusionnum` int(4) unsigned NOT NULL DEFAULT '0',
  `bless` int(4) unsigned NOT NULL DEFAULT '0',
  `countdown` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `skillslot` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `advancedtimes` int(4) unsigned NOT NULL DEFAULT '0',
  `critsymbolvalue` int(4) unsigned NOT NULL DEFAULT '0',
  `critsymbolendtime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `combat` int(4) unsigned NOT NULL DEFAULT '0',
  `leveluptime` bigint(4) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `relationer`
--

DROP TABLE IF EXISTS `relationer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `relationer` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `fansnum` int(20) unsigned NOT NULL DEFAULT '0',
  `showoffline` int(20) unsigned NOT NULL DEFAULT '0',
  `showhead` int(20) unsigned NOT NULL DEFAULT '0',
  `mappublic` int(20) unsigned NOT NULL DEFAULT '0',
  `shieldenemies` int(20) unsigned NOT NULL DEFAULT '0',
  `mood` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `autorefuse` int(20) unsigned NOT NULL DEFAULT '0',
  `lover_characterid` int(20) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `repocontainer`
--

DROP TABLE IF EXISTS `repocontainer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `repocontainer` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `repothing` text COLLATE utf8_unicode_ci,
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `restriction`
--

DROP TABLE IF EXISTS `restriction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `restriction` (
  `id` int(20) unsigned NOT NULL AUTO_INCREMENT,
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `shopid` int(20) unsigned NOT NULL DEFAULT '0',
  `shelfid` int(20) unsigned NOT NULL DEFAULT '0',
  `goodsid` int(20) unsigned NOT NULL DEFAULT '0',
  `buynum` int(20) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `character` (`characterid`)
) ENGINE=MyISAM AUTO_INCREMENT=133110 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sevendays`
--

DROP TABLE IF EXISTS `sevendays`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sevendays` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `continueddays` int(4) unsigned NOT NULL DEFAULT '0',
  `refreshcontinueddaytime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `rewardstatus` int(4) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `shrinebattle`
--

DROP TABLE IF EXISTS `shrinebattle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `shrinebattle` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `cleanbattle` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `daycleanbattle` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `smeltvalue`
--

DROP TABLE IF EXISTS `smeltvalue`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `smeltvalue` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `equipsmelt` int(4) unsigned NOT NULL DEFAULT '0',
  `highsmelt` int(4) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sougoulogin`
--

DROP TABLE IF EXISTS `sougoulogin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sougoulogin` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `hallstatus` int(10) unsigned NOT NULL DEFAULT '0',
  `inputstatus` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `spiritstone`
--

DROP TABLE IF EXISTS `spiritstone`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `spiritstone` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `equiptype` int(10) unsigned NOT NULL DEFAULT '0',
  `stone` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`characterid`,`equiptype`),
  KEY `character` (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `stamp`
--

DROP TABLE IF EXISTS `stamp`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `stamp` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `realm` int(4) unsigned NOT NULL DEFAULT '0',
  `stageid` int(4) unsigned NOT NULL DEFAULT '0',
  `bless` int(4) unsigned NOT NULL DEFAULT '0',
  `countdown` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `skillslot` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `advancedtimes` int(4) unsigned NOT NULL DEFAULT '0',
  `potentialnum` int(4) unsigned NOT NULL DEFAULT '0',
  `illusionnum` int(4) unsigned NOT NULL DEFAULT '0',
  `critsymbolvalue` int(4) unsigned NOT NULL DEFAULT '0',
  `critsymbolendtime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `combat` int(4) unsigned NOT NULL DEFAULT '0',
  `leveluptime` bigint(4) unsigned NOT NULL DEFAULT '0',
  `fashionid` int(4) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `stampfashion`
--

DROP TABLE IF EXISTS `stampfashion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `stampfashion` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `fashionid` int(4) unsigned NOT NULL DEFAULT '0',
  `bforever` int(4) unsigned NOT NULL DEFAULT '0',
  `expiretime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`characterid`,`fashionid`),
  KEY `character` (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `starbattle`
--

DROP TABLE IF EXISTS `starbattle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `starbattle` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `challengetimes` int(10) unsigned NOT NULL DEFAULT '0',
  `refreshtimes` int(10) unsigned NOT NULL DEFAULT '0',
  `refreshbattle` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `starbattleranktime`
--

DROP TABLE IF EXISTS `starbattleranktime`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `starbattleranktime` (
  `time` bigint(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`time`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `starbattlescore`
--

DROP TABLE IF EXISTS `starbattlescore`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `starbattlescore` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `score` int(10) unsigned NOT NULL DEFAULT '0',
  `scoretime` bigint(10) unsigned NOT NULL DEFAULT '0',
  `getscoretime` int(20) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `stranger`
--

DROP TABLE IF EXISTS `stranger`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `stranger` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `characterid_target` int(20) unsigned NOT NULL DEFAULT '0',
  `time` bigint(20) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`,`characterid_target`),
  KEY `characterid` (`characterid`),
  KEY `target` (`characterid_target`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `supervip`
--

DROP TABLE IF EXISTS `supervip`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `supervip` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `chargeemoney` int(10) unsigned NOT NULL DEFAULT '0',
  `resettime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `rewardstatus` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `swallowtimes`
--

DROP TABLE IF EXISTS `swallowtimes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `swallowtimes` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `times` int(4) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sword`
--

DROP TABLE IF EXISTS `sword`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sword` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `emoneytimes` int(10) unsigned NOT NULL DEFAULT '0',
  `moneytimes` int(10) unsigned NOT NULL DEFAULT '0',
  `emoneytimestotals` int(10) unsigned NOT NULL DEFAULT '0',
  `joinactivitystatus` int(10) unsigned NOT NULL DEFAULT '0',
  `lastemoneytime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `system`
--

DROP TABLE IF EXISTS `system`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `system` (
  `openservertime` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `closeservertime` bigint(20) unsigned DEFAULT NULL,
  `combinedtimes` int(20) unsigned DEFAULT '0',
  PRIMARY KEY (`openservertime`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `talisman`
--

DROP TABLE IF EXISTS `talisman`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `talisman` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `bshow` int(4) unsigned NOT NULL DEFAULT '0',
  `realm` int(4) unsigned NOT NULL DEFAULT '0',
  `stageid` int(4) unsigned NOT NULL DEFAULT '0',
  `potentialnum` int(4) unsigned NOT NULL DEFAULT '0',
  `illusionnum` int(4) unsigned NOT NULL DEFAULT '0',
  `bless` int(4) unsigned NOT NULL DEFAULT '0',
  `countdown` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `skillslot` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `advancedtimes` int(4) unsigned NOT NULL DEFAULT '0',
  `critsymbolvalue` int(4) unsigned NOT NULL DEFAULT '0',
  `critsymbolendtime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `combat` int(4) unsigned NOT NULL DEFAULT '0',
  `leveluptime` bigint(4) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `targetaward`
--

DROP TABLE IF EXISTS `targetaward`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `targetaward` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `awardstatus` binary(255) DEFAULT NULL,
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `teambattle`
--

DROP TABLE IF EXISTS `teambattle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `teambattle` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `wingsnake` int(10) unsigned NOT NULL DEFAULT '0',
  `wingsnakeclean` int(10) unsigned NOT NULL DEFAULT '0',
  `guardcloudcity` int(10) unsigned NOT NULL DEFAULT '0',
  `guardcloudcityclean` int(10) unsigned NOT NULL DEFAULT '0',
  `guardvein` int(10) unsigned NOT NULL DEFAULT '0',
  `guardveinclean` int(10) unsigned NOT NULL DEFAULT '0',
  `dragonarray` int(10) unsigned NOT NULL DEFAULT '0',
  `dragonarrayclean` int(10) unsigned NOT NULL DEFAULT '0',
  `godpoint` int(10) unsigned NOT NULL DEFAULT '0',
  `todaypoint` int(10) unsigned NOT NULL DEFAULT '0',
  `impasselinetimes` int(10) unsigned NOT NULL DEFAULT '0',
  `impasserewardtimes` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `territoryguild`
--

DROP TABLE IF EXISTS `territoryguild`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `territoryguild` (
  `sceneid` int(10) unsigned NOT NULL DEFAULT '0',
  `guildid` int(10) unsigned DEFAULT NULL,
  `occupytime` bigint(10) unsigned DEFAULT NULL,
  PRIMARY KEY (`sceneid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `territoryreward`
--

DROP TABLE IF EXISTS `territoryreward`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `territoryreward` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `territory` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `thundergoldendiamond`
--

DROP TABLE IF EXISTS `thundergoldendiamond`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `thundergoldendiamond` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `vipdailyisget` int(10) unsigned NOT NULL DEFAULT '1',
  `annualvipdailyisget` int(10) unsigned NOT NULL DEFAULT '1',
  `vipprivilegeisget` int(10) unsigned NOT NULL DEFAULT '1',
  `annualvipprivilegeisget` int(10) unsigned NOT NULL DEFAULT '1',
  `vipgrowstatus` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `viptitlestatus` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `todayquest`
--

DROP TABLE IF EXISTS `todayquest`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `todayquest` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `taskid` int(20) unsigned NOT NULL DEFAULT '0',
  `progress` int(4) unsigned NOT NULL DEFAULT '0',
  `acceptlevel` int(4) unsigned NOT NULL DEFAULT '0',
  `difficulty` int(4) unsigned NOT NULL DEFAULT '0',
  `repay` int(4) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tokenshopitems`
--

DROP TABLE IF EXISTS `tokenshopitems`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tokenshopitems` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `shelfid` int(10) unsigned NOT NULL DEFAULT '0',
  `shopitemids` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`characterid`,`shelfid`),
  KEY `character` (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tokenshoppersonitem`
--

DROP TABLE IF EXISTS `tokenshoppersonitem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tokenshoppersonitem` (
  `autoid` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `shelfid` int(10) unsigned NOT NULL DEFAULT '0',
  `shopitemid` int(10) unsigned NOT NULL DEFAULT '0',
  `buytimes` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`autoid`),
  KEY `character` (`characterid`),
  KEY `shop` (`characterid`,`shopitemid`)
) ENGINE=MyISAM AUTO_INCREMENT=8309 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tokentaskshop`
--

DROP TABLE IF EXISTS `tokentaskshop`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tokentaskshop` (
  `groupid` int(20) unsigned NOT NULL DEFAULT '0',
  `startday` int(10) unsigned NOT NULL DEFAULT '0',
  `serveritemtimes` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `serverpay` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`groupid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `treasure`
--

DROP TABLE IF EXISTS `treasure`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `treasure` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `times` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `turntablepersonal`
--

DROP TABLE IF EXISTS `turntablepersonal`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `turntablepersonal` (
  `serialnumber` int(10) unsigned NOT NULL DEFAULT '0',
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `time` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `lotteryid` int(4) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`serialnumber`),
  KEY `character` (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `turntablerecord`
--

DROP TABLE IF EXISTS `turntablerecord`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `turntablerecord` (
  `serialnumber` int(10) unsigned NOT NULL DEFAULT '0',
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `name` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `lotteryId` int(4) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`serialnumber`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `vip`
--

DROP TABLE IF EXISTS `vip`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vip` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `viplev` int(10) unsigned NOT NULL DEFAULT '0',
  `vipexp` int(10) unsigned NOT NULL DEFAULT '0',
  `giftstatus` int(10) unsigned NOT NULL DEFAULT '0',
  `weekgiftstatus` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `vipbattle`
--

DROP TABLE IF EXISTS `vipbattle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vipbattle` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `battletimes` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `vipfeedback`
--

DROP TABLE IF EXISTS `vipfeedback`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vipfeedback` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `rewardstatus` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `vipsystem`
--

DROP TABLE IF EXISTS `vipsystem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vipsystem` (
  `resettime` char(255) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  PRIMARY KEY (`resettime`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `welfarecommon`
--

DROP TABLE IF EXISTS `welfarecommon`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `welfarecommon` (
  `characterid` int(20) unsigned NOT NULL DEFAULT '0',
  `coronausemoneytoday` int(20) unsigned NOT NULL DEFAULT '0',
  `coronapoint` int(20) unsigned NOT NULL DEFAULT '0',
  `coronaetimes` int(20) unsigned NOT NULL DEFAULT '0',
  `bgetweixinreward` int(20) unsigned NOT NULL DEFAULT '0',
  `coronaweekgifttimes` int(20) unsigned NOT NULL DEFAULT '0',
  `offlineexp` int(20) unsigned NOT NULL DEFAULT '0',
  `turntablescore` int(20) unsigned NOT NULL DEFAULT '0',
  `updayrewardstatus` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `findresourcestimes` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `findresourceslev` int(20) unsigned NOT NULL DEFAULT '0',
  `activestatus` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `activerewardstatus` int(20) unsigned NOT NULL DEFAULT '0',
  `activityvipnumreward` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `wing`
--

DROP TABLE IF EXISTS `wing`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `wing` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `bshow` int(4) unsigned NOT NULL DEFAULT '0',
  `realm` int(4) unsigned NOT NULL DEFAULT '0',
  `stageid` int(4) unsigned NOT NULL DEFAULT '0',
  `potentialnum` int(4) unsigned NOT NULL DEFAULT '0',
  `illusionnum` int(4) unsigned NOT NULL DEFAULT '0',
  `bless` int(4) unsigned NOT NULL DEFAULT '0',
  `countdown` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `advancedtimes` int(4) unsigned NOT NULL DEFAULT '0',
  `critsymbolvalue` int(4) unsigned NOT NULL DEFAULT '0',
  `critsymbolendtime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `combat` int(4) unsigned NOT NULL DEFAULT '0',
  `leveluptime` bigint(4) unsigned NOT NULL DEFAULT '0',
  `fashionid` int(4) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `wingfashion`
--

DROP TABLE IF EXISTS `wingfashion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `wingfashion` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `fashionid` int(4) unsigned NOT NULL DEFAULT '0',
  `bforever` int(4) unsigned NOT NULL DEFAULT '0',
  `expiretime` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`characterid`,`fashionid`),
  KEY `character` (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `worldboss`
--

DROP TABLE IF EXISTS `worldboss`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `worldboss` (
  `bossid` int(10) unsigned NOT NULL DEFAULT '0',
  `killerid` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`bossid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `worshipcharacter`
--

DROP TABLE IF EXISTS `worshipcharacter`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `worshipcharacter` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `target` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `worshiptimes`
--

DROP TABLE IF EXISTS `worshiptimes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `worshiptimes` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `times` int(10) unsigned DEFAULT NULL,
  `worshiptime` bigint(19) unsigned DEFAULT NULL,
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `xnfaskill`
--

DROP TABLE IF EXISTS `xnfaskill`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `xnfaskill` (
  `characterid` int(10) NOT NULL,
  `xnfaiD` int(10) NOT NULL,
  `xnfalayer` smallint(2) NOT NULL DEFAULT '1',
  `xnfalevel` smallint(5) NOT NULL DEFAULT '1',
  `hasfailnum` smallint(2) NOT NULL DEFAULT '0',
  `epuratexnfa` char(255) COLLATE utf8_unicode_ci DEFAULT '',
  PRIMARY KEY (`characterid`,`xnfaiD`),
  KEY `character` (`characterid`)
) ENGINE=MyISAM AUTO_INCREMENT=5 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `xnfaskillcombat`
--

DROP TABLE IF EXISTS `xnfaskillcombat`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `xnfaskillcombat` (
  `characterid` int(10) NOT NULL,
  `combat` int(2) NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM AUTO_INCREMENT=5 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `xyzfactivity`
--

DROP TABLE IF EXISTS `xyzfactivity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `xyzfactivity` (
  `activitystatus` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`activitystatus`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `xyzfactivitypersonal`
--

DROP TABLE IF EXISTS `xyzfactivitypersonal`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `xyzfactivitypersonal` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `playerstatus` int(10) unsigned NOT NULL DEFAULT '0',
  `playerrank` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `yellowdiamond`
--

DROP TABLE IF EXISTS `yellowdiamond`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `yellowdiamond` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `dailyfloor` int(10) unsigned NOT NULL DEFAULT '0',
  `dailyisget` int(10) unsigned NOT NULL DEFAULT '0',
  `growstatus` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `bnewbie` int(10) unsigned NOT NULL DEFAULT '0',
  `yearisget` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `yellowvip`
--

DROP TABLE IF EXISTS `yellowvip`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `yellowvip` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `discountid` char(255) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `status` char(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`characterid`,`discountid`),
  KEY `characterid` (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `zxjsactivity`
--

DROP TABLE IF EXISTS `zxjsactivity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `zxjsactivity` (
  `activitystatus` int(10) unsigned NOT NULL DEFAULT '0',
  `activityday` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`activitystatus`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `zxjsactivitypersonal`
--

DROP TABLE IF EXISTS `zxjsactivitypersonal`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `zxjsactivitypersonal` (
  `characterid` int(10) unsigned NOT NULL DEFAULT '0',
  `playerstatus` int(10) unsigned NOT NULL DEFAULT '0',
  `onlinesecond` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`characterid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping routines for database 'newserver'
--
/*!50003 DROP PROCEDURE IF EXISTS `GS_SP_BUYAUCTION` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
CREATE DEFINER=`shunwang_gamedb`@`%` PROCEDURE `GS_SP_BUYAUCTION`(IN para_id INT UNSIGNED, IN para_characterid INT UNSIGNED, IN para_buycharacter INT UNSIGNED, IN para_equipid INT UNSIGNED, IN para_itemid INT UNSIGNED, IN para_money BIGINT UNSIGNED, IN para_emoney BIGINT UNSIGNED, IN para_charge BIGINT UNSIGNED
, IN para_container text, IN para_container_type INT UNSIGNED)
begin

	update currency set money=para_money,emoney=para_emoney,chargeemoney=para_charge where characterid = para_buycharacter;
	if para_itemid > 0 then
		update item set characterid=para_buycharacter where id=para_itemid;
	end if;
	if para_equipid > 0 then
		update equipment set characterid=para_buycharacter where id=para_equipid;
	end if;
	if para_container<>'' then
		update containers set thing=para_container where characterid=para_buycharacter and type= para_container_type;
	end if;

	delete from auctiongoods where id = para_id;

end ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `GS_SP_CHARACTER_RENAME` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
CREATE DEFINER=`shunwang_gamedb`@`%` PROCEDURE `GS_SP_CHARACTER_RENAME`(IN para_name char(255), IN para_id INT UNSIGNED)
begin
	update auctiongoods set charactername=para_name where characterid=para_id;
	update auctionincome set charactername=para_name where characterid=para_id;
	update auctionincome set buyername=para_name where characterid_buyer=para_id;
	update turntablerecord set name=para_name where characterid=para_id;
	update coronarecord set name=para_name where characterid=para_id;
	update bankrecord set name=para_name where characterid=para_id;
	update precinctwarrank set name=para_name where characterid=para_id;
	update `character` set name=para_name where characterid=para_id;
end ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `GS_SP_CREATE_CHARACTER` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
CREATE DEFINER=`shunwang_gamedb`@`%` PROCEDURE `GS_SP_CREATE_CHARACTER`(IN para_account char(255), IN para_serverid INT UNSIGNED, IN para_name char(255), IN para_sex INT UNSIGNED, IN para_body_avatar INT UNSIGNED, IN para_weapon_avatar INT UNSIGNED, IN para_profession INT UNSIGNED, IN para_sceneid INT UNSIGNED, IN para_posx float, IN para_posy float,  IN para_nowtime datetime)
begin
declare  ret    int  DEFAULT 0;
declare character_num int default 0;
declare last_insert_id int unsigned default 0;

select count(*) from `character` where account = para_account and serverid = para_serverid into character_num;

if character_num = 0 then
	select count(*) from `character` where `character`.name = para_name into ret;

	if ret = 0 then
  		insert into `character` (account, serverid, name, level, sceneid, posx, posy, sex, profession, create_character_time, body_avatar, weapon_avatar) values (para_account, para_serverid, para_name, 1, para_sceneid, para_posx, para_posy, para_sex, para_profession, para_nowtime, para_body_avatar, para_weapon_avatar);
		set last_insert_id = LAST_INSERT_ID();
		insert into `characterskill` (`characterid`, `base_skill`, `lv_item_use_num`) values (last_insert_id, "", 0);
		insert into `characterstatus` (characterid, statusinfo) values (last_insert_id, "");
	end if;
	select ret, para_name, last_insert_id;
end if;

end ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `GS_SP_CREATE_ROBOT` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
CREATE DEFINER=`shunwang_gamedb`@`%` PROCEDURE `GS_SP_CREATE_ROBOT`(IN robotnum INT UNSIGNED)
begin
	declare nNum int default 0;
	declare idCharacter int unsigned default 0;
	declare account CHAR(32) default "";
	declare unLevel int unsigned default 99;
	declare unHp int unsigned default 999999999;
	declare unCombat int unsigned default 0;
	declare datetime1 datetime default date_sub(now(), interval 1 day);
	declare datetime2 datetime default date_add(now(), interval 1 day);
	declare cur_rank int unsigned default 1;

	select max(characterid) into idCharacter from `character`;
	if isnull(idCharacter)  then
		set idCharacter=0;
	end if;

	select max(ranking) into cur_rank from `arenaranking`;
	if isnull(cur_rank)  then
		set  cur_rank=0;
	end if;

	set nNum = 1;
	myloop: LOOP
		if nNum > robotnum then
			LEAVE myloop;
		end if;

		set account = CONCAT('robot', CAST(nNum as char));
		set unLevel = 80;
		set unCombat = 836;
		set idCharacter = idCharacter + 1;
		set cur_rank = cur_rank + 1;

		insert into `character` (characterid, account, name, level, sceneid, posx, posy, combat, profession, offlinetime, logintime, serverid, hp, body_avatar, weapon_avatar, realm, stageid) values (idCharacter, account, account, unLevel, 6006, 38, 41, unCombat, 0, datetime1, datetime2, 1, unHp, 2000000, 2000001, 3, 1);
		insert into `horse`(characterid,ride,steplev,curchoosehorseid) values(idCharacter, 1, 6, 6);
		insert into `wing`(characterid,bshow,realm,stageid) values(idCharacter, 1, 3, 2);
		insert into `refine`(characterid,realm,stageid) values(idCharacter, 3, 2);
		insert into `puppet`(characterid,realm,stageid) values(idCharacter, 3, 2);
		insert into `talisman`(characterid,bshow,realm,stageid) values(idCharacter,1, 3, 2);
		insert into `stamp`(characterid,realm,stageid) values(idCharacter, 3, 2);
		insert into `muse`(characterid,realm,stageid) values(idCharacter, 3, 2);
		insert into `worshiptimes`(characterid,times) values(idCharacter, 100);
		insert into `arenacharacter` (characterid, challengenum)  values  (idCharacter, 0);
		insert into `arenaranking` (ranking, characterid)  values (cur_rank, idCharacter);
		insert into `noviceprocess` (characterid, completetask)  values (idCharacter, 10009);
		insert into `heaven` (characterid,activestatus,wearheavenid) value (idCharacter, 2, 1);

     		set nNum = nNum + 1;
	end  LOOP  myloop;

end ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `GS_SP_INSERT_ARENA_HISTORY` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
CREATE DEFINER=`shunwang_gamedb`@`%` PROCEDURE `GS_SP_INSERT_ARENA_HISTORY`(para_characterid int unsigned, para_sourcecharacterid int unsigned, para_targetcharacterid int unsigned, para_winner int unsigned, para_old_rank  int unsigned, para_new_rank int unsigned, para_target_name char(255))
begin
	declare history_num int unsigned;
	select count(*) from arenahistory where characterid = para_characterid into history_num;
	if history_num >= 20 then
		delete from arenahistory where characterid=para_characterid order by id limit 1;
	end if;
	insert into `arenahistory` (characterid, sourcecharacterid, targetcharacterid, winnercharacterid, old_rank, new_rank, target_name) values (para_characterid, para_sourcecharacterid, para_targetcharacterid, para_winner, para_old_rank, para_new_rank, para_target_name);
end ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `GS_SP_REGISTER_ACCOUNT` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
CREATE DEFINER=`shunwang_gamedb`@`%` PROCEDURE `GS_SP_REGISTER_ACCOUNT`(IN para_account char(255), IN para_nowtime datetime)
begin

	declare account_num int DEFAULT 0;
	declare gm_local int DEFAULT 0;

	select count(*), gm from `account` where account = para_account into account_num, gm_local;

	if account_num = 0 then
		insert into `account` values (para_account, para_nowtime, 0);
	else
		select account_num, gm_local;
	end if;
end ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `GS_SP_UPDATEAUCTION` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
CREATE DEFINER=`shunwang_gamedb`@`%` PROCEDURE `GS_SP_UPDATEAUCTION`(IN para_id INT UNSIGNED, IN para_price INT UNSIGNED)
begin
	declare d_lock int unsigned default 0;
	declare d_res int unsigned default 1;
	declare d_num int unsigned default 0;
	select buylock,num from auctiongoods where id=para_id into d_lock,d_num;
	if d_lock <> 0 then
		set d_res = 0;
	end if;

	if d_res = 1 && d_num > 0 then
		update auctiongoods set price=para_price,perprice=(para_price/d_num) where id=para_id;
	end if;
	select buylock from auctiongoods where id=para_id;
end ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `GS_SP_LOCKAUCTION` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
CREATE DEFINER=`shunwang_gamedb`@`%` PROCEDURE `GS_SP_LOCKAUCTION`(IN para_id INT UNSIGNED, IN para_characterid INT UNSIGNED, IN para_price INT UNSIGNED, IN para_item INT UNSIGNED, IN para_equip INT UNSIGNED)
begin
	declare d_lock int unsigned default 0;
	declare d_price int unsigned default 0;
	declare d_res int unsigned default 1;
	select price,buylock from auctiongoods where id=para_id into d_price,d_lock;
	if d_lock <> 0 then
		set d_res = 0;
	elseif d_price <> para_price then
		set d_res = 0;
	end if;

	if d_res = 1 then
		update auctiongoods set buylock=para_characterid where id=para_id;
	end if;
	select a.id,a.characterid,a.charactername,a.goodstype,a.data,a.selltype,a.price,b.thingcfgid,b.overlap,c.thingcfgid,c.strengthen,c.realm,c.stage,c.additional,c.randomfactor,a.buylock,d_res from auctiongoods a LEFT JOIN item b ON a.goodstype=para_item and a.data=b.id LEFT JOIN equipment c ON a.goodstype=para_equip and a.data=c.id  where a.id=para_id;
end ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `GS_SP_MERCHANDISE` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
CREATE DEFINER=`shunwang_gamedb`@`%` PROCEDURE `GS_SP_MERCHANDISE`(IN para_id INT UNSIGNED, IN para_things char(255), IN para_container text, IN para_emoney BIGINT UNSIGNED, IN para_charge BIGINT UNSIGNED, IN para_other_id INT UNSIGNED, IN para_other_things char(255), IN para_other_container text, IN para_other_emoney BIGINT UNSIGNED, IN para_other_charge BIGINT UNSIGNED, IN para_container_type INT UNSIGNED)
begin

declare str char(255);
if (length(para_things) > 0) then
	set str = concat('update item set characterid=', para_id, ' where id in(', para_things, ')');
	set @sql1 = str;
	prepare stmt_p from @sql1;
	execute stmt_p;

	set str = concat('update equipment set characterid=', para_id, ' where id in(', para_things, ' )');
	set @sql1 = str;
	prepare stmt_p from @sql1;
	execute stmt_p;
end if;

if (length(para_other_things) > 0) then
	set str = concat('update item set characterid=', para_other_id, ' where id in(', para_other_things, ' )');
	set @sql1 = str;
	prepare stmt_p from @sql1;
	execute stmt_p;

	set str = concat('update equipment set characterid=', para_other_id, ' where id in(', para_other_things, ' )');
	set @sql1 = str;
	prepare stmt_p from @sql1;
	execute stmt_p;
end if;

update currency set emoney=para_emoney,chargeemoney=para_charge  where characterid=para_id;
update currency set emoney=para_other_emoney,chargeemoney=para_other_charge where characterid=para_other_id;
update containers set thing=para_other_container where characterid=para_other_id and type=para_container_type;
update containers set thing=para_container where characterid=para_id and type= para_container_type;

end ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `GS_SP_SEARCHAUCTION` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
CREATE DEFINER=`shunwang_gamedb`@`%` PROCEDURE `GS_SP_SEARCHAUCTION`(IN para_mainfilter INT UNSIGNED, IN para_subfilter INT UNSIGNED, IN para_quality INT UNSIGNED, IN para_level INT UNSIGNED)
begin

declare str char(255);
if (length(para_things) > 0) then
	set str = concat('update item set characterid=', para_id, ' where id in(', para_things, ')');
	set @sql1 = str;
	prepare stmt_p from @sql1;
	execute stmt_p;

	set str = concat('update equipment set characterid=', para_id, ' where id in(', para_things, ' )');
	set @sql1 = str;
	prepare stmt_p from @sql1;
	execute stmt_p;
end if;

if (length(para_other_things) > 0) then
	set str = concat('update item set characterid=', para_other_id, ' where id in(', para_other_things, ' )');
	set @sql1 = str;
	prepare stmt_p from @sql1;
	execute stmt_p;

	set str = concat('update equipment set characterid=', para_other_id, ' where id in(', para_other_things, ' )');
	set @sql1 = str;
	prepare stmt_p from @sql1;
	execute stmt_p;
end if;

update currency set emoney=para_emoney  where characterid=para_id;
update currency set emoney=para_other_emoney where characterid=para_other_id;
update containers set thing=para_other_container where characterid=para_other_id and type=para_container_type;
update containers set thing=para_container where characterid=para_id and type= para_container_type;

end ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-06-13 11:16:49
