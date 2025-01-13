def search_out(doc, nlp):
  """Search for verbs with simple present tense  

  Args:
    doc (spacy.tokens.Doc): doc to be analyzed
    nlp (spacy.language.Language): context language

  Returns:
    list: list of spacy.tokens.Span
  """

  result = []

  _result = [t for t in doc if t.tag_ in ["VBZ", "VBP", "VB"] and t.dep_ == "ROOT" and "Tense=Pres" in t.morph]

  s = 0
  for index, t in enumerate(_result):
    i = t.i
    if i > s:
      result.append({"text": doc[s:i].text}) 
    result.append({"text": t.text, "meta": {"sign": "verb", "verb_lemma": t.lemma_, "gid": index}})
    s = i+1
  if s < len(doc):
    result.append({"text": doc[s:].text})
  return result
