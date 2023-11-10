# Converting a POSCAR file to a DataFrame
from my_package.textfile2df import poscar2df_coords 
df_coords = poscar2df_coords(filename='./POSCAR')

# converting POSCAR.nnlist to df_nnlist
from my_package.textfile2df import nnlist2df
df_nnlist = nnlist2df(POSCAR_nnlist='POSCAR.nnlist')

# 1. df_nnlist  -> df_nnlist_rm_duble（重複削除）
import pandas as pd
def mk_rm_duble_filter(df_nnlist):
    
    df_nnlist_grouped = df_nnlist.groupby(by='central atom').mean()
    # central atomカラムでgroupbyした後、index列(central atom)をカラムにする
    df_nnlist_grouped = df_nnlist_grouped.reset_index()
    
    rm_duble_filter = df_nnlist_grouped['central atom'] <= df_nnlist_grouped['neighboring atom']
    df_nnlist_rm_duble = df_nnlist_grouped[rm_duble_filter]
    
    rm_duble_filter = df_coords['central atom'].isin(df_nnlist_rm_duble['central atom'])
    
    return rm_duble_filter

# 2. クラスタ化された絶対中心座標をえる関数
# df_nnlistから重複削除（クラスタ化された絶対中心座標に絞る）
def get_df_coords_filterd(df_nnlist):
    rm_duble_filter = mk_rm_duble_filter(df_nnlist)
    df_coords_filterd = df_coords[rm_duble_filter]

    # 文字列を数値化する
    df_coords_filterd['x'] = pd.to_numeric(df_coords_filterd['x'], errors='coerce')
    df_coords_filterd['y'] = pd.to_numeric(df_coords_filterd['y'], errors='coerce')
    df_coords_filterd['z'] = pd.to_numeric(df_coords_filterd['z'], errors='coerce')

    return df_coords_filterd

df_coords_filterd = get_df_coords_filterd(df_nnlist)


# クラスタ化された相対中心座標を計算する関数
def get_cluster_relative_center(df_nnlist, rm_duble_filter):
    """
    Calculating relative center coordinates of cluster
    param1: df_nnlist
    
    output: df_cluster_relative_center
    """
    df_nnlist_grouped = df_nnlist.groupby(by='central atom').mean()
    # central atomカラムでgroupbyした後、index列(central atom)をカラムにする
    df_nnlist_grouped = df_nnlist_grouped.reset_index()
    # 重複削除
    df_cluster_relative_center = df_nnlist_grouped[rm_duble_filter]
    
    return df_cluster_relative_center

df_cluster_relative_center = get_cluster_relative_center(df_nnlist, mk_rm_duble_filter(df_nnlist))


# = 元のPOSCARファイルのdf + nnlistで得たクラスタ相対中心座標
def get_clusterd_coords(df_abs=df_coords_filterd, df_relative=df_cluster_relative_center):
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

df_coords_fix = get_clusterd_coords(df_abs=df_coords_filterd, df_relative=df_cluster_relative_center)


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
    os.makedirs('gen_data')
    df_coords_fix_str = df2str(df)
    wirte_header2poscar()
    write_species2poscar()
    
    print(f"{output_file} にクラスタ化後の内容が書き込まれました。")


df2poscar(df=df_coords_fix)


