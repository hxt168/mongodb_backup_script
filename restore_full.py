#!/usr/bin/env
import fun
import time
import os
from oss.oss_util import *
import zipfile

### config

## oss 
endpoint="oss.aliyuncs.com"
accessKeyId="xxx"
accessKeySecret="xxx"
bucket="db-backup"
# oss multi upload thread num
upload_thread_num=5

## mongodb config
db_host="127.0.0.1"
db_port=27017
db_user="test"
db_passwd="test" 
db_name="titan_test"

#  
#last_full_backup_file_name_on_oss="mongodb_backup_titan_201512221438.tar.gz"

# recent circle full backup direactory , the oss file name is  last_circle_backup_dir_name+last_full_backup_file_suffix
last_circle_backup_dir_name="mongodb_backup_titan_201512221438"

last_full_backup_file_suffix=".tar.gz"

restore_local_temp_path="/alidata1/dev/hanxuetong/temp_restore/"

# if mongo_shell not in PATH , need the mongo shell absolute path
mongo_shell_path="/alidata1/dev/hanxuetong/mongodb/mongodb-linux-x86_64-3.0.6/bin/"

# backup file has download to local ? if True,will not download backup files from oss
has_download_to_local=True
# if True, drop the database,then restore
is_drop_old_restore=True

def restore_full_mongodb(db_host, db_port,db_user, db_passwd, db_name, db_restore_path,is_drop=False):
	start_time = time.time()
	add_comm=""
	if is_drop:
		add_comm=" --drop "
	if db_user:
		add_comm=add_comm+" -u %s -p %s " % (db_user,db_passwd)
	if db_name:
		add_comm=add_comm+" -d %s " % (db_name)
	cmd="%smongorestore -h %s --port %s  %s %s" %(mongo_shell_path,db_host, db_port, add_comm,db_restore_path)
	print(cmd)
	os.system(cmd)
	fun.print_cost_time("restore mongodb", start_time)


	
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
				tar_uncompres_files(zip_path,parent)

def tar_uncompres_files(unZipSrc,targeDir):
	if not os.path.isfile(unZipSrc):
		return
	if not os.path.isdir(targeDir):
		os.makedirs(targeDir)
	start_time = time.time()
	os.system("tar -C %s -zxvf %s "
		%(targeDir,unZipSrc))
	fun.print_cost_time("untar files", start_time)	
				
def download_backup_to_local():
	oss=fun.get_oss_connect(endpoint, accessKeyId, accessKeySecret);
	last_full_backup_file_name_on_oss=last_circle_backup_dir_name+last_full_backup_file_suffix
	file_local_path=restore_local_temp_path+last_full_backup_file_name_on_oss;
	fun.make_direactory(os.path.dirname(file_local_path))
	fun.download_file_to_local(oss,bucket,file_local_path,last_full_backup_file_name_on_oss);
	
def restore_to_mongodb(full_restore_path):
	#full_restore_path=restore_path+"/full_backup"
	restore_full_mongodb(db_host, db_port,db_user, db_passwd, db_name, full_restore_path+"/"+db_name,is_drop_old_restore)

	
if __name__ == "__main__":
	start_time = time.time()
	restore_path=restore_local_temp_path
	if not has_download_to_local:
		print("download mongodb database from oss ...");
		download_backup_to_local()
		print("start unzip files ...");
		unzip_backup_file(restore_path)
	print("start restore files to db ...");
	restore_to_mongodb(restore_path+last_circle_backup_dir_name)
			
	fun.print_cost_time("all done ", start_time)
