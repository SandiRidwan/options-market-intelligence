
# ---------------------------------------------------------------------------
# KONTEN INSIGHT — Options Market Intelligence
# Sudut pandang: trader opsi/analis derivatif yang membaca posisi pasar.
# ---------------------------------------------------------------------------
from insight import register

register(
    "iv_smile",
    kesimpulan=(
        "IV smile/skew menunjukkan volatilitas tersirat berbeda antar-strike: "
        "opsi jauh dari harga (OTM) umumnya lebih mahal. Skew negatif (put lebih "
        "mahal) menandakan pasar membayar premium untuk perlindungan turun."),
    rekomendasi=[
        "Skew put mahal → pasar cemas turun; bila pandanganmu berbeda, JUAL "
        "perlindungan (jual put) untuk panen premi — dengan manajemen risiko ketat.",
        "Hindari beli opsi OTM yang sudah mahal (IV tinggi) — edge tipis setelah "
        "premi membengkak.",
        "Gunakan skew sebagai indikator sentimen: perubahannya lebih informatif "
        "dari levelnya.",
    ],
    risiko=(
        "Menjual perlindungan saat pasar cemas memberi premi menarik, tetapi "
        "risiko ekor (crash) bisa jauh melebihi premi terkumpul. Tanpa lindung "
        "nilai, kerugian dapat tak terbatas."),
    tingkat="tinggi",
)

register(
    "iv_skew",
    kesimpulan=(
        "IV skew berbeda antar-ticker: sebagian aset menunjukkan ketakutan turun "
        "yang lebih tinggi (skew curam), sebagian netral. Perbandingan ini "
        "mengungkap di mana risiko paling diprihakkan pasar."),
    rekomendasi=[
        "Ticker dengan skew curam = permintaan lindung tinggi; cari peluang di "
        "mana ekspektasi pasar mungkin terlalu pesimis.",
        "Diversifikasi: jangan bertaruh pada satu arah skew seluruh portofolio.",
        "Pantau pergeseran skew antar-ticker sebagai sinyal rotasi risiko.",
    ],
    risiko=(
        "Mengabaikan skew lintas-aset membuat portofolio rentan pada satu skenario "
        "risiko. Konsentrasi eksposur arah = kerugian besar bila skenario meleset."),
    tingkat="sedang",
)

register(
    "iv_both_sides",
    kesimpulan=(
        "IV smile CALL vs PUT membandingkan sisi call & put. Bila wing PUT lebih "
        "tinggi dari CALL, pasar membayar lebih untuk perlindungan turun — "
        "menandakan bias pesimis/hedging."),
    rekomendasi=[
        "Put wing mahal → permintaan lindung tinggi; jual put (panen premi) bila "
        "pandanganmu tidak sepessimis pasar, dengan manajemen risiko ketat.",
        "Selisih call-put wing melebar = kekhawatiran naik; gunakan sebagai "
        "sinyal rotasi.",
        "Jangan jual perlindungan tanpa lindung nilai risiko ekor (crash).",
    ],
    risiko=(
        "Menjual perlindungan saat pasar cemas memberi premi menarik, tetapi "
        "risiko ekor bisa jauh melebihi premi. Tanpa hedge, kerugian bisa tak "
        "terbatas saat crash."),
    tingkat="tinggi",
)

register(
    "moneyness",
    kesimpulan=(
        "Distribusi moneyness & premium menunjukkan di mana likuiditas & aktivitas "
        "terkonsentrasi — biasanya dekat ATM. Pemahaman ini menentukan pilihan "
        "strike yang dapat dieksekusi tanpa slippage besar."),
    rekomendasi=[
        "Pilih strike dekat ATM untuk likuiditas terbaik; hindari strike sangat "
        "OTM yang tipis (sulit keluar).",
        "Sesuaikan strategi dengan distribusi: bila aktivitas terkonsentrasi, "
        "ikut likuiditas, jangan melawan.",
        "Waspadai premium mahal di strike populer (permintaan tinggi).",
    ],
    risiko=(
        "Berniaga di strike tidak likuid berarti slippage besar & sulit keluar — "
        "keuntungan teori menguap dalam eksekusi."),
    tingkat="sedang",
)

register(
    "pcr",
    kesimpulan=(
        "Put/Call Ratio mengukur rasio volume put vs call. PCR tinggi = banyak "
        "beli perlindungan (pesimis); PCR rendah = banyak taruhan naik (optimis). "
        "PCR sering dipakai sebagai indikator kontrarian."),
    rekomendasi=[
        "PCR ekstrem (sangat tinggi/rendah) sering menandai titik balik — "
        "pertimbangkan sebagai sinyal kontrarian dengan konfirmasi lain.",
        "Jangan pakai PCR sendirian; gabungkan dengan skew & GEX untuk gambaran utuh.",
        "Bedakan volume (sentimen harian) dari open interest (posisi mengendap).",
    ],
    risiko=(
        "Menganggap PCR sebagai sinyal arah langsung berbahaya — ia mengukur "
        "AKTIVITAS, bukan arah pasti. Trader yang salah membaca bisa terjebak "
        "di titik balik yang salah."),
    tingkat="tinggi",
)

