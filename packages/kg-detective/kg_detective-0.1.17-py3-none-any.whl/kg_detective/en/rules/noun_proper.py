from spacy.matcher import DependencyMatcher
from kg_detective.lib import merge

def search_out(doc, nlp):
  """Search for proper nouns 

  Args:
    doc (spacy.tokens.Doc): doc to be analyzed
    nlp (spacy.language.Language): context language

  Returns:
    list: list of spacy.tokens.Span
  """

  result = []
  dep_matcher = DependencyMatcher(nlp.vocab)

  # adjer_noun
  propn = [
    {
      "RIGHT_ID": "propn",
      "RIGHT_ATTRS": {"POS": "PROPN"}
    },
  ]

  dep_matcher.add("noun_proper", [propn])

  matches = dep_matcher(doc)

  raw_matches = []

  for index, (_, [propn_id]) in enumerate(matches):
    propn_core = doc[propn_id]
    propn_tree = [e.i for e in propn_core.subtree]

    propn_assertion = len(propn_tree)>1 and len(propn_tree)==propn_tree[-1]-propn_tree[0]+1

    if propn_assertion:
      raw_matches.append((propn_tree[0], propn_tree[-1]+1, {"sign": "propn", "gid": index}))

  dep_matcher.remove("noun_proper")
  refined_matches = merge(raw_matches)

  # TODO: mark(doc, refined_matches)
  s = 0
  for start, end, meta in refined_matches:
    if start > s:
      text = doc[s:start].text
      result.append({"text": text})
    text = doc[start:end].text
    result.append({"text": text, "meta": meta})
    s = end
  if s < len(doc):
    text = doc[s:].text
    result.append({"text": text})

  return result
