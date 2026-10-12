# Telekom Markalarının Haber İtibarı

Turkcell, Türk Telekom ve Vodafone hakkında Ekim 2023 – Eylül 2025 arasında Google News'te çıkan 3.004 başlığın konu ve ton analizi.

Vaka sayfası: https://ozgurnurettinozturk.com/telekom-marka-itibar-analizi

## Bulgular

| Marka | Başlık (n) | Olumsuz | Net ton | Net ton, bağımsız basın |
|---|---:|---:|---:|---:|
| Turkcell | 706 | %7 | +27 | +19 |
| Türk Telekom | 600 | %10 | +16 | +16 |
| Vodafone | 311 | %6 | +32 | +32 |

- Türk Telekom'un olumsuz başlıklarının yarısından fazlası (58'in 30'u) her yaz duyurulan internet zamları.
- Turkcell'in en kötü ayı Nisan 2025: 15 olumsuz başlığın 11'i 9 Nisan şebeke kesintisiyle ilgili.
- Turkcell'in sorgu sonuçlarının %29'u kendi haber sitelerinden geliyor; bunlar çıkarılınca net ton +27'den +19'a iniyor.

## Yöntem

1. `01_topla.js` — Google News RSS'te her marka için aylık sorgu (72 sorgu), `haberler.tsv` üretir.
2. `02_analiz.py` — başlık bazında tekilleştirme, başlıkta marka geçen haberleri seçme (1.562), sahip olunan medya / bağımsız basın ayrımı, kural tabanlı konu (9 sınıf) ve ton (olumlu / nötr / olumsuz) etiketi, özet metrikler (`out/ozet.json`).
3. `03_dogrulama.py` — kuralların geliştirildiği 150 başlıklık örnek.
4. `04_holdout.py` — kurallar sabitlendikten sonra ayrı tutulan 150 başlıkta test: doğruluk %79, Cohen κ 0,64 (`out/holdout.json`).

Net ton = olumlu başlık payı − olumsuz başlık payı (−100 … +100). Spor sonuçları marka itibarı açısından nötr sayılır.

## Sınırlar

- Google News bir ayın tüm haberlerini değil, ilgili gördüğü bir örneği döndürür; haber hacmi ve sesten pay bu veriyle ölçülmez.
- Yalnızca başlıklar okundu; ton kurallarla atandı, ironi ve bağlam kaçabilir.
- Başlık verisi (`haberler.tsv`) ve elle etiketlenen örnekler, üçüncü taraf başlıkları içerdiği için depoda yok; `01_topla.js` ile yeniden toplanabilir. Google News sıralaması zamanla değiştiği için sonuçlar birebir aynı çıkmayabilir.

## Çalıştırma

```bash
pip install -r requirements.txt
python 02_analiz.py
```
