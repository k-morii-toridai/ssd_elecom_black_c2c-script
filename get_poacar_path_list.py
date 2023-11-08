import time
from pathlib import Path
import re
from tqdm import tqdm
import subprocess


def get_subdir_list(p_sub_list):
    """
    To get a sub directory path list, Use thie func().
    
    pram: p_aub_list: specify a directory which sub dirs is gotten from.
    """
    # 引数の直下のディレクトリ・パスの一覧を取得
    sub_dir_list_temp = []
    for p_sub in tqdm(p_sub_list):
        sub_dir_list_temp.append([p_s_s for p_s_s in p_sub.iterdir()])
    # ２次元リストを１次元リスト化
    return sum(sub_dir_list_temp, [])


p = Path('../cif/')
p_sub_list = [p_s for p_s in p.glob('[1-9]')]

cif_path_list = get_subdir_list(get_subdir_list(get_subdir_list(p_sub_list)))

def poscar_filter(cif_file_path):
    cif_file_path_str = str(cif_file_path)
    return not('.cif' in cif_file_path_str)

poscar_path_list = [str(path) for path in cif_path_list if poscar_filter(path)]

poscar_path_list = [Path(path) for path in poscar_path_list]


from multiprocessing import Pool, cpu_count

def get_poscar_list(path):
    return list(path.iterdir())

try:
    p = Pool(cpu_count()-1)
    before = time.time()
    poscar_list_temp = list(tqdm(p.imap_unordered(get_poscar_list, poscar_path_list), total=len(poscar_path_list)))
    after = time.time()
    print(f"it took {after - before}sec.")

finally:
    p.close()
    p.join()

    
import itertools
poscar_path_list_fix = list(itertools.chain.from_iterable(poscar_list_temp))


import numpy as np
np.save('poscar_path_list.npy', np.array(poscar_path_list_fix))

