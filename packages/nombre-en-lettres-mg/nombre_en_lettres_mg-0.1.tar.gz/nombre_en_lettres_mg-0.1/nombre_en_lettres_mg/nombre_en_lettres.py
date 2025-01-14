def nombre_en_lettres(num):
    # définitions des mots
    unités = ["", "iray", "roa", "telo", "efatra", "dimy", "enina", "fito", "valo", "sivy"]
    adolescents = ["folo", "iraika ambin'ny folo", "roa ambin'ny folo", "telo ambin'ny folo",
                   "efatra ambin'ny folo", "dimy ambin'ny folo", "enina ambin'ny folo",
                   "fito ambin'ny folo", "valo ambin'ny folo", "sivy ambin'ny folo"]
    dizaines = ["", "", "roapolo", "telopolo", "efapolo", "dimampolo",
                "enimpolo", "fitopolo", "valopolo", "sivifolo"]
    centaines = ["", "zato", "roanjato", "telonjato", "efa-jato",
                 "dimanjato", "eninjato", "fitonjato", "valonjato", "sivinjato"]
    milliers = ["", "arivo", "roa arivo", "telo arivo", "efatra arivo",
                "dimy arivo", "enina arivo", "fito arivo", "valo arivo", "sivy arivo"]
    dizaines_de_milliers = ["", "iray alina", "roa alina", "telo alina", "efatra alina",
                            "dimy alina", "enina alina", "fito alina", "valo alina", "sivy alina"]
    centaines_de_milliers = ["", "iray hetsy", "roa hetsy", "telo hetsy", "efatra hetsy",
                             "dimy hetsy", "enina hetsy", "fito hetsy", "valo hetsy", "sivy hetsy"]

    # cas spéciaux pour 0 et 1
    if num == 0:
        return "aotra"
    if num == 1:
        return "iray"

    # fonctions auxiliaires
    def traiter_dizaines(n, utilise_iray):
        if n < 10:
            return "iraika" if n == 1 and not utilise_iray else unités[n]
        elif n < 20:
            return adolescents[n - 10]
        elif n % 10 == 0:
            return dizaines[n // 10]
        else:
            unité = "iraika" if n % 10 == 1 and not utilise_iray else unités[n % 10]
            return f"{unité} amby {dizaines[n // 10]}"

    def traiter_centaines(n, utilise_iray):
        if n <= 99:
            return traiter_dizaines(n, utilise_iray)
        elif n <= 199:
            reste = n % 100
            return "zato" if reste == 0 else f"{traiter_dizaines(reste, utilise_iray)} amby zato"
        else:
            centaine = n // 100
            reste = n % 100
            utilise_iray = reste == 1
            unité = traiter_dizaines(reste, utilise_iray)
            return centaines[centaine] if reste == 0 else f"{unité} sy {centaines[centaine]}"

    def traiter_milliers(n, utilise_iray):
        if n <= 999:
            return traiter_centaines(n, utilise_iray)
        else:
            millier = n // 1000
            reste = n % 1000
            utilise_iray = reste == 1
            if reste == 0:
                return milliers[millier]
            elif reste <= 99:
                return f"{traiter_dizaines(reste, utilise_iray)} sy {milliers[millier]}"
            else:
                return f"{traiter_centaines(reste, utilise_iray)} sy {milliers[millier]}"

    def traiter_dizaines_de_milliers(n, utilise_iray):
        if n <= 9999:
            return traiter_milliers(n, utilise_iray)
        else:
            dizaine_de_milliers = n // 10000
            reste = n % 10000
            utilise_iray = reste == 1
            if reste == 0:
                return dizaines_de_milliers[dizaine_de_milliers]
            elif reste <= 999:
                return f"{traiter_centaines(reste, utilise_iray)} sy {dizaines_de_milliers[dizaine_de_milliers]}"
            else:
                return f"{traiter_milliers(reste, utilise_iray)} sy {dizaines_de_milliers[dizaine_de_milliers]}"

    def traiter_centaines_de_milliers(n, utilise_iray):
        if n <= 99999:
            return traiter_dizaines_de_milliers(n, utilise_iray)
        else:
            centaine_de_milliers = n // 100000
            reste = n % 100000
            utilise_iray = reste == 1
            if reste == 0:
                return centaines_de_milliers[centaine_de_milliers]
            elif reste <= 9999:
                return f"{traiter_milliers(reste, utilise_iray)} sy {centaines_de_milliers[centaine_de_milliers]}"
            else:
                return f"{traiter_dizaines_de_milliers(reste, utilise_iray)} sy {centaines_de_milliers[centaine_de_milliers]}"

    def traiter_millions(n, utilise_iray):
        if n <= 999999:
            return traiter_centaines_de_milliers(n, utilise_iray)
        else:
            million = n // 1000000
            reste = n % 1000000
            utilise_iray = reste == 1
            if reste == 0:
                return f"{nombre_en_lettres(million)} tapitrisa"
            else:
                return f"{traiter_centaines_de_milliers(reste, utilise_iray)} sy {nombre_en_lettres(million)} tapitrisa"

    def traiter_milliards(n, utilise_iray):
        if n <= 999999999:
            return traiter_millions(n, utilise_iray)
        else:
            milliard = n // 1000000000
            reste = n % 1000000000
            utilise_iray = reste == 1
            if reste == 0:
                return f"{nombre_en_lettres(milliard)} lavitrisa"
            else:
                return f"{traiter_millions(reste, utilise_iray)} sy {nombre_en_lettres(milliard)} lavitrisa"

    # gestion principale
    return traiter_milliards(num, utilise_iray=False)


# entrée utilisateur avec gestion des virgules ou des points
def convertir(nombre):
    num = nombre.replace(".", ",")
    try:
        # Séparer la partie entière et la partie décimale
        if ',' in num:
            entier, decimale = num.split(',')
            entier = int(entier.replace(",", ""))
            decimale = int(decimale)
            return f"{nombre_en_lettres(entier)} faingo {nombre_en_lettres(decimale)}"
        else:
            num = int(num.replace(",", ""))
            return nombre_en_lettres(num)
    except ValueError:
        return "Veuillez entrer un nombre valide."