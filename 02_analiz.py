"""Marka itibar analizi — Google News başlıkları (Turkcell, Türk Telekom, Vodafone; Eki 2023 – Eyl 2025).

Girdi : haberler.tsv  (marka sorgusu, ay, tarih, kaynak, alan, başlık)
Çıktı : out/etiketli.csv, out/ozet.json
"""
import json, re
from pathlib import Path
import pandas as pd

D = Path(__file__).parent
OUT = D / "out"; OUT.mkdir(exist_ok=True)

def low(s: str) -> str:
    return s.replace("İ", "i").replace("I", "ı").lower()

d = pd.read_csv(D / "haberler.tsv", sep="\t", encoding="utf-8-sig", quoting=3)
d["t"] = d.baslik.astype(str).map(low)

# 1) Aynı başlık birden fazla sorguda / ayda çıkabiliyor → başlık bazında tekilleştir
d["key"] = d.t.str.replace(r"[^\wçğıöşü ]", "", regex=True).str.replace(r"\s+", " ", regex=True).str.strip()
u = d.sort_values("tarih").drop_duplicates("key").copy()

# 2) Başlıkta hangi marka geçiyor (alt markalar dahil)
BRAND = {
    "turkcell": r"turkcell|superonline|\btv\+|\bfizy|\bbip\b|\bpasaj|lifecell|paycell|global bilgi|tumbara|game\+|\bgnç\b",
    "turk_telekom": r"türk telekom|tivibu|ttkom|\bselfy\b|\btelekom\b",
    "vodafone": r"vodafone|freezone",
}
for b, p in BRAND.items():
    u[b] = u.t.str.contains(p, regex=True)
u["n_marka"] = u[list(BRAND)].sum(axis=1)
core = u[u.n_marka > 0].copy()          # analiz evreni: başlıkta en az bir marka geçen haber

# 3) Sahip olunan medya (owned) vs bağımsız basın (earned)
OWNED = {
    "turkcell": r"turkcell\.com\.tr|superonline\.net|bip\.com|fizy\.com|tvplus\.com\.tr",
    "turk_telekom": r"turktelekom\.com\.tr|tivibu\.com\.tr|ttgv|turktelekomkariyer",
    "vodafone": r"vodafone\.com\.tr|vodafone\.com",
}
core["owned"] = False
for b, p in OWNED.items():
    core.loc[core.alan.str.contains(p, regex=True) & core[b], "owned"] = True

