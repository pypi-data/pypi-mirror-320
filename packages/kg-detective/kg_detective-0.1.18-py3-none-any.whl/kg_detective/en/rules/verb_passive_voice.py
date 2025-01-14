from spacy.matcher import DependencyMatcher
from kg_detective.lib import clean_merge, mark

def search_out(doc, nlp):
  """Search for verbs with passive voice  

  Args:
    doc (spacy.tokens.Doc): doc to be analyzed
    nlp (spacy.language.Language): context language

  Returns:
    list: list of spacy.tokens.Span
  """

  dep_matcher = DependencyMatcher(nlp.vocab)

  complex_passive = [
    {
      "RIGHT_ID": "core_verb",
      "RIGHT_ATTRS": {"POS": "VERB", "TAG": "VBN"}
    },
    {
      "LEFT_ID": "core_verb",
      "REL_OP": ">--",
      "RIGHT_ID": "aux_2",
      "RIGHT_ATTRS": {"DEP": "auxpass", "POS": "AUX", "lemma": "be", "TAG": {"IN": ["VBN", "VBG"]}}
    },
    {
      "LEFT_ID": "core_verb",
      "REL_OP": ">--",
      "RIGHT_ID": "aux_1",
      "RIGHT_ATTRS": {"DEP": "aux", "POS": "AUX"}
    }
  ]
  simple_passive = [
    {
      "RIGHT_ID": "core_verb",
      "RIGHT_ATTRS": {"POS": "VERB", "TAG": "VBN"}
    },
    {
      "LEFT_ID": "core_verb",
      "REL_OP": ">--",
      "RIGHT_ID": "aux",
      "RIGHT_ATTRS": {"DEP": "auxpass", "POS": "AUX", "lemma": "be", "TAG": {"NOT_IN": ["VBN", "VBG"]}}
    }
  ]

  dep_patterns = [simple_passive, complex_passive]
  dep_matcher.add("verb_passive_voice", dep_patterns)
  matches = dep_matcher(doc)

  raw_matches = []

  for index, (_, token_ids) in enumerate(matches):
    core_verb = doc[token_ids[0]]
    aux_tree = [e.i for e in doc[min(token_ids[1:]):max(token_ids[1:])+1]]
    aux_tree.sort()
    
    aux_assertion = len(aux_tree)==aux_tree[-1]-aux_tree[0]+1
    if aux_assertion:
      raw_matches.append((aux_tree[0], aux_tree[-1]+1, {"sign": "aux", "gid": index}))
      raw_matches.append((core_verb.i, core_verb.i+1, {"sign": "verbed", "verb_lemma": core_verb.lemma_, "gid": index}))

  dep_matcher.remove("verb_passive_voice")

  refined_matches = clean_merge(raw_matches)

  return mark(doc, refined_matches)
