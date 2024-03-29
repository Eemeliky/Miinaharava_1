"""
Miinaharava - yksinkertainen miinaharava peli.

@author: Eemeli Kyröläinen, student, Oulun yliopisto 2023

Peli toimii valmiiksi annetun haravasto kirjaston avulla. Pelissä on kolme vaikeustaso (helppo, normaali, vaikea).
Lisäksi voit luoda oman mukautetun pelin halutuilla dimensioilla ja miinojen määrällä. Peli tallentaa voitot/häviöt ja
niihin liittyvät statistiikan.
"""

import random
import haravasto
import time
import json
from datetime import datetime

pelidata = {
    "kentta": [],
    "kansi": [],
    "tyhjat": [],
    "aika": 0.0,
    "vuorot": 0,
    "ruutu": (0, 0),  # Viimeisin klikattu ruutu (x,y)
    "lopputulos": ""
}

asetukset = {
    "pelaaja_nimi": "Aasi",
    "vaikeustaso": "",
    "kentan_leveys": 0,
    "kentan_korkeus": 0,
    "ikkunan_leveys": 0,
    "ikkunan_korkeus": 0,
    "miinat": 0
}

# Vaikeustasot: [leveys, korkeus, miinojen määrä]
HELPPO = [9, 9, 10]
NORMAALI = [16, 16, 40]
VAIKEA = [30, 16, 99]

# Ruutujen arvoja kentällä/kannella
AVATTU = 1
AVAAMATON = 0
LIPPU = 9
MIINA = -1

LOPPU = ["häviö", "voitto", "lopetus"]  # Mahdolliset pelin lopputilanteet
SPRITE_SIVU = 40  # Vakio spriten koko (40x40)px
MINMAX = (2, 101)  # Pelikentän (minimi, maksimi) koko raja-arvot
# Suositeltu maksimi kentän koko 1920x1080 näytölle on 47x26 ruutua


def numeroi():
    """
    Laskee jokaisen miinoittamattoman ruudun arvon sen vieressä olevien miinojen mukaan.
    """
    kentta = pelidata["kentta"]
    y_raja = len(kentta) - 1
    x_raja = len(kentta[0]) - 1

    for y in range(len(kentta)):
        for x in range(len(kentta[0])):
            if kentta[y][x] == MIINA:
                continue

            # ylös
            if y > 0 and kentta[y - 1][x] == MIINA:
                kentta[y][x] += 1

            # alas
            if y < y_raja and kentta[y + 1][x] == MIINA:
                kentta[y][x] += 1

            # vasen
            if x > 0 and kentta[y][x - 1] == MIINA:
                kentta[y][x] += 1

            # oikea
            if x < x_raja and kentta[y][x + 1] == MIINA:
                kentta[y][x] += 1

            # vasen ylä
            if y > 0 and x > 0 and kentta[y - 1][x - 1] == MIINA:
                kentta[y][x] += 1

            # oikea ylä
            if y > 0 and x < x_raja and kentta[y - 1][x + 1] == MIINA:
                kentta[y][x] += 1

            # vasen ala
            if y < y_raja and x > 0 and kentta[y + 1][x - 1] == MIINA:
                kentta[y][x] += 1

            # oikea ala
            if y < y_raja and x < x_raja and kentta[y + 1][x + 1] == MIINA:
                kentta[y][x] += 1


def luo_kentta():
    """
    Asettaa pelidata arvot vakioiksi,
    luo kentän ja kannen (kaksiuloitteienen lista, jonka kaikki arvot = 0).
    Lisäksi luo listan, jossa on kaikki kentän ruutujen koordinaatti parit muodossa (x,y).
    """
    pelidata["vuorot"] = 0
    pelidata["lopputulos"] = LOPPU[2]
    pelidata["ruutu"] = (0, 0)

    kentta, kansi, tyhjat_ruudut = ([] for _ in range(3))

    for y in range(asetukset["kentan_korkeus"]):
        kentta.append([])
        kansi.append([])
        for x in range(asetukset["kentan_leveys"]):
            kentta[-1].append(0)
            kansi[-1].append(0)
            tyhjat_ruudut.append((x, y))

    pelidata["kentta"] = kentta
    pelidata["kansi"] = kansi
    pelidata["tyhjat"] = tyhjat_ruudut


