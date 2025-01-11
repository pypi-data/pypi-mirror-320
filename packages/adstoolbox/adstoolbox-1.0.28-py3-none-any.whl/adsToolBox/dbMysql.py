import os
import mysql.connector
import timeit
import polars as pl
from adsToolBox.timer import timer, get_timer
from adsToolBox.dataFactory import data_factory

class dbMysql(data_factory):
    def __init__(self, dictionnary: dict, logger, batch_size=10_000):
        """
        instancie la classe dbMysql, qui hérite de dataFactory
        :param dictionnary: Un dictionnaire contenant tous les paramètres nécéssaires pour lancer une connexion MySQL
        :param logger: Un logger ads qui va gérer les logs des actions de la classe
        :param batch_size: La taille des batchs en lecture et écriture
        """
        self.connection = None
        self.logger = logger
        self.__database = dictionnary.get("database")
        self.__user = dictionnary.get("user")
        self.__password = dictionnary.get("password")
        self.__port = dictionnary.get("port")
        self.__host = dictionnary.get("host")
        self.__batch_size = batch_size

    def connect(self, additionnal_parameters=None):
        """
        Lance la connexion avec les identifiants passés à l'initialisation de la classe
        Toutes les méthodes de la classe nécéssitent une connexion active
        :return: La connexion
        """
        if self.logger is not None: self.logger.info("Tentative de connexion avec la base de données.")
        try:
            self.connection = mysql.connector.connect(**{
                'user': self.__user,
                'password': self.__password,
                'host': self.__host,
                'port': self.__port,
                'database': self.__database,
            })
            if additionnal_parameters:
                cursor = self.connection.cursor()
                for param, value in additionnal_parameters.items():
                    cursor.execute(f"SET SESSION {param} = {value}")
                self.connection.commit()
            if self.logger is not None: self.logger.info("Connexion établie avec la base de données.")
            return self.connection
        except Exception as e:
            if self.logger is not None: self.logger.error(f"Échec de la connexion à la base de données: {e}")
            raise

    def sqlQuery(self, query):
        """
        Lit la base de données avec la reqûete query
        :param query: La requête
        :return: Les données lues avec un yield
        """
        self.logger.debug(f"Exécution de la requête de lecture: {query}")
        try:
            timer_start = timeit.default_timer()
            cpt_rows = 0
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                self.logger.info("Requête exécutée avec succès, début de la lecture des résultats.")
                while True:
                    rows = cursor.fetchmany(self.__batch_size)
                    if not rows:
                        break
                    yield rows
                    cpt_rows += len(rows)
                    self.logger.info(f"{cpt_rows} ligne(s) lue(s).")
            if get_timer():
                elapsed_time = timeit.default_timer() - timer_start
                self.logger.info(f"Temps d'exécution de sqlQuery: {elapsed_time:.4f} secondes.")
            return cpt_rows
        except Exception as e:
            self.logger.error(f"Échec de la lecture des données: {e}")
            raise

    @timer
    def sqlExec(self, query):
        """
        Exécute une requête sur la base de données, un create ou delete table par exemple
        :param query: La requête en question
        :return:
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                self.connection.commit()
                self.logger.info(f"Requête exécutée avec succès.")
        except Exception as e:
            self.logger.error(f"Échec de l'exécution de la requête: {e}")
            raise

    @timer
    def sqlScalaire(self, query):
        """
        Exécute une requête et retourne le premier résultat
        :param query: La requête en question
        :return: Le résultat de cette requête
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchone()
                self.logger.info(f"Requête scalaire exécutée avec succès.")
                data = result[0] if result else None
                return data
        except Exception as e:
            self.logger.error(f"Échec de l'exécution de la requête: {e}")
            raise

    @timer
    def insert(self, table, cols, row):
        """
        Insère une ligne de données dans la base de données
        :param table: Nom de la table dans laquelle insérer
        :param cols: Liste des colonnes dans lesquelles insérer
        :param row: Liste des valeurs à insérer
        :return: Le résultat de l'opération
        """
        try:
            with self.connection.cursor() as cursor:
                placeholders = ', '.join(['%s'] * len(cols))
                query = f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({placeholders})"
                cursor.execute(query, row)
                self.connection.commit()
                self.logger.info(f"{len(row)} valeurs insérées avec succès dans la table {table}")
                return ["SUCCESS"]
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f"Échec de l'insertion des données: {e}")
            return "ERROR", str(e), row

    @timer
    def insertMany(self, table, cols, rows):
        """
        Similaire à un insert classique, mais insère par batch de taille 'batch_size', avec executemany
        :param table: Nom de la table dans laquelle insérer
        :param cols: Liste des colonnes dans lequelles insérer
        :param rows: Liste des lignes à insérer
        :return: Le résultat de l'opération, l'erreur et le batch concerné en cas d'erreur
        """
        try:
            with self.connection.cursor() as cursor:
                placeholders = ', '.join(["%s"] * len(cols))
                query = f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({placeholders})"
                cursor.executemany(query, rows)
                self.connection.commit()
                self.logger.info(f"{len(rows)} lignes insérées avec succès dans la table {table}.")
                return ["SUCCESS"]
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f"Échec de l'insertion des données: {e}")
            return "ERROR", str(e), rows

    @timer
    def insertBulk(self, schema, table, cols, rows):
        """
        Similaire à insertMany, mais utilise une insertion en bulk, bien plus rapide
        :param table: Nom de la table dans laquelle insérer
        :param cols: Liste des colonnes dans lesquelles insérer
        :param schema: Nom du schéma où se trouve la table
        :param rows: Liste des lignes à insérer
        :return: Le résultat de l'opération, l'erreur et le batch concerné en cas d'erreur
        """
        try:
            if isinstance(rows, list):
                df = pl.DataFrame(rows, orient='row', strict=False, infer_schema_length=10_000)
            elif isinstance(rows, pl.DataFrame):
                df = rows
            else:
                raise ValueError("Les données doivent être une liste de tuples ou un DataFrame Polars.")
            with self.connection.cursor() as cursor:
                table = f"{schema}.{table}" if schema else table
                n_rows = df.shape[0]
                temp_file = "temp_bulk_insert.csv"
                for i in range(0, n_rows, self.__batch_size):
                    batch = df.slice(i, self.__batch_size)
                    batch.write_csv(temp_file, include_header=False)
                    query = f"""
                    LOAD DATA LOCAL INFILE '{temp_file}'
                    INTO TABLE {table}
                    FIELDS TERMINATED BY ','
                    LINES TERMINATED BY '\n'
                    ({", ".join(cols)})
                    """
                    cursor.execute(query)
            self.connection.commit()
            self.logger.info(f"{n_rows} ligne(s) insérée(s) avec succès dans la table {table}.")
            os.remove(temp_file)
            return ["SUCCESS"]
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f"Échec de l'insertion des données: {e}")
            return "ERROR", str(e), rows
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)