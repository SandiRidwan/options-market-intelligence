
# ---------------------------------------------------------------------------
# KONTEN INSIGHT — Options Market Intelligence
# Sudut pandang: trader opsi/analis derivatif yang membaca posisi pasar.
#
# Format rekomendasi KAYA (v2): setiap item = dict 4-field
#   {"aksi","langkah":[3 langkah konkret],"metrik","pemilik"}
# Konteks data: scan 41 ticker, ±469 kontrak CALL/PUT (yfinance);
# PCR berbasis VOLUME (open interest Yahoo sering 0).
# Edukasional, BUKAN saran investasi.
# ---------------------------------------------------------------------------
from insight import register

register(
    "iv_smile",
    kesimpulan=(
        "IV smile/skew menunjukkan volatilitas tersirat berbeda antar-strike: "
        "opsi jauh dari harga (OTM) umumnya lebih mahal. Skew negatif (put lebih "
        "mahal) menandakan pasar membayar premium untuk perlindungan turun."),
    rekomendasi=[
        {
            "aksi": "Panen premi di sayap put yang mahal (dengan manajemen risiko ketat)",
            "langkah": [
                "Dari tabel IV smile, urutkan strike per bucket moneyness dan tandai strike put yang IV-nya di atas MEDIAN IV kontrak sejenis.",
                "Bandingkan IV put sayap itu dengan IV ATM (delta ~0.5) untuk mengukur 'richness' premi put relatif.",
                "Hanya eksekusi jual put bila pandanganmu tidak sepessimis skew; kunci strike pada kontrak dengan volume tertinggi di bucket tersebut (likuid).",
            ],
            "metrik": "Selisih IV put sayap vs IV ATM (dalam poin IV) dan premium per kontrak; ambang richness ≥ 5 poin IV.",
            "pemilik": "Trader opsi / Manajer portofolio derivatif",
        },
        {
            "aksi": "Hindari membeli opsi OTM yang IV-nya sudah membengkak",
            "langkah": [
                "Filter kontrak OTM dengan IV di atas persentil 75 distribusi smile ticker tersebut.",
                "Hitung edge teoritis = (harga target - strike) - premi; tolak bila edge < premi setelah spread.",
                "Jika tetap perlu eksposur OTM, turunkan ke strike satu step lebih dekat ATM dengan spread lebih sempit.",
            ],
            "metrik": "Rasio edge/premi dan spread relatif (% dari mid); tolak bila keduanya tipis (<1x dan >5%).",
            "pemilik": "Trader opsi",
        },
        {
            "aksi": "Pantau PERUBAHAN skew sebagai sinyal sentimen, bukan levelnya",
            "langkah": [
                "Simpan snapshot IV smile harian per ticker (median IV + IV sayap).",
                "Hitung delta skew (IV sayap put - IV sayap call) 1 hari vs 5 hari.",
                "Perlakukan lonjakan delta skew sebagai sinyal rotasi; konfirmasi dengan PCR volume.",
            ],
            "metrik": "Perubahan delta skew (poin IV) harian dan 5-harian; sinyal bila bergerak >2 poin IV.",
            "pemilik": "Analis derivatif",
        },
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
        {
            "aksi": "Cari peluang di ticker ber-skew paling curam",
            "langkah": [
                "Hitung skew tiap ticker dari 41 ticker ter-scan sebagai (IV put OTM - IV call OTM) pada bucket moneyness yang sama.",
                "Peringkatkan ticker dari skew ter-tinggi (paling takut turun) ke rendah.",
                "Untuk kandidat teratas, cek apakah ekspektasi pasar terlihat berlebihan dengan membandingkan IV terhadap realised vol historis ticker.",
            ],
            "metrik": "Peringkat skew (poin IV) dan rasio IV/realised vol; kandidat bila rasio > 1.3.",
            "pemilik": "Analis derivatif",
        },
        {
            "aksi": "Diversifikasi agar tidak bertaruh pada satu arah skew seluruh portofolio",
            "langkah": [
                "Petakan eksposur skew tiap posisi ke kategori 'takut turun' / 'netral' / 'takut naik'.",
                "Batasi bobot total posisi pada satu kategori (mis. maks 40% dari modal opsi).",
                "Pasangkan ticker ber-skew curam dengan ticker netral untuk menyeimbangkan risiko arah.",
            ],
            "metrik": "Distribusi bobot eksposur per kategori skew (%) dan konsentrasi maksimum per kategori.",
            "pemilik": "Manajer risiko portofolio",
        },
        {
            "aksi": "Pantau pergeseran skew antar-ticker sebagai sinyal rotasi risiko",
            "langkah": [
                "Susun heatmap skew lintas 41 ticker dan simpan tiap hari.",
                "Deteksi ticker yang skew-nya berubah arah (curam→datar atau sebaliknya) melewati median lintas-aset.",
                "Tandai pergeseran itu sebagai kandidat rotasi eksposur, verifikasi dengan perubahan PCR volume.",
            ],
            "metrik": "Jumlah ticker yang berpindah kategori skew per sesi dan persentil skew lintas-aset.",
            "pemilik": "Analis derivatif",
        },
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
        {
            "aksi": "Jual put (panen premi) bila pandanganmu tidak sepessimis pasar",
            "langkah": [
                "Ukur selisih wing put vs wing call (IV put far-OTM - IV call far-OTM) per ticker.",
                "Saring ticker di mana wing put lebih tinggi signifikan dari wing call.",
                "Eksekusi jual put pada strike dengan volume tertinggi di wing tersebut, sertakan lindung nilai ekor (mis. beli put lebih jauh atau stop disiplin).",
            ],
            "metrik": "Selisih IV wing put-call (poin IV) dan rasio premi/risiko maksimum posisi; ambang selisih ≥ 5 poin IV.",
            "pemilik": "Trader opsi / Manajer portofolio derivatif",
        },
        {
            "aksi": "Gunakan pelebaran selisih call-put wing sebagai sinyal rotasi",
            "langkah": [
                "Lacak selisih wing call-put tiap ticker dari waktu ke waktu.",
                "Tandai pelebaran (call wing naik relatif put wing) sebagai tanda kekhawatiran sisi naik.",
                "Rotasi eksposur bertahap ke arah yang selisihnya melebar; konfirmasi dengan moneyness aktivitas volume.",
            ],
            "metrik": "Perubahan selisih wing call-put (poin IV) harian; sinyal bila melebar >2 poin IV.",
            "pemilik": "Analis derivatif",
        },
        {
            "aksi": "Jangan jual perlindungan tanpa lindung nilai risiko ekor",
            "langkah": [
                "Identifikasi strike ekor (deep OTM) dengan IV tinggi sebagai zona risiko crash.",
                "Alokasikan sebagian premi hasil jual put untuk membeli lindung nilai ekor (put jauh) atau opsi call sebagai hedge konveks.",
                "Tetapkan ukuran posisi sehingga kerugian skenario ekor tetap dalam batas toleransi (mis. ≤2% modal).",
            ],
            "metrik": "Rasio biaya hedge terhadap premi terkumpul (≤30%) dan kerugian skenario ekor (% modal).",
            "pemilik": "Manajer risiko portofolio",
        },
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
        {
            "aksi": "Pilih strike dekat ATM untuk likuiditas terbaik",
            "langkah": [
                "Dari distribusi moneyness, tandai bucket dengan volume & jumlah kontrak terbanyak (biasanya ATM/near-OTM).",
                "Hitung ITM share pada bucket itu untuk memastikan kedekatan dengan harga spot.",
                "Pilih strike di bucket tersebut; hindari strike deep OTM yang kontrak/volumenya tipis.",
            ],
            "metrik": "Volume per bucket moneyness dan ITM share; pilih bucket dengan volume tertinggi dan spread tersempit.",
            "pemilik": "Trader opsi",
        },
        {
            "aksi": "Ikuti likuiditas, jangan melawan distribusi aktivitas",
            "langkah": [
                "Bandingkan konsentrasi aktivitas (AT M vs sayap) per ticker.",
                "Bila aktivitas terkonsentrasi di satu zona, arahkan strategi ke zona itu alih-alih strike sepi.",
                "Sesuaikan ukuran posisi dengan kedalaman likuiditas zona terpilih.",
            ],
            "metrik": "Pangsa volume zona terpilih (% total kontrak) dan median bid-ask spread zona.",
            "pemilik": "Trader opsi",
        },
        {
            "aksi": "Waspadai premium mahal di strike populer",
            "langkah": [
                "Deteksi strike dengan volume tinggi tetapi premium/IV juga di atas median (permintaan tinggi).",
                "Bandingkan premi strike populer vs strike setara di bucket lain.",
                "Bila premi terlalu mahal, geser pemilihan ke strike alternatif dengan premium lebih wajar.",
            ],
            "metrik": "Premi & IV strike populer vs median bucket (poin IV / %); tolak bila >1.5x median.",
            "pemilik": "Analis derivatif",
        },
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
        {
            "aksi": "Perlakukan PCR ekstrem sebagai sinyal kontrarian (dengan konfirmasi)",
            "langkah": [
                "Hitung PCR berbasis VOLUME per ticker (open interest Yahoo sering 0, jadi volume lebih andal).",
                "Tandai PCR di luar persentil 10-90 riwayat ticker sebagai ekstrem.",
                "Konfirmasi arah dengan skew & GEX sebelum mengambil posisi kontrarian.",
            ],
            "metrik": "Persentil PCR volume (ekstrem = <10 atau >90) dan jumlah sinyal konfirmasi pendukung (skew/GEX).",
            "pemilik": "Analis derivatif",
        },
        {
            "aksi": "Jangan pakai PCR sendirian — gabungkan dengan skew & GEX",
            "langkah": [
                "Susun panel tiga sinyal: PCR volume, skew, dan rezim GEX tiap ticker.",
                "Cari titik di mana ketiganya searah (mis. PCR tinggi + skew curam + GEX negatif).",
                "Ambil keputusan hanya pada ticker dengan minimal dua sinyal konfirmasi.",
            ],
            "metrik": "Jumlah sinyal searah per ticker (target ≥2 dari 3) dan konsistensi antar-sesi.",
            "pemilik": "Trader opsi",
        },
        {
            "aksi": "Bedakan volume (sentimen harian) dari open interest (posisi mengendap)",
            "langkah": [
                "Bandingkan kolom volume vs open interest tiap kontrak.",
                "Utamakan PCR volume untuk sentimen harian karena OI gratis sering 0/tidak lengkap.",
                "Catat keterbatasan ini saat menarik kesimpulan posisi institusi.",
            ],
            "metrik": "Nisbah kelengkapan OI (% kontrak dengan OI > 0) sebagai penanda keandalan.",
            "pemilik": "Analis data / Kuant",
        },
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
        {
            "aksi": "Di rezim GEX positif, terapkan strategi range / jual volatilitas",
            "langkah": [
                "Hitung total GEX per ticker dan tandai tandanya (positif = meredam).",
                "Pilih strategi range (mis. iron condor / jual straddle) pada strike di dalam batas GEX.",
                "Batasi risiko pada break-even range dan siap keluar bila GEX berbalik negatif.",
            ],
            "metrik": "Level & tanda GEX serta lebar range break-even (poin harga); kelola bila GEX berbalik tanda.",
            "pemilik": "Trader opsi / Manajer portofolio derivatif",
        },
        {
            "aksi": "Di rezim GEX negatif, kurangi risiko arah & pertimbangkan beli volatilitas",
            "langkah": [
                "Deteksi ticker dengan GEX negatif (volatilitas cenderung melebar).",
                "Kurangi eksposur arah (directional) dan/atau beli straddle/strangle untuk menangkap gerakan.",
                "Gunakan strike dekat level GEX sebagai pemicu masuk-keluar.",
            ],
            "metrik": "Tanda GEX dan rasio beli-volatilitas vs eksposur arah (mis. ≥60% hedge konveks).",
            "pemilik": "Trader opsi",
        },
        {
            "aksi": "Pantau level GEX sebagai zona support/resistance yang mungkin bertahan",
            "langkah": [
                "Ekstrak strike dengan konsentrasi GEX terbesar per ticker.",
                "Tandai strike itu sebagai kandidat level support/resistance.",
                "Awasi apakah harga benar-benar tertahan di level itu; pakai sebagai filter entry.",
            ],
            "metrik": "Jarak harga terhadap level GEX terbesar (%) dan berapa kali level diuji.",
            "pemilik": "Analis derivatif",
        },
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
        {
            "aksi": "Perlakukan OI wall sebagai level support/resistance kandidat saat expiry",
            "langkah": [
                "Urutkan strike menurut OI dan tandai puncak-puncaknya sebagai OI wall.",
                "Catat jaraknya relatif harga spot dan waktu menuju expiry.",
                "Gunakan level itu sebagai acuan target/stop, bukan titik masuk buta.",
            ],
            "metrik": "OI per strike (relatif total) dan jarak level ke spot (%); valid bila OI wall >2x median strike.",
            "pemilik": "Analis derivatif",
        },
        {
            "aksi": "Hindari posisi arah yang melawan tembok OI besar tanpa katalis kuat",
            "langkah": [
                "Identifikasi OI wall terdekat di depan arah posisimu.",
                "Cek apakah ada katalis (berita/earnings) yang bisa menembusnya; bila tidak, kurangi ukuran posisi.",
                "Siapkan rencana keluar bila harga tertahan (pinning) menjelang expiry.",
            ],
            "metrik": "Rasio OI wall terhadap OI rata-rata strike dan ekspektasi waktu tinggal (hari) di level.",
            "pemilik": "Manajer risiko portofolio",
        },
        {
            "aksi": "Waspadai pergeseran OI menjelang expiry",
            "langkah": [
                "Bandingkan peta OI wall hari ini vs 3-5 hari lalu.",
                "Tandai wall yang bergeser strike atau mengecil.",
                "Perbarui level support/resistance dan sesuaikan posisi.",
            ],
            "metrik": "Perubahan OI puncak antar-sesi (%) dan arah pergeseran strike.",
            "pemilik": "Analis derivatif",
        },
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
        {
            "aksi": "Batasi trading pada kontrak likuid & ukur dampaknya pada slippage",
            "langkah": [
                "Filter kontrak dengan volume memadai dan median bid-ask spread sempit.",
                "Catat slippage aktual (harga eksekusi vs mid) pada eksekusi uji.",
                "Hindari kontrak di bawah ambang likuiditas yang telah kamu tetapkan.",
            ],
            "metrik": "Median bid-ask spread (% dari mid) dan slippage aktual (poin/tick) vs ambang toleransi.",
            "pemilik": "Trader opsi",
        },
        {
            "aksi": "Pecah posisi besar menjadi beberapa eksekusi di kontrak likuid",
            "langkah": [
                "Estimasi ukuran posisi vs volume harian kontrak.",
                "Bila posisi >10% volume harian, bagi menjadi beberapa tranche.",
                "Eksekusi tranche pada waktu berbeda untuk menekan dampak pasar.",
            ],
            "metrik": "Rasio ukuran posisi terhadap volume harian (%) dan slippage rata-rata per tranche.",
            "pemilik": "Eksekusi trading / Dealer opsi",
        },
        {
            "aksi": "Jadikan likuiditas filter WAJIB sebelum memilih strategi",
            "langkah": [
                "Tetapkan kriteria likuiditas minimum (volume, OI, spread) di config.",
                "Terapkan filter itu pada SEMUA kandidat strategi sebelum analisis lanjutan.",
                "Dokumentasikan kontrak yang gugur agar tidak dipertimbangkan ulang.",
            ],
            "metrik": "Jumlah kandidat lolos filter likuiditas dan median spread kandidat terpilih.",
            "pemilik": "Analis data / Kuant",
        },
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
        {
            "aksi": "Ukur biaya round-trip sebelum menilai profitabilitas",
            "langkah": [
                "Hitung spread relatif tiap kontrak sebagai % dari mid.",
                "Jumlahkan spread masuk + keluar untuk mendapatkan biaya round-trip.",
                "Kurangi edge teoritis dengan biaya round-trip; tolak strategi yang edge-nya habis.",
            ],
            "metrik": "Biaya round-trip (% dari mid) vs edge teoritis (%); syarat edge > 2x biaya.",
            "pemilik": "Trader opsi",
        },
        {
            "aksi": "Prioritaskan kontrak dengan spread quality baik untuk strategi aktif",
            "langkah": [
                "Peringkatkan kontrak menurut median bid-ask spread per bucket moneyness.",
                "Pilih strata spread tersempit untuk strategi frekuensi tinggi.",
                "Hindari kontrak dengan spread di atas persentil 75 untuk strategi aktif.",
            ],
            "metrik": "Median bid-ask spread per bucket dan persentil spread kontrak terpilih.",
            "pemilik": "Trader opsi",
        },
        {
            "aksi": "Untuk spread lebar, gunakan pesanan limit (bukan market)",
            "langkah": [
                "Identifikasi kontrak dengan spread lebar yang tetap ingin ditradingkan.",
                "Pasang limit order di dalam spread (mis. di tengah) alih-alih market order.",
                "Sesuaikan harga limit bertahap bila belum tereksekusi dalam batas waktu.",
            ],
            "metrik": "Selisih harga eksekusi vs mid (poin) dan rasio limit order yang terisi.",
            "pemilik": "Eksekusi trading / Dealer opsi",
        },
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
        {
            "aksi": "Waspadai konsentrasi di OTM jauh (indikasi spekulasi/lotre)",
            "langkah": [
                "Hitung pangsa volume pada bucket deep-OTM vs total volume.",
                "Bila deep-OTM dominan, tandai potensi pergerakan impulsif.",
                "Kurangi ukuran posisi arah dan waspadai volatility spike.",
            ],
            "metrik": "Pangsa volume deep-OTM (%) dan ekspektasi volatilitas harian (IV median bucket).",
            "pemilik": "Analis derivatif",
        },
        {
            "aksi": "Baca konsentrasi dekat ATM sebagai aktivitas institutional",
            "langkah": [
                "Bandingkan pangsa volume ATM/near-OTM vs sayap tiap ticker.",
                "Bila ATM dominan, asumsikan harga lebih terinformasi & stabil.",
                "Selaraskan ekspektasi volatilitas (cenderung lebih rendah) dengan temuan ini.",
            ],
            "metrik": "Pangsa volume ATM (%) dan penyimpangan IV terhadap median lintas-bucket.",
            "pemilik": "Analis derivatif",
        },
        {
            "aksi": "Sesuaikan ekspektasi volatilitas dengan pola konsentrasi",
            "langkah": [
                "Klasifikasikan tiap ticker: spekulatif (sayap) atau institutional (ATM).",
                "Petakan ekspektasi volatilitas per kelas berdasarkan pola itu.",
                "Kalibrasi ulang strategi (range vs beli volatilitas) sesuai kelas.",
            ],
            "metrik": "Persentase ticker per kelas konsentrasi dan akurasi ekspektasi volatilitas antar-sesi.",
            "pemilik": "Analis data / Kuant",
        },
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
        {
            "aksi": "Fokuskan analisis pada strike-volume tinggi",
            "langkah": [
                "Urutkan strike per ticker menurut volume dan tandai puncaknya.",
                "Periksa IV pada strike tersebut untuk melihat apakah premi juga tinggi.",
                "Pusatkan analisis & seleksi kontrak pada zona tersebut.",
            ],
            "metrik": "Volume strike terpilih (relatif total) dan IV-nya vs median bucket.",
            "pemilik": "Analis derivatif",
        },
        {
            "aksi": "Strike IV tinggi + volume besar = ekspektasi pelaku besar",
            "langkah": [
                "Deteksi irisan strike dengan IV di atas persentil 75 DAN volume di atas persentil 75.",
                "Tafsirkan irisan itu sebagai ekspektasi pergerakan dari pelaku besar.",
                "Gunakan zona ini untuk menyetel ekspektasi arah/volatilitas.",
            ],
            "metrik": "Jumlah strike pada irisan persentil tinggi dan kekuatan sinyal (IQR IV-nya).",
            "pemilik": "Analis derivatif",
        },
        {
            "aksi": "Hindari menebak di strike sepi (volume kecil)",
            "langkah": [
                "Saring keluar strike dengan volume di bawah persentil 25.",
                "Alihkan perhatian ke strike aktif terdekat bila ide muncul dari strike sepi.",
                "Catat strike sepi hanya sebagai konteks, bukan dasar transaksi.",
            ],
            "metrik": "Pangsa strike sepi yang dihindari (%) dan spread median strike aktif pengganti.",
            "pemilik": "Trader opsi",
        },
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
        {
            "aksi": "Jalankan item dengan tier prioritas tertinggi lebih dulu",
            "langkah": [
                "Urutkan item berdasarkan skor keputusan (tier A → tier terendah).",
                "Ambil item tier tertinggi dan tetapkan sebagai tugas berjalan.",
                "Turun ke tier berikutnya setelah tier atas selesai/ditutup.",
            ],
            "metrik": "Skor keputusan per item dan jumlah item tier tertinggi yang dieksekusi.",
            "pemilik": "Manajer portofolio derivatif",
        },
        {
            "aksi": "Sesuaikan bobot sinyal & ambang tier di config sesuai kebijakan organisasi",
            "langkah": [
                "Tinjau bobot sinyal & ambang tier yang berlaku di config.",
                "Kalibrasi terhadap toleransi risiko & tujuan organisasi.",
                "Dokumentasikan perubahan dan uji dampaknya pada keputusan historis.",
            ],
            "metrik": "Bobot & ambang tier yang dipakai dan perubahan distribusi tier sebelum/sesudah (%).",
            "pemilik": "Analis data / Kuant",
        },
        {
            "aksi": "Audit tiap keputusan lewat skor & justifikasi terukurnya",
            "langkah": [
                "Untuk tiap keputusan, periksa skor dan justifikasi yang menyertainya.",
                "Bandingkan keputusan dengan hasil nyata setelahnya.",
                "Perbarui formulasi sinyal bila ditemukan penyimpangan.",
            ],
            "metrik": "Tingkat kesesuaian keputusan vs hasil (%) dan frekuensi audit per periode.",
            "pemilik": "Manajer risiko portofolio",
        },
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
        {
            "aksi": "Untuk penjual opsi: panen premi di sayap IV tinggi (pahami risiko ekor)",
            "langkah": [
                "Baca boxplot: tandai bucket sayap (Deep ITM/Deep OTM) dengan median IV di atas ATM.",
                "Pilih strike di dalam bucket itu dengan spread tersempit.",
                "Ukur risiko ekor dan siapkan lindung nilai sebelum menjual.",
            ],
            "metrik": "Selisih median IV sayap vs ATM (poin IV) dan rasio premi terhadap risiko ekor.",
            "pemilik": "Trader opsi / Manajer portofolio derivatif",
        },
        {
            "aksi": "Untuk pembeli proteksi: sadari Anda membayar 'smile premium'",
            "langkah": [
                "Hitung premi lindung pada sayap vs alternatif (strike lebih dekat ATM).",
                "Bandingkan biaya lindung opsi dengan instrumen hedge lain.",
                "Pilih struktur hedge paling efisien biaya untuk profil risiko yang sama.",
            ],
            "metrik": "Biaya hedge (% premi) per struktur dan perlindungan efektif (poin strike yang dicover).",
            "pemilik": "Manajer risiko portofolio",
        },
        {
            "aksi": "Waspadai bucket dengan sebaran sangat lebar (likuiditas tipis)",
            "langkah": [
                "Identifikasi bucket dengan IQR IV terlebar pada boxplot.",
                "Periksa jumlah kontrak & spread pada bucket tersebut.",
                "Hindari atau kecilkan posisi di bucket ber-sebaran lebar itu.",
            ],
            "metrik": "IQR IV per bucket (poin IV) dan median bid-ask spread bucket; hindari bila spread >5% mid.",
            "pemilik": "Analis derivatif",
        },
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
        {
            "aksi": "Tandai strike yang terhubung ke banyak ticker sebagai level kunci",
            "langkah": [
                "Dari graph, hitung derajat koneksi tiap strike (berapa ticker terhubung).",
                "Tandai strike berderajat tinggi sebagai kandidat magnet harga / dinding.",
                "Pakai level itu sebagai acuan support/resistance bersama.",
            ],
            "metrik": "Derajat koneksi strike (jumlah ticker) dan jumlah strike dengan derajat di atas ambang.",
            "pemilik": "Analis derivatif",
        },
        {
            "aksi": "Untuk ticker dengan konsentrasi OI ekstrem pada satu strike, waspadai gerakan tajam",
            "langkah": [
                "Deteksi ticker yang hampir seluruh OI-nya menumpuk pada satu strike.",
                "Tandai strike itu sebagai pemicu gamma bila ditembus.",
                "Kurangi eksposur arah atau siapkan posisi konveks di sekitar level tersebut.",
            ],
            "metrik": "Pangsa OI pada strike dominan (%) dan jarak level ke spot (%); waspada bila >50%.",
            "pemilik": "Manajer risiko portofolio",
        },
        {
            "aksi": "Pantau perubahan jaringan antar-waktu (pergeseran simpul pusat)",
            "langkah": [
                "Simpan snapshot graph harian dan bandingkan struktur simpul pusat.",
                "Tandai strike/ticker yang berpindah menjadi pusat baru.",
                "Perbarui level kunci & fokus pasar sesuai pergeseran itu.",
            ],
            "metrik": "Perubahan derajat simpul pusat (%) dan jumlah simpul pusat baru per sesi.",
            "pemilik": "Analis data / Kuant",
        },
    ],
    risiko=(
        "Open interest dari sumber gratis (Yahoo) sering tidak lengkap/0, "
        "sehingga jaringan bisa bias. Menyimpulkan posisi institusi dari data "
        "tak lengkap berisiko keliru. Edukasional, bukan saran investasi."),
    tingkat="tinggi",
)
