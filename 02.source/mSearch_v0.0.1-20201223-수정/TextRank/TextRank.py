# -*- coding: utf-8 -*-
"""
@author: 박진수
"""
# pip install newspaper3k
# pip install konlpy
from newspaper import Article
from konlpy.tag import Kkma
from konlpy.tag import Okt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import normalize
import numpy as np


class SentenceTokenizer(object):
    def __init__(self):
        self.kkma = Kkma()
        self.twitter = Okt()
        self.stopwords = ['중인' ,'만큼', '마찬가지', '꼬집었', "연합뉴스", "데일리", "동아일보", "중앙일보", "조선일보", "기자"
                            ,"아", "휴", "아이구", "아이쿠", "아이고", "어", "나", "우리", "저희", "따라", "의해", "을", "를", "에", "의", "가",]
    def url2sentences(self, url):
        article = Article(url, language='ko')
        article.download()
        article.parse()
        sentences = self.kkma.sentences(article.text)

        for idx in range(0, len(sentences)):
            if len(sentences[idx]) <= 10:
                sentences[idx-1] += (' ' + sentences[idx])
                sentences[idx] = ''

        return sentences

    def text2sentences(self, text):
        sentences = self.kkma.sentences(text)
        for idx in range(0, len(sentences)):
            if len(sentences[idx]) <= 10:
                sentences[idx-1] += (' ' + sentences[idx])
                sentences[idx] = ''
        return sentences

    def get_nouns(self, sentences):
        nouns = []
        for sentence in sentences:
            if sentence != '':
                nouns.append(' '.join([noun for noun in self.twitter.nouns(str(sentence))
            if noun not in self.stopwords and len(noun) > 1]))

        return nouns


class GraphMatrix(object):
    def __init__(self):
        self.tfidf = TfidfVectorizer()
        self.cnt_vec = CountVectorizer()
        self.graph_sentence = []

    def build_sent_graph(self, sentence):
        tfidf_mat = self.tfidf.fit_transform(sentence).toarray()
        self.graph_sentence = np.dot(tfidf_mat, tfidf_mat.T)
        return self.graph_sentence

    def build_words_graph(self, sentence):
        cnt_vec_mat = normalize(self.cnt_vec.fit_transform(sentence).toarray().astype(float), axis=0)
        vocab = self.cnt_vec.vocabulary_
        return np.dot(cnt_vec_mat.T, cnt_vec_mat), {vocab[word] : word for word in vocab}

class Rank(object):
    def get_ranks(self, graph, d=0.85):  # d = damping factor
        A = graph
        matrix_size = A.shape[0]
        for id in range(matrix_size):
            A[id, id] = 0  # diagonal 부분을 0으로
            link_sum = np.sum(A[:, id])  # A[:, id] = A[:][id]
            if link_sum != 0:
                A[:, id] /= link_sum
            A[:, id] *= -d
            A[id, id] = 1

        B = (1 - d) * np.ones((matrix_size, 1))
        ranks = np.linalg.solve(A, B)  # 연립방정식 Ax = b
        return {idx: r[0] for idx, r in enumerate(ranks)}

class Class_TextRank(object):
    def __init__(self, text):
        self.sent_tokenize = SentenceTokenizer()
        if text[:5] in ('http:', 'https'):
            self.sentences = self.sent_tokenize.url2sentences(text)
        else:
            self.sentences = self.sent_tokenize.text2sentences(text)

        self.nouns = self.sent_tokenize.get_nouns(self.sentences)

        self.graph_matrix = GraphMatrix()
        self.sent_graph = self.graph_matrix.build_sent_graph(self.nouns)
        self.words_graph, self.idx2word = self.graph_matrix.build_words_graph(self.nouns)
        self.rank = Rank()
        self.sent_rank_idx = self.rank.get_ranks(self.sent_graph)
        self.sorted_sent_rank_idx = sorted(self.sent_rank_idx, key=lambda k: self.sent_rank_idx[k], reverse=True)
        self.word_rank_idx = self.rank.get_ranks(self.words_graph)
        self.sorted_word_rank_idx = sorted(self.word_rank_idx, key=lambda k: self.word_rank_idx[k], reverse=True)

    def summarize(self, sent_num=3):
        summary = []
        index=[]
        for idx in self.sorted_sent_rank_idx[:sent_num]:
            index.append(idx)

        index.sort()
        for idx in index:
            summary.append(self.sentences[idx])

        return summary

    def keywords(self, word_num=10):
        try:
            rank = Rank()
            rank_idx = rank.get_ranks(self.words_graph)
            sorted_rank_idx = sorted(rank_idx, key=lambda k: rank_idx[k], reverse=True)

            keywords = []
            index=[]

            for idx in sorted_rank_idx[:word_num]:
                index.append(idx)
            #index.sort()
            for idx in index:
                keywords.append(self.idx2word[idx])
            return keywords
        except:
            return "No Word"


