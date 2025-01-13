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
        "RIGHT_ID": "verb",
        "RIGHT_ATTRS": {"POS": {"IN": ["VERB", "AUX"]}, "DEP": {"IN": ["ROOT"]}, "LEMMA": {"NOT_IN": ["be"]}}
      },
      {
        "LEFT_ID": "verb",
        "REL_OP": ">++",
        "RIGHT_ID": "obj",
        "RIGHT_ATTRS": {"DEP": "ccomp"}
      },
    ],
  ]
  dep_matcher.add("nominal_object_clause", dep_patterns)
  matches = dep_matcher(doc)

  raw_matches = []
  for index, (_, [verb_id, clause_id]) in enumerate(matches):
    obj_tree = [e.i for e in doc[clause_id].subtree]
    obj_tree.sort()

    obj_assertion = len(obj_tree) == obj_tree[-1]-obj_tree[0]+1
    if obj_assertion:
      raw_matches.append((verb_id, verb_id+1, {"sign": "verb", "verb_lemma": doc[verb_id].lemma_, "gid": index}))
      raw_matches.append((obj_tree[0], obj_tree[-1]+1, {"sign":"obj_clause", "gid": index})) 

  dep_matcher.remove("nominal_object_clause")

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
