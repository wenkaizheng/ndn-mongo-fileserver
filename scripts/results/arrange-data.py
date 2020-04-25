#!/usr/bin/python
#.....................................................................
# Copyright (c) 2016-2019, Regents of the University of Arizona.
# Author:Wenkai Zheng<wenkaizheng@email.arizona.edu>
#
# You should have received a copy of the GNU General Public License along with
# this script e.g., in COPYING.md file. If not, see <http://www.gnu.org/licenses/>.
#
# DESCRIPTION:
# ------------
# This script accepts a log file including stats Interest from ivisa service and
# prints a statistical plot within a given time range.
#
# Interactive mode:
#   - Two inputs: The start time and end time, and any session's start time is
#     between these two inputs should be displayed as plot.
#   - One input: The start time, and any session's start time after this input
#     should be displayed as plot.
#   - No input: All session should be displayed as plot.
#.....................................................................
import os
import sys
import subprocess

import argparse
import datetime
import readline


def trunc_datetime2(line):
     global auto_complection
     global Months
     year = line.split(' ')[0].split('/')[2]
     months_small = line.split(' ')[0].split('/')[0]
     months_index = months_small[0].upper()+months_small[1]+months_small[2]
     month = Months[months_index]
     day = line.split(' ')[0].split('/')[1]
     hour = line.split(' ')[1].split(':')[0]
     minute = line.split(' ')[1].split(':')[1]
     second = line.split(' ')[1].split(':')[2]
     return datetime.datetime(
        int(year),
        int(month),
        int(day),
        int(hour),
        int(minute),
        int(second))

    
def trunc_datetime(line,save):
    global Months
    global auto_complete
    data = line.split()
    year = data[4]
    month = Months[data[1]]
    day = data[2]
    hour = data[3].split(':')[0]
    minute = data[3].split(':')[1]
    second = data[3].split(':')[2]
    # Nov/4/2019 18:55:59
    if save:
        temp = ''
        for i in range (0,len(data[1])):
            temp = temp + data[1][i].lower() if i == 0 else temp + data[1][i]
        date = temp + '/' + day + '/' + year + ' ' + hour + ':' + minute + ':' +second
        auto_complete.append(date)
    return datetime.datetime(
        int(year),
        int(month),
        int(day),
        int(hour),
        int(minute),
        int(second))

def sort_func(line):
    return trunc_datetime(line, False)

def sort_func2(arr):
    return trunc_datetime(arr[0], True)

def process():
    global id_map
    global content
    global session_num
    global rc
    for line in content:
        lines = line.split('session%3D')[1]
        session_id = lines.split('/')[0]
        if session_id not in id_map:
            id_map[session_id] = []
            id_map[session_id].append(line)
        else:
            id_map[session_id].append(line)
            
    session_num = len(id_map)
    for key in id_map:
        id_map[key] = sorted(id_map[key], key=sort_func)
        rc.append(id_map[key])
    rc = sorted(rc, key=sort_func2)
    
def check_two_date(date1, date2):
   global rc
   global writer
   result = []
   index = -1
   for arr in rc:
       index += 1
       first = arr[0].strip()
       #print first
       first_time = trunc_datetime(first,False)
       if date1 <= first_time and first_time <= date2:
            writer.append(index)
       if first_time > date2:
            break

def write_file():
    global writer
    global rc
    if len(writer) == 0:
        print("no such a session exist")
        exit(1)
    f = open('qualified_data.txt', 'w+')
    for index in writer:
        for line in rc[index]:
            f.write(line + '\n')

def convert_date(line):
    global Months
    line = line.strip().split()
    year = line[0].split('/')[2]
    months_small = line[0].split('/')[0]
    months_index = months_small[0].upper()+ months_small[1] + months_small[2]
    month = Months[months_index]
    day = line[0].split('/')[1]
    hour = line[1].split(':')[0]
    minute = line[1].split(':')[1]
    second = line[1].split(':')[2]
    return datetime.datetime(
        int(year),
        int(month),
        int(day),
        int(hour),
        int(minute),
        int(second))
def check_file(name):
    if not os.path.isfile(name):
          raise argparse.ArgumentTypeError("%s does not exist" % name)
    return name

def completer(text,state):
    global auto_complete
    global options
   # options = [cmd for cmd in auto_complete if cmd.startswith(text)]
    if state == 0:
       options = [cmd for cmd in auto_complete if cmd.startswith(text.lower())]
    if state < len(options):
        return options[state]
    else:
        return None
def network_completer(text,state):
    global network_options
    global network 
   # options = [cmd for cmd in auto_complete if cmd.startswith(text)]
    if state == 0:
       network = [cmd for cmd in network_options if cmd.startswith(text.lower())]
    if state < len(network):
        return network[state]
    else:
        return None
     
def find_first_match(user_input):
      global auto_complete
      for date in auto_complete:
          if date.startswith(user_input):
             return date
      return None
