# Copyright (C) DAPCOM Data Services S.L. - http://www.dapcom.es
# Contact: fapec@dapcom.es
#
# This wrapper has been prepared by DAPCOM
# for potential customers willing to use FAPEC in
# their Python code.
# It can be freely distributed and modified as needed,
# but this notice must be kept.
# Commercial use is only permitted if an adequate FAPEC
# license is acquired.
#

import sys

if sys.platform == "win32":
    import os
    lib_path = os.path.join(os.path.dirname(__file__), "lib")
    if (sys.version_info[1] >= 8):
        os.add_dll_directory(lib_path)
    else:
        os.environ['PATH'] = lib_path + os.pathsep + os.environ['PATH']

from ._fapyc import *





def fapyc_entrypoint():
    arguments = sys.argv
    if (len(arguments) == 1):
        print("Usage: fapyc  {-ow} {-mt <t>} {-o <fn>} <file/dir>")
        print("     -o <fn>       Specify output file name.")
        print("     -ow           Overwrite existing output file(s) without asking")
        print("     -mt <t>       Force multithread setting (1-16, default=auto)")
    else:
        i = 0
        array_n = len(arguments)
        overwrite = False
        threads = -1
        # Take the input file
        filename = arguments[-1]
        # Default output file
        output_file = filename + ".fapec"
        # First take the options
        while (i < array_n):
            # Activate overwrite without asking
            if (arguments[i] == "-ow"):
                overwrite = True
                i = i + 1
                continue
            # Multithread setting
            if (arguments[i] == "-mt"):
                # Do we have a numerical value with the argument?
                if ((i+1) < array_n and arguments[i + 1].isnumeric()):
                    threads = int(arguments[i + 1])
                    # Step two indexes instead of 1
                    i = i + 2
                    continue
                else:
                    print("No valid number of threads value.")  
                    exit(1)
            # Output file name
            if (arguments[i] == "-o"):
                if ((i+1) < array_n):
                    output_file = arguments[i+1] 
                    i = i + 2
                    continue
                else:
                    print("No valid output file name.")
                    exit(1)
            i = i + 1
        

        from fapyc import Fapyc
        fp = Fapyc(filename = filename)

        fp.fapyc_set_askOverwrite(not overwrite)
        fp.fapyc_set_nthreads(threads)

        fp.compress_auto(output = output_file)

        
            
        
        


def unfapyc_entrypoint():
    arguments = sys.argv
    if (len(arguments) == 1):
        print("Usage: unfapyc  {-ow} {-mt <t>}  {-list} {-part <i>} {-o <fn>} <file.fapec>")
        print("     -ow           Overwrite existing output file(s) without asking")
        print("     -mt <t>       Force multithread setting (1-16, default=auto)")
        print("     -list         Only list the .fapec file contents")
        print("     -part <i>     Decompress one part, give it by the index.")
        print("     -o <fn>       Specify output file name.")
    else:
        i = 0
        array_n = len(arguments)
        output_file = "."
        overwrite = False
        threads = -1
        show_list = False
        part = -1
        #Take the fapec file
        fapec_file = arguments[-1]
        # First take the options
        while (i < array_n):
        # Activate overwrite without asking
            if (arguments[i] == "-ow"):
                overwrite = True
                i = i + 1
                continue
            if (arguments[i] == "-mt"):
                # Do we have a numerical value with the argument?
                if ((i+1) < array_n and arguments[i + 1].isnumeric()):
                    threads = int(arguments[i + 1])
                    # Is the numerical value between 1 and 16?
                    if (threads >= 1 and threads <= 16): 
                        # Step two indexes instead of 1
                        i = i + 2
                        continue
                    else:
                        print("The number of threads must be between 1 and 16.")
                        exit(1)  
                else:
                    print("No valid number of threads value.")  
                    exit(1)
            if (arguments[i] == "-list"):
                show_list = True
                break
            if (arguments[i] == "-part"):
                # Do we have a numerical value with the argument?
                if ((i+1) < array_n and arguments[i + 1].isnumeric()):
                    part = int(arguments[i + 1])
                    i = i + 2
                    continue    
                else:
                    print("Invalid number part")
                    exit(1)
                        # Output file name
            if (arguments[i] == "-o"):
                if ((i+1) < array_n):
                    output_file = arguments[i+1] 
                    i = i + 2
                    continue
                else:
                    print("No valid output file name.")
                    exit(1)
            #No valid argument
            i = i + 1
        from fapyc import Unfapyc
        uf = Unfapyc(filename = fapec_file)
        uf.fapyc_set_askOverwrite(not overwrite)
        uf.fapyc_set_nthreads(threads)
        # Get the number of parts in the file
        nparts = uf.fapyc_get_farch_num_parts()
        n = range(nparts)
        # Get the name of the parts
        if show_list:
            for part_i in n:
                pname = uf.fapyc_get_part_name(part_i)
                print("Part: " + str(part_i) + " Name: " + pname)
            exit(0)
        uf.decompress(partindex = part, output = output_file)
