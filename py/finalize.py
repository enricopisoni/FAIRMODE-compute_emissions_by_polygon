import os
import sys

import post_proc
from fairmode_parameters import build_merge as build_merge
from fairmode_parameters import build_out as build_out

if __name__ == "__main__":
    """ " Brief description"""
    
    if len(sys.argv) == 3:
        print('set folder from external script')
        split_folder = sys.argv[1]
        merge_target_folder = sys.argv[2]
        print('out, merge_target')
        print(split_folder, merge_target_folder)
    elif len(sys.argv) == 2:
        print('set folders from app root')
        app_root = sys.argv[1]
        split_folder = build_out(app_root)
        merge_target_folder = build_merge(app_root)
    else:
        print('set folders from code')
        app_root = 'D:\WORK\projects\8-FAIRMODE\FAIRMODE_TOOLS_DEVELOPMENT\COMPUTE_EMISS_BY_POLYGON'
        #out = 'D:\WORK\projects\8-FAIRMODE\FAIRMODE_TOOLS_DEVELOPMENT\COMPUTE_EMISS_BY_POLYGON'
        split_folder = os.path.join(app_root, 'output')
        merge_target_folder = os.path.join(app_root, 'merge')

    post_proc.finalize(split_folder, merge_target_folder)


