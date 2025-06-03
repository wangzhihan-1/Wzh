from gensim.corpora import Dictionary
from gensim.models import LdaModel
from gensim.models import CoherenceModel
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import itertools
import pprint
import pyLDAvis.gensim_models
import pyLDAvis


# 读取数据集
data = pd.read_excel('歌词分词结果.xlsx')

# 将文本进行分词
text_cut = []
for text in data['text_cut']:
    if isinstance(text, str):  # 检查该值是否为字符串类型
        text_cut.append(text.split())
    else:
        text_cut.append([])  # 如果不是字符串类型，可以添加一个空列表或者做其他处理

# 打印分词结果示例
print(text_cut[:5])  # 打印前5条文本的分词结果



dictionary = Dictionary(text_cut) # 创建词典
corpus = [dictionary.doc2bow(text) for text in text_cut] # 将文本转换为词袋表示

# 输出词典和文档数量
print('Number of unique tokens: %d' % len(dictionary))
print('Number of documents: %d' % len(corpus))


# 困惑度
perplexities = []
for i in range(2, 11):
    print(i, end=' ')
    model = LdaModel(corpus=corpus, # 语料库
                     id2word=dictionary, # 词典
                     alpha=0.01, # 文档-主题分布的超参数
                     eta=0.01, # 主题-词语分布的超参数
                     iterations=100, # 迭代次数
                     num_topics=i, # 主题数量
                     random_state=1) # 随机数种子
    perplexity = model.log_perplexity(corpus) # 计算困惑度
    perplexities.append(perplexity)

# 画图展示困惑度
perplexity_series = pd.Series(np.exp2(-np.array(perplexities)), index=range(2, 11)) # 计算并保存困惑度
perplexity_series.to_csv('困惑度.txt', header=None)

fig, ax = plt.subplots()
color = 'tab:red'
ax.set_xlabel('Topic num')
ax.set_ylabel('Perplexity', color=color)
ax.plot(range(2, 11), np.exp2(-np.array(perplexities)), 'o-', color=color) # 画图
ax.tick_params(axis='y', labelcolor=color)

fig.tight_layout()
plt.savefig('perplexity.png', dpi=600, bbox_inches='tight')
plt.show()

# 一致性
coherences = []
for i in range(2, 11):
    print(i, end=' ')
    model = LdaModel(corpus=corpus,
                     id2word=dictionary,
                     alpha=0.01,
                     eta=0.01,
                     iterations=100,
                     num_topics=i,
                     random_state=1)
    coherence_model = CoherenceModel(model=model,
                                     texts=text_cut,
                                     corpus=corpus,
                                     dictionary=dictionary,
                                     coherence='c_v',
                                     processes=1)
    coherence = coherence_model.get_coherence()
    coherences.append(coherence)

# 画图展示一致性
coherence_series = pd.Series(coherences, index=range(2, 11))
coherence_series.to_csv('一致性.txt', header=None)

fig, ax = plt.subplots()
color = 'tab:blue'
ax.set_xlabel('Topic num')
ax.set_ylabel('Coherence', color=color)
ax.plot(range(2, 11), coherences, 'o-', color=color)
ax.tick_params(axis='y', labelcolor=color)

fig.tight_layout()
plt.savefig('coherence.png', dpi=600, bbox_inches='tight')
plt.show()


#===最优主题数建模
num_topics=7  #主题数
lda =  LdaModel(
                corpus=corpus,
                id2word=dictionary,
                alpha=0.01,
                eta=0.01,
                iterations=100,
                num_topics=num_topics,
                random_state =1
                )

#展示主题
pprint.pprint(lda.show_topics(num_topics=num_topics,num_words=30))


#===保存主题-词分布
topic = []
for i in range(num_topics):
    topic.append(np.array(lda.show_topic(i,topn=100))[:,0])
    topic.append(np.array(lda.show_topic(i,topn=100))[:,1])
topic = pd.DataFrame(topic).T
topic.columns = list(itertools.chain(*[['topic{}_word'.format(i),'topic{}_distribution'.format(i)] for i in range(num_topics)]))
topic.to_excel('主题-词分布{}.xlsx'.format(num_topics))

#===保存文档-主题分布
data_lda = lda.get_document_topics(corpus,minimum_probability=0)
data_lda = pd.DataFrame([dict(data_lda[i]) for i in range(data.shape[0])])
data_lda.columns=['topic{}'.format(i) for i in range(num_topics)]
for i in range(num_topics):
    data['topic{}'.format(i)] = data_lda['topic{}'.format(i)].values
data['max_topic'] = np.argmax(data[['topic{}'.format(i) for i in range(num_topics)]].values,axis=1)
data.to_excel('数据+LDA结果{}.xlsx'.format(num_topics),index=0)



# 假设 lda 是您的 LDA 模型，corpus 是文档-词矩阵，dictionary 是您的词典
vis = pyLDAvis.gensim_models.prepare(lda, corpus, dictionary)
