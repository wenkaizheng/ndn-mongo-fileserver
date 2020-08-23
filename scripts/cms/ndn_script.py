#!/usr/bin/python
# Copyright (c) 2019-2020, Regents of the University of Arizona.
# Author: Wenkai Zheng <zmkzmj@gmail.com>
# You should have received a copy of the GNU General Public License along with
# this script e.g., in COPYING.md file. If not, see <http://www.gnu.org/licenses/>.
from __future__ import print_function
import argparse
import pickle
import os.path
import io
import shutil
import subprocess
import dateutil.parser
import sys
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from MY_FILE import myFile
from MY_FILE import bcolors
# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']
#SCOPES = ['https://www.googleapis.com/auth/drive.file']
'''
Using the file id to run the download command from gdrive
everytime before run the gdrive command, we need to check the 
token is fresh, if it is not, we need to update it.
and it return the value from gdrive command.
'''
def download(id, creds):
    print(bcolors.HEADER + "download is starting right now" + bcolors.ENDC)
    id = id.encode("utf-8")
    directorys = directory.encode("utf-8")
    update_token(creds)
    g = directorys + 'gdrive --access-token ' + \
        creds.token + ' download --force ' + id
    #print(g)
    process = None
    output = None
    err = None
    if version == 'debug':
      # with open(env_path + 'file_record.txt', 'a') as log
        process = subprocess.Popen(g, shell=True,stderr = subprocess.PIPE,stdout =log)
        output,err = process.communicate()
        if err:
            write_rdebug_record(err)
    else:
       process = subprocess.Popen(g, shell=True,stderr = subprocess.PIPE,stdout = fp)
       output, err = process.communicate()
    rc = process.returncode
    if rc !=0:
       print(bcolors.WARNING + err + bcolors.ENDC)
    else:
       print(bcolors.OKBLUE +"download is completed" + bcolors.ENDC)
    return rc

'''
Write the status of file when it updates.
that is the info version.
'''

def write_record(file_instance):
    with open( 'file_record.txt', 'a') as f:
        f.write(str(file_instance))

'''
Write the output from video script to log file
that is the debug version.
'''
def write_rdebug_record(output):
    with open( 'file_record.txt', 'a') as f:
        f.write(output)

'''
Binary data serialization saver data-s
update the content of file_coll to this saver 
'''
def dump_data(file_coll):
    with open( 'data-s', 'wb') as token:
        pickle.dump(file_coll, token)

'''
Binary data serialization saver data-s
load the content of file_coll to dictionary
'''
def load_data():
    rc = None
    with open( 'data-s', 'rb') as token:
        rc = pickle.load(token)
    return rc

'''
Video script caller
call encoder, packager, chunker,and finally generate html file.
'''
def driver_script(file_name, file_instance, file_coll):

    #pwd = os.path.abspath(env_path + "../video/driver.sh")
    #pwd1 = os.path.dirname(os.path.realpath("packager.sh")) +'/packager.sh'
    #file_name_prefix = file_name[:file_name.rfind('.')]
    #base = '/ndn/web/video'
    if encode(file_name, file_instance, file_coll) == 1:
       return 
    if packaged(file_name, file_instance, file_coll) == 1:
       return 
    if chunker(file_name, file_instance, file_coll) == 1:
       return 
    if html1(file_name, file_instance, file_coll) == 1:
        return
    if html2(file_name, file_instance, file_coll) == 1:
        return


'''
Chunker script usage
chunk the video file to MongoDB
change the status to chunked if success.
'''
def chunker(file_name, file_instance, file_coll):
    print(bcolors.HEADER +"chunking is starting right now"+bcolors.ENDC)
    pwd = os.path.abspath(env_path + folder_name)
    file_name_prefix = file_name[:file_name.rfind('.')]
    base = '/ndn/web/video'
    version = '1'
    segmentSize = '8000'
    chunker = (directory + 'chunker ' + base + '/' + file_name_prefix + ' -i '
               + pwd + '/' + file_name_prefix + ' -s '
               + segmentSize + ' -e ' + version + ' && wait')
    if driver_script_helper(chunker,"chunk") == 0:
       # print('chunked alreay in here')
        file_instance.set_status('chunked')
        dump_data(file_coll)
        write_record(file_instance)
        print(bcolors.OKBLUE + "chunking is completed" + bcolors.ENDC)
        return 0
    else:
        file_instance.set_status("fail -- chuncked")
        dump_data(file_coll)
        write_record(file_instance)
        return 1

