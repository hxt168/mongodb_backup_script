#!/usr/bin/env
import fun
import time
import config
from oss.oss_util import *

# need delete filename prefix
oss_file_pre="mongodb_cycle_backup_test_titan_"

# not delete file dir
un_delete_file_dir=["mongodb_cycle_backup_test_titan_20151123152558"]

def check_in_array():
	if "healing potion" in inventory:
		print "You will live to fight another day."

if __name__ == "__main__":
	start_time = time.time()
	
	oss=fun.get_oss_connect(config.endpoint, config.accessKeyId, config.accessKeySecret);

	file_list_on_oss=fun.list_bucket_files(oss,config.bucket,oss_file_pre)
	for each in file_list_on_oss:
		file_name=each[0];
		file_dir_name=file_name.split("/")[0]
		print(file_dir_name)
		if file_dir_name not in un_delete_file_dir:
			fun.del_bucket_file(oss,config.bucket,file_name)
			print("del "+file_name)

	fun.print_cost_time("all done ", start_time)
	fun.list_bucket_files(oss,config.bucket)