# 4) Konu etiketleri (öncelik sırasıyla; ilk eşleşen kazanır)
TOPIC = [
    ("Kesinti & şikâyet", r"kesinti|çöktü|arıza|erişim sorun|sorun mu|sorun yaşan|internet sorun|neden çekmiyor|yavaşladı|internet gitti|düşük internet hız|şikayet|şikâyet|mağdur|tepki"),
    ("Regülasyon, siyaset & hukuk", r"\bbtk\b|ceza|dava|mahkeme|yargıtay|danıştay|rekabet kurulu|soruşturma|yasak|erişim engeli|vergi|hukuksuz|ihale|lisans|imtiyaz|25 yıl|bakan|uraloğlu|milletvekil|vekil|iktidar|ballı maaş|arpalık|netgsm|muhtar|kamu"),
    ("Finans & hisse", r"hisse|borsa|bilanço|\bkâr|\bkar\b|karı|kârı|net kar|gelir|çeyrek|temettü|hedef fiyat|milyon dolar|milyar|tahvil|kredi|yatırımcı|nyse|ttkom|tcell|piyasa değeri|ebitda|varlık kiralama|iflas|servet"),
    ("Spor & sponsorluk", r"süper kupa|sultanlar ligi|kadın futbol|voleybol|basketbol|\bmaç|\blig\b|ligi|takım|transfer|milli|şampiyon|futbol|stadyum|\bpark\b|arena|galibiyet|euroleague|bsl|eurocup|turnuva|smaç|filenin|devirdi|başantrenör|antrenör|sezon|kiraladı|bisiklet|granfondo|golf|fenerbahçe|galatasaray|beşiktaş|efes|darüşşafaka|sponsor|oyuncu|emilli|e-?spor"),
    ("Yönetim & strateji", r"\bceo\b|genel müdür|yönetim kurulu|icra kurulu|atandı|atama|görev değişi|görevden|istifa|veda|yönetim değişikliği|başkan yardımcısı|satın al|şirket kur|yeni şirket|kuruyor|sattı|satıyor|satış(ı|ını)? |el değiştir|strateji|hedef|personel alımı|kimin\?|ventures|girişim"),
    ("Teknoloji & altyapı", r"\b5g|5\.5g|\b6g|fiber|altyapı|veri merkezi|yapay zek|uydu|mbps|gbps|tbps|terabit|wi-fi|wifi|bulut|siber|kuantum|test|şebeke|nokia|ericsson|huawei|zte|ulak|inovasyon|gigabit|internet hız|baz istasyon|yerli|ar-ge|teknoloji|dijital|enerji yönetimi|e-?sim"),
    ("Ürün, tarife & kampanya", r"tarife|kampanya|paket|hediye|indirim|fiyat|zam|fatura|ücret|bedava|ücretsiz|\btv\+|tivibu|\bfizy|\bbip\b|pasaj|reklam|abone|\bhat\b|sim kart|cihaz|iphone|samsung|galaxy|pixel|nubia|uygulama|kolaylık|ayrıcalık|mağaza|bayi|çekiliş|devreder|game ?pass|game\+|ödeme|\bpay\b|paycell|\bred\b|müşteri|30\. yıl|superbox|selfy|freezone|gnç"),
    ("Sosyal sorumluluk & etkinlik", r"ödül|sürdürülebilir|yeşil|güneş enerjisi|eğitim|burs|kadın|gençler|erişilebilir|engelsiz|deprem|bağış|gönüllü|okul|lise|öğrenci|engelli|sosyal sorumluluk|vakf|sergi|caretta|zekâ gücü|bilim|festival|konser|sinema|\bakm\b|etkinlik|coffee|listesi|en iyi şirket|en değerli"),
]
def topic(t: str) -> str:
    for name, p in TOPIC:
        if re.search(p, t):
            return name
    return "Diğer"
core["konu"] = core.t.map(topic)

# 5) Ton sözlüğü (başlık düzeyi; negatif önce kontrol edilir)
# Sözlük: genel kalıplar; spor sonuçları marka itibarı açısından nötr sayılır (yalnız olumsuz olaylar işaretlenir)
NEG = r"iflas|ballı maaş|alınmadı|birinci derecede sorumlu|sorumlu türk telekom|engel(i|ledi)|itiraf|pahalı|kesinti|çöktü|arıza|sorun|ceza|dava|mahkeme|yargıtay|tepki|şikayet|şikâyet|mağdur|skandal|soruşturma|\bzam\b|zam geldi|zamlandı|zamlar|geriledi|düştü|düşüş|kayıp|kaybediyor|zarar|battı|yasak|hukuksuz|iptal|arpalık|yavaş|çekmiyor|çalışmıyor|aksaklık|erişim engeli|kriz|sızıntı|dolandırıc|ihlal|bozdu|haciz|grev|işten çıkar|yalanla|kapıştı|olaylı|şok fatura|ırkçı|parti damgası|tartışma|boykot"
POS = r"ödül|rekor|büyüdü|büyüme|bir ilk|ilk kez|ilke imza|dünyada ilk|yatırım|başarı|lider|zirve|kazandı|hediye|müjde|iş ?birliği|işbirliği|ortaklık|ortağı|güçlerini birleştir|en hızlı|hızlı internet|\d+ ?mbps|gbps|tbps|\b5g|5\.5g|\b6g|artış|arttı|güçlü|avantaj|ücretsiz|bedava|fırsat|iki katı|ikiye katla|yarı yarıya|kutladı|kutlu|yeni dönem|hayata geçirdi|destek|indirim|yükseldi|teşekkür|gurur|katkı|sürdürülebilir|yeşil|net sıfır|en iyi|en değerli|kolaylık|ayrıcalık|güçlendir|yenilikçi|birinci|ikincisi|tasarruf|ilgi gördü|çözüldü|ulaştı|öncü|hamle|açılış|merkez açtı|yenilendi|yeniledi|yaygınlaş|hazır|vizyon|şekillendir|buluştur|tanıştır|jest|taşındı|net k[aâ]r|k[aâ]r elde|eklendi|ziyan olmuyor|temizliği|proje"
OVERRIDE_POS = r"azalt|harekete geçti|çözüldü"
def tone(t: str, konu: str) -> int:
    neg = re.search(NEG, t)
    if neg and re.search(OVERRIDE_POS, t):
        return 1
    if neg:
        return -1
    if konu == "Spor & sponsorluk":
        return 0
    if re.search(POS, t):
        return 1
    return 0