'''
Encoder script usage
encode the video file and generate 5 mp4 file
change the status to encoded if success.
'''
def encode(file_name, file_instance, file_coll):
    print(bcolors.HEADER +"encoding is starting right now"+bcolors.ENDC)
    encode = directory + env_path + '../../video/transcoder.sh ' + file_name + ' && wait'
    print(encode)
    if driver_script_helper(encode,"encode") == 0:
        file_instance.set_status('encoded')
        dump_data(file_coll)
        write_record(file_instance)
        print(bcolors.OKBLUE + "encoding is completed" + bcolors.ENDC)
        return 0
    else:
        file_instance.set_status("fail -- encoded")
        dump_data(file_coll)
        write_record(file_instance)
        return 1
'''
Packager script usage
package the encoded video file with hls protocol and create a folder to collect
change the status to packaged if success.
'''
def packaged(file_name, file_instance, file_coll):
    print(bcolors.HEADER +"packaging is starting right now"+bcolors.ENDC)
    pwd = './'
    pwd1 = directory + env_path + "../../video/packager.sh"
    file_name_prefix = file_name[:file_name.rfind('.')]
    protocol = 'hls'
    playlist = 'playlist.m3u8'
    package = (pwd1+' ' + '.'+' ' + file_name_prefix + ' '
               + pwd + file_name_prefix + '/' + protocol + ' '
               + protocol + ' && wait')
    if driver_script_helper(package,"package") == 0:
        file_instance.set_status('packaged')
        dump_data(file_coll)
        write_record(file_instance)
        print(bcolors.OKBLUE + "packaging is completed" + bcolors.ENDC)
        return 0
    else:
        file_instance.set_status("fail -- packaged")
        dump_data(file_coll)
        write_record(file_instance)
        return 1

'''
Html1 script usage
generate the ndn webage by using curl command in two step
each step holds different status
change the status to web1, web2 if success.
'''
def html1(file_name, file_instance, file_coll):
    print(bcolors.HEADER +"html1 is starting right now"+bcolors.ENDC)
    global manifestUrl
    file_name_prefix = file_name[:file_name.rfind('.')]
    manifestUrl = base + '/' + file_name_prefix + '/' + protocol + '/' + playlist
    curl_one = (directory + 'curl ' + inputs + ' | ' + 'sed -n ' + "'0, /begin url section/p'"
                + ' > ' + file_name_prefix + '.html ' + '&& ' + 'printf '
                + line + ' >> ' + file_name_prefix + '.html')
    if driver_script_helper(curl_one,"html1") == 0:
        file_instance.set_status('web1')
        dump_data(file_coll)
        write_record(file_instance)
        print(bcolors.OKBLUE + "html1 is completed" + bcolors.ENDC)
        return 0
    else:
        file_instance.set_status("fail -- html1")
        dump_data(file_coll)
        write_record(file_instance)
        return 1
'''
Html2 script usage
generate the ndn webage by using curl command in two step
each step holds different status
change the status to web1, web2 if success.
'''
def html2(file_name, file_instance, file_coll):
    print(bcolors.HEADER +"html2 is starting right now"+bcolors.ENDC)
    global manifestUrl
    file_name_prefix = file_name[:file_name.rfind('.')]
    manifestUrl = base + '/' + file_name_prefix + '/' + protocol + '/' + playlist
    curl_two = (directory + 'curl ' + inputs + ' | ' + 'sed -n ' + "'/end url section/, $p'"
               + ' >> ' + file_name_prefix + '.html')
    if driver_script_helper(curl_two,"html2") == 0:
        file_instance.set_status('web2')
        dump_data(file_coll)
        write_record(file_instance)
        print(bcolors.OKBLUE + "html2 is completed" + bcolors.ENDC)
        return 0
    else:
        file_instance.set_status("fail -- html2")
        dump_data(file_coll)
        write_record(file_instance)
        return 1

'''
Driver script helper
using the process to run the command and return the value from that command.
'''
def driver_script_helper(command,stage):
   # fp = open(os.devnull, 'w') as fp:
    process = None
    output = None
    err = None
    if version == 'debug':
      # with open(env_path + 'file_record.txt', 'a') as log
        process = subprocess.Popen(command, shell=True,stderr = subprocess.PIPE,stdout =log)
        output,err = process.communicate()
        if err:
            write_rdebug_record(err)
    else:
       process = subprocess.Popen(command, shell=True,stderr = subprocess.PIPE,stdout = fp)
       output, err = process.communicate()
    rc = process.returncode
    print('--------------------'+str(rc))
    if rc !=0:
        print(bcolors.WARNING + "This error occurs when current stage is "+stage + bcolors.ENDC)
        print(bcolors.WARNING+ err + bcolors.ENDC)
    return rc

