import jieba
import pandas as pd

# 读取Excel文件
df = pd.read_excel('歌词清洗结果.xlsx')

# 确保'歌词'列存在
if '歌词' not in df.columns:
    raise ValueError("Excel文件中没有'歌词'列")

# 对歌词进行分词处理
def segment_lyrics(lyrics):
    # 使用jieba进行分词
    seg_list = jieba.cut(lyrics)
    return ' '.join(seg_list)

# 应用分词函数到歌词列
df['分词结果'] = df['歌词'].apply(segment_lyrics)

# 只保留分词结果列
result_df = df[['分词结果']]

# 将结果保存到新文件
result_df.to_csv('歌词分词结果.txt', index=False, sep='\t', encoding='utf-8')

print("分词结果已保存到'歌词分词结果.txt'")