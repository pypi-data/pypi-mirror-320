from spacy.matcher import DependencyMatcher
from kg_detective.lib import merge

def search_out(doc, nlp):
  """Search for  

  Args:
    doc (spacy.tokens.Doc): doc to be analyzed
    nlp (spacy.language.Language): context language

  Returns:
    list: list of spacy.tokens.Span
  """
  result = []

  dep_matcher = DependencyMatcher(nlp.vocab)
  dep_patterns = [
    [
      {
        "RIGHT_ID": "copular",
        "RIGHT_ATTRS": {"POS": "AUX", "DEP": "ROOT", "LEMMA": "be"}
      },
      {
        "LEFT_ID": "copular",
        "REL_OP": ">++",
        "RIGHT_ID": "predicative",
        "RIGHT_ATTRS": {"DEP": {"IN": ["ccomp", "advcl"]}}
      },
    ],
  ]
  dep_matcher.add("nominal_predicative_clause", dep_patterns)
  matches = dep_matcher(doc)

  raw_matches = []
  for index, (_, [copular_id, clause_id]) in enumerate(matches):
    predicative_tree = [e.i for e in doc[clause_id].subtree]
    predicative_tree.sort()

    predicative_assertion = len(predicative_tree) == predicative_tree[-1] - predicative_tree[0] + 1
    if predicative_assertion:
      raw_matches.append((copular_id, copular_id+1, {"sign": "copular_part", "copular_lemma": doc[copular_id].lemma_, "gid": index})) 
      raw_matches.append((predicative_tree[0], predicative_tree[-1]+1, {"sign": "pred_clause", "gid": index})) 

  dep_matcher.remove("nominal_predicative_clause")

  refined_matches = merge(raw_matches)

  # TODO: mark(doc, refined_matches)
  s = 0
  for start, end, meta in refined_matches:
    if start > s:
      result.append({"text": doc[s:start].text})
    result.append({"text": doc[start:end].text, "meta": meta})
    s = end
  if s < len(doc):
    result.append({"text": doc[s:].text})

  return result 