'''
Check the credential if it is fresh
if it is not, refresh it.
all gdrive command need this token from creds to run.
'''
def update_token(creds):
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

'''
Check if all 5 encoded file are generated already
'''
def check_all_encode(prefix):
    count = 5
    real_count = check_encoded_number(prefix)
    if real_count != count:
        return False
    else:
        return True

'''
Return the number of encoded file.
'''
def check_encoded_number(prefix):
    encoded_arr = [folder_name + '/' + prefix+'_h264_1080p.mp4', folder_name + '/' + prefix+'_h264_240p.mp4', folder_name +
                   '/'+prefix+'_h264_360p.mp4', folder_name + '/' + prefix+'_h264_480p.mp4', folder_name + '/' + prefix+'_h264_720p.mp4']
    num = 0
    for i in encoded_arr:
        if os.path.exists(i):
            num += 1
    return num
'''
Check if the log file is up to date
'''
def check_log(file_coll):
    with open('file_record.txt') as f:
        content = f.readlines()
    last_place = content[-1]
    last_status = last_place.split()[5]
    last_id = last_place.split()[1]
    last_name = last_place.split()[2]
    last_type = last_place.split()[0]
    last_time = last_place.split()[3] + ' ' + last_place.split()[4]
    last_parent = last_place.split()[6]
    find = False
    for parent in file_coll:
        for file in file_coll[parent]:
            if file.get_id() == last_id:
                find = True
                if file.get_status() != last_status:
                    write_record(file)
                    return 
    if not find:
        if last_status != 'deleted':
            added =  file_instance = myFile(
                last_name, last_id, last_type, last_time, 'deleted', last_parent)
            write_record(added)
    

    
'''
Check the file status from file_coll, because this script should resume the
work from previous step. 
1. if the status of the file is initial, just go through step from download the file,
encode, package, chunk, and eventually generate html file.
2. if the status of the file is download, to check if the encode process is in the middle,
if it is in the middle, delete all encoded mp4 file and go through encode, package, 
chunk, and eventually generate html file. if the video filen is not in the disk, download it 
again and then go through encode, package, chunk, and eventually generate html file.
3. if the status of the file is encoded, check if the all 5 encoded mp4 5 is the disk, if no,
delete the whatever is left, and reencode that video file, and then go through package, chunk, 
and eventually generate html file. if yes, check if it is in the middle of package porcess,
if yes, we need to delete the package folder, if no we don't do anything, for this two situation
we also go through package, chunk, and eventually generate html file.
4. if the status of the file is chunked, todo we need to check the MongoDB. If we html is alreay exists,
we need to delete it and generate the html file again.
5. if the status of the file is either the web1 or web2, check if the 
html file exists, if not, we generate it. if yes, if the status is web1, we generate 
the html in step2 for changing the status to web2, if the status is html and js
second which means all process is done.
'''
def check_status(file_coll, creds, items):
    global directory
    global folder_name
    for key in file_coll:
        for file_instance in file_coll[key]:
            rc = search_items(file_instance.get_parent(), items)
            if rc != folder_name:
                continue
            directory = 'cd '+folder_name+' && '
            status = file_instance.get_status()
            name = file_instance.get_name()
            file_id = file_instance.get_id()
            web = name[:name.rfind('.')]+'.html'
            prefix = name[:name.rfind('.')]
            if status.startswith("fail") and recover == "yes":
               delete(name)
               delete_encoder(name)
               delete_packager(name)
               delete_packager(name)
               status ='initial'
               file_instance.set_status(status)
               dump_data(file_coll)
               write_record(file_instance)
            if status == 'initial':
                rv = download(file_id, creds)
                if rv == 0:
                   file_instance.set_status("download")
                   dump_data(file_coll)
                   write_record(file_instance)
                   driver_script(name, file_instance, file_coll)

            elif status == 'download':
                # todo check if the file exist and process
                rv = 0
                if os.path.exists(folder_name+'/'+name):
                    print("the file is exist in the disk")
                    pass
                else:
                    rv = download(file_id, creds)
                if check_encoded_number(prefix) > 0:
                    delete_encoder(name)
                if rv == 0:
                    driver_script(name, file_instance, file_coll)
            elif status == 'encoded':
                if check_all_encode(prefix):
                    pass
                else:
                    delete_encoder(name)
                    driver_script(name, file_instance, file_coll)
                    continue
                # in the middle of package
                if os.path.exists(folder_name + '/' + prefix):
                    delete_packager(name)
                packaged(name, file_instance, file_coll)
                chunker(name, file_instance, file_coll)
                html1(name, file_instance, file_coll)
                html2(name, file_instance, file_coll)

            elif status == 'packaged':
                if os.path.exists(folder_name + '/' + prefix):
                    pass
                else:
                    packaged(name, file_instance, file_coll)
                # todo wait for MongoDB stuff
                # in the middle of chunck
                chunker(name, file_instance, file_coll)
                html1(name, file_instance, file_coll)
                html2(name, file_instance, file_coll)

            elif status == 'chunked':
                # todo we need to check MongoDB before generate html
                # in the middle of html
                if os.path.exists(folder_name + '/' + web):
                    delete_html(name)
                html1(name, file_instance, file_coll)
                html2(name, file_instance, file_coll)
            # only one left is html but we need to have two
            elif status == 'web1' or status == 'web2':
                if not os.path.exists(folder_name + '/' + web):
                   html1(name, file_instance, file_coll)
                   html2(name, file_instance, file_coll)
                else:
                    if file_instance.get_status() == 'web1':
                       html2(name, file_instance, file_coll)