def luo_turva_alue(aloitus_x, aloitus_y):
    """
    Poistaa pelin aloitus ruudun mahdollisista miinoille sallituista paikoista
    ja luo 3x3 turva-alueen tämän ruudun ympärille, jos mahdollista.
    :param aloitus_x: Pelin aloitus ruudun x koordinaatti
    :param aloitus_y: Pelin aloitus ruudun y koordinaatti
    :return: Listan, joka sisältää koordinaatti parit aloitus ruudun ympärillä olevista ruuduista
    """
    pelidata["tyhjat"].remove((aloitus_x, aloitus_y))
    turva_alue = []

    for k_pari in pelidata["tyhjat"]:
        x, y = k_pari

        # vasen ylä
        if x == aloitus_x - 1 and y == aloitus_y - 1:
            turva_alue.append((x, y))

        # ylös
        elif x == aloitus_x and y == aloitus_y - 1:
            turva_alue.append((x, y))

        # oikea ylä
        elif x == aloitus_x + 1 and y == aloitus_y - 1:
            turva_alue.append((x, y))

        # vasen
        elif x == aloitus_x - 1 and y == aloitus_y:
            turva_alue.append((x, y))

        # oikea
        elif x == aloitus_x + 1 and y == aloitus_y:
            turva_alue.append((x, y))

        # vasen ala
        elif x == aloitus_x - 1 and y == aloitus_y + 1:
            turva_alue.append((x, y))

        # alas
        elif x == aloitus_x and y == aloitus_y + 1:
            turva_alue.append((x, y))

        # oikea ala
        elif x == aloitus_x + 1 and y == aloitus_y + 1:
            turva_alue.append((x, y))

    for ruutu in turva_alue:
        pelidata["tyhjat"].remove(ruutu)

    return turva_alue


def miinoita(turva_alue):
    """
    Asettaa kentälle asetukset["miinat"] arvon verran miinoja satunnaisiin paikkoihin.
    :param turva_alue: 3x3 alue, jonne miinat asetetaan viimeisenä
    """
    luku = 0

    while luku < asetukset["miinat"]:
        if not pelidata["tyhjat"]:
            x, y = turva_alue.pop()
            pelidata["kentta"][y][x] = MIINA
        else:
            idx = random.randint(0, len(pelidata["tyhjat"]) - 1)
            x, y = pelidata["tyhjat"].pop(idx)
            pelidata["kentta"][y][x] = MIINA
        luku += 1

    pelidata["tyhjat"] = []


def piirra_kentta():
    """
    Käsittelijäfunktio, joka piirtää kaksiulotteisena listana kuvatun miinakentän
    ruudut näkyviin peli-ikkunaan. Funktiota kutsutaan aina, kun pelimoottori pyytää
    ruudun näkymän päivitystä.
    """
    haravasto.tyhjaa_ikkuna()
    haravasto.piirra_tausta()
    haravasto.aloita_ruutujen_piirto()

    for y, rivi in enumerate(pelidata['kentta']):
        for x, asia in enumerate(rivi):
            ruutu_x = x * SPRITE_SIVU
            ruutu_y = asetukset["ikkunan_korkeus"] - (SPRITE_SIVU * (y + 1))

            if pelidata['kansi'][y][x] == LIPPU:
                haravasto.lisaa_piirrettava_ruutu('f', ruutu_x, ruutu_y)

            elif pelidata['kansi'][y][x] == AVATTU:
                if asia == MIINA:
                    haravasto.lisaa_piirrettava_ruutu('x', ruutu_x, ruutu_y)
                else:
                    haravasto.lisaa_piirrettava_ruutu(str(asia), ruutu_x, ruutu_y)
            else:
                haravasto.lisaa_piirrettava_ruutu(" ", ruutu_x, ruutu_y)

    if pelidata["lopputulos"] == LOPPU[0]:
        # tarkistaa, että punainen miina löytyy haravastosta
        if "xr" in haravasto.grafiikka["kuvat"]:
            ruutu_x = pelidata["ruutu"][0] * SPRITE_SIVU
            ruutu_y = asetukset["ikkunan_korkeus"] - (SPRITE_SIVU * (pelidata["ruutu"][1] + 1))
            haravasto.lisaa_piirrettava_ruutu('xr', ruutu_x, ruutu_y)

    haravasto.piirra_ruudut()


