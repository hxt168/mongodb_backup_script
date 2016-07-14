#!/usr/bin/env
import fun
import time
import config
import json
import lock_check
from oss.oss_util import *

def get_format_time(secs):
	return time.strftime("%Y%m%d%H%M%S",time.localtime(secs)) 

# increment backup
def do_inc_backup():
	is_need_new_circle=False
	# every n day to full backup
	full_backup_period=config.full_backup_period
	#config.db_one_cycle_backup_pre_name="mongodb_cycle_backup_titan_"
	
	local_cycle_info_path=config.db_backup_root_path+"/"+"mongodb_inc_backup_info.json"
	local_cycle_info_con=fun.read_file(local_cycle_info_path)
	last_circle_backup_time=0
	if local_cycle_info_con:
		local_cycle_info=json.loads(local_cycle_info_con)
		last_circle_backup_time_str=local_cycle_info["last_circle_backup_time"]
		last_circle_backup_time=int(last_circle_backup_time_str)
		db_one_cycle_backup_name=local_cycle_info["last_circle_backup_dir_name"]
	else:
		# not backuped 
		is_need_new_circle=True

	now_time=int(time.time())
	if (now_time-last_circle_backup_time)>60*60*24*full_backup_period:
		# need new circle
		db_one_cycle_backup_name=config.db_one_cycle_backup_pre_name+get_format_time(now_time)
		is_need_new_circle=True
	#else:
	#	db_one_cycle_backup_name=config.db_one_cycle_backup_pre_name+get_format_time(last_circle_backup_time)
	
	start_inc_backup(db_one_cycle_backup_name,last_circle_backup_time)
	
	#save inc_backup_info
	if is_need_new_circle:
		local_last_time_info='{"last_circle_backup_time":"%d","last_circle_backup_dir_name":"%s"}' % (now_time,db_one_cycle_backup_name)
		fun.write_file(local_cycle_info_path,local_last_time_info)


def start_inc_backup(db_one_cycle_backup_name,last_circle_backup_time):
	db_host=config.db_host
	db_port=config.db_port
	db_user=config.db_user
	db_passwd=config.db_passwd
	db_name=config.db_name

	upload_flag=0  # 0:not upload  1:upload full backup file 2: upload inc oplog backup file
	db_backup_root_path=config.db_backup_root_path
	#db_one_cycle_backup_name=r"back_%s" %(time.strftime("%Y%m%d"))
	
	db_backup_path=db_backup_root_path+db_one_cycle_backup_name
	db_full_backup_name="full_backup"
	db_full_backup_path=db_backup_path+"/"+db_full_backup_name
	db_inc_backup_name=r"inc_backup/oplog_%s" %(time.strftime("%Y%m%d%H%M%S"))
	db_inc_backup_path=db_backup_path+"/"+db_inc_backup_name

	local_last_time_file_path=db_backup_path+"/"+"last.json"

	conn=fun.get_pymongo_connect(db_host, db_port, db_user, db_passwd,"admin")
	# server oplog last time
	remote_last_time=fun.get_last_oplog_timestamp(conn,db_name)
	last_time_long=None
	last_time_inc=None
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
			upload_flag=2
	else:
		#full backup
		fun.backup_full_mongodb(db_host,db_port, db_user, db_passwd, db_name, db_full_backup_path)
		upload_flag=1
	local_last_time_info='{"time":"%d","inc":"%d"}' % (remote_last_time.time, remote_last_time.inc)
	fun.write_file(local_last_time_file_path,local_last_time_info)
	if config.is_upload_to_oss!=0 and upload_flag!=0:
		if upload_flag==2:
			print("upload inc oplog backup file...")			
			db_zip_to_backup_path=db_inc_backup_path
			db_backup_zip_name=db_one_cycle_backup_name+"/"+db_inc_backup_name+config.compress_suffix			
			db_backup_zip_path=db_backup_root_path+"/"+db_backup_zip_name
			zip_and_upload_oss(db_zip_to_backup_path,db_backup_zip_name,db_backup_zip_path)
			
		# upload full backup file and del last backup direactory
		if upload_flag==1:
			print("upload full db backup file...")
			#full db upload
			db_zip_to_backup_path=db_full_backup_path
			db_backup_zip_name=db_one_cycle_backup_name+"/full_backup"+config.compress_suffix		
			db_backup_zip_path=db_backup_root_path+"/"+db_backup_zip_name
			zip_and_upload_oss(db_zip_to_backup_path,db_backup_zip_name,db_backup_zip_path)
			if last_circle_backup_time!=0:
				#del local last circle's oplog inc files
				last_cycle_backup_name=config.db_one_cycle_backup_pre_name+get_format_time(last_circle_backup_time)
				last_db_backup_path=db_backup_root_path+last_cycle_backup_name
				fun.del_dir_or_file(last_db_backup_path)
				
		
def do_full_backup():
	db_backup_dir=config.db_backup_root_path+config.db_backup_dir_name;
	## backup mongodb to local
	fun.backup_mongodb(config.db_host, config.db_user, config.db_passwd, config.db_name, db_backup_dir)
	if config.is_upload_to_oss!=0:
		db_backup_zip_name=config.db_backup_dir_name+config.compress_suffix;
		db_backup_zip_path=config.db_backup_root_path+db_backup_zip_name;
		zip_and_upload_oss(db_backup_dir,db_backup_zip_name,db_backup_zip_path)
	
def zip_and_upload_oss(db_backup_dir,db_backup_zip_name,db_backup_zip_path):
	print("begin zip files...")
	#db_backup_zip_name=config.db_backup_dir_name+".zip";
	#db_backup_zip=config.db_backup_root_path+db_backup_zip_name;
	if not os.path.exists(db_backup_dir):
		raise IOError('to zip file not exist !')
	## zip 
	if config.compress_suffix ==".tar.gz":
		fun.tar_files(db_backup_dir,db_backup_zip_path)
	else:
		fun.zip_files(db_backup_dir,db_backup_zip_path)
	
	print("begin upload to oss...")
	oss=fun.get_oss_connect(config.endpoint, config.accessKeyId, config.accessKeySecret);
	## upload to oss
	fun.large_multi_upload_file(oss,config.bucket,db_backup_zip_path,db_backup_zip_name, config.upload_thread_num)
	
	remote_file_size=fun.get_remote_file_size(oss,config.bucket,db_backup_zip_name)
	local_size=os.path.getsize(db_backup_zip_path)
	if remote_file_size !=0 and remote_file_size == local_size:
		fun.del_dir_or_file(db_backup_dir)
		fun.del_dir_or_file(db_backup_zip_path)
		print(db_backup_zip_name+" upload success done! ")
	else:
		print db_backup_zip_name+" upload fail fail !!! remote_file_size:%d , local_size:%d " % (remote_file_size,local_size)	
	#fun.list_bucket_files(oss,config.bucket)



if __name__ == "__main__":
	lock=lock_check.LockCheck();
	is_lock=lock.is_lock()
	if not is_lock:
		try:
			lock.lock();
			start_time = time.time()
			print("begin to dump mongodb database ...");
			
			is_inc_backup=config.is_inc_backup
			fun.mongo_shell_path=config.mongo_shell_path
			if is_inc_backup==1:
				do_inc_backup()
			else:
				do_full_backup()
			#time.sleep(10)
			fun.print_cost_time("all done ", start_time)
			
		except Exception, e:
			raise e
		finally:
			lock.release()
	else:
		print "now is running backup db,exit!"
