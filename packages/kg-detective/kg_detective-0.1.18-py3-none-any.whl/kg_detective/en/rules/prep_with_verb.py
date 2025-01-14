from spacy.matcher import DependencyMatcher
from kg_detective.lib import clean_merge, mark

def search_out(doc, nlp):
  """Search for prepositions with verb 

  Args:
    doc (spacy.tokens.Doc): doc to be analyzed
    nlp (spacy.language.Language): context language

  Returns:
    list: list of spacy.tokens.Span
  """

  dep_matcher = DependencyMatcher(nlp.vocab)
  dep_patterns = [
    [
      {
        "RIGHT_ID": "verb",
        "RIGHT_ATTRS": {"POS": "VERB"}
      },
      {
        "LEFT_ID": "verb",
        "REL_OP": ">++",
        "RIGHT_ID": "prep",
        "RIGHT_ATTRS": {"DEP": "prt", "POS": "ADP"}
      },
    ],
    [
      {
        "RIGHT_ID": "verb",
        "RIGHT_ATTRS": {"POS": "VERB"}
      },
      {
        "LEFT_ID": "verb",
        "REL_OP": ">++",
        "RIGHT_ID": "prep",
        "RIGHT_ATTRS": {"DEP": "prep", "POS": "ADP"}
      },
      {
        "LEFT_ID": "prep",
        "REL_OP": ">++",
        "RIGHT_ID": "pobj",
        "RIGHT_ATTRS": {"DEP": "pobj"}
      }
    ],
  ]
  dep_matcher.add("prep_with_verb", dep_patterns)
  matches = dep_matcher(doc)

  raw_matches = []
  for index, (_, token_ids) in enumerate(matches):
    verb_core = doc[token_ids[0]]
    prep_core = doc[token_ids[1]]

    verb_subtree = [list(e.subtree) for e in verb_core.rights if e.dep_ not in ["punct", "cc", "conj"]]
    _verb_tree = sum(verb_subtree, [])
    _verb_tree.append(verb_core)
    verb_tree = [e.i for e in _verb_tree]
    verb_tree.sort()
    verb_assertion = len(verb_tree)==verb_tree[-1]-verb_tree[0]+1 and verb_core.i==verb_tree[0]
 
    prep_tree = [e.i for e in prep_core.subtree]
    prep_tree.sort()
    prep_assertion = len(prep_tree)==prep_tree[-1]-prep_tree[0]+1 and prep_core.i==prep_tree[0]

    print(verb_assertion)
    print(prep_assertion)
    if verb_assertion and prep_assertion:
      if len(prep_tree)==1: # prt
        raw_matches.append((verb_tree[0], verb_tree[-1]+1, {"sign": "verb_prt", "verb_lemma": verb_core.lemma_, "gid": index}))
      else:
        raw_matches.append((verb_tree[0], prep_tree[0], {"sign": "verb_part", "verb_lemma": verb_core.lemma_, "gid": index}))
        raw_matches.append((prep_tree[0], prep_tree[-1]+1, {"sign": "prep_part", "gid": index}))

  dep_matcher.remove("prep_with_verb")
      
  refined_matches = clean_merge(raw_matches)

  return mark(doc, refined_matches)
