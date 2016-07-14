#!/usr/bin/env
import fun
import time
import os
from oss.oss_util import *
import zipfile

### config

## oss 
endpoint="oss.aliyuncs.com"
accessKeyId="xxxx"
accessKeySecret="xxxx"
bucket="db-backup"
# oss multi upload thread num
upload_thread_num=5

## mongodb config
db_host="localhost"
db_port=27017
db_user="tests"
db_passwd="tests" 
db_name="titan_test"

#  recent circle backup direactory on oss
last_circle_backup_dir_name="mongodb_cycle_backup_test_titan_20151221113136"
restore_local_temp_path="H:\\pythoncode\\temp\\restore\\"

# if mongo_shell not in PATH , need the mongo shell absolute path
mongo_shell_path=""

# backup file has download to local ? if True,will not download backup files from oss
has_download_to_local=False
# if True, drop the database,then restore
is_drop_old_restore=True


def restore_full_mongodb(db_host, db_port,db_user, db_passwd, db_name, db_restore_path,is_drop=False,mongo_shell_path=""):
	start_time = time.time()
	add_comm=""
	if is_drop:
		add_comm=" --drop "
	if db_user:
		add_comm=add_comm+" -u %s -p %s --authenticationDatabase admin " % (db_user,db_passwd)
	if db_name:
		add_comm=add_comm+" -d %s " % (db_name)
	cmd="%smongorestore -h %s --port %s  %s %s" %(mongo_shell_path,db_host, db_port, add_comm,db_restore_path)
	print(cmd)
	os.system(cmd)
	fun.print_cost_time("restore mongodb", start_time)

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
	
def unZipFile(unZipSrc,targeDir):
	if not os.path.isfile(unZipSrc):
		return
	if not os.path.isdir(targeDir):
		os.makedirs(targeDir)
	unZf = zipfile.ZipFile(unZipSrc,'r')
	for name in unZf.namelist() :
		unZfTarge = os.path.join(targeDir,name)
		if unZfTarge.endswith("/"):
			#empty dir
			splitDir = unZfTarge[:-1]
			if not os.path.exists(splitDir):
				os.makedirs(splitDir)
		else:
			splitDir,_ = os.path.split(unZfTarge)
			if not os.path.exists(splitDir):
				os.makedirs(splitDir)
			hFile = open(unZfTarge,'wb')
			hFile.write(unZf.read(name))
			hFile.close()
	unZf.close()

def tar_uncompres_files(unZipSrc,targeDir):
	if not os.path.isfile(unZipSrc):
		return
	if not os.path.isdir(targeDir):
		os.makedirs(targeDir)
	start_time = time.time()
	os.system("tar -C %s -zxvf %s "
		%(targeDir,unZipSrc))
	fun.print_cost_time("untar files", start_time)	
	
def unzip_backup_file(dir_path):
	for parent,dirnames,filenames in os.walk(dir_path):
		for filename in filenames:
			fname=os.path.splitext(filename)
			if fname[1] == '.zip':
				zip_path=os.path.join(parent,filename);
				#unzip_dir_path=os.path.join(parent,fname[0]);
				unZipFile(zip_path,parent)
			if fname[1] == '.gz':
				zip_path=os.path.join(parent,filename);
				#unzip_dir_path=os.path.join(parent,fname[0]);
				tar_uncompres_files(zip_path,parent)

def download_backup_to_local():
	oss=fun.get_oss_connect(endpoint, accessKeyId, accessKeySecret);
	file_list_on_oss=fun.list_bucket_files(oss,bucket,last_circle_backup_dir_name+"/")
	for each in file_list_on_oss:
		file_name=each[0];
		file_local_path=restore_local_temp_path+file_name;
		fun.make_direactory(os.path.dirname(file_local_path))
		fun.download_file_to_local(oss,bucket,file_local_path,file_name);
	
def restore_to_mongodb(restore_path):
	full_restore_path=restore_path+"/full_backup"
	restore_full_mongodb(db_host, db_port,db_user, db_passwd, db_name, full_restore_path+"/"+db_name,is_drop_old_restore,mongo_shell_path)
	inc_dir_restore_path=restore_path+"/inc_backup"
	for parent,dirnames,filenames in os.walk(inc_dir_restore_path):
		dirnames= sorted(dirnames)
		for dirname in dirnames:
			oplog_dir_path=os.path.join(parent,dirname);
			restore_oplog_mongodb(db_host, db_port,db_user, db_passwd, oplog_dir_path,mongo_shell_path)
	
if __name__ == "__main__":
	start_time = time.time()
	restore_path=restore_local_temp_path+"/"+last_circle_backup_dir_name
	if not has_download_to_local:
		print("download mongodb database from oss ...");
		download_backup_to_local()
		print("start unzip files ...");
		unzip_backup_file(restore_path)
	print("start restore files to db ...");
	restore_to_mongodb(restore_path)
			
	fun.print_cost_time("all done ", start_time)
