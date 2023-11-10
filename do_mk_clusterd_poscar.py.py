import os
import time
import subprocess
from multiprocessing import Pool, cpu_count
from tqdm import tqdm
import numpy as np


# remake poscar_folder_abs_path list
print(f"Now loading poscar_path_list from .npy file...Please wait a half minite.")
poscar_path_list = np.load('poscar_path_list.npy', allow_pickle=True)
print(f"poscar_path_list was loaded from .npy file!!!")
poscar_folder_path = [os.path.split(p)[0] for p in tqdm(poscar_path_list)]
poscar_folder_abs_path = ['/mnt/ssd_elecom_black_c2c' + p.split('..')[1] for p in tqdm(poscar_folder_path)]
print(f"poscar_folder_abs_path was completely made!!!")


# make clusterd poscar file from POSCAR file and POSCAR.nnlist file
def cd_dir_and_mk_clusterd_poscar(poscar_folder_path):
    # 1. Change current dir to dir that exists a POSCAR file
    os.chdir(poscar_folder_path)
    
    # 2. Run mk_clusterd_poscar.py
    error_list = []
    try:
        subprocess.run(['python3', '/mnt/ssd_elecom_black_c2c/ssd_elecom_black_c2c-script/mk_clusterd_poscar.py'], 
                       stdout=subprocess.DEVNULL, 
                       stderr=subprocess.DEVNULL,)
    except Exception as e:
        error_list.append(poscar_folder_path)
 

# make some clusterd poscar file
before = time.time()
try:
    p = Pool(cpu_count() - 1)
    print(f"Now make some clusterd poscar file!!!")
    list(tqdm(p.imap(cd_dir_and_mk_clusterd_poscar, poscar_folder_abs_path), total=len(poscar_folder_abs_path)))
    
finally:
    p.close()
    p.join()
after = time.time()
print(f"it took {after - before}sec.")
