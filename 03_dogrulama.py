"""Sözlük tabanlı ton etiketinin, 150 başlıklık rastgele örnekte elle verilen etiketlerle karşılaştırılması."""
import json
import pandas as pd
from pathlib import Path
D = Path(__file__).parent
POS = [1027,669,244,59,237,352,1531,1182,1050,1511,1219,175,654,1105,275,1106,298,591,1138,1403,986,809,561,65,141,394,755,353,184,816,514,615,1117,1285,99,985,1259,566,680,239,51,70,76,411,135,1004,970,1551,780,123,706,1197,67,1000,1018,1102,772,1251,1258,730,415,350,1284,907,838,1339,744]
NEG = [381,1458,274,1399,693,997,607,1112,1078]
s = pd.read_csv(D / "out/dogrulama_ornek.csv", index_col=0)
s["elle"] = 0
s.loc[s.index.isin(POS), "elle"] = 1
s.loc[s.index.isin(NEG), "elle"] = -1
s.to_csv(D / "out/dogrulama_ornek.csv")
acc = (s.ton == s.elle).mean()
cm = pd.crosstab(s.elle, s.ton, rownames=["elle"], colnames=["sözlük"])
prec_neg = ((s.ton == -1) & (s.elle == -1)).sum() / max((s.ton == -1).sum(), 1)
rec_neg = ((s.ton == -1) & (s.elle == -1)).sum() / max((s.elle == -1).sum(), 1)
from sklearn.metrics import cohen_kappa_score
k = cohen_kappa_score(s.elle, s.ton)
print(cm); print(f"doğruluk {acc:.2f}  kappa {k:.2f}  neg kesinlik {prec_neg:.2f} duyarlılık {rec_neg:.2f}")
print("elle net:", round(((s.elle==1).mean()-(s.elle==-1).mean())*100,1), "sözlük net:", round(((s.ton==1).mean()-(s.ton==-1).mean())*100,1))
print(s[s.ton != s.elle][["baslik","ton","elle"]].to_string())
json.dump({"n": len(s), "dogruluk": round(acc, 3), "kappa": round(k, 3), "neg_kesinlik": round(prec_neg, 3), "neg_duyarlilik": round(rec_neg, 3),
           "cm": cm.to_dict()}, open(D / "out/dogrulama.json", "w"), ensure_ascii=False, default=int)
