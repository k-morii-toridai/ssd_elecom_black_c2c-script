import pandas as pd
from my_package.textfile2df import poscar2df_coords 
from my_package.textfile2df import nnlist2df


df_coords = poscar2df_coords(filename='./POSCAR')


# #行の表示数の上限を撤廃
# pd.set_option('display.max_rows', None)

df_nnlist = nnlist2df(POSCAR_nnlist='POSCAR.nnlist')

def get_elem_max_filter(df_nnlist=df_nnlist):
    """
    To get cluster center abs coords from df_coords, Please use this filter.
    
    Input: df_nnlist 
 -> Output: The max number of element 
            in neighboring column of df_nnlist, 
            when df_nnlist groupbyed neighboring column and .count() 
    """
    elem_max_num = df_nnlist.groupby('central atom').count()['neighboring atom'].max()
    elem_max_num_filter = df_nnlist.groupby('central atom').count()['neighboring atom'] == elem_max_num
    # elem_max_num_filter_list = elem_max_num_filter.to_list()
    elem_max_num_filter_list = pd.Series(elem_max_num_filter.to_list())
    return elem_max_num_filter_list


def get_all_non_clusterd_atom(df_nnlist=df_nnlist, df_coords=df_coords):
    """
    dependency: get_elem_max_filter(), get_right_value()
    
    To get non-clusterd central atom list, Use this func.
    
    Input: DataFrames
 -> Output: a list 
    
    param1: df_nnlist=df_nnlist
    param2: df_coords=df_coords
    """
    
    # 入力値が左側の数値と同じ場合、対応する右側の数値を返す関数
    def get_neighboring_atoms_list(central_atom_id, df_nnlist=df_nnlist):
        """
        To get all central atoms of a cluster(:neighbors), Input a number of cluster center element number(:central atom)

        Input: central atom column element In df_nnlist
     -> Output: All neighboring atom column element that Input(:elemnt) match central atom column element

        param1: Input: central atom column element In df_nnlist
        """
        # 左側の列から対応する行を選択し、右側の数値を取得
        # result = df_nnlist[df_nnlist['central atom'] == input_value]['neighboring atom'].values
        neighboring_atoms_list = df_nnlist[df_nnlist['central atom'] == central_atom_id]['neighboring atom'].tolist()
        return neighboring_atoms_list
    
    
    elem_max_num_filter = get_elem_max_filter(df_nnlist=df_nnlist)
    # クラスタ(原子団)の中心の原子のid(central atomの値)のリスト
    cluster_central_atom_list = df_coords[elem_max_num_filter]['central atom'].tolist()
    # クラスタ(原子団)に属するすべての原子のid(central atomの値)を取得
    cluster_all_atom_list_duplicated = [get_neighboring_atoms_list(elem) for elem in cluster_central_atom_list]
    # 2重リストを1重リストにflatten
    cluster_all_atom_list_duplicated_flatten = [item for sublist in cluster_all_atom_list_duplicated for item in sublist]
    # flat_listの重複削除
    cluster_all_atom_set = set(cluster_all_atom_list_duplicated_flatten)
    
    # 元のposcarのcentral atomの一覧を取得
    all_central_atom_set = set(df_coords['central atom'].tolist())
    
    # クラスタ(原子団)に属さない原子のid(central atomの値)を取得
    all_non_clusterd_atom_list = list(all_central_atom_set.difference(cluster_all_atom_set))
    
    return all_non_clusterd_atom_list


def get_all_non_clusterd_atom_filter(df_nnlist=df_nnlist, df_coords=df_coords):
    """
    To convert list to filter, Use thie func.
    """
    all_non_clusterd_atom_list = get_all_non_clusterd_atom(df_nnlist=df_nnlist, df_coords=df_coords)
    all_non_clusterd_atom_filter = df_coords['central atom'].apply(lambda row: row in all_non_clusterd_atom_list)
    return all_non_clusterd_atom_filter


central_atom_filter_fix = get_elem_max_filter() | get_all_non_clusterd_atom_filter()


