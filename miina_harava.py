"""
Miinaharava - yksinkertainen miinaharava peli.

@author: Eemeli Kyröläinen, Oulun yliopisto

Peli toimii valmiiksi annetun haravasto kirjaston avulla. Pelissä on kolme vaikeustaso (helppo, normaali, vaikea).
Lisäksi voit luoda oman mukautetun pelin halutuilla dimensioilla ja miinojen määrällä. Peli tallentaa [IMPLEMENT SAVES]
"""

import random
import haravasto
import time
from datetime import datetime

pelidata = {
    "kentta": [],
    "kansi": [],
    "tyhjat": [],
    "aloitus_aika": 0.0
}

asetukset = {
    "pelaaja_nimi": "P1",
    "vaikeustaso": "",
    "kentan_leveys": 0,
    "kentan_korkeus": 0,
    "ikkunan_leveys": 0,
    "ikkunan_korkeus": 0,
    "miinat": 0
}

# Vaikeus tasot: [leveys, korkeus, miinojen määrä]
HELPPO = [9, 9, 10]
NORMAALI = [16, 16, 40]
VAIKEA = [30, 16, 99]

SPRITE_SIVU = 40  # Vakio spriten koko (40x40)px


def numeroi():
    """
    Laskee jokaisen ruudun arvon sen vieressä olevien miinojen mukaan.
    """
    kentta = pelidata["kentta"]
    y_raja = len(kentta) - 1
    x_raja = len(kentta[0]) - 1

    for y in range(y_raja + 1):
        for x in range(x_raja + 1):
            if kentta[y][x] == -1:
                continue

            if y > 0 and kentta[y - 1][x] == -1:
                kentta[y][x] += 1

            if y < y_raja and kentta[y + 1][x] == -1:
                kentta[y][x] += 1

            if x > 0 and kentta[y][x - 1] == -1:
                kentta[y][x] += 1

            if x < x_raja and kentta[y][x + 1] == -1:
                kentta[y][x] += 1

            if y > 0 and x > 0 and kentta[y - 1][x - 1] == -1:
                kentta[y][x] += 1

            if y > 0 and x < x_raja and kentta[y - 1][x + 1] == -1:
                kentta[y][x] += 1

            if y < y_raja and x > 0 and kentta[y + 1][x - 1] == -1:
                kentta[y][x] += 1

            if y < y_raja and x < x_raja and kentta[y + 1][x + 1] == -1:
                kentta[y][x] += 1


def luo_kentta():
    """
    alustaa  tyhjän miina kentän
    :return:
    """
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
    Luo 3x3 turva-alueen aloitus kohdan ympärille, jos miinojen lkm. sallii sen
    :param aloitus_x: Pelin aloitus ruudun x koordinaatti
    :param aloitus_y: Pelin aloitus ruudun y koordinaatti
    :return: Listan, joka sisältää koordinaatti parit aloitus ruudun ympärillä olevista ruuduista
    """
    pelidata["tyhjat"].remove((aloitus_x, aloitus_y))
    turva_alue = []
    for k_pari in pelidata["tyhjat"]:
        x, y = k_pari

        # vas ylä
        if x == aloitus_x - 1 and y == aloitus_y - 1:
            turva_alue.append((x, y))

        # ylös
        elif x == aloitus_x and y == aloitus_y - 1:
            turva_alue.append((x, y))

        # oikea ylä
        elif x == aloitus_x + 1 and y == aloitus_y - 1:
            turva_alue.append((x, y))

        # vas
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
    Asettaa kentälle N kpl miinoja satunnaisiin paikkoihin.
    :param turva_alue:
    """

    luku = 0
    while luku < asetukset["miinat"]:
        if not pelidata["tyhjat"]:
            x, y = turva_alue.pop()
            pelidata["kentta"][y][x] = -1
        else:
            idx = random.randint(0, len(pelidata["tyhjat"]) - 1)
            x, y = pelidata["tyhjat"].pop(idx)
            pelidata["kentta"][y][x] = -1
        luku += 1

    pelidata["tyhjat"] = []


