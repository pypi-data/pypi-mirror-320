import threading
from typing import Dict

from duowen_huqie.nlp.query import FulltextQueryer
from duowen_huqie.nlp.rag_tokenizer import RagTokenizer
from duowen_huqie.nlp.synonym import SynonymDealer
from duowen_huqie.nlp.term_weight import TermWeightDealer


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

    def add_word(self, word, frequency: int, pos: str):
        self.tokenizer.add_word(word, frequency=frequency, pos=pos)

    def del_word(self, word):
        self.tokenizer.del_word(word)

    def update_word(self, word, frequency: int, pos: str):
        self.tokenizer.update_word(word, frequency=frequency, pos=pos)

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

