import pandas as pd

dj_df = pd.read_csv('./hw7/dj_data.csv',dtype = {'real_result': str,'sim_result': str})
bv_df = pd.read_csv('./hw7/bv_data.csv',dtype = {'real_result': str,'sim_result': str,'answer': str})

def hamming_dis(row):
    a_str = row['real_result']
    b_str = row['sim_result']
    assert len(a_str) == len(b_str)
    dis = 0
    for i in range(len(a_str)):
        if a_str[i] != b_str[i]:
            dis += 1
    return dis

dj_df['hamming_dis'] = dj_df.apply(hamming_dis, axis=1)
bv_df['hamming_dis'] = bv_df.apply(hamming_dis, axis=1)
print(dj_df.head())
print(bv_df.head())

dj_df.to_csv('./hw7/dj_data.csv', index = False)
bv_df.to_csv('./hw7/bv_data.csv', index = False)