core["ton"] = [tone(t, k) for t, k in zip(core.t, core.konu)]

core["ceyrek"] = pd.PeriodIndex(core.ay, freq="Q").astype(str)
core.drop(columns=["key"]).to_csv(OUT / "etiketli.csv", index=False, encoding="utf-8")

# 6) Özet metrikler
NAMES = {"turkcell": "Turkcell", "turk_telekom": "Türk Telekom", "vodafone": "Vodafone"}
long = core.melt(id_vars=["tarih", "ay", "ceyrek", "alan", "kaynak", "baslik", "konu", "ton", "owned", "n_marka"],
                 value_vars=list(BRAND), var_name="b", value_name="var")
long = long[long["var"]].drop(columns="var")

res = {"ham_satir": int(len(d)), "tekil_baslik": int(len(u)), "marka_basligi": int(len(core)),
       "kaynak_sayisi": int(core.alan.nunique()), "markalar": {}}
tot = len(long)
for b, g in long.groupby("b"):
    earned = g[~g.owned]
    res["markalar"][b] = {
        "ad": NAMES[b], "n": int(len(g)), "sov": round(len(g) / tot * 100, 1),
        "owned_pay": round(g.owned.mean() * 100, 1),
        "pos": round((g.ton == 1).mean() * 100, 1), "neg": round((g.ton == -1).mean() * 100, 1),
        "net": round(((g.ton == 1).mean() - (g.ton == -1).mean()) * 100, 1),
        "net_earned": round(((earned.ton == 1).mean() - (earned.ton == -1).mean()) * 100, 1),
        "net_owned": round(((g[g.owned].ton == 1).mean() - (g[g.owned].ton == -1).mean()) * 100, 1) if g.owned.any() else None,
        "konu": {k: round(v * 100, 1) for k, v in g.konu.value_counts(normalize=True).items()},
        "konu_net": {k: round(((x.ton == 1).mean() - (x.ton == -1).mean()) * 100, 1) for k, x in g.groupby("konu") if len(x) >= 15},
        "ceyrek_n": {k: int(v) for k, v in g.groupby("ceyrek").size().items()},
        "ceyrek_net": {k: round(((x.ton == 1).mean() - (x.ton == -1).mean()) * 100, 1) for k, x in g.groupby("ceyrek")},
        "ay_neg": {k: int((x.ton == -1).sum()) for k, x in g.groupby("ay")},
        "top_kaynak": earned.kaynak.value_counts().head(5).to_dict(),
    }
for b in BRAND:
    q = d[d.marka == b]
    res["markalar"][b]["sorgu_sonuc"] = int(len(q))
    res["markalar"][b]["baslikta_oran"] = round(q.t.str.contains(BRAND[b], regex=True).mean() * 100, 1)
res["ceyrek_sov"] = {q: {b: round(v / len(x) * 100, 1) for b, v in x.b.value_counts().items()} for q, x in long.groupby("ceyrek")}
res["ortak_baslik"] = int((core.n_marka >= 2).sum())
res["ortak_konu"] = core[core.n_marka >= 2].konu.value_counts().to_dict()
(OUT / "ozet.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
long.to_csv(OUT / "marka_uzun.csv", index=False, encoding="utf-8")
print(json.dumps({k: v for k, v in res.items() if k != "markalar"}, ensure_ascii=False)[:600])
for b, m in res["markalar"].items():
    print(b, {k: m[k] for k in ["n", "sov", "owned_pay", "pos", "neg", "net", "net_earned", "net_owned"]})
    print("  konu", m["konu"]); print("  konu_net", m["konu_net"])
