from spacy.matcher import DependencyMatcher
from kg_detective.lib import merge

def search_out(doc, nlp):
  """Search for definite article with noun 

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
        "RIGHT_ATTRS": {"POS":"NOUN"}
      },
      {
        "LEFT_ID": "noun",
        "REL_OP": ">>",
        "RIGHT_ID": "def_art",
        "RIGHT_ATTRS": {"POS": "DET", "LEMMA": "the"}
      },
    ],
  ]
  dep_matcher.add("det_definite_art", dep_patterns)
  matches = dep_matcher(doc)

  raw_matches = []
  for index, (_, [noun_id, def_art_id]) in enumerate(matches):
    noun_subtree = [list(e.subtree) for e in doc[noun_id].lefts]  
    noun_tree = [e.i for e in sum(noun_subtree, [])]
    noun_tree.append(noun_id)
    noun_tree.sort()

    def_art_assertion = def_art_id in noun_tree 
    noun_assertion = len(noun_tree)>0 and noun_tree[-1]-noun_tree[0]+1==len(noun_tree) and noun_id== noun_tree[-1]
    
    if def_art_assertion and noun_assertion:
      raw_matches.append((noun_tree[0], noun_tree[-1]+1, {"sign": "def_art_noun", "gid": index}))
  
  dep_matcher.remove("det_definite_art")

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