def main():

    article = "금융계열사를 거느린 삼성, 현대차, 미래에셋 등 7개 그룹의 자본 적정성을 깐깐하게 보는 금융그룹 통합감독제도가 이달부터 시범 운영에 들어간 가운데, 특정 기업의 지배구조를 압박하는 수단이 될 수 있다는 우려가 나온다. 현재는 금융당국이 자본 적정성 기준선을 100%로 정했지만 향후 상향할 가능성이 있기 때문이다. 새로운 기준이 도입되면 대다수 금융그룹의 자본 적정성이 100%대로 떨어져, 향후 기준선을 상향할 경우 이들 금융그룹엔 큰 부담이 될 수밖에 없다.금융당국 관계자는 2일 문화일보와의 통화에서 “지금 당장은 시범 운영 기간이라 기준선인 100% 이외의 숫자를 제시하지 않았지만 향후 다른 숫자를 제시할 가능성도 있다”면서 “하반기 현장실사와 자본 규제안 세부 기준을 확정하면서 숫자가 달라질 수 있다”고 말했다. 금융당국은 집중위험과 전이위험 산출 기준을 올해 말까지 확정하고 내년 6월까지 모범규준을 수정·보완 계획인데 이 과정에서 자본 적정성 비율을 상향할 가능성을 시사한 셈이다.금융당국은 100%는 최소기준일 뿐 충분한 수준으로는 생각하고 있지 않다. 실제 보험업법의 지급여력비율(RBC) 기준은 100%지만 금융당국은 보험사의 RBC 비율이 150% 밑으로 떨어지면 자본확충을 유도한다.은행권도 국제결제은행(BIS) 기준 자기자본비율 기준치는 8%지만 금융당국의 추가자본확충 요구에 평균 15%대의 비율을 유지하고 있다.만약 금융당국이 금융그룹에 대한 자본 적정성 비율을 현행 100%에서 상향하면 삼성, 현대차, 미래에셋 등 대다수 금융그룹은 이를 맞추기 위해 자본을 확충하거나 비금융 계열사 주식을 매각해야 한다.특히 삼성의 경우 삼성생명이 보유한 삼성전자의 주식을 ‘시가’로 계산한 집중위험 항목을 반영하면 자본 적정성 비율은 110%대로 떨어지는 것으로 나타났다. 20조 원에 달하는 자본을 확충하긴 쉽지 않은 만큼 삼성생명은 삼성전자 주식을 매각하는 방식으로 자본 적정성을 맞출 가능성이 커지는 셈이다.일각에선 금융그룹통합감독제도가 보험업법을 대신해 삼성의 지배구조 개편을 압박하는 데 활용될 것이란 전망도 나온다. 현재 국회에는 보험사가 보유한 계열사 주식을 취득원가 아닌 시가로 평가하는 보험업법 개정안이 발의돼 있는데 야당의 반대로 통과는 어려운 상황이다.국회 정무위 관계자는 “현재 보험업법 통과가 어려워 보이기는 하지만, 이 법이 개정되면 삼성생명은 자산의 3%가 넘는 20조 원가량의 삼성전자 주식을 팔아야 한다”고 말했다.황혜진 기자 best@munhwa.com[Copyrightⓒmunhwa.com '대한민국 오후를 여는 유일석간 문화일보' 무단 전재 및 재배포 금지( 구독신청:02)3701-5555 )]"
    textrank = Class_TextRank(article)
    print(textrank.keywords())
    row_text = ''
    for row in textrank.summarize(3):
        print(row)
        row_text += row
    print(row_text)

if __name__ == '__main__':
    main()
