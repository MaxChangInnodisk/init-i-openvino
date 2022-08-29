import sys, os, glob, shutil
from distutils.core import setup
from Cython.Build import cythonize
from datetime import datetime, timezone, timedelta

# we'd better have Cython installed, or it's a no-go
try:
    from Cython.Distutils import build_ext
except:
    print("You don't seem to have Cython installed. Please get a")
    print("copy from www.cython.org and install it")
    sys.exit(1)

def get_time(zone='+8'):
    # 設定為 +8 時區
    tz = timezone(timedelta(hours=zone))
    # 取得現在時間、指定時區、轉為 ISO 格式
    datetime.now(tz).isoformat()
    return datetime.now(tz).strftime("%y%m%d-%H%M")

# get custom argument: if no key return None , if no value return default
def get_args(args:list, key:str, default:str=None):
    if key in args:
        idx = args.index(key)
        try:
            val = args[int(idx)+1]           # get value of argument
            [ sys.argv.remove(i) for i in [key, val] ] # remove argument or setup will get error
            return os.path.abspath(val)
        except Exception as e:
            if default:
                return default        
            else:
                raise Exception('Could not find the value of argument ({})'.format(key))
    else:
        return default

# print help
def helper():
    info = [
        "$ python setup.py build_ext --inplace --src <the_source_path> [Options]",
        "",
        "[Options]",
        "--dst       if not provide the destination path, will backup and replace the original one.",
        "--backup    change the backup path, the default is './backup'",
        "--build     change the path of build folder, the default is './build'",
        "--exclude   exclude file, using | to split each argument, e.g. '*/web|*.pyc'. "
        "" ]
    [print(i) for i in info]
    sys.exit(1)

# setup basic variable
args = sys.argv

# show helper 
if not (('build_ext' in args) and ('--inplace' in args) and ('--src' in args)) or (('--help' in args) and ('-h' in args)): helper()

# ------------------------------------------------------------------------------------------------------------------------------
# parse custom variable
print('parse custom option')
src_path        = get_args(args, '--src') 
dst_path        = get_args(args, '--dst', src_path)                   
backup_path     = get_args(args, '--backup', './backup') 
build_path      = os.path.normpath(get_args(args, '--build', './build') )
exclude_list    = get_args(args, '--exclude', "" )

# if the source is exists, clear pycahe folder
if not os.path.exists(src_path):
    raise Exception('Could not find the source path ({})'.format(src_path))                
else:
    print('clear pycache')
    [ shutil.rmtree(f) for f in glob.glob(f"{src_path}/**/__pycache__", recursive=True) ] 

# backup the old one with time if the source path is same with the destination path or the backup option is enable
if (src_path==dst_path) or backup_path :
    print('backup the original file')
    if not os.path.exists(backup_path): os.makedirs(backup_path)
    shutil.copytree(src_path, os.path.join(backup_path, "{}_backup_{}".format(os.path.basename(src_path), get_time(+8) )))

# create a temp_dst for setup.py if the source path is not same with the destination path
temp_dst = os.path.join( os.getcwd(), '{}_temp'.format(os.path.basename(dst_path)) )
shutil.copytree(src_path, temp_dst)
print('create a temp_dst ({})'.format(temp_dst))

# distutils
# cpature all python files but exclude __init__.py
print('start package')

# Get list of excludes
exclude_list = [] if exclude_list=="" else exclude_list.split("|")

# Get pure data
exts = []
for f in glob.glob(f"{temp_dst}/**/*.py", recursive=True):
    
    jump_flag = False
    for excl in exclude_list:
        if excl in f: jump_flag = True

    if jump_flag: continue

    exts.append(f)

# Package
setup(
    name=temp_dst,
    ext_modules=cythonize(exts),
    cmdclass = {'build_ext': build_ext},
    # build_dir=build_path
)

# remove build and `.py`
[ os.remove(f) for f in exts ]
[ os.remove(f) for f in glob.glob(f"{temp_dst}/**/*.c", recursive=True) ]

# overwrite
if os.path.exists(dst_path):
    shutil.rmtree(dst_path)
shutil.move(temp_dst, dst_path)

# remove 
[ shutil.rmtree(path) for path in [build_path, temp_dst, backup_path] if os.path.exists(path) ]