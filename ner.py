import spacy

ENTITY = tuple[str, int, int, str]


class NER:

    def __init__(self, model: str = "de_core_news_sm"):
        self.ner = spacy.load(model)

    def perform_ner(self, text: str) -> list[ENTITY]:
        """
        given some text, perform NER and return a list of entities
        :param text: input text to analyze
        :return: list of ENTITY, which is a tuple representing the entity text, start and end index
            and the entity label
        """
        doc = self.ner(text)
        # we can extract alot of attributes from spacy
        return [(ent.text, ent.start_char, ent.end_char, ent.label_) for ent in doc.ents]
