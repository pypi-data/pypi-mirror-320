spam_words = {
        "gratuit": 0.8,
        "argent": 0.7,
        "gagner": 0.9,
        "loterie": 0.85,
        "urgent": 0.75,
        "offre": 0.7,
        "promotion": 0.65,
        "gagnant": 0.8,
        "prix": 0.7,
        "crédit": 0.7,
        "casino": 0.9,
        "félicitations": 0.8,
        "mbrok":0.8,
        "gagné": 0.8,
        "free": 0.8,
        "money": 0.7,
        "win": 0.9,
        "lottery": 0.85,
        "urgent": 0.75,
        "offer": 0.7,
        "promotion": 0.65,
        "winner": 0.8,
        "prize": 0.7,
        "credit": 0.7,
        "casino": 0.9 ,
        "congratulations": 0.8,
        "won":0.8,
        "r7bti": 0.9,
        "rebe7ti":0.9,
        "ma7dod": 0.8,
        "hemza":0.7,
        "l3ard": 0.75,
        "fa2izin":0.8,
        "fa2iz":0.8,
        "fabor":0.9,
         "chance":0.7,
        "dkhol":0.6,
        "lien":0.6

}

"""#Filtring

## Spam filtring
"""

def detecter_lien(tweet):
    pattern = r"(https?://[^\s]+|www\.[^\s]+)"
    return re.findall(pattern, tweet)

def spam_analysis(phrases, spam_dict):
    positive_spam = []
    neutral_phrases = []

    for phrase in phrases:
        matches = find_similar_brands(phrase, spam_dict, threshold=0.7)
        matched_words = [match['matched_brand'] for match in matches]

        if matched_words:
            score_sum = sum(spam_dict[word] for word in matched_words)
            if detecter_lien(phrase)!=[]:score_sum+=0.5
            if score_sum > 1:
                  positive_spam.append((phrase, score_sum))

        else:neutral_phrases.append(phrase)

    return positive_spam , neutral_phrases

"""## filring on brand"""

def filterbrand(l,brands):
  v=[]
  nv=[]
  for i in l:
    matches = find_similar_brands(i[0], [brands], threshold=0.7)
    l1=[]
    for match in matches:
      l1.append(match['matched_brand'])
    if brands in l1:
      v.append(i)
    else:
      nv.append(i)
  return v,nv

"""# filtring on features"""

def filterproduit(l,qualité,prix):
  lq=[]
  lp=[]
  lr=[]
  for i in l:
    matchesquality = find_similar_brands(i[0], qualité, threshold=0.7)
    matchesprix = find_similar_brands(i[0], prix, threshold=0.8)
    l1=[]
    l2=[]
    for match in matchesquality:
      l1.append(match['matched_brand'])
    if l1!=[]:
      lq.append(i)
    for match in matchesprix:
      l2.append(match['matched_brand'])
    if l2!=[]:
      lp.append(i)
    if l1==[]and l2==[]: lr.append(i)
  return lq,lp,lr
qualité=["qualité, quality, kalité","jawda","ljawda","lqualité","lqualiti"]

prix=['taman','price',"pri","lprix","prix",'flous','derham','dh','dhs','dirham','ghali','rkhis']