'''
Delete the video file
'''
def delete(file_name):
    # delete it self
    file_name = folder_name + '/' + file_name
    print(file_name)
    if os.path.exists(file_name):
        os.remove(file_name)

'''
Delete the packager folder
'''
def delete_packager(file_name):
    prefix = file_name[:file_name.rfind('.')]
    prefix = folder_name + '/' + prefix
    print(prefix)
    if os.path.exists(prefix):
        shutil.rmtree(prefix)

'''
Delete the encoded mp4 files
'''
def delete_encoder(file_name):
    # delete the encoder
    prefix = file_name[:file_name.rfind('.')]
    encoded_arr = encoded_arr = [folder_name + '/' + prefix+'_h264_1080p.mp4', folder_name + '/' + prefix+'_h264_240p.mp4',
                                 folder_name + '/'+prefix+'_h264_360p.mp4', folder_name + '/' + prefix+'_h264_480p.mp4', folder_name + '/' + prefix+'_h264_720p.mp4']
    count = 5
    for i in range(0, count):
        print(encoded_arr[i])
        if os.path.exists(encoded_arr[i]):
            os.remove(encoded_arr[i])

'''
Delete the ndn-webpage file
'''
def delete_html(file_name):
    prefix = file_name[:file_name.rfind('.')]
    prefix = folder_name + '/' + prefix
    html_file = prefix+'.html'
    print(html_file)
    if os.path.exists(html_file):
        os.remove(html_file)
'''
Clear the current working directory
'''
def clear_pwd(path):
    file_list = os.listdir(path)
    for i in file_list:
        if os.path.isdir(i):
            shutil.rmtree(i)
        elif os.path.isfile(i):
             if i =='file_record.txt' or i == 'data-s':
                 os.remove(i)

'''
Change the name of all prcess
which include video file, encoded file, package folder, and html file
todo we need to include the MongoDB part for changing the name.
'''
def change_name(old, new):
    old_prefix = old[:old.rfind('.')]
    new_prefix = new[:new.rfind('.')]
    old_encoded_arr = [folder_name + '/' + old_prefix+'_h264_1080p.mp4', folder_name+'/' + old_prefix+'_h264_240p.mp4', folder_name +
                       '/'+old_prefix+'_h264_360p.mp4', folder_name+'/'+old_prefix+'_h264_480p.mp4', folder_name+'/'+old_prefix+'_h264_720p.mp4']
    new_encoded_arr = [folder_name + '/'+new_prefix+'_h264_1080p.mp4', folder_name+'/'+new_prefix+'_h264_240p.mp4', folder_name +
                       '/'+new_prefix+'_h264_360p.mp4', folder_name+'/'+new_prefix+'_h264_480p.mp4', folder_name+'/'+new_prefix+'_h264_720p.mp4']
    # name of file replacement
    os.rename(folder_name + '/' + old, folder_name + '/' + new)
    # encoder replacement
    for i in range(0, 5):
        os.rename(old_encoded_arr[i], new_encoded_arr[i])
    # package replacement
    os.rename(folder_name + '/' + old_prefix, folder_name + '/' + new_prefix)
    # html replacement
    os.rename(folder_name + '/' + old_prefix + '.html',
              folder_name + '/' + new_prefix+'.html')

