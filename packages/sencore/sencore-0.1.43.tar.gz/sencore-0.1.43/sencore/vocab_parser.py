from sencore.parser import Parser
import spacy

class VocabParser(Parser):
  """``VocabParser`` is to detect vocabularies from sentence. Inherit ``Parser``, implements ``digest``.
  """

  _pkgindices = {
    "en": "en_core_web_trf",
    "es": "es_dep_news_trf",
    "de": "de_dep_news_trf",
    "fr": "fr_dep_news_trf",
  }

  def __init__(self, lang: str, poses: list=[]):
    """Initialize nlp processor according to language

    Args:
      lang (str): language abbreviation
    """

    super().__init__(lang) 
    self._nlp = spacy.load(self.__class__._pkgindices[lang])
    self._poses = poses

  def digest(self, sentence):
    """Parse sentence into vocabularies with linguistic meta info

    Args:
      sentence (str): sentence to be parsed

    Returns:
      list[dict]: keys are ``word``, ``pos``, "lemma", "start" and "end". 
    
    """

    doc = self._nlp(sentence)
    if len(self._poses)>0:
      result = [{"word": e.text, "pos": e.pos_, "lemma": e.lemma_, "start": e.i, "end": e.i+1} for e in doc if e.pos_ in self._poses]
    else:
      result = [{"word": e.text, "pos": e.pos_, "lemma": e.lemma_, "start": e.i, "end": e.i+1} for e in doc]

    return result 
