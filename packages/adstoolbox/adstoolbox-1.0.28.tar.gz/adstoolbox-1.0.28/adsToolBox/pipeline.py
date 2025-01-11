from .timer import timer
from .logger import Logger
import polars as pl

class pipeline:
    def __init__(self, dictionnary: dict, logger: Logger):
        """
        Initialise un pipeline avec les informations de connexions aux bases de données
        :param dictionnary: le dictionnaire qui contient les informations du pipeline
            - 'db_source': la base de données source
            - 'query_source': la requête à envoyer à la source
            - 'tableau': les données sous forme de tableau (source alternative)
            - 'db_destination': la base de données destination
            - 'executemany' ou 'bulk'
            - 'batch_size': la taille des lots pour le traitement en batch
        :param logger: le logger pour gérer la journalisation des évènements du pipeline
        """
        self.logger = logger
        self.__db_source = dictionnary.get('db_source')
        self.__query_source = dictionnary.get('query_source')
        self.__tableau = dictionnary.get('tableau')
        self.db_destination = dictionnary.get('db_destination')
        self.mode = dictionnary.get("mode", "bulk")
        # self.checkup = dictionnary.get("checkup", False)
        self.__batch_size = dictionnary.get('batch_size', 10_000)
        self.db_destination.get('db').__batch_size = self.__batch_size
        if self.__db_source is not None:
            self.__db_source.__batch_size = self.__batch_size

    def _data_generator(self):
        """
        Générateur de données qui itère sur les données sources, qu'elles proviennent d'un tableau en mémoire
        ou d'une base de données, en les renvoyant sous forme de DataFrame par lots (batches).
        :return: Yield un DataFrame Polars contenant un batch de données.
        :raises ValueError: Si deux sources de données sont spécifiées (tableau et base de données)
        ou si aucune source de données valide n'est définie.
        """
        self.logger.info("Chargement des données depuis la source...")
        if self.__tableau is not None and self.__db_source is not None:
            msg = "Deux sources de données différentes sont définies, veuillez n'en choisir qu'une."
            self.logger.error(msg)
            raise ValueError(msg)
        if self.__tableau is not None and len(self.__tableau) > 0:
            for start in range(0, len(self.__tableau), self.__batch_size):
                batch = self.__tableau[start:start + self.__batch_size]
                try:
                    yield pl.DataFrame(batch, orient='row', strict=False, infer_schema_length=10_000)
                except Exception as e:
                    self.logger.error(f"Échec de la création du dataframe: {e}")
                    yield None, batch
        elif self.__db_source and self.__query_source:
            self.logger.disable()
            self.__db_source.connect()
            self.logger.enable()
            for batch in self.__db_source.sqlQuery(self.__query_source):
                try:
                    yield pl.DataFrame(batch, orient='row', strict=False, infer_schema_length=10_000)
                except Exception as e:
                    self.logger.error(f"Échec de la création du dataframe: {e}")
                    yield None, batch
        else:
            raise ValueError("Source de données non supportée.")

    @timer
    def run(self):
        """
        Exécute le pipeline en insérant des données depuis la source vers la destination définie.
        :return: Une liste des lots rejetés contenant les erreurs lors de l'insertion.
        :raises Exception: Si une erreur autre qu'une erreur d'insertion survient pendant l'exécution du pipeline
        """
        rejects = []
        res = {"nb_lines_success": 0, "nb_lines_error": 0, "errors": rejects}
        source_data = []
        try:
            self.logger.disable()
            self.db_destination['db'].connect()
            self.logger.enable()
            name = self.db_destination.get('name', 'bdd')
            self.logger.info(f"Connexion à {name} réussie.")
            for batch_df in self._data_generator():
                if isinstance(batch_df, tuple) and batch_df[0] is None:
                    rejects.append((name, "Échec création dataframe", batch_df[1]))
                    res["nb_lines_error"] += len(batch_df[1])
                else:
                    source_data.extend(batch_df.rows())
                    if self.mode == "bulk":
                        insert_result = self.db_destination.get("db").insertBulk(
                            table=self.db_destination.get('table'),
                            cols=self.db_destination.get('cols'),
                            schema=self.db_destination.get('schema'),
                            rows=batch_df.rows()
                        )
                    elif self.mode == "executemany":
                        insert_result = self.db_destination.get("db").insertMany(
                            table=self.db_destination.get("table"),
                            cols=self.db_destination.get('cols'),
                            rows=batch_df.rows()
                        )
                    else:
                        raise ValueError("Mode de pipeline non accepté: 'executemany' ou 'bulk'")
                    if insert_result[0] == "ERROR":
                        rejects.append((name, insert_result, batch_df.rows()))
                        res["nb_lines_error"] += len(batch_df)
                    else:
                        res["nb_lines_success"] += len(batch_df)
        except Exception as e:
            self.logger.enable()
            self.logger.error(f"Échec de l'exécution du pipeline: {e}")
            raise
        return res
