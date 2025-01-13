from spacy.matcher import DependencyMatcher
from kg_detective.lib import merge

def search_out(doc, nlp):
  """Search for prepositions with noun 

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
        "RIGHT_ID": "noun",
        "RIGHT_ATTRS": {"POS": "NOUN"}
      },
      {
        "LEFT_ID": "noun",
        "REL_OP": ">",
        "RIGHT_ID": "prep",
        "RIGHT_ATTRS": {"DEP": "prep", "POS": "ADP"}
      },
      {
        "LEFT_ID": "prep",
        "REL_OP": ">",
        "RIGHT_ID": "prep_obj",
        "RIGHT_ATTRS": {"DEP": "pobj"}
      },
    ],
  ]
  dep_matcher.add("prep_with_noun", dep_patterns)
  matches = dep_matcher(doc)

  raw_matches = []
  for index, (_, token_ids) in enumerate(matches):
    noun_core = doc[token_ids[0]]
    noun_tree = [e.i for e in noun_core.subtree]
    noun_tree_assertion =  len(noun_tree) == noun_tree[-1]-noun_tree[0]+1
    if noun_tree_assertion:
      raw_matches.append((noun_tree[0], noun_tree[-1]+1, {"sign": "noun_phrase", "noun_core": noun_core.text, "gid": index}))

  dep_matcher.remove("prep_with_noun")

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
