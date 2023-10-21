import random
import haravasto

pelidata = {
    "kentta": [],
    "kansi": [],
    "miinat": 0,
    "kentan_leveys": 0,
    "kentan_korkeus": 0
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

            if y > 0 and kentta[y-1][x] == -1:
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

    for y in range(pelidata["kentan_korkeus"]):
        kentta.append([])
        kansi.append([])
        for x in range(pelidata["kentan_leveys"]):
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
    while luku < pelidata["miinat"]:
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
                                                  pelidata["kentan_korkeus"] - (SPRITE_SIVU * (y + 1)))
            elif pelidata['kansi'][y][x] == 1:
                if asia == -1:
                    haravasto.lisaa_piirrettava_ruutu('x',
                                                      x * SPRITE_SIVU,
                                                      pelidata["kentan_korkeus"] - (SPRITE_SIVU * (y + 1)))
                else:
                    haravasto.lisaa_piirrettava_ruutu(str(asia),
                                                      x * 40,
                                                      pelidata["kentan_korkeus"] - (SPRITE_SIVU * (y + 1)))
            else:
                haravasto.lisaa_piirrettava_ruutu(" ",
                                                  x * 40,
                                                  pelidata["kentan_korkeus"] - (SPRITE_SIVU * (y + 1)))

    if "game_over" in pelidata:
        if "xr" in haravasto.grafiikka["kuvat"]:
            haravasto.lisaa_piirrettava_ruutu('xr',
                                              pelidata["game_over"][0] * SPRITE_SIVU,
                                              pelidata["kentan_korkeus"] - (SPRITE_SIVU * (pelidata["game_over"][1]+1)))
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
    if avaamattomat == pelidata["miinat"]:
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
    ruutu_y = (pelidata["kentan_korkeus"] - 1) - (y // SPRITE_SIVU)

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
                    else:
                        tulvataytto(ruutu_x, ruutu_y)

        elif tapahtuma == haravasto.HIIRI_OIKEA:

            if pelidata["kansi"][ruutu_y][ruutu_x] == 0:
                pelidata["kansi"][ruutu_y][ruutu_x] = 9

            elif pelidata["kansi"][ruutu_y][ruutu_x] == 9:
                pelidata["kansi"][ruutu_y][ruutu_x] = 0


def aseta_vaikeustaso(vaikeustaso):
    pelidata["kentan_leveys"] = vaikeustaso[0]
    pelidata["kentan_korkeus"] = vaikeustaso[1]
    pelidata["miinat"] = vaikeustaso[2]


def luo_mukautettu_peli():
    while True:
        try:
            pelidata["kentan_leveys"] = int(input("Anna pelikentän leveys(max 100): "))
        except ValueError:
            print("Leveys täytyy olla kokonaisluku!")

        if 101 > pelidata["kentan_leveys"] > 0:
            break
        else:
            print("Leveys on oltava välillä (0 - 100)")

    while True:
        try:
            pelidata["kentan_korkeus"] = int(input("Anna pelikentän korkeus(max 100): "))
        except ValueError:
            print("Korkeus täytyy olla kokonaisluku!")

        if 101 > pelidata["kentan_korkeus"] > 0:
            break
        else:
            print("Korkeus on oltava välillä (0 - 100)")

    while True:
        try:
            pelidata["miinat"] = int(input("Anna miinojen määrä: "))
        except ValueError:
            print("Miinojen määrä on olta kokonaisluku!")

        if pelidata["kentan_leveys"] * pelidata["kentan_korkeus"] > pelidata["miinat"] >= 0:
            break
        else:
            print("Kentällä on oltava vähitään 1 tyhjä ruutu!")
            print("sallittu miinojen määrä (0 - {a})"
                  .format(a=pelidata["kentan_leveys"] * pelidata["kentan_korkeus"] - 1))


def parametrien_syotto():
    pelidata["pelaaja_nimi"] = input("Anna pelaaja nimi: ")

    print("Vaikeustasot, Kentän koko, miinojen määrä:")
    print(f"Helppo(h) = {HELPPO[0]}x{HELPPO[1]}, {HELPPO[2]} miinaa")
    print(f"Normaali(n) = {NORMAALI[0]}x{NORMAALI[1]}, {NORMAALI[2]} miinaa")
    print(f"Vaikea(v) = {VAIKEA[0]}x{VAIKEA[1]}, {VAIKEA[2]} miinaa")
    print("Mukautettu(m) = NxN, ? miinaa")

    while True:
        valinta = input("Anna vaikeustaso: ").lower()
        if valinta == "h" or valinta == "helppo":
            aseta_vaikeustaso(HELPPO)
            break
        elif valinta == "n" or valinta == "normaali":
            aseta_vaikeustaso(NORMAALI)
            break
        elif valinta == "v" or valinta == "vaikea":
            aseta_vaikeustaso(VAIKEA)
            break
        elif valinta == "m" or valinta == "mukautettu":
            luo_mukautettu_peli()
            break


def main():
    """
    Lataa pelin grafiikat, luo peli-ikkunan ja asettaa siihen piirtokäsittelijän.
    """
    parametrien_syotto()
    luo_kentta()
    haravasto.lataa_kuvat("spritet")
    haravasto.luo_ikkuna(SPRITE_SIVU * pelidata["kentan_leveys"],
                         SPRITE_SIVU * pelidata["kentan_korkeus"])
    haravasto.aseta_hiiri_kasittelija(kasittele_hiiri)
    haravasto.aseta_piirto_kasittelija(piirra_kentta)
    haravasto.aloita()


if __name__ == '__main__':
    main()
