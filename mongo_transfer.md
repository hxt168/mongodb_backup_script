

mongo2向mongo3迁移同步
---


1.记录当前oplog时间点
---

(1)打开syn_replay_oplog.py，修改配置（需先配置好）
```
### config

## mongo2的数据库（源数据库）的配置，用于从此处下载oplog记录,可以用second主机。
src_db_host="127.0.0.1"
src_db_port=27018
# 用户需要有查询local表下的oplog.rs的权限，一般是admin表的backup角色
src_db_user="testb"
src_db_passwd="testb" 
src_db_name="che"


##   mongo3的数据库（目标数据库）的配置，用来执行oplog记录, 需要primary主机
target_db_host="127.0.0.1"
target_db_port=27017
target_db_user="tests"
target_db_passwd="tests" 
target_db_name="che"

# 备份恢复oplog的临时目录
restore_local_temp_path="H:\\pythoncode\\temp\\oplog_temp\\"

# 如果使用mongo客户端绿色版的，写上mongo客户端的绝对路径
mongo_shell_path=""
```
(2) 执行syn_replay_oplog.py，在restore_local_temp_path的目录下会生成last.json文件，记录了当前oplog时间点


2. 全量导出mongo2的数据库数据
---
（1）修改config.properties配置（需先配置好）
```
## 阿里云oss 连接配置（此处不上传oss，没用）
endpoint= oss.aliyuncs.com
accessKeyId = xxxxxxx
accessKeySecret = xxxxxxx
bucket = db-backup
## mongo2（源数据库） 连接配置
# 建议用从库的地址，减少对主库压力
db_host= localhost
db_port= 27017
# 需要对应数据库权限的用户
db_user= testb
db_passwd= testb
db_name= che
# 备份到本地的临时目录 
db_backup_root_path= /temp/titan_full_temp_backup/
# 如果使用mongo客户端绿色版的，写上mongo客户端的绝对路径
mongo_shell_path= /alidata1/dev/hanxuetong/mongodb/mongodb-linux-x86_64-3.0.6/bin/
# 增量备份还是全量备份 1: 增量备份  0:全量备份 （这里全量备份选0）
is_inc_backup=0
# 每多少天进行一次全量备份(这里没用)
full_backup_period=7
# 是否上传到oss，如果 1 ，上传成功后会删除本地备份文件；0:不上传到oss（这里不上传oss，选0）
is_upload_to_oss= 0
```
（2）执行start.py全量备份，备份后db_backup_root_path路径下会有备份数据



3. 将刚才备份的全量导入mongo3数据库
---
（1）打开restore_full.py，修改配置（需先配置好）
```
## 阿里云oss 配置（这里不从oos下载，没用）
endpoint="oss.aliyuncs.com"
accessKeyId="xxxxxxx"
accessKeySecret="xxxxxxx"
bucket="db-backup"

## mongodb3（目标库） 导入的配置
db_host="localhost"
db_port=27017
# 数据库对应的用户
db_user="test"
db_passwd="test" 
db_name="che"

#  recent circle backup direactory on oss 最新备份文件的周期名， (步骤2中源数据库备份的名称，如mongodb_backup_titan_201512242039)
last_circle_backup_dir_name="mongodb_cycle_backup_titan_20151124141133"

#  （此处无用）
last_full_backup_file_suffix=".tar.gz"
#  备份恢复的目录，实际全量备份的路径为 restore_local_temp_path+last_circle_backup_dir_name+db_name   （此处恢复的路径为步骤2中源数据库备份的路径：db_backup_root_path）
restore_local_temp_path="H:\\pythoncode\\temp\\restore\\"
#  如果使用mongo客户端绿色版的，写上mongo客户端的绝对路径
mongo_shell_path="/alidata1/dev/hanxuetong/mongodb/mongodb-linux-x86_64-3.0.6/bin/"
# backup file has download to local ? if True,will not download backup files from oss
# 是否备份文件已经下载到本地，如果true，则不会从oss下载和解压，本地已有 （已下载，设为True）
has_download_to_local=True
# 恢复时是否先删除旧的数据库 （需删除原数据库，设为True）
is_drop_old_restore=True  
```

（2）执行restore_full.py全量恢复到mongo3（目标数据库）


4.重复运行下syn_replay_oplog.py，对mongo3（目标数据库）进行下数据同步
---

5.部署网站,开始双写
---

6. 运行syn_replay_oplog.py，再同步一次
---

























































