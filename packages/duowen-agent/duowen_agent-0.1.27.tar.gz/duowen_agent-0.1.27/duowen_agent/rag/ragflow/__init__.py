import threading
from typing import Dict

from duowen_agent.rag.ragflow.nlp.query import FulltextQueryer
from duowen_agent.rag.ragflow.nlp.rag_tokenizer import RagTokenizer
from duowen_agent.rag.ragflow.nlp.synonym import SynonymDealer
from duowen_agent.rag.ragflow.nlp.term_weight import TermWeightDealer


class NLP:

    def __init__(
        self,
        tokenizer: RagTokenizer = None,
        tw: TermWeightDealer = None,
        syn: SynonymDealer = None,
    ):

        self.tokenizer = tokenizer if tokenizer else RagTokenizer()
        self.tw = tw if tw else TermWeightDealer(self.tokenizer)
        self.syn = syn if syn else SynonymDealer()
        self.query = FulltextQueryer(self.tokenizer, self.tw, self.syn)

    def content_cut(self, text: str):
        return self.tokenizer.tokenize(text)

    def content_sm_cut(self, text: str):
        return self.tokenizer.fine_grained_tokenize(self.tokenizer.tokenize(text))

    def term_weight(self, text: str):
        match, keywords = self.query.question(text)
        if match:
            return match.matching_text
        else:
            return None


class NLPWrapper:

    def __init__(self):
        self.nlp_instance: Dict[str, NLP] = {}
        self.lock = threading.Lock()

    def __contains__(self, item: str) -> bool:
        return item in self.nlp_instance

    def __getitem__(self, item: str):
        if item in self.nlp_instance:
            return self.nlp_instance[item]
        else:
            raise KeyError(f"RagTokenizerWrapper not found instance {item}")

    def __setitem__(self, key: str, value: RagTokenizer):
        if key in self.nlp_instance:
            del self.nlp_instance[key]
        self.nlp_instance[key] = NLP()

    def __delitem__(self, key: str):
        if key in self.nlp_instance:
            del self.nlp_instance[key]


nlp_server = NLPWrapper()


if __name__ == "__main__":

    nlp = NLP()
    text = "刚刚有一个疯子杀死了我的女友，经过惨烈的搏斗，我杀死了他。但我的内心是熊熊燃烧的怒火，我不服为什么是我要遭受这一切，我要报复！这时候，我看见了另一个我挽着我的女友走了过去。"
    text = "Apache Spark 是一个用于大规模数据处理的统一分析引擎。它提供了 Java、Scala、Python 和 R 的高级 API，以及支持通用执行图的优化引擎。它还支持包括 Spark SQL 用于 SQL 和结构化数据处理、Spark 上的 pandas API 用于 pandas 工作负载、MLlib 用于机器学习、GraphX 用于图处理以及 Structured Streaming 用于增量计算和流处理的丰富高级工具集。 "

    print(nlp.content_cut(text))
    print(nlp.content_sm_cut(text))
    print(nlp.term_weight(text))
