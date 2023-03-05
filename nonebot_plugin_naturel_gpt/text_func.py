from nonebot.log import logger

TEXT_FUNC_ENABLE = True
try:
    import numpy as np
    import jieba
except:
    TEXT_FUNC_ENABLE = False
    logger.warning("无法导入 numpy 或 jieba 库，无法使用记忆增强功能")


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