'''
Search the name from specific id in items
this items is created by the gdrive command 
which includes all file info.
'''
def search_items(id, items):
    #print(items)
    for item in items:
        item = item.split('\n')[:-1]
        file_id = item[0][item[0].find(':')+2:]
        name = item[1][item[1].find(':')+2:]
        if id == file_id:
            return name
    return None

'''
After a file is insert we dump the data-s and save status in the log file.
Start download it, encode, package, chunk, and generate html file.
'''
def new_file(file_coll,file_instance,file_id,creds,name):
    dump_data(file_coll)
    write_record(file_instance)
    rv = download(file_id, creds)
    if rv == 0:
       file_instance.set_status("download")
       dump_data(file_coll)
       write_record(file_instance)
       driver_script(name, file_instance, file_coll)

'''
Construct a list with all info from google drive, and it should be call when process func is called
'''
def process_helper(creds):
    update_token(creds) 
    query = '\"'+ 'name = ' + '\'' +  folder_name   + '\''   + '\"' 
    g = 'gdrive --access-token ' + creds.token + ' list -q ' + query
    #print(g)
    process = subprocess.Popen(g, shell=True, stdout=subprocess.PIPE)
    output, err = process.communicate()
    output_list = output.split('\n')[1:-1]
    items = []
    file_info = None
    for file_info in output_list:
        if file_info.split()[2] == "dir":
           break
    if file_info == None:
        return []
    file_id = file_info.split()[0]
    update_token(creds)
    query = '\"'+ 'parents = ' + '\''+file_id + '\'' + ' and trashed = false' +'\"'
    g = 'gdrive --access-token ' + creds.token + ' list -q ' + query
    #print(g)
    process = subprocess.Popen(g, shell=True, stdout=subprocess.PIPE)
    output, err = process.communicate()
    output_list = output.split('\n')[1:-1]
    #print(output_list)
    for data in output_list:
        id = data.split()[0]
        update_token(creds)
        g = 'gdrive --access-token '+creds.token + ' info ' + id
        process = subprocess.Popen(g, shell=True, stdout=subprocess.PIPE)
        output, err = process.communicate()
        if output.startswith("Id:"):
           items.append(output)
    
    update_token(creds)
    g = 'gdrive --access-token '+creds.token + ' info ' + file_id
    process = subprocess.Popen(g, shell=True, stdout=subprocess.PIPE)
    output, err = process.communicate()
    items.append(output)
    return items

