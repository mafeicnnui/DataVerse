# 数据库结构说明（MySQL）

本项目默认使用的 MySQL 连接：`10.2.39.59:3306`，用户：`puppet`，密码：`Puppet@123`，库：`db_expert`。

后端 ORM 映射的表为 `t_db_source`（首次运行会自动创建，若不存在）：

```sql
CREATE TABLE `t_db_source` (
  `id`          INT(11) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `ip`          VARCHAR(100) NOT NULL COMMENT '数据库IP',
  `port`        VARCHAR(20)  NOT NULL COMMENT '数据库端口',
  `database`    VARCHAR(40)  NOT NULL COMMENT '数据库名称',
  `user`        VARCHAR(20)  DEFAULT NULL COMMENT '用户名',
  `password`    VARCHAR(200) DEFAULT NULL COMMENT '密码',
  `db_type`     VARCHAR(20)  DEFAULT NULL COMMENT '数据库类型,t_dmlx(dm=01)', 
  `db_env`      VARCHAR(1)   DEFAULT NULL COMMENT '数据库环境,t_dmlx(dm=02)',
  `description` VARCHAR(40)  DEFAULT NULL COMMENT '数据源描述',
  `status`      VARCHAR(1)   DEFAULT NULL COMMENT '数据源状态,t_dmlx(dm=03)', 
  `create_time` DATETIME     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `creator`     VARCHAR(20)  DEFAULT NULL COMMENT '创建人',
  `update_time` DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最近更新时间',
  `updator`     VARCHAR(20)  DEFAULT NULL COMMENT '更新人',
  PRIMARY KEY (`id`)
) ENGINE=INNODB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;
```

说明：应用启动时使用 SQLAlchemy 的 `create_all` 仅“创建不存在的表”，不会自动修改已存在表的字段定义/注释/默认值。如需迁移，请使用 Alembic 或手工执行 DDL。

> 后续如新增表结构，请在本文件继续追加章节；README 仅保留入口链接。
