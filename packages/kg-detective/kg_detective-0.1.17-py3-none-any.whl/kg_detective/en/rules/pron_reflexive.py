import os
def search_out(doc, nlp):
  """Search for reflexive pronouns 

  Args:
    doc (spacy.tokens.Doc): doc to be analyzed
    nlp (spacy.language.Language): context language

  Returns:
    list: list of spacy.tokens.Token
  """

  pkg_path = os.path.dirname(__file__)
  REFLEXIVE = open(pkg_path + '/pron_reflexive.txt', 'r').read().splitlines() 

  _result = [t for t in doc if t.text.lower() in REFLEXIVE]

  result = []
  s = 0
  for index, t in enumerate(_result):
    i = t.i
    if i > s:
      result.append({"text": doc[s:i].text}) 
    result.append({"text": t.text, "meta": {"sign": "reflexive_pron", "gid": index}})
    s = i+1
  if s < len(doc):
    result.append({"text": doc[s:].text})
  return result
