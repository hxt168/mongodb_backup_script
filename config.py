import os  
import time
import properties_util

config_path=os.path.split(os.path.realpath(__file__))[0]+"/config.properties"
p=properties_util.Properties(config_path)
properties = p.getProperties()

## oss config
endpoint=properties["endpoint"]
accessKeyId=properties["accessKeyId"]
accessKeySecret=properties["accessKeySecret"]
bucket=properties["bucket"]
# oss multi upload thread num
upload_thread_num=5

## mongodb config
db_host=properties["db_host"]
db_port=int(properties["db_port"])
db_user=properties["db_user"]
db_passwd=properties["db_passwd"]
db_name=properties["db_name"]

# db backup to local   temp root path
#db_backup_root_path="/tmp/"
db_backup_root_path=properties["db_backup_root_path"]
# 1: increment backup  0:full backup
is_inc_backup=int(properties["is_inc_backup"])

# if mongo_shell not in PATH , need the mongo shell absolute path
mongo_shell_path=properties["mongo_shell_path"]

### full backup config

# db backup to local   temp directory name
db_backup_dir_name=r"mongodb_backup_titan_%s" %(time.strftime("%Y%m%d%H%M"))

### increment backup config

# every n day to full backup
full_backup_period=int(properties["full_backup_period"])
# db backup to local   temp directory name
db_one_cycle_backup_pre_name="mongodb_cycle_backup_test_titan_"
# compress file suffix  .zip  or   .tar.gz
compress_suffix=".tar.gz"

#  is upload to oss, 1: upload to oss,delete local file  0: no upload 
is_upload_to_oss=int(properties["is_upload_to_oss"])