df_coords_abs_center = df_coords[central_atom_filter_fix]

def df_elem_str2num(df_coords_abs_center=df_coords_abs_center):
    # 文字列を数値化する
    df_coords_abs_center['x'] = pd.to_numeric(df_coords_abs_center['x'], errors='coerce')
    df_coords_abs_center['y'] = pd.to_numeric(df_coords_abs_center['y'], errors='coerce')
    df_coords_abs_center['z'] = pd.to_numeric(df_coords_abs_center['z'], errors='coerce')
    return df_coords_abs_center

df_coords_abs_center = df_elem_str2num(df_coords_abs_center=df_coords_abs_center)



df_nnlist_grouped = df_nnlist.groupby('central atom').mean()
# central atomカラムでgroupby.mean()した後、index列(central atom)をカラムにする   
df_nnlist_grouped = df_nnlist_grouped.reset_index()   
# 意味のないカラムを落とす
df_nnlist_grouped = df_nnlist_grouped[['central atom', 'X', 'Y', 'Z']]

# フィルターで必要なクラスタの相対中心座標に絞る
df_cluster_relative_center = df_nnlist_grouped[central_atom_filter_fix]


def get_clusterd_coords(df_abs=df_coords_abs_center, df_relative=df_cluster_relative_center):
    df_coords_x = df_abs['x'] + df_relative['X']
    df_coords_y = df_abs['y'] + df_relative['Y']
    df_coords_z = df_abs['z'] + df_relative['Z']
    df_coords_species = df_abs['Species']

    # カラム名を指定してデータフレームを作成
    df_coords_fix = pd.DataFrame({
        'X': df_coords_x,
        'Y': df_coords_y,
        'Z': df_coords_z,
        'Species': df_coords_species,
    })

    return df_coords_fix


df_coords_fix = get_clusterd_coords(df_abs=df_coords_abs_center, df_relative=df_cluster_relative_center)


# 元のPOSCARファイルから5行目までを抽出して、新しいPOSCARファイルに書き込む関数
import os
def df2poscar(df=df_coords_fix, original_file="./POSCAR", output_file="gen_data/POSCAR"):
    """
    Writing the DataFrame(:df_coords_fix) to a POSCAR file.
    param1: DataFrame that has 'X', 'Y', 'Z' columns about coords.
    param2: original POSCAR file
    param3: generated POSCAR file
    """
    
    # df_coords_fixを文字列に変換
    def df2str(df):
        df_coords_fix_str = df[['X', 'Y', 'Z']].to_string(header=False, index=False, index_names=False)
        return df_coords_fix_str

    
    # df_coords_fixから元素種を文字列として抽出する関数
    def return_species(df):
        species_line = ' '.join(df['Species'].unique())
        num_line = ' '.join([str(len(df[df['Species'] == specie])) for specie in df['Species'].unique()])
        return species_line + '\n' + num_line

    
    # 元のPOSCARファイルの5行目までを抽出し，新しいファイルに書き込む
    def wirte_header2poscar():
        # 最初の5行を抽出
        with open(original_file, 'r') as infile:
            lines = infile.readlines()[:5]
        # 新しいPOSCARファイルに書き込む
        with open(output_file, 'w') as outfile:
            outfile.writelines(lines)
    
    
    # 新しいPOSCARファイルに書き込んでいく
    def write_species2poscar():
        with open(output_file, 'a') as file:
            # すでに存在するテキストファイルに元素種を追記
            file.write(return_species(df) + '\n')
            # 元素種まで書かれたファイルにDirectという文字をを追記
            file.write('Direct\n')
            # 直交座標を追記
            file.write(df_coords_fix_str + '\n')


    # 関数をcall
    None if os.path.exists("gen_data") else os.makedirs('gen_data')
    df_coords_fix_str = df2str(df)
    wirte_header2poscar()
    write_species2poscar()
    
    print(f"{output_file} にクラスタ化後の内容が書き込まれました。")
    
    
df2poscar()
