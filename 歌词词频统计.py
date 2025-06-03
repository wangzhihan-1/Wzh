import re
import jieba
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
import numpy as np
from PIL import Image

# 设置中文字体，确保中文能正常显示
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题


# 读取歌词分词结果文件
def read_lyrics_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return content


# 分词并统计词频
def count_word_frequency(text):
    # 去除标点符号和特殊字符
    text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', ' ', text)
    # 使用jieba进行分词
    words = jieba.cut(text)
    # 过滤掉长度为1的词（如单字）
    words = [word for word in words if len(word) > 1]
    # 统计词频
    word_count = Counter(words)
    return word_count


# 绘制词频条形图
def plot_bar_chart(word_count, top_n=20):
    # 获取前top_n个高频词
    top_words = word_count.most_common(top_n)
    words, counts = zip(*top_words)

    # 创建画布
    plt.figure(figsize=(12, 8))
    # 绘制条形图
    bars = plt.bar(words, counts, color='skyblue')

    # 添加标题和标签
    plt.title('歌词词频统计条形图')
    plt.xlabel('词语')
    plt.ylabel('词频')
    plt.xticks(rotation=45, ha='right')

    # 在每个条形上添加数值标签
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2., height + 0.1,
                 f'{height}', ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig('word_frequency_bar_chart.png')
    plt.show()


# 保存词频结果到CSV文件
def save_to_csv(word_count, file_path):
    # 将Counter转换为DataFrame
    df = pd.DataFrame.from_dict(word_count, orient='index', columns=['词频'])
    # 按词频降序排序
    df = df.sort_values(by='词频', ascending=False)
    # 保存为CSV文件
    df.to_csv(file_path, encoding='utf-8-sig')
    print(f"词频统计结果已保存到{file_path}")


# 绘制词云图
def plot_word_cloud(word_count, mask_path=None):
    # 将Counter转换为字典
    word_dict = dict(word_count)

    # 如果提供了mask图片，使用mask
    if mask_path:
        mask = np.array(Image.open(mask_path))
        wc = WordCloud(
            font_path="simhei.ttf",  # 指定中文字体路径
            mask=mask,
            background_color='white',
            max_words=200,
            max_font_size=100,
            random_state=42
        )
    else:
        wc = WordCloud(
            font_path="simhei.ttf",  # 指定中文字体路径
            background_color='white',
            max_words=200,
            max_font_size=100,
            random_state=42
        )

    # 生成词云
    wc.generate_from_frequencies(word_dict)

    # 显示词云图
    plt.figure(figsize=(10, 8))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.title('歌词词云图')
    plt.savefig('word_cloud.png')
    plt.show()


# 主函数
def main():
    # 文件路径
    file_path = '歌词分词结果.txt'
    csv_path = 'word_frequency.csv'
    mask_path = None  # 可以指定一个图片路径作为词云形状，如mask_path = 'cloud_mask.png'

    # 读取文件
    content = read_lyrics_file(file_path)

    # 分词并统计词频
    word_count = count_word_frequency(content)
    print(f"总词数: {sum(word_count.values())}")
    print(f"唯一词数: {len(word_count)}")
    print("高频词示例:")
    for word, count in word_count.most_common(10):
        print(f"{word}: {count}")

    # 绘制条形图
    plot_bar_chart(word_count)

    # 保存到CSV
    save_to_csv(word_count, csv_path)

    # 绘制词云图
    plot_word_cloud(word_count, mask_path)


if __name__ == "__main__":
    main()