def tulvataytto(aloitus_x, aloitus_y):
    """
    Avaa 'floodfill'-algoritmilla klikatun ruudun viereiset ruudut, jos ne ovat tyhjiä.
    :param aloitus_x: klikatun ruudun x-arvo
    :param aloitus_y: klikatun ruudun y-arvo
    """
    kentta = pelidata["kentta"]
    kansi = pelidata["kansi"]
    taytto_lista = [(aloitus_x, aloitus_y)]
    y_raja = len(kentta)
    x_raja = len(kentta[0])

    while taytto_lista:
        x, y = taytto_lista.pop()
        if kentta[y][x] != MIINA and kansi[y][x] == AVAAMATON:
            kansi[y][x] = 1
            if not kentta[y][x] > 0:

                # alas
                if y > 0 and kansi[y - 1][x] == AVAAMATON:
                    taytto_lista.append((x, y - 1))

                # ylös
                if y < y_raja - 1 and kansi[y + 1][x] == AVAAMATON:
                    taytto_lista.append((x, y + 1))

                # vasen
                if x > 0 and kansi[y][x - 1] == AVAAMATON:
                    taytto_lista.append((x - 1, y))

                # oikea
                if x < x_raja - 1 and kansi[y][x + 1] == AVAAMATON:
                    taytto_lista.append((x + 1, y))

                # vasen ala
                if y > 0 and x > 0 and kansi[y - 1][x - 1] == AVAAMATON:
                    taytto_lista.append((x - 1, y - 1))

                # oikea ala
                if y > 0 and x < x_raja - 1 and kansi[y - 1][x + 1] == AVAAMATON:
                    taytto_lista.append((x + 1, y - 1))

                # vasen ylä
                if y < y_raja - 1 and x > 0 and kansi[y + 1][x - 1] == AVAAMATON:
                    taytto_lista.append((x - 1, y + 1))

                # oikea ylä
                if y < y_raja - 1 and x < x_raja - 1 and kansi[y + 1][x + 1] == AVAAMATON:
                    taytto_lista.append((x + 1, y + 1))

    pelidata["vuorot"] += 1
    voitto_tarkistus()


def nayta_miinat():
    """
    Käy läpi kentän miinat ja asettaa ne näkyviksi. Kutsutaan vain 'häviö'-tilanteessa.
    """
    for y, rivi in enumerate(pelidata["kentta"]):
        for x, ruutu in enumerate(rivi):
            if ruutu == MIINA:
                pelidata["kansi"][y][x] = AVATTU

    pelidata["aika"] = round(time.time() - pelidata["aika"])
    pelidata["lopputulos"] = LOPPU[0]
    print("GAME OVER!")
    print("Klikkaa minne tahansa pelikentällä palataksesi päävalikkoon")


def voitto_tarkistus():
    """
    Käy läpi kentän miinat ja kannen, jos avaamattomat ruudut = miinojen lmk.
    --> lisää voittoajan pelidataan["aika"]
    """
    avaamattomat = 0
    for y, rivi in enumerate(pelidata["kansi"]):
        for x, ruutu in enumerate(rivi):
            if ruutu == AVAAMATON or ruutu == LIPPU:
                avaamattomat += 1

    if avaamattomat == asetukset["miinat"]:
        #  Muuttaa kentällä olevat avaamattomat ruudut lipuiksi
        for y, rivi in enumerate(pelidata["kansi"]):
            for x, ruutu in enumerate(rivi):
                if ruutu == AVAAMATON:
                    pelidata["kansi"][y][x] = LIPPU

        pelidata["aika"] = round(time.time() - pelidata["aika"])
        pelidata["lopputulos"] = LOPPU[1]
        print("VOITIT PELIN!!!")
        print("Klikkaa minne tahansa pelikentällä palataksesi päävalikkoon")


