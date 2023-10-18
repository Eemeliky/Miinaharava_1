import random
import haravasto

peli_data = {
    "kentta": [],
    "kansi": [],
}


MIINAT = 3
KENTTA_LEVEYS = 15
KENTTA_KORKEUS = 10
SPRITE_SIVU = 40  # muuta jos käytät eri kokoisia spritejä (vakio 40x40px).
IKKUNAN_LEVEYS = SPRITE_SIVU * KENTTA_LEVEYS
IKKUNAN_KORKEUS = SPRITE_SIVU * KENTTA_KORKEUS


def numeroi():
    """
    Laskee jokaisen ruudun arvon sen vieressä olevien miinojen mukaan.
    """
    kentta = peli_data["kentta"]
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


def alusta_peli():
    """
    alustaa  tyhjän miina kentän
    :return:
    """
    kentta, kansi, tyhjat_ruudut = ([] for _ in range(3))

    for y in range(KENTTA_KORKEUS):
        kentta.append([])
        kansi.append([])
        for x in range(KENTTA_LEVEYS):
            kentta[-1].append(0)
            kansi[-1].append(0)
            tyhjat_ruudut.append((x, y))

    peli_data["kentta"] = kentta
    peli_data["kansi"] = kansi
    peli_data["tyhjat"] = tyhjat_ruudut


def luo_turva_alue(aloitus_x, aloitus_y):
    """
    Luo 3x3 turva-alueen aloitus kohdan ympärille, jos miinojen lkm. sallii sen
    :param aloitus_x: Pelin aloitus ruudun x koordinaatti
    :param aloitus_y: Pelin aloitus ruudun y koordinaatti
    :return: Listan, joka sisältää koordinaatti parit aloitus ruudun ympärillä olevista ruuduista
    """
    peli_data["tyhjat"].remove((aloitus_x, aloitus_y))
    turva_alue = []
    for k_pari in peli_data["tyhjat"]:
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
        peli_data["tyhjat"].remove(ruutu)

    return turva_alue


def miinoita(turva_alue):
    """
    Asettaa kentälle N kpl miinoja satunnaisiin paikkoihin.
    :param turva_alue:
    """

    luku = 0
    while luku < MIINAT:
        if not peli_data["tyhjat"]:
            break
        idx = random.randint(0, len(peli_data["tyhjat"]) - 1)
        x, y = peli_data["tyhjat"].pop(idx)
        peli_data["kentta"][y][x] = -1
        luku += 1


    peli_data["tyhjat"] = []


def piirra_kentta():
    """
    Käsittelijäfunktio, joka piirtää kaksiulotteisena listana kuvatun miinakentän
    ruudut näkyviin peli-ikkunaan. Funktiota kutsutaan aina kun pelimoottori pyytää
    ruudun näkymän päivitystä.
    """
    haravasto.tyhjaa_ikkuna()
    haravasto.piirra_tausta()
    haravasto.aloita_ruutujen_piirto()
    for y, rivi in enumerate(peli_data['kentta']):
        for x, asia in enumerate(rivi):
            if peli_data['kansi'][y][x] == 9:
                haravasto.lisaa_piirrettava_ruutu('f',
                                                  x * SPRITE_SIVU,
                                                  IKKUNAN_KORKEUS - (SPRITE_SIVU * (y + 1)))
            elif peli_data['kansi'][y][x] == 1:
                if asia == -1:
                    haravasto.lisaa_piirrettava_ruutu('x',
                                                      x * SPRITE_SIVU,
                                                      IKKUNAN_KORKEUS - (SPRITE_SIVU * (y + 1)))
                else:
                    haravasto.lisaa_piirrettava_ruutu(str(asia),
                                                      x * 40,
                                                      IKKUNAN_KORKEUS - (SPRITE_SIVU * (y + 1)))
            else:
                haravasto.lisaa_piirrettava_ruutu(" ",
                                                  x * 40,
                                                  IKKUNAN_KORKEUS - (SPRITE_SIVU * (y + 1)))

    if "game_over" in peli_data:
        if "xr" in haravasto.grafiikka["kuvat"]:
            haravasto.lisaa_piirrettava_ruutu('xr',
                                              peli_data["game_over"][0] * SPRITE_SIVU,
                                              IKKUNAN_KORKEUS - (SPRITE_SIVU * (peli_data["game_over"][1] + 1)))
    haravasto.piirra_ruudut()


