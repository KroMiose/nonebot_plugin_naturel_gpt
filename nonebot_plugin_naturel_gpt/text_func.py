from nonebot.log import logger

TEXT_FUNC_ENABLE = True
try:
    import numpy as np
    import jieba
except:
    TEXT_FUNC_ENABLE = False
    logger.warning("无法导入 numpy 或 jieba 库，无法使用记忆增强功能")

def compare_text(text1: str, text2: str) -> float:
    if not TEXT_FUNC_ENABLE:
        return 0
    long_text = text1 if len(text1) > len(text2) else text2
    short_text = text1 if len(text1) < len(text2) else text2

    # 滑动窗口截取较长的文本与短文本比较计算相似度取最大值
    max_sim = 0
    for i in range(len(long_text) - len(short_text) + 1):
        sim = cos_sim(long_text[i:i + len(short_text)], short_text)
        if sim > max_sim:
            max_sim = sim
    return max_sim

# 计算两个句子的余弦相似度
def cos_sim(sentence1:str, sentence2:str) -> float:
    if not TEXT_FUNC_ENABLE:
        return 0
    # 对句子进行分词
    words1 = list(jieba.cut(sentence1))
    words2 = list(jieba.cut(sentence2))

    # 构建词汇表
    vocab = list(set(words1 + words2))

    # 将分词结果转换为向量
    vec1 = [words1.count(word) for word in vocab]
    vec2 = [words2.count(word) for word in vocab]

    # 计算向量的余弦值
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

if __name__ == '__main__':
    # 计算两个句子的相似度
    print(cos_sim('我喜欢吃苹果', '我喜欢吃香蕉'))