import re
import threading
from typing import Optional, List, Dict, Union, Tuple

import nltk
from jieba import Tokenizer
from jieba.analyse import TFIDF, TextRank
from jieba.posseg import POSTokenizer
from nltk import RegexpParser
from nltk import pos_tag
from nltk import word_tokenize
from nltk.data import find
from nltk.stem import PorterStemmer, WordNetLemmatizer
from rake_nltk import Rake

from duowen_agent.rag.ragflow.nlp.stopwords import STOPWORDS
from .comm import (
    full_to_half_width,
    str_contains_chinese,
    str_contains_english,
    traditional_to_simplified,
    is_chinese_char,
)


def ensure_nltk_resource(resource_name):
    try:
        # 检查资源是否存在
        find(resource_name)
    except LookupError:
        # 如果资源不存在，则下载
        print(f"Resource '{resource_name}' not found. Downloading...")
        nltk.download(resource_name.split("/")[-1])


# Punkt 分词器	tokenizers/punkt
# 停用词库	corpora/stopwords
# WordNet 词库	corpora/wordnet
# POS 标注器	taggers/averaged_perceptron_tagger

ensure_nltk_resource("tokenizers/punkt")
ensure_nltk_resource("tokenizers/punkt_tab")
ensure_nltk_resource("corpora/stopwords")
ensure_nltk_resource("corpora/wordnet")
ensure_nltk_resource("taggers/averaged_perceptron_tagger")
ensure_nltk_resource("taggers/averaged_perceptron_tagger_eng")