register(
    "gex",
    kesimpulan=(
        "Gamma Exposure (GEX) menunjukkan konsentrasi gamma dealer. GEX positif "
        "cenderung meredam volatilitas (dealer hedging stabilkan harga); GEX "
        "negatif cenderung memperkuat gerakan (volatilitas melebar)."),
    rekomendasi=[
        "Dalam rezim GEX positif, harga cenderung mean-reverting → strategi "
        "range/jual volatilitas lebih cocok.",
        "Dalam rezim GEX negatif, gerakan cenderung ekstrem → kurangi risiko arah, "
        "pertimbangkan beli volatilitas.",
        "Pantau level GEX sebagai zona support/resistance yang mungkin bertahan.",
    ],
    risiko=(
        "Mengabaikan rezim GEX berarti salah memilih strategi: menjual volatilitas "
        "di rezim negatif dapat berujung kerugian besar saat harga bergerak ekstrem."),
    tingkat="tinggi",
)

register(
    "oi_walls",
    kesimpulan=(
        "Open-Interest Walls menandai strike dengan OI besar — sering bertindak "
        "sebagai magnet atau tembok harga saat mendekati expiry (pinning effect)."),
    rekomendasi=[
        "Perlakukan OI wall sebagai level support/resistance kandidat saat expiry.",
        "Hindari posisi arah yang melawan tembok OI besar tanpa katalis kuat.",
        "Waspadai pergeseran OI menjelang expiry (posisi bergeser = level berubah).",
    ],
    risiko=(
        "Memasuki posisi melawan tembok OI besar bisa terjebak konsolidasi "
        "berkepanjangan (harga dipin) yang menguras nilai waktu opsi."),
    tingkat="sedang",
)

register(
    "liquidity",
    kesimpulan=(
        "Liquidity map mengidentifikasi kontrak dengan volume & OI tinggi. "
        "Likuiditas adalah pembeda antara teori & eksekusi nyata — kontrak tak "
        "likuid berarti biaya transaksi tersembunyi."),
    rekomendasi=[
        "Batasi trading pada kontrak likuid (volume/OI memadai); ukur dampaknya "
        "pada slippage.",
        "Untuk posisi besar, pecah menjadi beberapa eksekusi di kontrak likuid.",
        "Gunakan likuiditas sebagai filter WAJIB sebelum memilih strategi.",
    ],
    risiko=(
        "Strategi sempurna di atas kertas bisa merugi hanya karena slippage & "
        "spread di kontrak tak likuid. Biaya eksekusi mengonsumsi seluruh edge."),
    tingkat="tinggi",
)

register(
    "spread_quality",
    kesimpulan=(
        "Kualitas bid-ask spread (relatif premium) menentukan biaya masuk-keluar. "
        "Spread lebar menggerus keuntungan sejak transaksi pertama; spread sempit "
        "memungkinkan strategi frekuensi lebih tinggi."),
    rekomendasi=[
        "Ukur biaya round-trip (masuk+keluar) sebelum menilai profitabilitas — "
        "spread adalah biaya nyata.",
        "Prioritaskan kontrak dengan spread quality baik untuk strategi aktif.",
        "Untuk spread lebar, gunakan pesanan limit (bukan market) untuk menekan biaya.",
    ],
    risiko=(
        "Mengabaikan spread membuat backtest tampak menguntungkan tapi rugi di "
        "realitas. Biaya tersembunyi ini adalah pembunuh diam-diam paling umum "
        "di trading opsi."),
    tingkat="tinggi",
)

register(
    "totals",
    kesimpulan=(
        "Total volume per moneyness menunjukkan di mana minat pasar terkonsentrasi "
        "— mengungkap apakah aktivitas dominan spekulatif (OTM jauh) atau "
        "institutional (ATM/near-OTM)."),
    rekomendasi=[
        "Konsentrasi di OTM jauh mengindikasikan spekulasi/lotre; waspadai "
        "pergerakan impulsif.",
        "Konsentrasi dekat ATM menandakan aktivitas institutional; harga lebih "
        "terinformasi & stabil.",
        "Gunakan pola ini untuk menyesuaikan ekspektasi volatilitas.",
    ],
    risiko=(
        "Membaca salah sifat aliran (spekulatif vs institutional) membuat "
        "ekspektasi volatilitas keliru. Respons yang salah terhadap sinyal bisa "
        "memperbesar kerugian."),
    tingkat="sedang",
)

