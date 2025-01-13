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
        "RIGHT_ID": "root",
        "RIGHT_ATTRS": {"POS": {"IN": ["VERB", "AUX"]}, "DEP": "ROOT"},
      },
      {
        "LEFT_ID": "root",
        "REL_OP": ">",
        "RIGHT_ID": "subject_verb",
        "RIGHT_ATTRS": {"POS": {"IN": ["VERB", "AUX"]}, "DEP": "csubj"}
      },
      {
        "LEFT_ID": "subject_verb",
        "REL_OP": ">",
        "RIGHT_ID": "subj",
        "RIGHT_ATTRS": {"DEP": {"IN": ["nsubj", "nsubjpass"]}, "TAG": {"IN": ["WDT", "WP", "WP$", "WRB"]}}
      },
    ],
  ]
  dep_matcher.add("nominal_subject_clause", dep_patterns)
  matches = dep_matcher(doc)

  raw_matches = []
  for index, (_, [_, clause_id, _]) in enumerate(matches):
    subj_tree = [e.i for e in doc[clause_id].subtree]
    subj_tree.sort()

    subj_assertion = len(subj_tree) == subj_tree[-1]-subj_tree[0]+1
    if subj_assertion:
      raw_matches.append((subj_tree[0], subj_tree[-1]+1, {"sign": "subj_clause", "gid": index})) 

  dep_matcher.remove("nominal_subject_clause")

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
