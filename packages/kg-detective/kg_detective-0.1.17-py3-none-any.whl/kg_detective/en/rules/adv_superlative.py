from spacy.matcher import DependencyMatcher
from kg_detective.lib import merge


def search_out(doc, nlp):
  """Search for superlative adverbs 

  Args:
    doc (spacy.tokens.Doc): doc to be analyzed

  Returns:
    list: list of spacy.tokens.Span
    nlp (spacy.language.Language): context language
  """
  result = []

  dep_matcher = DependencyMatcher(nlp.vocab)

  patterns = [
    [{"LOWER": "the", "OP": "?"}, {"POS": "ADV", "OP": "?"}, {"LOWER": "most"}, {"POS": "ADV"}],
    [{"LOWER": "the", "OP": "?"}, {"POS": "ADV", "OP": "?"}, {"TAG": "RBS"}],
  ]

  # verb adv-est
  verb_advest = [
    {
      "RIGHT_ID": "verb",
      "RIGHT_ATTRS": {"POS": "VERB"}
    },
    {
      "LEFT_ID": "verb",
      "REL_OP": ">",
      "RIGHT_ID": "advest",
      "RIGHT_ATTRS": {"POS": "ADV", "TAG": "RBS"} 
    }
  ]

  # verb the most/least adv
  verb_st_adv = [
    {
      "RIGHT_ID": "verb",
      "RIGHT_ATTRS": {"POS": "VERB"}
    },
    {
      "LEFT_ID": "verb",
      "REL_OP": ">",
      "RIGHT_ID": "adv",
      "RIGHT_ATTRS": {"POS": "ADV", "TAG": "RB"}
    },
    {
      "LEFT_ID": "adv",
      "REL_OP": ">-",
      "RIGHT_ID": "st",
      "RIGHT_ATTRS": {"POS": "ADV", "LEMMA": {"IN": ["least", "most"]}}
    }
  ] 

  raw_matches = []

  dep_patterns = [verb_advest, verb_st_adv]
  dep_matcher.add("adv_superlative", dep_patterns)

  matches = dep_matcher(doc)

  for index, (_, token_ids) in enumerate(matches):
    verb_core = doc[token_ids[0]]
    adv_core = doc[token_ids[1]]

    adv_tree = [e.i for e in list(adv_core.subtree)]
    adv_tree.sort()

    adv_assertion = len(adv_tree) == adv_tree[-1]-adv_tree[0]+1
    verb_assertion = verb_core.i<adv_tree[0]
    
    if adv_assertion and verb_assertion:
      raw_matches.append((verb_core.i, verb_core.i+1, {"sign": "verb_core", "verb_lemma": verb_core.lemma_, "gid": index}))
      raw_matches.append((adv_tree[0], adv_tree[-1]+1, {"sign": "advest", "gid": index}))

  dep_matcher.remove("adv_superlative")

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
