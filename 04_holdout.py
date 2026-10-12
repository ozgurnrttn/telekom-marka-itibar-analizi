"""Sözlük, kalıplar belirlendikten SONRA çekilen yeni 150 başlıkta (holdout) test edilir."""
import json
import pandas as pd
from pathlib import Path
from sklearn.metrics import cohen_kappa_score
D = Path(__file__).parent
POS = [1201,798,596,506,1141,478,515,1266,208,820,233,771,1196,666,291,1034,1521,1031,1225,663,422,1385,709,776,183,122,460,1124,689,707,675,906,1001,1020,50,1355,1267,110,443,1169,1253,942,495,126,817,731,317,790,589,871,1332,20,315,1494]
NEG = [1452,1534,1084,1091,648,716,106,1445,1234,121,1236,842,368,25,1079,1471,435,1230,916,672,824,723]
h = pd.read_csv(D / "out/dogrulama_holdout.csv", index_col=0)
h["elle"] = 0
h.loc[h.index.isin(POS), "elle"] = 1
h.loc[h.index.isin(NEG), "elle"] = -1
h.to_csv(D / "out/dogrulama_holdout.csv")
cm = pd.crosstab(h.elle, h.ton, rownames=["elle"], colnames=["sözlük"])
acc = (h.ton == h.elle).mean(); k = cohen_kappa_score(h.elle, h.ton)
tp = ((h.ton == -1) & (h.elle == -1)).sum()
r = {"n": len(h), "dogruluk": round(acc, 3), "kappa": round(k, 3),
     "neg_kesinlik": round(tp / max((h.ton == -1).sum(), 1), 3), "neg_duyarlilik": round(tp / max((h.elle == -1).sum(), 1), 3),
     "pos_kesinlik": round(((h.ton == 1) & (h.elle == 1)).sum() / max((h.ton == 1).sum(), 1), 3),
     "pos_duyarlilik": round(((h.ton == 1) & (h.elle == 1)).sum() / max((h.elle == 1).sum(), 1), 3),
     "net_elle": round(((h.elle == 1).mean() - (h.elle == -1).mean()) * 100, 1),
     "net_sozluk": round(((h.ton == 1).mean() - (h.ton == -1).mean()) * 100, 1),
     "cm": [[int(cm.loc[i, j]) if (i in cm.index and j in cm.columns) else 0 for j in (-1, 0, 1)] for i in (-1, 0, 1)]}
print(cm); print(r)
print(h[h.ton != h.elle][["baslik", "ton", "elle"]].to_string())
json.dump(r, open(D / "out/holdout.json", "w"), ensure_ascii=False)
