"""
explanations.py
===============
Narasi penjelasan untuk SETIAP chart & tabel di dashboard.

STANDAR WAJIB (aturan permanen, lihat registry E56):
  Setiap elemen visual harus punya tiga hal:
    · KENAPA   — mengapa metrik/analisis ini dipilih (masalah & konteks)
    · TUJUAN   — pertanyaan bisnis apa yang dijawab
    · DAMPAK   — implikasi / keputusan / tindakan yang timbul
  plus CARA BACA bila grafiknya tidak intuitif.

Modul ini dipisah dari dashboard agar:
  - teks tetap terjaga walau kode berubah
  - mudah diterjemahkan (i18n)
  - bisa diaudit: apakah semua elemen sudah punya penjelasan

Cara pakai:
    import explanations as X
    X.render("iv_smile")           # tampilkan box penjelasan di Streamlit
    X.text("iv_smile")             # ambil teks polos (untuk README/report)
"""

from __future__ import annotations

# Kunci = id elemen; nilai = dict dengan kenapa/tujuan/dampak/cara baca.
EXPLAIN = {
    # ------------------------------------------------------------------ tabs
    "iv_smile": {
        "judul": "IV Smile / Skew per Moneyness",
        "kenapa": "Volatilitas implisit (IV) bukan angka tunggal — ia berubah "
                  "menurut seberapa jauh strike dari harga sekarang. Ini bukti "
                  "bagaimana pasar memberi harga risiko pada tiap level.",
        "tujuan": "Mengetahui di titik mana pasar menuntut premi volatilitas "
                  "paling mahal, dan apakah bentuknya simetris atau miring.",
        "dampak": "Bila sayap (OTM/ITM) jauh lebih mahal dari ATM, opsi di sana "
                  "mahal untuk dibeli — trader harus pilih strategi spread, bukan "
                  "beli opsi tunggal. Bentuk asimetris menandakan bias arah pasar.",
        "baca": "Sumbu-X = moneyness (Deep ITM → Deep OTM). Sumbu-Y = IV (%). "
                "Kurva berbentuk U = smile; puncak tidak seimbang = skew.",
    },
    "iv_skew": {
        "judul": "IV Skew per Ticker",
        "kenapa": "Beberapa ticker punya permintaan opsi 'jauh' (strike ekstrem) "
                  "yang tidak wajar — tanda spekulasi atau antisipasi peristiwa.",
        "tujuan": "Mengurutkan ticker berdasarkan seberapa 'miring' kurva IV-nya, "
                  "untuk menemukan saham dengan ekspektasi pergerakan tajam.",
        "dampak": "Ticker dengan skew ekstrem layak diawasi (kemungkinan berita/"
                  "earnings); sekaligus menandakan opsi jauh mahal di sana.",
        "baca": "Nilai = IV rata-rata OTM − ITM (poin persen). Positif besar = "
                "OTM jauh lebih mahal (spekulatif).",
    },
    "iv_both_sides": {
        "judul": "IV Smile — CALL vs PUT",
        "kenapa": "CALL dan PUT punya profil risiko berlawanan; memisahkannya "
                  "mengungkap ke arah mana pasar lebih takut.",
        "tujuan": "Melihat premi mana yang lebih mahal — perlindungan turun (put) "
                  "atau spekulasi naik (call).",
        "dampak": "Put wing lebih tinggi = pasar membayar mahal untuk lindung nilai "
                  "penurunan → bias defensif; strategi penjualan put premium bisa "
                  "menarik di sana (dengan risiko sesuai).",
        "baca": "Batang biru = CALL, merah = PUT, per bucket moneyness. Bandingkan "
                "tinggi keduanya di Deep OTM.",
    },
    "pcr": {
        "judul": "Put/Call Ratio (volume)",
        "kenapa": "PCR adalah indikator sentimen klasik: membandingkan aktivitas "
                  "opsi bearish (put) vs bullish (call). PCR tinggi = hedging.",
        "tujuan": "Mengukur apakah pasar secara keseluruhan sedang bullish "
                  "(PCR<1) atau defensif/bearish (PCR>1), per ticker & agregat.",
        "dampak": "Bila indeks (SPY/QQQ) PCR≈1 sementara saham individual PCR<0,5, "
                  "pasar 'hedge indeks tapi bullish saham' → risk-on yang hati-hati. "
                  "Ini konteks penting sebelum ambil posisi.",
        "baca": "Garis putus-putus = 1,0 (netral). Merah >1,2 (bearish/hedged), "
                "hijau <0,8 (bullish). Label memuat volume C/P mentah.",
    },
    "gex": {
        "judul": "Gamma Exposure (GEX) by Ticker",
        "kenapa": "Dealer market-maker menahan posisi opsi dan harus lindung nilai; "
                  "konsentrasi gamma menentukan seberapa 'lengket' harga di suatu level.",
        "tujuan": "Menemukan ticker dengan exposure gamma terbesar — kandidat "
                  "pergerakan harga yang lebih teredam atau justru melonjak.",
        "dampak": "Ticker GEX tinggi cenderung bergerak lebih stabil (dealer "
                  "menyerap gerak); level strike gamma tertinggi menjadi magnet "
                  "harga jangka pendek.",
        "baca": "GEX di sini PROXY dari open interest tertimbang kedekatan ATM "
                "(bukan gamma Black-Scholes penuh). Semakin tinggi % = semakin "
                "besar pengaruh level tersebut.",
    },
    "oi_walls": {
        "judul": "Open-Interest Walls (per ticker)",
        "kenapa": "Open interest menumpuk di strike tertentu; tumpukan ini sering "
                  "bertindak sebagai magnet/support-resistance karena dealer hedging.",
        "tujuan": "Mengidentifikasi level strike harga yang paling 'berat' secara "
                  "posisi untuk diperhatikan.",
        "dampak": "Level OI besar = kandidat support/resistance. Trader menghindari "
                  "menaruh stop tepat di dinding, atau memanfaatkannya sebagai target.",
        "baca": "Sumbu-Y = strike; panjang batang = besar open interest. Stripe "
                "terbesar = level (wall) yang paling berpengaruh.",
    },
    "liquidity": {
        "judul": "Liquidity Map",
        "kenapa": "Opsi dengan spread lebar sulit & mahal untuk masuk/keluar — "
                  "biaya tersembunyi yang sering diabaikan analisis harga.",
        "tujuan": "Memisahkan kontrak yang benar-benar dapat ditransaksikan dari "
                  "yang 'hanya terlihat murah'.",
        "dampak": "Hindari kontrak spread >8% walau premisnya menarik; pilih OI "
                  "besar + spread tipis. Likuiditas menentukan hasil nyata, bukan "
                  "harga teoretis.",
        "baca": "Kiri-bawah = likuid & murah (OI besar, spread kecil). Ukuran titik "
                "= jumlah kontrak; warna = total volume.",
    },
    "spread_quality": {
        "judul": "Kualitas Bid-Ask Spread",
        "kenapa": "Distribusi spread menunjukkan seberapa 'sehat' pasar opsi di "
                  "dataset — apakah banyak kontrak yang praktis tidak likuid.",
        "tujuan": "Mengukur proporsi kontrak yang layak ditransaksikan vs yang "
                  "sebaiknya dilewati.",
        "dampak": "Kalau mayoritas spread lebar, strategi apa pun harus memperhitungkan "
                  "slippage besar → kurangi ukuran posisi atau pilih instrumen lain.",
        "baca": "Kelompok: rapat (<1%), wajar (1–3%), lebar (3–8%), sangat lebar (>8%).",
    },
    "moneyness": {
        "judul": "Distribusi Moneyness & Premium",
        "kenapa": "Komposisi kontrak per tingkat moneyness + premi rata-ratanya "
                  "menunjukkan di mana pasar menaruh uang.",
        "tujuan": "Mengetahui apakah aktivitas terkonsentrasi pada kontrak dekat "
                  "harga (ATM) atau jauh (spekulatif).",
        "dampak": "Dominasi Deep OTM = banyak taruhan berisiko (murah tapi probabilitas "
                  "kecil). Dominasi ATM = fokus trading volatilitas jangka pendek.",
        "baca": "Pie kiri = jumlah kontrak per bucket; batang kanan = premi rata-rata $.",
    },
    "totals": {
        "judul": "Kontrak Paling Aktif (volume)",
        "kenapa": "Volume menunjukkan di mana perhatian nyata pasar — bukan sekadar "
                  "daftar kontrak yang ada.",
        "tujuan": "Menyoroti kontrak paling banyak diperdagangkan sebagai referensi "
                  "likuiditas & minat pasar.",
        "dampak": "Kontrak bervolume besar lebih mudah dieksekusi & mencerminkan "
                  "konsensus pasar — basis analisis lanjutan yang lebih andal.",
        "baca": "Diurutkan berdasarkan volume; kolom moneyness & IV membantu menilai "
                "posisi relatif terhadap harga.",
    },
    "vol_by_moneyness": {
        "judul": "Total Volume per Moneyness",
        "kenapa": "Sebaran volume menjelaskan di mana likuiditas sesungguhnya "
                  "berada (dekat/sedang/jauh dari harga).",
        "tujuan": "Membaca apakah pasar berdagang tenang (ATM) atau agresif (wing).",
        "dampak": "Bucket dengan volume terbesar = paling dapat dipercaya untuk "
                  "analisis harga; bucket tipis = kurang representatif.",
        "baca": "Batang tinggi = lebih banyak kontrak diperdagangkan pada bucket itu.",
    },
    "score": {
        "judul": "Skor Kontrak (bila tersedia)",
        "kenapa": "Skor komposit menggabungkan delta, volume/OI, gamma, dan bonus "
                  "likuiditas menjadi satu peringkat praktis.",
        "tujuan": "Membantu menyaring kandidat kontrak yang seimbang antara sensitivitas "
                  "harga dan kemudahan eksekusi.",
        "dampak": "Digunakan sebagai shortlist analisis; bukan sinyal beli — perlu "
                  "dikombinasikan dengan pandangan arah pasar.",
        "baca": "Hanya muncul pada dataset yang menyertakan kolom skor.",
    },
}


