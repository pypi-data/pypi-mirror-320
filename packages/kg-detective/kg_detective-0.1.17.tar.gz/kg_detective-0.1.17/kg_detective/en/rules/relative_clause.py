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
        "RIGHT_ID": "noun",
        "RIGHT_ATTRS": {"POS": "NOUN"}
      },
      {
        "LEFT_ID": "noun",
        "REL_OP": ">++",
        "RIGHT_ID": "clause",
        "RIGHT_ATTRS": {"DEP": "relcl"}
      },
    ],
  ]
  dep_matcher.add("relative_clause", dep_patterns)

  raw_matches = []

  matches = dep_matcher(doc)

  for index, (_, [noun_id, clause_id]) in enumerate(matches):
    whole_noun_tree = [e.i for e in doc[noun_id].subtree]
    clause_tree = [e.i for e in doc[clause_id].subtree]
  
    noun_tree = list(set(whole_noun_tree) - set(clause_tree))

    noun_tree.sort()
    clause_tree.sort()

    noun_assertion = len(noun_tree) == noun_tree[-1]-noun_tree[0]+1
    clause_assertion = len(clause_tree) == clause_tree[-1]-clause_tree[0]+1

    if noun_assertion and clause_assertion:
      raw_matches.append((noun_tree[0], noun_tree[-1]+1, {"sign": "noun_part", "gid": index}))
      raw_matches.append((clause_tree[0], clause_tree[-1]+1, {"sign": "clause_part", "gid": index})) 

  dep_matcher.remove("relative_clause")

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
