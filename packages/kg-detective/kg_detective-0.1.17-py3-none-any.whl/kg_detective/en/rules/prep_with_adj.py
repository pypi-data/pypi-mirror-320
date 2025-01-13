from spacy.matcher import DependencyMatcher
from kg_detective.lib import merge

def search_out(doc, nlp):
  """Search for prepositions with adj 

  Args:
    doc (spacy.tokens.Doc): doc to be analyzed
    nlp (spacy.language.Language): context language

  Returns:
    list: list of spacy.tokens.Span
  """
  result = []

  # pattern: as ... as ...
  dep_matcher = DependencyMatcher(nlp.vocab)
  dep_patterns = [
    [
      {
        "RIGHT_ID": "aux",
        "RIGHT_ATTRS": {"POS": {"IN": ["AUX", "VERB"]}, "LEMMA": "be"}
      },
      {
        "LEFT_ID": "aux",
        "REL_OP": ">",
        "RIGHT_ID": "adj",
        "RIGHT_ATTRS": {"DEP": "acomp", "POS": {"IN": ["ADJ", "VERB"]}}
      },
      {
        "LEFT_ID": "adj",
        "REL_OP": ">",
        "RIGHT_ID": "prep",
        "RIGHT_ATTRS": {"DEP": "prep", "POS": "ADP"}
      },
    ],
  ]
  dep_matcher.add("prep_with_adj", dep_patterns)
  matches = dep_matcher(doc)

  s = 0
  for index, (_, [aux, adj, prep]) in enumerate(matches):
    if adj == prep-1:
      if aux > s:
        result.append({"text": doc[s:aux].text})
      result.append({"text": doc[aux].text, "meta": {"sign": "aux", "aux_lemma": doc[aux].lemma_, "gid": index}})
      s = aux+1
      if adj > s:
        result.append({"text": doc[s:adj].text})
      s = prep + 1
      result.append({"text": doc[adj:s].text, "meta": {"sign": "adj_prep", "adj_lemma": doc[adj].lemma_, "gid": index}})
  if s < len(doc):
    result.append({"text": doc[s:].text})

  dep_matcher.remove("prep_with_adj")

  return result