class RagTokenizer:
    def __init__(
        self,
        min_keywords_upper_limit: int = 10,
        max_keywords_upper_limit: int = None,
        ratio: float = 0.02,
        pos_filt: List[str] = None,
    ):
        """
        :param ratio: Ratio for topK estimation based on text length.
        :param min_keywords_upper_limit: Maximum limit for topK.

        """

        self.stopwords = STOPWORDS.copy()

        self.tokenizer = Tokenizer()

        self.pos_tokenizer = POSTokenizer(self.tokenizer)

        self.tfidf = TFIDF()
        self.tfidf.stop_words = self.stopwords

        self.textrank = TextRank()
        self.textrank.tokenizer = self.pos_tokenizer
        self.textrank.stop_words = self.stopwords
        if pos_filt is None:
            self.pos_filt = (
                "n",
                "nz",
                "nr",
                "nrt",
                "ns",
                "nt",
                "v",
                "vn",
                "j",
                "t",
                "i",
                "l",
            )
        else:
            self.pos_filt = pos_filt
        self.textrank.pos_filt = frozenset(self.pos_filt)

        self.stemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()

        self.min_keywords_upper_limit = min_keywords_upper_limit
        self.max_keywords_upper_limit = (
            max_keywords_upper_limit if max_keywords_upper_limit else 999999999
        )
        self.ratio = ratio
        self.load_dict_status = False

    def is_load_dict_status(self):
        return self.load_dict_status

    def add_stopword(self, word: str):
        """添加停词"""
        self.stopwords.add(word)

    def add_word(self, word, frequency: int = None, pos: str = None):
        """添加词性标注"""
        self.tokenizer.add_word(word, frequency, pos)

    def del_word(self, word):
        """添加词性标注"""
        self.tokenizer.del_word(word)

    def update_word(self, word, frequency: int = None, pos: str = None):
        self.del_word(word)
        self.add_word(word, frequency, pos)

    def extract_keywords_tfidf(
        self, text: str, max_keywords_per_chunk: Optional[int] = 10, search_cut=True
    ) -> List[str]:
        keywords = self.tfidf.extract_tags(
            sentence=text, topK=max_keywords_per_chunk, allowPOS=self.pos_filt
        )
        if search_cut:
            data = []
            for i in keywords:
                data.extend(self.tokenizer.lcut_for_search(i))
            return data
        else:
            return keywords

    def extract_keywords_textrank(
        self, text: str, max_keywords_per_chunk: Optional[int] = 10, search_cut=True
    ) -> List[str]:
        keywords = self.textrank.textrank(
            sentence=text, topK=max_keywords_per_chunk, allowPOS=self.pos_filt
        )
        if search_cut:
            data = []
            for i in keywords:
                data.extend(
                    [i for i in self.tokenizer.lcut_for_search(i) if len(i) > 1]
                )
            return data
        else:
            return keywords

    def lemmatization(self, text: Union[List[str], str]) -> List[str]:

        if isinstance(text, str):
            _text = [text]
        else:
            _text = text

        data = []
        for line in _text:
            data.append(
                "_".join(
                    [
                        self.stemmer.stem(self.lemmatizer.lemmatize(t))  # 词形转换
                        for t in word_tokenize(line)
                    ]
                )
            )
        data = [
            i.lower()
            for i in data
            if not str_contains_chinese(i)
            and i.lower() not in self.stopwords
            and str_contains_english(i)
        ]
        if data:
            return data
        else:
            return []

    def content_eng_sm_cut(self, text):
        _text = self.extract_eng(text)
        if not str_contains_english(_text):
            return []
        words = word_tokenize(_text)

        return self.lemmatization(words)

    def content_eng_cut(self, text):

        _text = self.extract_eng(text)
        if not str_contains_english(_text):
            return []
        # 分词
        words = word_tokenize(_text)

        # 词性标注
        pos_tags = pos_tag(words)

        grammar = r"""
            NP: {<DT>?<JJ>*<NN.*>+}  # 名词短语
            VP: {<VB.*><NP|PP>*}     # 动词短语
        """

        chunk_parser = RegexpParser(grammar)

        # 应用语法规则
        tree = chunk_parser.parse(pos_tags)

        # 提取名词短语
        phrases = []
        for subtree in tree.subtrees():
            if subtree.label() in ("NP", "VP"):  # 只提取名词短语
                # print(subtree.leaves())
                if all(pos.startswith("NN") for word, pos in subtree.leaves()):
                    for word, pos in subtree.leaves():
                        phrases.append(word)
                else:
                    # print(subtree.leaves())
                    phrase = " ".join(word for word, pos in subtree.leaves())
                    phrases.append(phrase)

        return self.lemmatization(phrases)

    def content_cn_sm_cut(self, text: str):
        """细切"""
        data = [
            i
            for i in self.tokenizer.lcut_for_search(text)
            if i.lower() not in self.stopwords and str_contains_chinese(i)
        ]
        if data:
            return data
        else:
            return []

    def content_cn_cut(self, text: str):
        """粗切"""
        data = [
            i
            for i in self.tokenizer.lcut(text)
            if i.lower() not in self.stopwords and str_contains_chinese(i)
        ]
        if data:
            return data
        else:
            return []

    def content_cut(self, text: str):
        _text = self.preprocess_text(text)
        return self.content_cn_cut(_text) + self.content_eng_cut(_text)

    def content_sm_cut(self, text: str):
        _text = self.preprocess_text(text)
        return self.content_cn_sm_cut(_text) + self.content_eng_sm_cut(_text)

    @staticmethod
    def preprocess_text(text: str) -> str:
        line = full_to_half_width(text)
        line = traditional_to_simplified(line)
        return line

    def _estimate_topk_cn(self, text: str) -> int:
        effective_length = len(re.findall(r"[\u4e00-\u9fa5]", text))
        estimated_topk = int(effective_length * self.ratio)

        return max(
            self.min_keywords_upper_limit,
            min(estimated_topk, self.max_keywords_upper_limit),
        )

    def _estimate_topk_en(self, text: str) -> int:
        effective_length = len(re.findall(r"[a-zA-Z0-9]+", text))
        estimated_topk = int(effective_length * self.ratio)
        return max(
            self.min_keywords_upper_limit,
            min(estimated_topk, self.max_keywords_upper_limit),
        )

    @staticmethod
    def extract_eng(text: str) -> str:
        # 保留字母、空格、常见的标点符号（如 ' - . , ? !）
        cleaned_text = re.sub(r"[^a-zA-Z\s'\-.,?!]", " ", text)
        # 去除多余的空格
        return re.sub(r"\s+", " ", cleaned_text).strip()

    def extract_eng_keywords(self, text: str) -> List[str]:
        _r = Rake(max_length=self._estimate_topk_en(text))
        _r.extract_keywords_from_text(text)
        data = []
        for line in _r.get_ranked_phrases():
            data.append(
                "_".join(
                    [
                        self.stemmer.stem(self.lemmatizer.lemmatize(t))  # 词形转换
                        for t in word_tokenize(line)
                    ]
                ).lower()
            )
        return data

    def term_weight(self, text: str) -> List[Tuple[str, float]]:
        _text = self.preprocess_text(text)
        _top_cn_K = self._estimate_topk_cn(_text)
        _textrank_data = self.textrank.extract_tags(
            sentence=_text, topK=_top_cn_K, withWeight=True, allowPOS=self.pos_filt
        )
        if _textrank_data:
            _cn_data = _textrank_data
        else:
            _cn_data = self.tfidf.extract_tags(
                sentence=_text, topK=_top_cn_K, withWeight=True, allowPOS=self.pos_filt
            )

        _data = []
        if _cn_data:
            for i in _cn_data:
                _is_valid = False
                for j in self.pos_tokenizer.lcut(i[0]):
                    if j.flag and j.flag in self.pos_filt:
                        _is_valid = True
                if _is_valid:
                    _data.append((i[0], round(i[1], 2)))

        _data.extend([[i, 1.0] for i in self.content_eng_cut(text)])  # 英文临时处理
        return _data

    def extract_keywords(self, text, mode="textrank", search_cut=False) -> set[str]:

        _text = self.preprocess_text(text)
        zh_num = len([1.0 for c in _text if is_chinese_char(c)])
        if zh_num == 0:
            return set(self.extract_eng_keywords(_text))

        if mode == "tfidf":
            _data = self.extract_keywords_tfidf(
                _text, self._estimate_topk_cn(_text), search_cut
            )

        elif mode == "textrank":
            _data = self.extract_keywords_textrank(
                _text, self._estimate_topk_cn(_text), search_cut
            )
        else:
            raise ValueError(f"RagTokenizer.extract_keywords Unsupported mode: {mode}")

        _en_data = self.extract_eng(_text)

        if _en_data:
            return set(_data + self.extract_eng_keywords(_en_data))
        else:
            return set(_data)

    def question_extract_keywords(self, text, search_cut=False):
        """由于用户问题可能较短 导致textrank算法无法提取关键词，采用双算法兼容模式"""
        _text = self.preprocess_text(text)
        zh_num = len([1 for c in _text if is_chinese_char(c)])
        if zh_num == 0:
            return set(self.extract_eng_keywords(_text))

        _tfidf_data = self.extract_keywords_tfidf(
            _text, self._estimate_topk_cn(_text), search_cut
        )

        _textrank_data = self.extract_keywords_textrank(
            _text, self._estimate_topk_cn(_text), search_cut
        )

        _en_data = self.extract_eng(_text)

        if _en_data:
            return set(
                _tfidf_data + _textrank_data + self.extract_eng_keywords(_en_data)
            )
        else:
            return set(_tfidf_data + _textrank_data)


