/*
SQLyog Ultimate v12.08 (64 bit)
MySQL - 5.6.44-log : Database - db_expert
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`db_expert` /*!40100 DEFAULT CHARACTER SET utf8mb4 */;

/*Table structure for table `t_db_source` */

CREATE TABLE `t_db_source` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ip` varchar(100) NOT NULL COMMENT '数据库IP',
  `port` varchar(20) NOT NULL COMMENT '数据库端口',
  `user` varchar(20) DEFAULT NULL COMMENT '用户名',
  `password` varchar(200) DEFAULT NULL COMMENT '密码',
  `db_type` varchar(20) DEFAULT NULL COMMENT '数据库类型',
  `db_env` varchar(1) DEFAULT NULL COMMENT '数据库环境',
  `description` varchar(40) DEFAULT NULL COMMENT '数据源描述',
  `status` varchar(1) DEFAULT NULL COMMENT '数据源状态',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `creator` varchar(20) DEFAULT NULL COMMENT '创建人',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最近更新时间',
  `updator` varchar(20) DEFAULT NULL COMMENT '更新人',
  PRIMARY KEY (`id`),
  KEY `ix_t_db_source_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4;

/*Data for the table `t_db_source` */

insert  into `t_db_source`(`id`,`ip`,`port`,`user`,`password`,`db_type`,`db_env`,`description`,`status`,`create_time`,`creator`,`update_time`,`updator`) values (1,'10.2.39.40','3306','hopsonone','hopsonone123','0','3','dev-mysql-master','1','2025-09-02 14:30:02',NULL,'2025-09-02 14:30:13',NULL),(2,'10.2.39.46','3306','hopsonone','hopsonone123','0','3','dev-mysql-slave','1','2025-09-02 14:30:02',NULL,'2025-09-02 14:30:13',NULL),(3,'10.2.39.80','3306','hopsonone','hopsonone123','0','2','test-mysql-master','1','2025-09-02 14:30:02',NULL,'2025-09-02 14:30:13',NULL);

/*Table structure for table `t_dmlx` */

CREATE TABLE `t_dmlx` (
  `dm` varchar(10) NOT NULL COMMENT '大类代码',
  `mc` varchar(100) DEFAULT NULL COMMENT '大类名称',
  `status` varchar(1) DEFAULT NULL COMMENT '大类状态,0:失效，1：有效',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`dm`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

/*Data for the table `t_dmlx` */

insert  into `t_dmlx`(`dm`,`mc`,`status`,`create_time`,`update_time`) values ('01','数据源类型','1','2025-08-25 14:21:56','2025-08-25 14:21:56'),('02','数据库环境','1','2025-08-25 14:21:56','2025-08-25 14:21:56'),('03','数据源状态','1','2025-08-25 14:21:56','2025-08-25 14:21:56'),('04','服务器类型','1','2025-09-04 10:01:04','2025-09-04 10:01:04'),('05','服务器状态','1','2025-09-04 10:12:32','2025-09-04 10:12:32'),('06','认证方式','1','2025-09-04 14:13:26','2025-09-04 14:13:26');

/*Table structure for table `t_dmmx` */

CREATE TABLE `t_dmmx` (
  `dm` varchar(10) NOT NULL COMMENT '代码大类',
  `dmm` varchar(20) NOT NULL COMMENT '代码小类',
  `dmmc` varchar(200) DEFAULT NULL COMMENT '小类名称',
  `status` varchar(1) DEFAULT NULL COMMENT '小类状态,0:失效，1：有效',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`dm`,`dmm`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

/*Data for the table `t_dmmx` */

insert  into `t_dmmx`(`dm`,`dmm`,`dmmc`,`status`,`create_time`,`update_time`) values ('01','0','mysql','1','2025-08-25 14:21:56','2025-08-25 14:21:56'),('01','1','oracle','1','2025-08-25 14:21:56','2025-08-25 14:21:56'),('01','2','sqlserver','1','2025-08-25 14:21:56','2025-08-25 14:21:56'),('01','3','postgresql','1','2025-08-25 14:21:56','2025-08-25 14:21:56'),('01','4','mongodb','1','2025-08-25 14:21:56','2025-08-25 14:21:56'),('01','5','redis','1','2025-08-25 14:21:56','2025-08-25 14:21:56'),('01','6','elasticsearch','1','2025-08-25 14:21:56','2025-08-25 14:21:56'),('01','7','clickhouse','1','2025-08-25 14:21:56','2025-08-25 14:21:56'),('01','8','doris','1','2025-08-25 14:21:56','2025-08-25 14:21:56'),('02','1','生产环境','1','2025-08-25 14:21:56','2025-08-25 14:21:56'),('02','2','测试环境','1','2025-08-25 14:21:56','2025-08-25 14:21:56'),('02','3','开发环境','1','2025-08-25 14:21:56','2025-08-25 14:21:56'),('02','4','预生产环境','1','2025-08-25 14:21:56','2025-08-25 14:21:56'),('03','0','无效','1','2025-08-25 14:21:56','2025-08-25 14:21:56'),('03','1','有效','1','2025-08-25 14:21:56','2025-08-25 14:21:56'),('04','1','windows','1','2025-09-04 10:01:20','2025-09-04 10:01:20'),('04','2','linux','1','2025-09-04 10:01:40','2025-09-04 10:01:40'),('05','0','无效','1','2025-09-04 10:12:55','2025-09-04 10:12:55'),('05','1','有效','1','2025-09-04 10:12:59','2025-09-04 10:12:59'),('06','1','口令','1','2025-09-04 14:14:07','2025-09-04 14:14:07'),('06','2','密钥','1','2025-09-04 14:14:11','2025-09-04 14:14:11');

/*Table structure for table `t_server` */

CREATE TABLE `t_server` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '标识',
  `server_desc` varchar(100) DEFAULT NULL COMMENT '服务器描述',
  `server_ip` varchar(100) NOT NULL COMMENT '服务器地址',
  `server_port` varchar(10) NOT NULL COMMENT '服务器端口',
  `server_user` varchar(20) NOT NULL COMMENT '用户名',
  `server_pass` varchar(200) NOT NULL COMMENT '密码',
  `server_os` varchar(100) NOT NULL COMMENT '系统,t_dmlx(dm=04)',
  `status` varchar(20) NOT NULL COMMENT '状态,t_dmlx(dm=05)',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `creator` varchar(20) DEFAULT NULL COMMENT '创建人',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `updator` varchar(20) DEFAULT NULL COMMENT '更新人',
  `auth_memthod` varchar(20) DEFAULT NULL COMMENT '认证方式,t_dmlx(dm=06)',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4;

/*Data for the table `t_server` */

insert  into `t_server`(`id`,`server_desc`,`server_ip`,`server_port`,`server_user`,`server_pass`,`server_os`,`status`,`create_time`,`creator`,`update_time`,`updator`,`auth_memthod`) values (1,'开发mysql服务器','172.26.29.101','65508','hopson','Tong2@01!8*','2','1','2025-09-04 11:27:51',NULL,'2025-09-04 15:01:31',NULL,'1'),(2,'开发sqlserver服务器','10.2.39.9','3389','administratar','Tong2@01!8*','1','1','2025-09-04 11:27:56',NULL,'2025-09-04 11:27:56',NULL,'1'),(3,'aliyun-dev','39.106.33.183','22','root','MAfeiCNnui791005','2','1','2025-09-05 17:25:09',NULL,'2025-09-05 17:25:06',NULL,'1');

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
