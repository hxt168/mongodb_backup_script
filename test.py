#!/usr/bin/env
import fun
import time
import config
from oss.oss_util import *
import properties_util

if __name__ == "__main__":
	start_time = time.time()
	
	print("begin to dump mongodb database ...");
	db_backup_dir=config.db_backup_root_path+config.db_backup_dir_name;
	## backup mongodb to local
	#fun.backup_mongodb(config.db_host, config.db_user, config.db_passwd, config.db_name, db_backup_dir)
	
	print("begin zip files...")
	db_backup_zip_name=config.db_backup_dir_name+".zip";
	db_backup_zip=config.db_backup_root_path+db_backup_zip_name;
	## zip 
	#fun.zip_files(db_backup_dir,db_backup_zip)
	
	print("begin upload to oss...")
	oss=fun.get_oss_connect(config.endpoint, config.accessKeyId, config.accessKeySecret);
	## upload to oss
	#fun.upload_file_to_bucket(oss,config.bucket,db_backup_zip,db_backup_zip_name)
	#fun.upload_large_file_to_bucket(oss,config.bucket,db_backup_zip,db_backup_zip_name, 5)
	
	db_backup_zip="H:\\pythoncode\\temp\\mongodb_cycle_backup_titan_20151120182050_full.zip"
	db_backup_zip_name="mongodb_cycle_backup_titan_20151120182050_full.zip"
	#fun.large_multi_upload_file(oss,config.bucket,db_backup_zip,db_backup_zip_name, config.upload_thread_num)
	#fun.download_file_to_local(oss,config.bucket,db_backup_zip,db_backup_zip_name)
	#fun.del_bucket_file(oss,config.bucket,"mongodb_backup_201511201758.zip")
	#fun.del_dir_or_file("H:\\pythoncode\\temp\\mongodb_backup_201511031636.zip")

	fun.print_cost_time("all done ", start_time)
	#fun.list_bucket_files(oss,config.bucket)
	p=properties_util.Properties("config.properties")
	
	print os.path.split(os.path.realpath(__file__))[0];
	