def piirra_kentta():
    """
    Käsittelijäfunktio, joka piirtää kaksiulotteisena listana kuvatun miinakentän
    ruudut näkyviin peli-ikkunaan. Funktiota kutsutaan aina kun pelimoottori pyytää
    ruudun näkymän päivitystä.
    """
    haravasto.tyhjaa_ikkuna()
    haravasto.piirra_tausta()
    haravasto.aloita_ruutujen_piirto()
    for y, rivi in enumerate(pelidata['kentta']):
        for x, asia in enumerate(rivi):
            if pelidata['kansi'][y][x] == 9:
                haravasto.lisaa_piirrettava_ruutu('f',
                                                  x * SPRITE_SIVU,
                                                  asetukset["ikkunan_korkeus"] - (SPRITE_SIVU * (y + 1)))
            elif pelidata['kansi'][y][x] == 1:
                if asia == -1:
                    haravasto.lisaa_piirrettava_ruutu('x',
                                                      x * SPRITE_SIVU,
                                                      asetukset["ikkunan_korkeus"] - (SPRITE_SIVU * (y + 1)))
                else:
                    haravasto.lisaa_piirrettava_ruutu(str(asia),
                                                      x * 40,
                                                      asetukset["ikkunan_korkeus"] - (SPRITE_SIVU * (y + 1)))
            else:
                haravasto.lisaa_piirrettava_ruutu(" ",
                                                  x * 40,
                                                  asetukset["ikkunan_korkeus"] - (SPRITE_SIVU * (y + 1)))

    if "game_over" in pelidata:
        if "xr" in haravasto.grafiikka["kuvat"]:
            haravasto.lisaa_piirrettava_ruutu('xr',
                                              pelidata["game_over"][0] * SPRITE_SIVU,
                                              asetukset["ikkunan_korkeus"] -
                                              (SPRITE_SIVU * (pelidata["game_over"][1] + 1)))
    haravasto.piirra_ruudut()


def tulvataytto(aloitus_x, aloitus_y):
    """
    Merkitsee planeetalla olevat tuntemattomat alueet turvalliseksi siten, että
    täyttö aloitetaan annetusta x, y -pisteestä.
    """
    kentta = pelidata["kentta"]
    kansi = pelidata["kansi"]
    fill_list = [(aloitus_x, aloitus_y)]
    y_raja = len(kentta)
    x_raja = len(kentta[0])
    while len(fill_list) > 0:
        x, y = fill_list.pop()
        if kentta[y][x] != -1 and kansi[y][x] == 0:
            kansi[y][x] = 1
            if not kentta[y][x] > 0:
                # tarkistetaan alas
                if y > 0 and kansi[y - 1][x] == 0:
                    fill_list.append((x, y - 1))

                # tarkistetaan ylös
                if y < y_raja - 1 and kansi[y + 1][x] == 0:
                    fill_list.append((x, y + 1))

                # tarkistetaan vasen
                if x > 0 and kansi[y][x - 1] == 0:
                    fill_list.append((x - 1, y))

                # tarkistetaan oikea
                if x < x_raja - 1 and kansi[y][x + 1] == 0:
                    fill_list.append((x + 1, y))

                # tarkistetaan vasen ala
                if y > 0 and x > 0 and kansi[y - 1][x - 1] == 0:
                    fill_list.append((x - 1, y - 1))

                # tarkistetaan oikea ala
                if y > 0 and x < x_raja - 1 and kansi[y - 1][x + 1] == 0:
                    fill_list.append((x + 1, y - 1))

                # tarkistetaan vasen ylä
                if y < y_raja - 1 and x > 0 and kansi[y + 1][x - 1] == 0:
                    fill_list.append((x - 1, y + 1))

                # tarkistetaan oikea ylä
                if y < y_raja - 1 and x < x_raja - 1 and kansi[y + 1][x + 1] == 0:
                    fill_list.append((x + 1, y + 1))

    voitto_tarkistus()


def nayta_miinat():
    for y, rivi in enumerate(pelidata["kentta"]):
        for x, ruutu in enumerate(rivi):
            if ruutu == -1:
                pelidata["kansi"][y][x] = 1
    print("GAME OVER!")
    print("Klikkaa minne tahansa pelikentällä lopettaaksesi pelin")


def voitto_tarkistus():
    avaamattomat = 0
    for y, rivi in enumerate(pelidata["kansi"]):
        for x, ruutu in enumerate(rivi):
            if ruutu == 0 or ruutu == 9:
                avaamattomat += 1
    if avaamattomat == asetukset["miinat"]:
        for y, rivi in enumerate(pelidata["kansi"]):
            for x, ruutu in enumerate(rivi):
                if ruutu == 0:
                    pelidata["kansi"][y][x] = 9
        pelidata["voitto"] = (0, 0)
        print("VOITIT PELIN!!!")
        print("Klikkaa minne tahansa pelikentällä lopettaaksesi pelin")


