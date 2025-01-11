import pytds
import pymssql
import timeit
import polars as pl
from .timer import timer, get_timer
from .dataFactory import data_factory

class dbMssql(data_factory):
    def __init__(self, dictionnary: dict, logger, batch_size=10_000):
        """
        instancie la classe dbMssql, qui hérite de dataFactory
        :param dictionnary: Un dictionnaire contenant tous les paramètres nécéssaires pour lancer une connexion sql server
        :param logger: un logger ads qui va gérer les logs des actions de la classe
        :param batch_size: la taille des batchs en lecture et écriture
        :param package: le package à utiliser ('pymssql' qui gère les connexion encryptées mais qui encode mal des
            caractères spéciaux en bulk ou alors 'pytds' qui est moins permissif et ne gère pas les connexion encryptées
            mais n'encode pas mal les caractères spéciaux
        """
        self.connection = None
        self.logger = logger
        self.__database = dictionnary.get('database')
        self.__user = dictionnary.get('user')
        self.__password = dictionnary.get('password')
        self.__port = dictionnary.get('port')
        self.__host = dictionnary.get('host')
        self.__charset = dictionnary.get('charset', 'UTF-8')
        self.__batch_size = batch_size
        self.__package = dictionnary.get('package', 'pymssql')


    @timer
    def connect(self):
        """
        lance la connexion avec les identifiants passés à l'initialisation de la classe
        toutes les méthodes de la classe nécéssitent une connexion active
        :return: la connexion
        """
        if self.logger is not None: self.logger.info("Tentative de connexion avec la base de données.")
        try:
            if self.__package == 'pytds':
                self.connection = pytds.connect(
                    dsn=self.__host,
                    port=self.__port,
                    user=self.__user,
                    password=self.__password,
                    database=self.__database,
                    autocommit=False,
                )
                self.sqlExec("SET DATEFORMAT ymd;")
            elif self.__package == 'pymssql':
                server = f"{self.__host}:{self.__port}" if self.__port else self.__host
                self.connection = pymssql.connect(
                    server=server,
                    user=self.__user,
                    password=self.__password,
                    database=self.__database,
                    charset=self.__charset
                )
            if self.logger is not None: self.logger.info(f"Connexion établie avec la base de données via {self.__package}.")
            return self.connection
        except Exception as e:
            if self.logger is not None: self.logger.error(f"Échec de la connexion à la base de données: {e}")
            raise

    def sqlQuery(self, query):
        """
        lit la base de données avec la requête query
        :param query: la requête
        :return: les données lues avec yield
        """
        self.logger.debug(f"Exécution de la requête de lecture : {query}")
        try:
            timer_start = timeit.default_timer()
            cpt_rows = 0
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                #cols = [desc[0] for desc in cursor.description]
                self.logger.info("Requête exécutée avec succès, début de la lecture des résultats.")
                while True:
                    rows = cursor.fetchmany(self.__batch_size)
                    if not rows:
                        break
                    yield rows
                    cpt_rows+=len(rows)
                    self.logger.info(f"{cpt_rows} lignes lues.")
            if get_timer():
                elapsed_time = timeit.default_timer() - timer_start
                self.logger.info(f"Temps d'exécution de sqlQuery: {elapsed_time:.4f} secondes")
            return cpt_rows
        except Exception as e:
            self.logger.error(f"Échec de la lecture des données: {e}")
            raise

    @timer
    def sqlExec(self, query):
        """
        execute une requête sur la base de données, un create ou delete table par exemple
        :param query: la requête
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
        execute une requête et retourne le premier résultat
        :param query: la requête
        :return: le résultat de la requête
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchone()
                self.logger.info(f"Requête exécutée avec succès.")
                data = result[0] if result else None
                return data
        except Exception as e:
            self.logger.error(f"Échec de l'exécution de la requête: {e}")
            raise


    @timer
    def insert(self, table, cols, row):
        """
        insère des données dans la base de données
        :param table: nom de la table dans laquelle insérer
        :param cols: liste des colonnes dans lesquelles insérer
        :param row: liste des valeurs à insérer
        :return: le résultat de l'opération, l'erreur et la la ligne concernée en cas d'erreur
        """
        try:
            with self.connection.cursor() as cursor:
                placeholders = ", ".join(["%s"] * len(cols))
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
        similaire à insert classique, mais insère par batch de taille 'batch_size', avec executemany
        :param table: nom de la table dans laquelle insérer
        :param cols: liste des colonnes dans lesquelles insérer
        :param rows: liste des lignes à insérer
        :return: le résultat de l'opération, l'erreur et la le batch concerné en cas d'erreur
        """
        try:
            with self.connection.cursor() as cursor:
                placeholders = ", ".join(["%s"] * len(cols))
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
        similaire à insertMany, mais utilise bulk_copy, bien plus rapide
        :param schema: nom du schéma
        :param table: nom de la table dans laquelle insérer
        :param cols: liste des colonnes dans lesquelles insérer
        :param rows: liste des lignes à insérer
        :return: le résultat de l'opération, l'erreur et la le batch concerné en cas d'erreur
        """
        try:
            if isinstance(rows, list):
                df = pl.DataFrame(rows, orient='row', strict=False, infer_schema_length=10_000)
            elif isinstance(rows, pl.DataFrame):
                df = rows
            else:
                raise ValueError("Les données doivent être une liste de tuples ou un DataFrame Polars")
            data = [tuple(str(value) if value else None for value in row) for row in df.iter_rows(named=False)]
            with self.connection.cursor() as cursor:
                if self.__package == 'pytds':
                    table, schema = (s[1:-1] if '[' in s else s for s in (table, schema))
                    cursor.copy_to(
                        data=data,
                        table_or_view=table,
                        columns=cols,
                        schema=schema
                    )
                elif self.__package == 'pymssql':
                    cursor.execute(f"SELECT TOP 0 * FROM {schema}.{table}")
                    columns = [desc[0] for desc in cursor.description]
                    if all(isinstance(col, str) for col in cols):
                        col_ids = [columns.index(col)+1 for col in cols]
                    elif all(isinstance(col, int) for col in cols):
                        col_ids = cols
                    else:
                        raise ValueError("Les colonnes doivent être des chaînes de caractères.")
                    self.connection.bulk_copy(
                        table_name=f"{schema}.{table}",
                        elements=data,
                        column_ids=col_ids,
                        batch_size=self.__batch_size
                    )
                self.connection.commit()
            self.logger.info(f"{len(data)} ligne(s) insérée(s) avec succès dans la table {table}.")
            return ["SUCCESS"]
        except Exception as e:
            self.connection.rollback()
            error_msg = ""
            if "Type de colonne non valide du client bcp" in str(e):
                error_msg += (
                    "Il est possible qu'une contrainte existe dans la table de destination, "
                    "ce qui cause l'erreur. Il est recommandé d'utiliser une table sans "
                    "contraintes pour les destinations de pipeline. Un VARCHAR(MAX) peut aussi poser problème"
                )
            error_msg+=str(e)
            self.logger.error(f"Échec de l'insertion des données: {error_msg}")
            return "ERROR", str(e), rows