def text(key: str, lang: str = "id") -> str:
    """Kembalikan teks polos (untuk README/report)."""
    e = EXPLAIN.get(key)
    if not e:
        return ""
    parts = [f"**{e['judul']}**",
             f"- **Kenapa:** {e['kenapa']}",
             f"- **Tujuan:** {e['tujuan']}",
             f"- **Dampak:** {e['dampak']}"]
    if e.get("baca"):
        parts.append(f"- **Cara baca:** {e['baca']}")
    return "\n".join(parts)


def render(key: str, expanded: bool = False, st=None):
    """Tampilkan kotak penjelasan di Streamlit (impor st bila tidak diberikan)."""
    if st is None:
        import streamlit as st  # noqa
    e = EXPLAIN.get(key)
    if not e:
        return
    with st.expander(f"💡 {e['judul']} — Kenapa · Tujuan · Dampak", expanded=expanded):
        st.markdown(
            f"**🔎 Kenapa** — {e['kenapa']}\n\n"
            f"**🎯 Tujuan** — {e['tujuan']}\n\n"
            f"**📈 Dampak** — {e['dampak']}"
        )
        if e.get("baca"):
            st.caption(f"👁️ Cara baca: {e['baca']}")


def audit() -> dict:
    """Cek kelengkapan: setiap entri wajib punya kenapa/tujuan/dampak."""
    rep = {}
    for k, v in EXPLAIN.items():
        rep[k] = all(v.get(f) for f in ("kenapa", "tujuan", "dampak"))
    return rep


if __name__ == "__main__":
    ok = audit()
    n_ok = sum(ok.values())
    print(f"Penjelasan terdaftar: {len(ok)} | lengkap: {n_ok}")
    for k, v in ok.items():
        print(f"  {'OK ' if v else 'MISSING'} {k}")