def tulvataytto(aloitus_x, aloitus_y):
    """
    Merkitsee planeetalla olevat tuntemattomat alueet turvalliseksi siten, että
    täyttö aloitetaan annetusta x, y -pisteestä.
    """
    kentta = peli_data["kentta"]
    kansi = peli_data["kansi"]
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
    for y, rivi in enumerate(peli_data["kentta"]):
        for x, ruutu in enumerate(rivi):
            if ruutu == -1:
                peli_data["kansi"][y][x] = 1
    print("GAME OVER!")
    print("Klikkaa minne tahansa pelikentällä lopettaaksesi pelin")


def voitto_tarkistus():
    avaamattomat = 0
    for y, rivi in enumerate(peli_data["kansi"]):
        for x, ruutu in enumerate(rivi):
            if ruutu == 0 or ruutu == 9:
                avaamattomat += 1
    if avaamattomat == MIINAT:
        for y, rivi in enumerate(peli_data["kansi"]):
            for x, ruutu in enumerate(rivi):
                if ruutu == 0:
                    peli_data["kansi"][y][x] = 9
        peli_data["voitto"] = (0, 0)
        print("VOITIT PELIN!!!")
        print("Klikkaa minne tahansa pelikentällä lopettaaksesi pelin")


def kasittele_hiiri(x, y, tapahtuma, _):
    """
    Tätä funktiota kutsutaan kun käyttäjä klikkaa sovellusikkunaa hiirellä.
    Tulostaa hiiren sijainnin sekä painetun napin terminaaliin.
    """
    ruutu_x = x // SPRITE_SIVU
    ruutu_y = (KENTTA_KORKEUS - 1) - (y // SPRITE_SIVU)

    if "voitto" in peli_data:
        if tapahtuma == haravasto.HIIRI_VASEN:
            haravasto.lopeta()
    elif "game_over" in peli_data:
        if tapahtuma == haravasto.HIIRI_VASEN:
            haravasto.lopeta()

    else:
        if tapahtuma == haravasto.HIIRI_VASEN:
            if peli_data["kansi"][ruutu_y][ruutu_x] != 9:

                if peli_data["kentta"][ruutu_y][ruutu_x] == -1:
                    peli_data["game_over"] = (ruutu_x, ruutu_y)
                    nayta_miinat()
                else:
                    if peli_data["tyhjat"]:
                        turva_alue = luo_turva_alue(ruutu_x, ruutu_y)
                        miinoita(turva_alue)
                        numeroi()
                        tulvataytto(ruutu_x, ruutu_y)
                    else:
                        tulvataytto(ruutu_x, ruutu_y)

        elif tapahtuma == haravasto.HIIRI_OIKEA:

            if peli_data["kansi"][ruutu_y][ruutu_x] == 0:
                peli_data["kansi"][ruutu_y][ruutu_x] = 9

            elif peli_data["kansi"][ruutu_y][ruutu_x] == 9:
                peli_data["kansi"][ruutu_y][ruutu_x] = 0


def parametrien_syotto():
    if MIINAT > KENTTA_KORKEUS * KENTTA_LEVEYS - 1:
        print("ERROR! KENTÄLLÄ ON OLTAVA VÄHITÄÄN YKSI TYHJÄ RUUTU")
        return False
    return True


def main():
    """
    Lataa pelin grafiikat, luo peli-ikkunan ja asettaa siihen piirtokäsittelijän.
    """
    if parametrien_syotto():
        alusta_peli()
        haravasto.lataa_kuvat("spritet")
        haravasto.luo_ikkuna(IKKUNAN_LEVEYS, IKKUNAN_KORKEUS)
        haravasto.aseta_hiiri_kasittelija(kasittele_hiiri)
        haravasto.aseta_piirto_kasittelija(piirra_kentta)
        haravasto.aloita()


if __name__ == '__main__':
    main()
