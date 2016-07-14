

功能
---
定期对mongodb数据库数据进行全量备份或增量备份，并压缩上传到阿里云oss。（增量备份暂只能在mongodb副本集架构时使用）

脚本运行环境
---
使用python语言编写，需安装python,pymongo和mongodb shell客户端（测试时使用python 2.7.6,pymongo 3.0.3和mongodb shell 2.0.4）。


脚本部署步骤
---
1. 将脚本放到一台linux主机
2. 如果是增量备份，创建mongodb 备份角色用户或更高权限的admin库用户。（导出时会先切换到admin库来验证权限，需有查询local库，mongodump local库和mongodump目标库的权限）
```
	use admin
	db.addUser( { user: "xxxxx",
				  pwd: "xxxxx",
				  roles: [ "backup" ]
				} )
```
3. 编辑config.properties，修改oss、mongodb连接等配置信息
```
	## 阿里云oss 连接配置
	endpoint= oss.aliyuncs.com
	accessKeyId = xxxxxxx
	accessKeySecret = xxxxxxx
	bucket = db-backup
	## mongodb 连接配置
	# 建议用从库的地址，减少对主库压力
	db_host= localhost
	db_port= 27017
	# 如果是增量备份方案，为步骤2中的创建的用户，或更高权限的admin用户；如果是全量备份方案，则只需有目标库的操作权限
	db_user= testb
	db_passwd= testb
	# 目标库
	db_name= che
	# 备份到本地的临时目录 
	db_backup_root_path= /temp/titan_backup/
	# 如果使用mongo客户端绿色版的，写上mongo客户端的绝对路径
	mongo_shell_path= /alidata1/dev/hanxuetong/mongodb/mongodb-linux-x86_64-3.0.6/bin/
	# 增量备份还是全量备份 1: 增量备份  0:全量备份
	is_inc_backup=1
	# 每多少天进行一次全量备份
	full_backup_period=7
	# 是否上传到oss，如果 1 ，上传成功后会删除本地备份文件；0:不上传到oss
	is_upload_to_oss= 0
```
4. 将start.py加入linux定时任务。crontab任务配置如 0 4 * * * python /xxx/start.py >> /xxx/xxx.log 2>&1



增量时恢复步骤：
---
1. 创建mongodb 具有applyOps权限的角色 以及用此角色的用户。（需有执行 mongorestore --oplogReplay的用户权限）
```
	use admin
	db.createRole(
	   {
		 role: "applyOpsRole",
		 privileges: [
		   { resource: { anyResource: true }, actions: [ "anyAction"] }
		 ],
		 roles: []
	   }
	)
	db.addUser( { user: "xxxx",
			  pwd: "xxxx",
			  roles: [ "applyOpsRole" ]
			} )
```
2. 修改 restore_inc.py里的配置
```
	## 阿里云oss 配置
	endpoint="oss.aliyuncs.com"
	accessKeyId="xxxxxxx"
	accessKeySecret="xxxxxxx"
	bucket="db-backup"

	## mongodb导入的配置
	db_host="localhost"
	db_port=27017
	# 步骤1创建的用户
	db_user="testr"
	db_passwd="testr" 
	db_name="che"

	#  recent circle backup direactory on oss 最新备份文件的周期名，即备份临时目录中mongodb_inc_backup_info.json的last_circle_backup_dir_name 或 oss中文件夹名
	last_circle_backup_dir_name="mongodb_cycle_backup_titan_20151124141133"
	#  从oss上下载到本地的临时目录
	restore_local_temp_path="H:\\pythoncode\\temp\\restore\\"
	#  如果使用mongo客户端绿色版的，写上mongo客户端的绝对路径
	mongo_shell_path= "/alidata1/dev/hanxuetong/mongodb/mongodb-linux-x86_64-3.0.6/bin/"
	# backup file has download to local ? if True,will not download backup files from oss
	# 是否备份文件已经下载到本地，如果true，则不会从oss下载和解压，本地已有
	has_download_to_local=False
	# 恢复时是否先删除旧的数据库
	is_drop_old_restore=True
```
3. 导入期间停止mongodb写入
4. 执行 restore_inc.py


全量时恢复步骤：
---
1. 修改 restore_full.py里的配置
```
	## 阿里云oss 配置
	endpoint="oss.aliyuncs.com"
	accessKeyId="xxxxxxx"
	accessKeySecret="xxxxxxx"
	bucket="db-backup"

	## mongodb导入的配置
	db_host="localhost"
	db_port=27017
	# 数据库对应的用户
	db_user="test"
	db_passwd="test" 
	db_name="che"

	#  recent circle backup direactory on oss 最新备份文件的周期名， oss 上存储的文件名称是  last_circle_backup_dir_name+last_full_backup_file_suffix
	last_circle_backup_dir_name="mongodb_cycle_backup_titan_20151124141133"
	
	last_full_backup_file_suffix=".tar.gz"
	#  备份的目录，实际全量备份的路径为 restore_local_temp_path+last_circle_backup_dir_name+db_name
	restore_local_temp_path="H:\\pythoncode\\temp\\restore\\"
	#  如果使用mongo客户端绿色版的，写上mongo客户端的绝对路径
	mongo_shell_path="/alidata1/dev/hanxuetong/mongodb/mongodb-linux-x86_64-3.0.6/bin/"
	# backup file has download to local ? if True,will not download backup files from oss
	# 是否备份文件已经下载到本地，如果true，则不会从oss下载和解压，本地已有
	has_download_to_local=False
	# 恢复时是否先删除旧的数据库
	is_drop_old_restore=True
```
2. 执行 restore_full.py

相关:
---

增量备份实现原理
---
一个周期内（如一星期）先备份一次全量数据库，然后后面每次备份 上次记录点到最新时间内的oplog文件。
Oplog 记录了MongoDB数据库的更改操作信息，其保存在local库的oplog.rs表，在集群架构才存在，单机不会有，故增量备份不能在单机下使用。从库是通过异步复制主库的Oplog文件，从而达到与主库的同步。
oplog有大小限制，超过指定大小，新的记录会覆盖旧的操作记录。



全量脚本执行时的流程
---
1. 备份mongodb数据库到本地
2. 进行压缩
3. 上传到oss
4. 检验oss与本地文件的大小是否相同
5. 删除本地备份文件


增量脚本执行时的流程
---
1. 读取上一个周期执行信息判断是否需要创建新的周期
2. 获得mongodb上oplog最近记录的时间点current timestamp position
3. 从本地读取上一次执行时mongodb的oplog时间点
4. dump导出全量数据或增量oplog文件到本地，增量oplog文件的导出范围是 上次oplog记录点到最新时间内的oplog文件
5. 保存步骤2获取的current timestamp position到本地，作为下一次执行步骤3中的时间点
6. 进行压缩
7. 上传到oss
8. 删除本地备份文件


恢复时脚本执行的流程
---
1. 从oss上下载指定周期的备份文件到本地
2. 对全量文件和增量oplog的zip文件进行解压
3. 用 mongorestore对全量文件进行导入
4. 用 mongorestore --oplogReplay 分别对各时间段的oplog文件进行导入