class RagTokenizerWrapper:
    """
    建议集成流程为

    from duowen_agent.rag.rag_tokenizer import rag_tokenizers,RagTokenizer
    import threading

    app_name = 'xxx'

    lock. = threading.Lock()

    def get_tokenizer_instance(app_name):
        with lock:
            if app_name in rag_tokenizers:
                return rag_tokenizers[app_name]

            else:
                _tokenizer = RagTokenizer()

                # 完成个性化加载
                _tokenizer.add_word()

                rag_tokenizers[app_name] = _tokenizer

                return rag_tokenizers[app_name]
    """

    def __init__(self):
        self.rag_tokenizer_instance: Dict[str, RagTokenizer] = {}
        self.lock = threading.Lock()

    def __contains__(self, item: str) -> bool:
        return item in self.rag_tokenizer_instance

    def __getitem__(self, item: str):
        if item in self.rag_tokenizer_instance:
            return self.rag_tokenizer_instance[item]
        else:
            raise KeyError(f"RagTokenizerWrapper not found instance {item}")

    def __setitem__(self, key: str, value: RagTokenizer):
        if key in self.rag_tokenizer_instance:
            del self.rag_tokenizer_instance[key]
        self.rag_tokenizer_instance[key] = RagTokenizer()

    def __delitem__(self, key: str):
        if key in self.rag_tokenizer_instance:
            del self.rag_tokenizer_instance[key]


rag_tokenizers = RagTokenizerWrapper()
