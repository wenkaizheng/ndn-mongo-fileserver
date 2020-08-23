Description:
This script goes through all video files in a specific google drive folder and connects with
ndn-mongo-fileserver, if there is any change from google drive folder e.g. update, delete, insert, this script will handle it.

Some prerequisites for this script: 
1.Install gdrive from this link:
  https://github.com/prasmussen/gdrive
  Choose a proper way to install gdrive from the link.
2.Install google authenticate module and enable google drive api from this link:
  https://developers.google.com/drive/api/v3/quickstart/python
  After you are done with step 1 in the link, you will get a json file, and please name it "credapi.json", and also make sure it is in the cms folder.
  Note: Step 2 in the link includes commands for all python modules you need to install, please follow those commands.
  Step 3 in the link will be Run the sample code, please you can run this sample code before you run this script.
3.Install dateutil module: pip install python-dateutil.

How to run this script:
This script needs two options when you want to run it.
-v means version (you should choose from either info or debug)
-n means the name of folder (the name of folder in google drive)
For example if you want to run it in info mode with folder ndn you should apply python ndn_script.py -v info -n ndn
-d means delete all uncessary files from current working directory (you should choose from yes or no)
-r means recover if any middle step fail from previous turn (you should choose from yes or no) 
You can also use python ndn_script.py -h or python ndn_script.py --help to check usage.

Some features of this script:
1.Reflects user operations from google drive:
Insert: 
When a user inserts a new file into his folder, this script will create a user folder and download this file in the disk. And then runs the scripts in
the video folder for encoding, packing, and chunking this file, and eventually generates a html file.
Delete: 
When a user deletes a file in his folder, this script will delete all corresponding file such as encoded file, package folder, and html file in the disk.
Update: 
When a user modifies the name of file, this script will rename all corresponding file such as encoded file, package folder, and html file in the disk.
2.Generates some file during the runtime:
Log file "file_record.txt": 
This script provide two different modes which are info mode and debug mode. Either one will generate file_record.txt as a log file to
check the status of each file e.g. initial,download, encoded, packaged, chunked, html and js first, html and js second, deleted, change the name. The only difference between them is that debug version contain outpt from video scirpts. But the info version only contains the meta data from file e.g. name, id, status, parent_id, last modify date and type. Those status will allow developers to check the working process, and when the script crashes in any time with any reason, developer can check what is the previous process. 
Binary file data-s: 
This binary file data-s is used for recording status of file as well, but it can load and dump with any data structure. More specificlly, 
data-s is about data serialization which allows the script itself to check the status of each file very quick, once the script knows the status of file, it can resume to work from previous process even the script crashes in the middle. So if data-s exits in current working directory, this script will chcek the data-s to see if there is any work need to resume before go through google drive.

Ongoing task:
Testing this script.
1.Insert a file to a folder.   -- Done
2.Rename a file to a folder.   -- Done
3.Delte a file to a folder.    -- Done
4.Manually test about crash this script in middle (downlaod, encode, package, chunk, generate html).  -- Done
5.Provide a different log file for testing this script crash in the middle (downlaod, encode, package, chunk, generate html).  -- Pending

Next step: For checking the chunk process with MongoDB is not done yet, I thought we talked 
some magic functions about delete and rename files in MongoDB before, but those magic functions are not implemented yet.