def case(date):
     if len(date) == 4:
          if date.lower() == 'exit':
               return 'exit'
          return date.lower()
     else:
          return date.lower()

writer = []
rc = []
content = []
id_map = {}
auto_complete = []
session_num = 0
options = []
Months = {
    'Jan': 1,
    'Feb': 2,
    'Mar': 3,
    'Apr': 4,
    'May': 5,
    'Jun': 6,
    'Jul': 7,
    'Aug': 8,
    'Sep': 9,
    'Oct': 10,
    'Nov': 11,
    'Dec': 12}
network_options = ['jitter', 'rebuffers', 'rtt','retx','timeout','nack','segments']
network = []

parser = argparse.ArgumentParser(prog='arrange-data.py')
parser.add_argument('-p', choices=['jitter', 'rebuffers', 'rtt','retx','timeout','nack','segments'], metavar='Valid Options',
                        nargs=1,help='Your choice of options is jitter, rebuffers, or rtt',required =False)
parser.add_argument('i', metavar='Input File', nargs=1, type = check_file,
                        help='You need to have a input file for drawing plots')
result = parser.parse_args(sys.argv[1:])
   
d = vars(result)
file_name = d['i'][0]
with open(file_name) as f:
    content = f.readlines()
    content = [x.strip() for x in content]
    process()
    print 'Number of video sessions: ' + str(session_num)
    start_times = rc[0][0].split()[1] + '/' \
        + rc[0][0].split()[2] + '/' + rc[0][0].split()[4] + ' ' \
        + rc[0][0].split()[3]
    print 'Earliest time is ' + rc[0][0].split()[1] + '/' \
        + rc[0][0].split()[2] + '/' + rc[0][0].split()[4] + ' ' \
        + rc[0][0].split()[3]
    end_times = rc[-1][0].split()[1] + '/' \
        + rc[-1][0].split()[2] + '/' + rc[-1][0].split()[4] + ' ' \
        + rc[-1][0].split()[3]
    print 'Lastest time is ' + rc[-1][0].split()[1] + '/' \
        + rc[-1][0].split()[2] + '/' + rc[-1][0].split()[4] + ' ' \
        + rc[-1][0].split()[3]
    readline.set_completer_delims('\t\n')
    readline.parse_and_bind("set show-all-if-unmodified on")
    readline.parse_and_bind("set completion-query-items 10000")
    readline.parse_and_bind("tab: complete")
    auto_complete = sorted(auto_complete, key=trunc_datetime2)
    from_argu = True

while (True):
    try:
        start_time = ''
        end_time = ''
        if result.p ==None:
           print 'You can choose one of the network charaistics from jitter, rebuffers, rtt, retx, timeout, nack, segments'
           readline.set_completer(network_completer)
           type_plot = raw_input()
           from_argu = False
        readline.set_completer(completer)
        print 'Please type a date range'
        print 'Start date/time:'
        start = raw_input()
        start = case(start)
        if start == 'exit':
            break;
        if len(start) != 0:
            start_time = start
        else:
             start_time = start_times
        print 'End date/time:'
        end = raw_input()
        end = case(end)
        if end == 'exit':
            break;
        if len(end)!= 0:
            end_time = end
        else:
             end_time = end_times
        if from_argu:
           type_plot = d['p'][0]
        command = ''
        if type_plot == 'jitter' or type_plot == 'rtt':
            command = 'python session-avg-' + type_plot + '.py'
        else:
            command = 'python session-' + type_plot + '.py'
        judge = False
        #judge format in here
        if start_time.count('/')!=2 or start_time.count(':')!=2:
             rv = find_first_match(start_time)
             if rv == None:
                print "Warning there is no matching options"
                continue
             start_time = rv
        
        if end_time.count('/')!=2 or end_time.count(':')!=2:
              rv = find_first_match(end_time)
              if rv == None:
                print "Warning there is no matching options"
                continue;
              end_time = rv
        print 'Start time is '+start_time + ' End time is '+ end_time
        if len(start) == 0 and len(end) == 0:
            print 'print all plot'
            judge = True
            command = command + ' ' + file_name
        # we need to have 2 situtation which means either start or and end is blank
        elif len(start) == 0 or len(end) == 0:
            print 'one date specific'
            #check_one_date(convert_date(date_range))
            check_two_date(convert_date(start_time),
                       convert_date(end_time))
            write_file()
            command = command + ' qualified_data.txt'
        else:
            print 'two date specific'
            check_two_date(convert_date(start_time),
                       convert_date(end_time))
            write_file()
            command = command + ' qualified_data.txt'
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        output, err = process.communicate()
        print output
        if judge == False:
            os.remove('qualified_data.txt')
    except ValueError:
         print 'Your input date is invalid; hour should between 0-23, minute and '+\
        'second should between 0-59, day should be 1-30 or 31 '
         continue
    except IndexError:
        print 'Your input is missing some part and correct date should' + \
       'be month/day/year hour:minute:second'
        continue
    except KeyError:
        print 'Use valid months please such as Nov,Dec'
        continue
