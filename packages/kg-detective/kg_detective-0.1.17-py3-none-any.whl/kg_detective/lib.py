def clean_gid(first, second, gids):
  """clean two tuples, which have three elements respectively 

  Args:
    first (tuple): (start, end, {"gid": gid_x})
    second (tuple): (start, end, {"gid": gid_y})
    gids (set): gids should be cleaned

  Returns:
    int: gid to be cleaned 
  """

  if second[2]["gid"] in gids:
    return second[2]["gid"]
  if first[2]["gid"]==second[2]["gid"]:
    return None
  if first[1] <= second[0] or first[0] >= second[1]:
    return None
  else:
    return second[2]["gid"]



def merge(matches):
  """Make order of a list of tuples, which have four elements

  Args:
    matches (list): [(s1, e1, {"gid": gid1}), (s2, e2, {"gid": gid1}), (s3, e3, {"gid": gid2}), ...]

  Returns:
    list: tuples

  Examples:
    >>> refine([(1, 4, {"gid": 1}), (4, 10, {"gid": 1}), (5, 6, {"gid": 2}), (12, 14, {"gid": 2})])
    [(1, 4, {"gid": 1}), (4, 10, {"gid": 1})]
  """
  _matches = sorted(matches, key=lambda m: m[0])
 
  if len(_matches) <= 1:
    return _matches
  result = [_matches[0]]
  gids = set()
  for m in _matches[1:]: 
    gid = clean_gid(result[-1], m, gids) 
    if gid==None:
      result.append(m)
    else:
      gids.add(gid)
  return result 

