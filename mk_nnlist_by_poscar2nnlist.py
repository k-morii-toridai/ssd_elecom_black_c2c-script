import numpy as np
import os
import subprocess
from multiprocessing import Pool, cpu_count
from tqdm import tqdm
import time


print(f"Now loading poscar_path_list from .npy file...Please wait a half minite.")
poscar_path_list = np.load('poscar_path_list.npy', allow_pickle=True)
print(f"poscar_path_list was loaded from .npy file!!!")
poscar_folder_path = [os.path.split(p)[0] for p in tqdm(poscar_path_list)]
poscar_folder_abs_path = ['/mnt/ssd_elecom_black_c2c' + p.split('..')[1] for p in tqdm(poscar_folder_path)]
print(f"poscar_folder_abs_path was completely made!!!")


def cd_dir_and_pos2nnlist(poscar_folder_path):
    # 1. Change current dir to dir that exists a POSCAR file
    os.chdir(poscar_folder_path)
    
    # 2. Run poscar2nnlist
    try:
        subprocess.run(['/mnt/ssd_elecom_black_c2c/ssd_elecom_black_c2c-script/neib_code/poscar2nnlist', 'POSCAR', '2'], stdout=subprocess.DEVNULL)
    except Exception as e:
        pass


before = time.time()
try:
    p = Pool(cpu_count() - 1)
    print(f"Now poscar2nnlist in making POSCAR.nnlist from POSCAR!!!")
    list(tqdm(p.imap(cd_dir_and_pos2nnlist, poscar_folder_abs_path), total=len(poscar_folder_abs_path)))
    
finally:
    p.close()
    p.join()
after = time.time()
print(f"it took {after - before}sec.")