def kasittele_hiiri(x, y, tapahtuma, _):
    """
    Tätä funktiota kutsutaan kun käyttäjä klikkaa sovellusikkunaa hiirellä.
    Tulostaa hiiren sijainnin sekä painetun napin terminaaliin.
    """
    ruutu_x = x // SPRITE_SIVU
    ruutu_y = (asetukset["kentan_korkeus"] - 1) - (y // SPRITE_SIVU)

    if "voitto" in pelidata:
        if tapahtuma == haravasto.HIIRI_VASEN:
            haravasto.lopeta()
    elif "game_over" in pelidata:
        if tapahtuma == haravasto.HIIRI_VASEN:
            haravasto.lopeta()

    else:
        if tapahtuma == haravasto.HIIRI_VASEN:
            if pelidata["kansi"][ruutu_y][ruutu_x] != 9:

                if pelidata["kentta"][ruutu_y][ruutu_x] == -1:
                    pelidata["game_over"] = (ruutu_x, ruutu_y)
                    nayta_miinat()
                else:
                    if pelidata["tyhjat"]:
                        turva_alue = luo_turva_alue(ruutu_x, ruutu_y)
                        miinoita(turva_alue)
                        numeroi()
                        tulvataytto(ruutu_x, ruutu_y)
                        pelidata["aloitus_aika"] = time.time()
                    else:
                        tulvataytto(ruutu_x, ruutu_y)

        elif tapahtuma == haravasto.HIIRI_OIKEA:

            if pelidata["kansi"][ruutu_y][ruutu_x] == 0:
                pelidata["kansi"][ruutu_y][ruutu_x] = 9

            elif pelidata["kansi"][ruutu_y][ruutu_x] == 9:
                pelidata["kansi"][ruutu_y][ruutu_x] = 0


def aseta_vaikeustaso(vaikeustaso):
    asetukset["kentan_leveys"] = vaikeustaso[0]
    asetukset["kentan_korkeus"] = vaikeustaso[1]
    asetukset["miinat"] = vaikeustaso[2]
    asetukset["ikkunan_leveys"] = asetukset["kentan_leveys"] * SPRITE_SIVU
    asetukset["ikkunan_korkeus"] = asetukset["kentan_korkeus"] * SPRITE_SIVU


def tarkista_syote(teksti, rajat):
    """
    Tarkistaa että käyttäjän antama syote on kelvollinen (kokonaisluku)
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

    return syote


def luo_mukautettu_peli():
    mukautettu = []
    leveys = tarkista_syote("leveys", (1, 101))
    korkeus = tarkista_syote("korkeus", (1, 101))
    mukautettu.append(leveys)
    mukautettu.append(korkeus)
    mukautettu.append(tarkista_syote("miinojen määrä", (0, leveys * korkeus)))
    aseta_vaikeustaso(mukautettu)


def parametrien_syotto():
    while True:
        nimi = input("Anna pelaaja nimi: ")
        if "|" in nimi:
            print("'|' ei ole kelvollinen merkki pelaaja nimessä")
            # rikkoo tulosten tallennuksen, koska se käyttää |-merkkiä jakamaan tulokset
        else:
            asetukset["pelaaja_nimi"] = nimi
            break

    print("Vaikeustasot, Kentän koko, miinojen määrä:")
    print(f"Helppo(h) = {HELPPO[0]}x{HELPPO[1]}, {HELPPO[2]} miinaa")
    print(f"Normaali(n) = {NORMAALI[0]}x{NORMAALI[1]}, {NORMAALI[2]} miinaa")
    print(f"Vaikea(v) = {VAIKEA[0]}x{VAIKEA[1]}, {VAIKEA[2]} miinaa")
    print("Mukautettu(m) = NxN, ? miinaa")

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


def tallenna_tulokset():
    if "voitto" in pelidata:
        paiva_aika = datetime.now().strftime("%d/%m/%Y %H:%M")
        aika = time.strftime("%H:%M:%S", time.gmtime(time.time() - pelidata["aloitus_aika"]))
        with open("tulokset.txt", "a+") as tulokset:
            tulos_lista = [paiva_aika,
                           asetukset["vaikeustaso"],
                           asetukset["pelaaja_nimi"],
                           aika,
                           str(asetukset["kentan_leveys"]),
                           str(asetukset["kentan_korkeus"]),
                           str(asetukset["miinat"])]
            tulos_rivi = "|".join(tulos_lista) + "\n"
            tulokset.write(tulos_rivi)


def main():
    """
    Kysyy käyttäjältä pelin parametrit, Lataa pelin grafiikat, luo peli-ikkunan ja asettaa siihen piirtokäsittelijän.
    """
    parametrien_syotto()
    luo_kentta()
    haravasto.lataa_kuvat("spritet")
    haravasto.luo_ikkuna(SPRITE_SIVU * asetukset["kentan_leveys"],
                         SPRITE_SIVU * asetukset["kentan_korkeus"])
    haravasto.aseta_hiiri_kasittelija(kasittele_hiiri)
    haravasto.aseta_piirto_kasittelija(piirra_kentta)
    haravasto.aloita()
    tallenna_tulokset()


if __name__ == '__main__':
    main()