'''
Using the gdrive command to list all file info
and get the id from each file to access the more specifc info from each file
construct the myFile object by using those info which includes 
name, id, type, time and parent. and the status is initial at first.
the file_coll is a dictionary which use parent id as key and list of myFile object as value
if the type is folder and it does not exist, we create it. if the type is video file,
check if the parent id is already in file_coll, if yes we need to check if this file is
already in the list, if yes we need to compare the last modified date, if the 
last modified date changed, we need to change the name of all corresponding files and folders 
in the disk. if no, we add it by using this parent id. 
if the parent id is not in file_coll, we create it and add current file into it.
'''
def process(creds):
    # gdrive stuff to get meta data from each file
    global folder_name
    global directory
    items = process_helper(creds)
    while not items:
        print("This folder is not exist in google drive, please try another one")
        folder_name = raw_input()
        items = process_helper(creds)
    file_coll = None
    if os.path.exists('data-s'):
        with open('data-s', 'rb') as token:
            file_coll = pickle.load(token)
            #print(file_coll)
        check_log(file_coll)
        check_status(file_coll, creds, items)
        # print(file_coll)
    else:
        file_coll = {}
    # checking if we delete anything
    compare_coll = []
    if not items:
        print('No files found.')
    else:
        print('Files:')
       # print(items)
        for item in items:
            item = item.split('\n')[:-1]
            file_id = item[0][item[0].find(':')+2:]
            name = item[1][item[1].find(':')+2:]
            mime_type = item[3][item[3].find(':')+2:]
           # print(name,time,parent,file_id,mime_type,file_id)
            print("The file name is " + name)
            if mime_type == 'application/vnd.google-apps.folder':
               continue
            if mime_type.rfind('video') == -1:
                continue
            time = item[6][item[6].find(':')+2:]
            parent = item[9][item[9].find(':')+2:]
           # print('80th   ' + parent)
            file_instance = myFile(
                name, file_id, mime_type, dateutil.parser.parse(time), 'initial', parent)
            compare_coll.append(file_instance)
            # this file belongs to that folder.
            if parent in file_coll:
                record = file_coll[parent]
                rfind = False
                for re in record:
                    if re == file_instance:
                        rfind = True
                        # user modifies the name of file
                        if file_instance.get_time() > re.get_time():
                            print("533th")
                            old_name = re.get_name()
                            re.set_time(file_instance.get_time())
                            re.set_name(file_instance.get_name())
                            re.set_status('change name from ' + old_name)
                            dump_data(file_coll)
                            write_record(re)
                           # folder_name = search_items(parent, items)
                            print(folder_name)
                            directory = 'cd '+folder_name+' && '
                            change_name(old_name, file_instance.get_name())
                if not rfind:
                    # new file insert into this folder
                    #folder_name = folder_name
                    print("549th")
                    directory = 'cd '+folder_name+' && '
                    file_coll[parent].append(file_instance)
                    new_file(file_coll,file_instance,file_id,creds,name)
            # create the new folder and insert the file into it
            else:
                print("555th")
                file_coll[parent] = []
                file_coll[parent].append(file_instance)
                if not os.path.exists(folder_name):
                    os.mkdir(folder_name)
                directory = 'cd '+folder_name+' && '
                new_file(file_coll,file_instance,file_id,creds,name)

    for key in file_coll:
        for fi in file_coll[key][:]:
            if fi in compare_coll:
                continue
                # copy[key].append(fi)
            else:
                delete_name = fi.get_name()
                #folder_name = search_items(fi.get_parent(),items)
                directory = 'cd '+folder_name+' && '
                delete(delete_name)
                delete_encoder(delete_name)
                delete_packager(delete_name)
                delete_html(delete_name)
                fi.set_status('deleted')
                write_record(fi)
                file_coll[key].remove(fi)
                dump_data(file_coll)

    # write_record(file_coll)

'''
Check if the token file is exist, if not, it will open broswer for user to choose 
account and do the authorization. if yes it will get the credential for checking 
if the token is fresh, if no, we need to refresh it. This process is only executed 
in the first turn loop. After we get credential, we can use it to get fresh token,
so we don't need to dump the token everytime. 
'''
def start():
    creds = None
    count = 0
    print(env)
    while True:
        if count == 0:
            """
            Netwrok stuff to get token with google drive server
            """
            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    creds = pickle.load(token)
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                         'credapi.json', SCOPES)
                    creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        process(creds)
        count += 1


env_path = ''
env = os.path.abspath('./')
env = env.split('/')[-1]
if env == 'normal':
    env_path = '../'
parser = argparse.ArgumentParser(prog='ndn_script.py')
parser.add_argument('-v', choices=['info', 'debug'], metavar='info or debug',
                    nargs=1, help='please choose a right version')
parser.add_argument('-n', metavar='name of folder', nargs=1,
                        help='please give a name of folder')
parser.add_argument('-d', metavar='yes or no', nargs=1,
                        help='please choose clear directory or not')
parser.add_argument('-r', metavar='yes or no', nargs=1,
                        help='if there is error occurs in the middle, please choose retry or not')
result = parser.parse_args(sys.argv[1:])
if result.v == None:
    parser.print_help(sys.stderr)
    sys.exit(1)
if result.n == None:
    parser.print_help(sys.stderr)
    sys.exit(1)
if result.d == None:
    parser.print_help(sys.stderr)
    sys.exit(1)
if result.r == None:
    parser.print_help(sys.stderr)
    sys.exit(1)
version = result.v[0]
folder_name = result.n[0]
clear = result.d[0]
recover = result.r[0]
if clear == 'yes':
    clear_pwd('./')
#print(version,folder_name)
directory = ''
fp = open(os.devnull, 'w')
log = open('file_record.txt', 'a')
base = '/ndn/web/video'
protocol = 'hls'
playlist = 'playlist.m3u8'
inputs = ('https://gist.githubusercontent.com/chavoosh/f7db8dc41c3e8bb8e6a058b1ea342b5a/raw'
              + '/cb9ea05b57f769f845398721f68c3f6f4b3b88ac/base.html')
manifestUrl = ''
line = ('      <!-- manifest uri -->\n')
line += '      ' + "'<span id= 'manifestUri' hidden>'"+manifestUrl + "'</span>\n\n'"
line = '"' + line + '"'
start()