def liputus(x, y):
    """
    Lisää ruutuun lipun tai poistaa olemassa olevan lipun
    :param x: Klikatun ruudun x-indeksi
    :param y: Klikatun ruudun y-indeksi
    """
    if pelidata["kansi"][y][x] == AVAAMATON:
        pelidata["kansi"][y][x] = LIPPU

    elif pelidata["kansi"][y][x] == LIPPU:
        pelidata["kansi"][y][x] = AVAAMATON


def ruudun_avaus(x, y):
    """
    Tarkistaa ruudun avaukseen liittyvät tapaukset ja suorittaa siihen liittyvät toiminnot
    :param x: Klikatun ruudun x-indeksi
    :param y: Klikatun ruudun y-indeksi
    """
    pelidata["ruutu"] = (x, y)
    if pelidata["kansi"][y][x] != LIPPU:  # Tarkistetaan, että klikattu ruutu ei ole lippu

        if pelidata["kentta"][y][x] == MIINA:  # Jos klikattu ruutu on miina -> Game over
            nayta_miinat()

        else:
            if pelidata["tyhjat"]:  # Tarkistetaan onko klikkaus pelin aloitus
                turva_alue = luo_turva_alue(x, y)
                miinoita(turva_alue)
                numeroi()
                pelidata["aika"] = time.time()
            tulvataytto(x, y)