register(
    "vol_by_moneyness",
    kesimpulan=(
        "Volume & IV per strike memetakan di mana premi tinggi & aktivitas besar. "
        "Kombinasi keduanya sering menandai zona kepentingan pasar yang paling "
        "diperhatikan."),
    rekomendasi=[
        "Fokuskan analisis pada strike-volume tinggi: di situ informasi & "
        "likuiditas bertemu.",
        "Strike dengan IV tinggi + volume besar = ekspektasi pergerakan dari "
        "pelaku besar.",
        "Hindari menebak di strike sepi (volume kecil).",
    ],
    risiko=(
        "Mengambil posisi di zona sepi tanpa sinyal berarti bertaruh pada "
        "kebetulan. Pasar yang tidak aktif sering bergerak tidak terduga."),
    tingkat="sedang",
)


# --- Decision engine: keputusan terukur (skor + tier + justifikasi) ---
register(
    "decision",
    kesimpulan=(
        "Selain narasi, sistem kini menghasilkan SKOR KEPUTUSAN numerik per item "
        "(anomali/negara/ticker/metrik) berbasis sinyal berbobot, lalu memetakan "
        "ke TIER AKSI via ambang. Keputusan dapat dibandingkan & diurutkan."),
    rekomendasi=[
        "Jalankan item dengan tier prioritas tertinggi lebih dulu.",
        "Sesuaikan bobot sinyal & ambang tier di config sesuai kebijakan organisasi.",
        "Audit tiap keputusan lewat skor & justifikasi terukurnya.",
    ],
    risiko=(
        "Keputusan tanpa skor terukur cenderung subjektif & tidak konsisten. "
        "Namun skor pun bisa salah bila formulasi sinyal keliru — karena itu "
        "setiap keputusan menyertakan justifikasi yang dapat diaudit."),
    tingkat="tinggi",
)


# --------------------------------------------------------------------------
# Chart ECharts (v2) — insight & rekomendasi.
# --------------------------------------------------------------------------

register(
    "echarts_boxplot",
    kesimpulan=(
        "Boxplot IV per bucket moneyness menampilkan MEDIAN, SEBARAN, dan "
        "PENCILAN. Bila kotak di kedua sayap (Deep ITM/Deep OTM) lebih tinggi "
        "dari ATM, itu tanda VOLATILITY SMILE klasik: pasar membayar premi lebih "
        "untuk strike ekstrem (lindung nilai & spekulasi). Sebaran lebar = "
        "penetapan harga opsi tidak merata (likuiditas tidak merata)."),
    rekomendasi=[
        "Untuk penjual opsi (premium seller), sayap dengan IV tinggi menawarkan "
        "premi menarik — tetapi pahami risiko ekor yang menyertainya.",
        "Untuk pembeli proteksi, sadari Anda membayar 'smile premium'; "
        "bandingkan instrumen lindung nilai alternatif.",
        "Waspadai bucket dengan sebaran sangat lebar: harga antar-kontrak tidak "
        "konsisten, tanda likuiditas tipis.",
    ],
    risiko=(
        "Membaca satu nilai IV tanpa melihat sebaran menyembunyikan bahwa strike "
        "tertentu jauh lebih mahal dari yang tampak. Keputusan hedging/spekulasi "
        "berbasis angka tunggal bisa salah harga. Edukasional, bukan saran investasi."),
    tingkat="sedang",
)

register(
    "echarts_graph",
    kesimpulan=(
        "Graph memetakan hubungan ticker↔strike berdasarkan open interest. "
        "Simpul ticker besar yang terhubung ke banyak strike menandakan posisi "
        "terkonsentrasi; strike yang muncul di BANYAK ticker menandakan level "
        "harga 'bersama' (mis. angka psikologis / level indeks) tempat posisi "
        "menumpuk. Ini mengungkap struktur posisi, bukan sekadar volume."),
    rekomendasi=[
        "Tandai strike yang terhubung ke banyak ticker sebagai level kunci — "
        "potensi magnet harga / dinding dukungan-resistensi.",
        "Untuk ticker dengan konsentrasi OI ekstrem pada satu strike, waspadai "
        "pergerakan tajam bila level itu ditembus (pemicu gamma).",
        "Pantau perubahan jaringan antar-waktu; pergeseran simpul pusat = "
        "pergeseran fokus pasar.",
    ],
    risiko=(
        "Open interest dari sumber gratis (Yahoo) sering tidak lengkap/0, "
        "sehingga jaringan bisa bias. Menyimpulkan posisi institusi dari data "
        "tak lengkap berisiko keliru. Edukasional, bukan saran investasi."),
    tingkat="tinggi",
)
