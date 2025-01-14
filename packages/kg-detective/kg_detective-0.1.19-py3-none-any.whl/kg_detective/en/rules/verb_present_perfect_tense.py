from spacy.matcher import DependencyMatcher
from kg_detective.lib import clean_merge, mark

def search_out(doc, nlp):
  """Search for verbs with present perfect tense  

  Args:
    doc (spacy.tokens.Doc): doc to be analyzed
    nlp (spacy.language.Language): context language

  Returns:
    list: list of spacy.tokens.Span
  """

  dep_matcher = DependencyMatcher(nlp.vocab)
  have_verb_ed = [
    {
      "RIGHT_ID": "core_verb",
      "RIGHT_ATTRS": {"POS": "VERB", "TAG": "VBN", "DEP": "ROOT"}
    },
    {
      "LEFT_ID": "core_verb",
      "REL_OP": ">",
      "RIGHT_ID": "aux",
      "RIGHT_ATTRS": {"DEP": "aux", "POS": "AUX", "lemma": "have", "TAG": {"IN": ["VB", "VBP", "VBZ"]}}
    }
  ]

  dep_patterns = [have_verb_ed]
  dep_matcher.add("verb_present_perfect_tense", dep_patterns)
  matches = dep_matcher(doc)

  raw_matches = []
  for index, (_, [verb_id, aux_id]) in enumerate(matches):
    verb = doc[verb_id]
    aux = doc[aux_id]

    aux_verb_assertion = aux_id<verb_id
    if aux_verb_assertion:
      raw_matches.append((aux_id, verb_id+1, {"sign": "have_done", "verb_lemma": verb.lemma_, "gid": index})) 

  dep_matcher.remove("verb_present_perfect_tense")

  refined_matches = clean_merge(raw_matches)

  return mark(doc, refined_matches)
