def search_out(doc, nlp):
  """Search for verbs with verb modal   

  Args:
    doc (spacy.tokens.Doc): doc to be analyzed

  Returns:
    list: list of spacy.tokens.Span
  """


  _result = [t for t in doc if t.tag_=="MD"]

  result = []
  s = 0
  for index, t in enumerate(_result):
    i = t.i
    if i > s:
      result.append({"text": doc[s:i].text}) 
    result.append({"text": t.text, "meta": {"sign": "verb_modal", "verb_lemma": t.lemma_, "gid": index}})
    s = i+1
  if s < len(doc):
    result.append({"text": doc[s:].text})
  return result
