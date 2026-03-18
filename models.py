class Algoritm:
    def __init__(self, id_algoritm, nume, tip):
        self.id = id_algoritm
        self.nume = nume
        self.tip = tip

class Cheie:
    def __init__(self, id_cheie, valoare_cheie, lungime_biti, iv, id_algoritm):
        self.id = id_cheie
        self.valoare_cheie = valoare_cheie
        self.lungime_biti = lungime_biti
        self.iv = iv
        self.id_algoritm = id_algoritm

class Fisier:
    def __init__(self, id_fisier, nume, path, hash_original, stare, id_cheie_activa):
        self.id = id_fisier
        self.nume = nume
        self.path = path
        self.hash_original = hash_original
        self.stare = stare
        self.id_cheie_activa = id_cheie_activa

class Performanta:
    def __init__(self, id_test, id_fisier, framework, time_ms, memorie_mb, data_test):
        self.id = id_test
        self.id_fisier = id_fisier
        self.framework = framework
        self.time_ms = time_ms
        self.memorie_mb = memorie_mb
        self.data_test = data_test