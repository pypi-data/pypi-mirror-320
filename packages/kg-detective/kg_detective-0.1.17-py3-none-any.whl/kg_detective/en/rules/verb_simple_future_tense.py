from spacy.matcher import DependencyMatcher
from kg_detective.lib import merge

def search_out(doc, nlp):
  """Search for verbs with simple future tense 

  Args:
    doc (spacy.tokens.Doc): doc to be analyzed
    nlp (spacy.language.Language): context language

  Returns:
    list: list of spacy.tokens.Span
  """

  result = []

  dep_matcher = DependencyMatcher(nlp.vocab)

  will_verb = [
    {
      "RIGHT_ID": "core_verb",
      "RIGHT_ATTRS": {"POS": {"IN": ["VERB", "AUX"]}, "TAG": {"IN": ["VB", "VBN"]}, "DEP": "ROOT"}
    },
    {
      "LEFT_ID": "core_verb",
      "REL_OP": ">",
      "RIGHT_ID": "aux",
      "RIGHT_ATTRS": {"DEP": "aux", "POS": "AUX", "lemma": "will"}
    },
  ]

  dep_patterns = [will_verb]
  dep_matcher.add("verb_simple_future_tense", dep_patterns)
  matches = dep_matcher(doc)

  raw_matches = []
  for index, (_, [verb_id, aux_id]) in enumerate(matches):
    verb = doc[verb_id]
    aux = doc[aux_id]

    aux_verb_assertion = aux_id<verb_id
    if aux_verb_assertion:
      raw_matches.append((aux_id, verb_id+1, {"sign": "will_do", "verb_lemma": verb.lemma_, "gid": index})) 

  dep_matcher.remove("verb_simple_future_tense")

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

