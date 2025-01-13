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
        "RIGHT_ID": "core_verb",
        "RIGHT_ATTRS": {"POS": "VERB", "DEP": "ROOT", "TAG": "VBN"}
      },
      {
        "LEFT_ID": "core_verb",
        "REL_OP": ">",
        "RIGHT_ID": "advcl_verb",
        "RIGHT_ATTRS": {"POS": "VERB", "DEP": "advcl", "TAG": "VBN"}
      },
      {
        "LEFT_ID": "core_verb",
        "REL_OP": ">",
        "RIGHT_ID": "aux_core_have",
        "RIGHT_ATTRS": {"POS": "AUX", "DEP": "aux", "TAG": "VB", "LOWER": "have"}
      },
      {
        "LEFT_ID": "core_verb",
        "REL_OP": ">",
        "RIGHT_ID": "aux_core_md",
        "RIGHT_ATTRS": {"POS": "AUX", "DEP": "aux", "TAG": "MD"}
      },
      {
        "LEFT_ID": "advcl_verb",
        "REL_OP": ">",
        "RIGHT_ID": "aux_advcl",
        "RIGHT_ATTRS": {"POS": "AUX", "DEP": "aux", "TAG": "VBD", "LEMMA": "have"}
      },
    ],
  ]
  dep_matcher.add("subjunctive_past", dep_patterns)
  matches = dep_matcher(doc)

  raw_matches = []
  for index, (_, [core_verb_id, advcl_verb_id, core_aux_have_id, core_aux_md_id, advcl_aux_id]) in enumerate(matches):
    clause_tree = [e.i for e in doc[advcl_verb_id].subtree]
    clause_tree.sort()

    verb_assertion = core_aux_have_id+1==core_verb_id and core_aux_md_id < core_aux_have_id
    clause_assertion = len(clause_tree)==clause_tree[-1]-clause_tree[0]+1
  
    if verb_assertion and clause_assertion:
      raw_matches.append((core_aux_md_id, core_verb_id+1, {"sign": "verb_part", "gid": index}))
      raw_matches.append((clause_tree[0], clause_tree[-1]+1, {"sign": "clause_part", "gid": index}))

  dep_matcher.remove("subjunctive_past")

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

