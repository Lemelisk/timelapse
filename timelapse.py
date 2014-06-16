#!/usr/bin/python3

import argparse;
from datetime import datetime, timedelta;
import os
import sys
import shutil
import glob

parser = argparse.ArgumentParser(description='Build timelapse video')
parser.add_argument('-d', '--directory', help='Input directory', required=True)
parser.add_argument('-s', '--start', help='Start time', required=True)
parser.add_argument('-e', '--end', help='End time', required=True)
parser.add_argument('-o', '--output', help='Output filename', required=False, default="timelapse.mp4")
parser.add_argument('-i', '--interval', help='Interval of raw images', required=False, default=5)
parser.add_argument('-f', '--framerate', help='desired framerate for output', required=False, default=25)
parser.add_argument('-t', '--tempdir', help='Directory for temporary files', required=False, default="temp/")
parser.add_argument(      '--pattern', help='Pattern used for encoding Date/Time in source filenames', required=False, default="%Y%m%d%H%M%S")
parser.add_argument(      '--startimage', help='Use this file as first image if the regular one does not exist', required=False, default="black.jpg")

args = vars(parser.parse_args())

def fillBlanks(directory, pattern, interval, start, end, startimage):
  current = start
  
  if not os.path.isfile(directory + current.strftime(pattern) + ".jpg"):
    #sys.exit("First file not found, aborting");
    print("Start image does not exist, copying dummy")
    shutil.copy(startimage, directory + current.strftime(pattern) + ".jpg")
    
  while current <= end:
    if not os.path.exists(directory + current.strftime(pattern) + ".jpg"):
      print("missing file " + directory + current.strftime(pattern) + ".jpg, copying last frame")
      shutil.copy(directory + (current-interval).strftime(pattern) + ".jpg", directory + current.strftime(pattern) + ".jpg")
    current += interval
  return

def generateSequence(directory, pattern, interval, start, end, tempdir):
  if not os.path.isdir(tempdir+"seq"):
    print("Generating symlinks for range {0} to {1}".format(start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S")))
    os.mkdir(tempdir)
    os.mkdir(tempdir + "seq/")
    
    #files = glob.glob(directory + "*.jpg")
    #count = 1
    #for f in files:
    #  print("linking {0} to {1}".format(f, tempdir + "seq/img{0:0>5d}".format(count) + ".jpg"))
    #  os.symlink("../../" + f, tempdir + "seq/img{0:0>5d}".format(count) + ".jpg")
    #  count += 1
    current = start
    count = 1
    while current <= end:
      src = os.path.abspath(directory + current.strftime(pattern) + ".jpg")
      dst = tempdir + "seq/img{0:0>5d}".format(count) + ".jpg"
      #print("linking {0} to {1}".format(src, dst))
      os.symlink(src, dst)
      current += interval
      count += 1
  else:
    print("tempdir exists, assuming correct sequence links for ffmpeg are therein")
  return
  
def createMovie(framerate, tempdir, output):
  print("calling \"ffmpeg -f image2 -i {0}seq/img%05d.jpg -c:v libx264 -r {1} {2}\"".format(tempdir, framerate, output))
  os.system("ffmpeg -f image2 -i {0}seq/img%05d.jpg -c:v libx264 -r {1} {2}".format(tempdir, framerate, output))
  return

def cleanUp(tempdir):
  return
  
if __name__ == '__main__':
  print("Generating timelapse movie")
  pattern = args['pattern']
  start = datetime.strptime(args['start'], pattern);
  end = datetime.strptime(args['end'], pattern);
  interval = timedelta(seconds=int(args['interval']));
  
  print("Starting at {0}".format(start.strftime("%Y-%m-%d %H:%M:%S")))
  print("Up to {0}".format(end.strftime("%Y-%m-%d %H:%M:%S")))
  
  
  print("1 - Fillung up missing images")
  fillBlanks(args['directory'], pattern, interval, start, end, args['startimage'])
  
  print("2 - Generate symlink sequence for ffmpeg")
  generateSequence(args['directory'], pattern, interval, start, end, args['tempdir'])
  
  print("3 - Generate timelapse movie")
  createMovie(args['framerate'], args['tempdir'], args['output'])
  
  print("4 - Cleaning up temporary files")
  cleanUp(args['tempdir'])
