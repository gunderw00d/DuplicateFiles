# os.listdir(path='.')   # Get list of items in the current dir.

# function doIt(path='.')
#   dirContents = os.listdir(path)
#   foreach entry in dirContents:
#     if (is directory(entry)):
#       doIt(entry)
#     else if (is Image File Extension):
#       dict[jpegFileName] += full path of entry  # list of paths that contain this file name

# function handleDuplicates(dict)
#   foreach k,v in dict:
#     if (length(v) == 1):                 # lone copy of file!
#       copy to dest dir with full path
#     else:
#       foreach path in v:
#         read jpeg exif data
#         os.stat(path)
#         if first, write down st_size, st_ctime/_atime/_mtime, based on what's right
#         if not first, compare st_size, times - close enough?  Wipe 
