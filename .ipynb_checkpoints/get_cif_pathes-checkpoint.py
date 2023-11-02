def get_subdir_list(p_sub_list):
    """
    To get a sub directory path list, Use thie func().
    
    pram: p_aub_list: specify a directory which sub dirs is gotten from.
    """
    # 引数の直下のディレクトリ・パスの一覧を取得
    sub_dir_list_temp = []
    for p_sub in p_sub_list:
        sub_dir_list_temp.append([p_s_s for p_s_s in p_sub.iterdir()])
    # ２次元リストを１次元リスト化
    return sum(sub_dir_list_temp, [])


from pathlib import Path
p = Path('../cif/')
p_sub_list = [p_s for p_s in p.glob('[0-9]')]

cif_path_list = get_subdir_list(get_subdir_list(get_subdir_list(p_sub_list)))

import re
def cif_filter(cif_file_path):
    pattern = '.*\.cif'
    cif_file_path_str = str(cif_file_path)
    return bool(re.match(pattern, cif_file_path_str))


cif_path_list = [path for path in cif_path_list if cif_filter(path)]


import pandas as pd
from os import path
def path2df(cif_path_list):

    dict_ = {"cif_AbsPath": [str(elem) for elem in cif_path_list],
             "FolderPath": [path.split(cif_path)[0] for cif_path in cif_path_list],
             "FileName": [path.split(cif_path)[1] for cif_path in cif_path_list],
             "cif_s_dir": [str(elem).split('/')[2] for elem in cif_path_list],
             "cif_ss_dir": [str(elem).split('/')[3] for elem in cif_path_list],
             "cif_sss_dir": [str(elem).split('/')[4] for elem in cif_path_list],
            }
    
    return pd.DataFrame(dict_)


df = path2df(cif_path_list)


def mk_cif_folder_name(df):
    """
    To create a cif_FolderName column, Use thie func().
    """
    return df['FolderPath'] + '/' + df['FileName'].split(".")[0]


df['cif_FolderName'] = df.apply(mk_cif_folder_name, axis=1)


import os
def mk_cif_num_folder(cif_folder_name):
        """
        To create a new dirctory which name is CIF file number, Use thie func().

        param1: example: cif_folder_name='../cif/1/00/00/1000000'
        created: a directory which name is a CIF file number
        """
        os.makedirs(cif_folder_name)
        
        

        
import time 
from tqdm import tqdm
tqdm.pandas()

before = time.time()
df.progress_apply(lambda row: mk_cif_num_folder(row['cif_FolderName']), axis=1)
after = time.time()
print(f"it took {after - before}sec.")

# df_1 = df[df['cif_s_dir'] == '1']
# df_2 = df[df['cif_s_dir'] == '2']
# df_3 = df[df['cif_s_dir'] == '3']
# df_4 = df[df['cif_s_dir'] == '4']
# df_5 = df[df['cif_s_dir'] == '5']
# df_6 = df[df['cif_s_dir'] == '6']
# df_7 = df[df['cif_s_dir'] == '7']
# df_8 = df[df['cif_s_dir'] == '8']
# df_9 = df[df['cif_s_dir'] == '9']



# from pymatgen.io.cif import CifParser
# def cif2poscar(cif_abs_path):
#         """
#         To convert a cif to POSCAR file, Use this func().

#         param1: example: cif_file='1507756.cif'
#         created: a POSCAR file
#         """
        
#         error1_list = []
#         error2_list = []
#         error3_list = []
#         error4_list = []
        
#         try:
#             parser = CifParser(cif_abs_path)
#         except Exception as e:
#             error1_list.append(cif_abs_path)          
#         else:
#             try:
#                 structure = parser.get_structures()[0]
#             except Exception as e:
#                 error2_list.append(cif_abs_path)              
#             else:
#                 try:
#                     # make cif file number
#                     cif_file_number = cif_abs_path.split(".cif")[0]
#                 except Exception as e:
#                     error3_list.appned(cif_abs_path)
#                 else:
#                     try:
#                         # Createしたフォルダに，POSCARファイルとして書き出し
#                         structure.to(fmt="poscar", filename=f"{cif_file_number}/POSCAR") 
#                     except Exception as e:
#                         error4_list.append(cif_abs_path)
                        
                        
                        
# import time
# from tqdm import tqdm
# import warnings
# warnings.simplefilter('ignore')

# def do_cif2poscar(df=df_3):
#     before = time.time()
#     for elem in tqdm(df['cif_AbsPath'].values):
#         cif2poscar(elem)
#     after = time.time()
#     print(f"it took {after - before}sec.")
    
    
# do_cif2poscar(df_1)
