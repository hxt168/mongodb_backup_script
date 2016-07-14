#!/usr/bin/env
import fun
import time
import os
import json


### config


## src  mongodb config,to download oplog,second better
src_db_host="127.0.0.1"
src_db_port=27018
src_db_user="testb"
src_db_passwd="testb" 
src_db_name="che"


## target mongodb config,to relpay oplog, need primary
target_db_host="127.0.0.1"
target_db_port=27017
target_db_user="tests"
target_db_passwd="tests" 
target_db_name="che"


restore_local_temp_path="H:\\pythoncode\\temp\\oplog_temp\\"

# if mongo_shell not in PATH , need the mongo shell absolute path
mongo_shell_path=""



def oplog_backup(db_backup_root_path):
	db_host=src_db_host
	db_port=src_db_port
	db_user=src_db_user
	db_passwd=src_db_passwd
	db_name=src_db_name
	
	db_backup_path=db_backup_root_path

	db_inc_backup_name=r"oplog_backup/oplog_%s" %(time.strftime("%Y%m%d%H%M%S"))
	db_inc_backup_path=db_backup_path+"/"+db_inc_backup_name

	local_last_time_file_path=db_backup_path+"/"+"last.json"

	conn=fun.get_pymongo_connect(db_host, db_port, db_user, db_passwd,"admin")
	# server oplog last time
	remote_last_time=fun.get_last_oplog_timestamp(conn,db_name)
	last_time_long=None
	last_time_inc=None
	has_last_time_file=0;
	local_last_time_info=fun.read_file(local_last_time_file_path)
	if local_last_time_info:
		json_local_last_time=json.loads(local_last_time_info)
		last_time_long=json_local_last_time["time"]
		last_time_inc=json_local_last_time["inc"]
		fun.dump_oplog_mongodb(db_host, db_port, db_user, db_passwd, db_name, db_inc_backup_path,last_time_long,last_time_inc)
		db_inc_oplog_rs_path=db_inc_backup_path+"/local/oplog.rs.bson"
		if not fun.is_file_not_empty(db_inc_oplog_rs_path): #no new oplog record
			fun.del_dir_or_file(db_inc_backup_path)
		else:
			inc_oplog_rs_mv_to_path=db_inc_backup_path+"/oplog.bson"
			fun.move_file(db_inc_oplog_rs_path,inc_oplog_rs_mv_to_path)
			fun.del_dir_or_file(db_inc_backup_path+"/local/")
		has_last_time_file=1
	else:
		print "has not record oplog time,this run will save this recent oplog time";
	local_last_time_info='{"time":"%d","inc":"%d"}' % (remote_last_time.time, remote_last_time.inc)
	fun.write_file(local_last_time_file_path,local_last_time_info)
	if has_last_time_file==1:
		return db_inc_backup_path;
	else:
		return None;


def restore_oplog_mongodb(db_host, db_port,db_user, db_passwd, db_restore_path,mongo_shell_path=""):
	start_time = time.time()
	if db_user:
		cmd="%smongorestore --oplogReplay -h %s --port %s -u %s -p %s %s" %(mongo_shell_path,db_host, db_port,db_user, db_passwd, db_restore_path)
		print(cmd)
		os.system(cmd)
	else:
		cmd="%smongorestore --oplogReplay -h %s --port %s %s" %(mongo_shell_path,db_host, db_port, db_restore_path)
		print(cmd)
		os.system(cmd)
	fun.print_cost_time("restore oplog", start_time)



	
if __name__ == "__main__":
	start_time = time.time()
	
	fun.mongo_shell_path=mongo_shell_path
	
	db_inc_backup_path=oplog_backup(restore_local_temp_path)
	#time.sleep(15)
	#db_inc_backup_path="H:\\pythoncode\\temp\\oplog_temp\\oplog_backup\\oplog_20151224194545"
	print db_inc_backup_path
	if db_inc_backup_path:
		restore_oplog_mongodb(target_db_host, target_db_port,target_db_user, target_db_passwd, db_inc_backup_path,mongo_shell_path)
			
	fun.print_cost_time("syn done ", start_time)