def kasittele_hiiri(x, y, tapahtuma, _):
    """
    Tätä funktiota kutsutaan, kun käyttäjä klikkaa sovellusikkunaa hiirellä.
    :param x: Klikkauksen x-koordinaatti peli-ikkunassa
    :param y: Klikkauksen y-koordinaatti peli-ikkunassa
    :param tapahtuma: hiiren nappi(vasen, oikea tai keski)
    :param _: käyttämätön muuttuja, muokkausnäppäimille
    """
    ruutu_x = x // SPRITE_SIVU
    ruutu_y = (asetukset["kentan_korkeus"] - 1) - (y // SPRITE_SIVU)

    if ruutu_x > -1 and ruutu_y > -1:  # Tarkistetaan, että klikkaus on pelikentällä,
        # koska on mahdollista klikata pelikentän ulkopuolelle, mutta sovellusikkunan sisälle

        if pelidata["lopputulos"] == LOPPU[1] or pelidata["lopputulos"] == LOPPU[0]:
            if tapahtuma == haravasto.HIIRI_VASEN:
                haravasto.lopeta()

        else:
            if tapahtuma == haravasto.HIIRI_VASEN:
                ruudun_avaus(ruutu_x, ruutu_y)

            elif tapahtuma == haravasto.HIIRI_OIKEA:
                liputus(ruutu_x, ruutu_y)


def aseta_vaikeustaso(vaikeustaso):
    """
    Asetetaan asetuksien parametrit annetun vaikeustason mukaan.
    :param vaikeustaso: lista [kentän leveys, kentän korkeus, miinojen lkm.]
    """
    asetukset["kentan_leveys"] = vaikeustaso[0]
    asetukset["kentan_korkeus"] = vaikeustaso[1]
    asetukset["miinat"] = vaikeustaso[2]
    asetukset["ikkunan_leveys"] = asetukset["kentan_leveys"] * SPRITE_SIVU
    asetukset["ikkunan_korkeus"] = asetukset["kentan_korkeus"] * SPRITE_SIVU


def tarkista_syote(teksti, rajat):
    """
    Tarkistaa että käyttäjän antama syöte on kelvollinen.
    :param teksti: kysytyn syötteen nimi/teksti
    :param rajat: kokonaisluku pari (min, max)
    :return: Palauttaa kelvollisen syötteen (kokoinaisluku)
    """
    while True:
        try:
            syote = int(input(f"Anna pelikentän {teksti}: "))
            if rajat[1] > syote > rajat[0]:
                break
            else:
                print(f"On oltava välillä ({rajat[0] + 1} - {rajat[1] - 1})")
        except ValueError:
            print("Täytyy olla kokonaisluku!")
        print()

    return syote


def luo_mukautettu_peli():
    """
    Luo vaikeustasolistan käyttäjän antamien syötteiden mukaan.
    """
    mukautettu = []
    leveys = tarkista_syote("leveys", MINMAX)
    korkeus = tarkista_syote("korkeus", MINMAX)
    mukautettu.append(leveys)
    mukautettu.append(korkeus)
    mukautettu.append(tarkista_syote("miinojen määrä", (0, leveys * korkeus)))
    aseta_vaikeustaso(mukautettu)


def parametrien_syotto():
    """
    Kysyy käyttältä nimen ja vaikeustason peliin ja tarkistaa käyttäjän antamat syötteet.
    """
    nimi = input("Anna pelaaja nimi: ")
    asetukset["pelaaja_nimi"] = nimi

    print()
    print("|  Vaikeustaso  | Kentän koko |  miinojen määrä |")
    print("_________________________________________________")
    print(f"|   Helppo(h)   |    ({HELPPO[0]}x{HELPPO[1]})    |    {HELPPO[2]} miinaa")
    print(f"|  Normaali(n)  |   ({NORMAALI[0]}x{NORMAALI[1]})   |    {NORMAALI[2]} miinaa")
    print(f"|   Vaikea(v)   |   ({VAIKEA[0]}x{VAIKEA[1]})   |    {VAIKEA[2]} miinaa")
    print("| Mukautettu(m) |    (NxN)    |    ?? miinaa")

    while True:
        valinta = input("Anna vaikeustaso: ").lower()

        if valinta == "h" or valinta == "helppo":
            asetukset["vaikeustaso"] = "helppo"
            aseta_vaikeustaso(HELPPO)
            break

        elif valinta == "n" or valinta == "normaali":
            asetukset["vaikeustaso"] = "normaali"
            aseta_vaikeustaso(NORMAALI)
            break

        elif valinta == "v" or valinta == "vaikea":
            asetukset["vaikeustaso"] = "vaikea"
            aseta_vaikeustaso(VAIKEA)
            break

        elif valinta == "m" or valinta == "mukautettu":
            asetukset["vaikeustaso"] = "mukautettu"
            luo_mukautettu_peli()
            break

        else:
            print("Virheellinen syöte!")
            print()
            continue

    for _ in range(3):
        print()


def tallenna_tulokset():
    """
    Tallentaa tulokset tiedostoon 'tulokset.json', tiedosto luodaan, jos sitä ei ole olemassa.
    """
    if pelidata["lopputulos"] == LOPPU[2]:
        if pelidata["vuorot"] > 0:
            pelidata["aika"] = round(time.time() - pelidata["aika"])
        else:
            pelidata["aika"] = 0

    paiva_aika = datetime.now().strftime("%d/%m/%Y %H:%M")
    data = {"tulokset": []}
    tulos = {"pvm": paiva_aika,
             "vaikeustaso": asetukset["vaikeustaso"],
             "nimi": asetukset["pelaaja_nimi"],
             "aika": pelidata["aika"],
             "leveys": asetukset["kentan_leveys"],
             "korkeus": asetukset["kentan_korkeus"],
             "miinat": asetukset["miinat"],
             "vuorot": pelidata["vuorot"],
             "lopputulos": pelidata["lopputulos"]
             }

    uusi_tiedosto = True
    try:
        with open("tulokset.json", "x") as _:
            data["tulokset"].append(tulos)
    except OSError:
        uusi_tiedosto = False

    with open("tulokset.json", "r+", encoding="utf-8") as tiedosto:
        if uusi_tiedosto:
            json.dump(data, tiedosto, ensure_ascii=False, indent=4)
        else:
            tiedosto_data = json.load(tiedosto)
            tiedosto_data["tulokset"].append(tulos)
            tiedosto.seek(0)
            json.dump(tiedosto_data, tiedosto, ensure_ascii=False, indent=4)


def t_sort(data):
    """
    Sorttaus-funktio, top-10 listojen järjestämiseen
    """
    return float(data["aika"])


def tulosta_taulukko(tulosdata, taso, kaikki=False):
    """
    Tulostaa halutun Top-10 listan tai kaikki mahdolliset tulokset tiedostosta 'tulokset.json'.
    :param tulosdata: dict, tulokset listassa
    :param taso: str, vaikeustaso
    :param kaikki: lippu kaikkien pelin tuloksien tulostukseen
    """
    print()

    if not kaikki:
        tuloslista = []
        for rivi in tulosdata:
            if rivi["lopputulos"] == LOPPU[1] and rivi["vaikeustaso"] == taso:
                tuloslista.append(rivi)
        tuloslista.sort(key=t_sort)

        print(f"| TOP-10 ({taso}) |")
        for num, tulos in enumerate(tuloslista):
            if num > 10:
                break
            aika_s = float(tulos["aika"])
            if aika_s > 86399:  # Maksimi aika valitulle tulostus formatille on 86399s(=23:59:59)
                aika_s = 86399
            aika = time.strftime("%H:%M:%S", time.gmtime(aika_s))
            print(f"{num + 1}. {tulos['nimi']} - {aika} ({tulos['pvm']})")

    else:
        print(f"| tulokset.json |")
        for tulos in tulosdata:
            aika_s = float(tulos["aika"])
            if aika_s > 86399:  # Maksimi aika valitulle tulostus formatille on 86399s(=23:59:59)
                aika_s = 86399
            aika = time.strftime("%H:%M:%S", time.gmtime(aika_s))
            print(f"({tulos['pvm']}) {tulos['nimi']} - {aika}, "
                  f"[{tulos['leveys']}x{tulos['korkeus']}:{tulos['miinat']}], "
                  f"vuorot:{tulos['vuorot']}, {tulos['lopputulos']}")


def tulosvalikko():
    """
    Valikko tallennettujen tulosten tulostukseen.
    """
    tiedosto = False

    try:
        with open("tulokset.json", "r", encoding="utf-8") as tiedosto:
            tiedosto_data = json.load(tiedosto)
            tiedosto = True
    except OSError:
        print("'tulokset.json' ei löydy!")
        print("Pelaa vähintään 1 peli ja yritä sitten uudestaan.")
        input("Paina ENTER palataksesi päävalikkoon...")

    if tiedosto:
        while True:
            print()
            print("| Tulosvalikko |")
            print("  - Tulosta kaikki(k)")
            print("  - Palaa päävalikkoon(b)")
            print("  | Top-10 list |")
            print("    - Helppo(h)")
            print("    - Normaali(n)")
            print("    - Vaikea(v)")

            valinta = input("Anna valinta: ").lower()

            if valinta == "b" or valinta == "palaa päävalikkoon":
                break

            elif valinta == "h" or valinta == "helppo":
                tulosta_taulukko(tiedosto_data["tulokset"], "helppo")

            elif valinta == "n" or valinta == "normaali":
                tulosta_taulukko(tiedosto_data["tulokset"], "normaali")

            elif valinta == "v" or valinta == "vaikea":
                tulosta_taulukko(tiedosto_data["tulokset"], "vaikea")

            elif valinta == "k" or valinta == "tulosta kaikki":
                tulosta_taulukko(tiedosto_data["tulokset"], "-", True)

            else:
                print("Virheellinen syöte!")


def paavalikko():
    """
    Pelin päävalikko. uusi peli: Kysyy käyttäjältä pelin parametrit, Lataa pelin grafiikat,
    luo peli-ikkunan ja asettaa siihen piirtokäsittelijän. tulostaulukko: avaa tulostaulukko valikon.
    lopeta: lopettaa pelin.
    """
    print("- - -Miinaharava- - -")
    print("")

    while True:
        print("| Päävalikko |")
        print("  - Uusi peli(u)")
        print("  - Tulostaulukko(t)")
        print("  - Lopeta(q)")
        valinta = input("Anna valinta: ").lower()

        if valinta == "q" or valinta == "lopeta":
            break

        elif valinta == "u" or valinta == "uusi peli":
            parametrien_syotto()
            luo_kentta()
            haravasto.lataa_kuvat("spritet")
            haravasto.luo_ikkuna(SPRITE_SIVU * asetukset["kentan_leveys"],
                                 SPRITE_SIVU * asetukset["kentan_korkeus"])
            haravasto.aseta_hiiri_kasittelija(kasittele_hiiri)
            haravasto.aseta_piirto_kasittelija(piirra_kentta)
            haravasto.aloita()
            tallenna_tulokset()

        elif valinta == "t" or valinta == "tulostaulukko":
            for _ in range(10):
                print()
            tulosvalikko()

        else:
            print("Virheellinen syöte!")
            print()
            continue

        for _ in range(10):
            print()


def main():
    paavalikko()


if __name__ == '__main__':
    main()
