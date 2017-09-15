from distutils.core import setup 
import py2exe
import sys

includes = ["encodings", "encodings.*"]    
sys.argv.append("py2exe")  
py2exe_options = {
      "bundle_files": 1,
      "dll_excludes": [ "crypt32.dll", "mpr.dll" ]
}

setup(options = {'py2exe': py2exe_options},  
      zipfile=None,   
      console = [{"script":'weiboPicDownloader.py'}])
