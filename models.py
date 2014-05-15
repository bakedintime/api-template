import re
import pyodbc
import logging
import ConfigParser
import logging.handlers

class MSDriver():
    def __init__(self):
        # Initializes settings file.
        self.settings = ConfigParser.SafeConfigParser()
        self.settings.read('conf/settings.cfg')

        # Connects to mes***REMOVED***ges database.
        self.segurosDB = pyodbc.connect(
            'DSN=%s;UID=%s;PWD=%s;DATABASE=%s' % 
            (
                self.settings.get('SegurosDB', 'dsn'),
                self.settings.get('SegurosDB', 'uid'),
                self.settings.get('SegurosDB', 'pwd'),
                self.settings.get('SegurosDB', 'database')
            ), 
            autocommit=True
        )

        # Creates logging configuration.
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)
        # Assign handler to configure logger's format.
        handler = logging.handlers.RotatingFileHandler(
            self.settings.get('Logging','logpath'),
            maxBytes=self.settings.get('Logging','maxBytes'),
            backupCount=self.settings.get('Logging','backupCount')
        )
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(mes***REMOVED***ge)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def run_query(self, query, params=None, nonQuery=True):
        # TODO
        # support multiple statements with rollback functionality
        # This will be implemented on v1.2 of models module
        cursor = self.segurosDB.cursor()
        try:
            if params:
                # Check that equal number of parameter placeholders are given
                placeholders = [m.start() for m in re.finditer('\?',query)]
                if len(placeholders) == len(params):
                    if nonQuery:
                        cursor.execute(query, *params)
                        return True
                    else:
                        cursor.execute(query, *params)
                        rows = cursor.fetchall()
                        cursor.close()
                        return rows
                else:
                    raise Exception('Given unequal length of parameter placeholders and parameters to query.')
            else:
                if nonQuery:
                    cursor.execute(query)
                    return True
                else:
                    cursor.execute(query)
                    rows = cursor.fetchall()
                    cursor.close()
                    return rows
        except Exception, e:
            # Catch Integrity errors and other exceptions
            cursor.close()
            self.logger.debug('Exception while running query %s with params %s, %s' % (query, params, str(e)))
            return False

    def get_connection(self):
        return self.segurosDB.cursor()

    def get_response_mes***REMOVED***ge(self, state, motif):
        cursor = self.segurosDB.cursor()
        query = "exec %s ?, ?, ?" % self.settings.get('SegurosDB','getResponseMes***REMOVED***ge')
        self.logger.debug('Executing query %s with params: %s, %s, %s' %
            (query, state, motif, '1778')
        )
        cursor.execute(query, unicode(state).encode('utf8'), unicode(motif).encode('utf8'), '1778')
        row = cursor.fetchone()
        cursor.close()
        if row:
            try:
                self.logger.debug('Obtained mes***REMOVED***ge is %s' % (row[0].decode('utf8')))
                return row[0].decode('utf8')
            except Exception,e:
                # cp1252 encoding is used on windows version
                self.logger.debug('Decoding wasn\'t possible converting to unicode first. %s' % (str(e)))
                self.logger.debug('Obtained mes***REMOVED***ge is %s' % (row[0].decode('cp1252')))
                return row[0].decode('cp1252')
        else:
            return 'Este men***REMOVED***je no ha sido configurado'

    # Stored procedures

    def is_payment_enabled(self, telephone, fechaBloqueo, estaBloqueado):
        cursor = self.segurosDB.cursor()
        query = "exec %s ?, ?, ?" % (self.settings.get('SegurosDB','isPaymentEnabled'))
        self.logger.debug('Executing query %s with param: %s, %s, %s' % (query, telephone, fechaBloqueo, estaBloqueado))
        cursor.execute(
            query,
            unicode(telephone).encode('utf8'),
            unicode(fechaBloqueo).encode('utf8'),
            estaBloqueado
        )
        row = cursor.fetchone()
        cursor.close()
        if row:
            return row
        else:
            return None

    def is_blocked_IMEI(self, number):
        return False

    def exists_certificate(self, number, _type):
        cursor = self.segurosDB.cursor()
        try:
            query = "exec %s ?" % (self.settings.get('SegurosDB','getAllCertificates'))
            self.logger.debug('Executing query %s with param: %s' % (query, number))
            cursor.execute(
                query,
                unicode(number).encode('utf8'),
            )
            rows = cursor.fetchall()
            certificates = {}
            for row in rows:
                certificates[row[0]] = row[1]
            if _type in certificates:
                return True
            else:
                return False

        except Exception,e:
            self.logger.error(str(e), exc_info=True)
            return False
        finally:
            cursor.close()

    def change_number(self, imei, number):
        cursor = self.segurosDB.cursor()
        try:
            query = "exec %s ?, ?" % (self.settings.get('SegurosDB','changeNumber'))
            self.logger.debug('Executing query %s with param: %s, %s' % (query, imei, number))
            cursor.execute(
                query,
                unicode(imei).encode('utf8'),
                unicode(number).encode('utf8')
            )
            row = cursor.fetchone()
            if row:
                return row
            else:
                return None
        except Exception,e:
            self.logger.error(str(e), exc_info=True)
            return False
        finally:
            cursor.close()

    def claim_subscription(self, codigoReclamo):
        cursor = self.segurosDB.cursor()
        try:
            query = "exec %s ?" % (self.settings.get('SegurosDB','claimSubscription'))
            self.logger.debug('Executing query %s with param: %s' % (query, codigoReclamo))
            cursor.execute(
                query,
                unicode(codigoReclamo).encode('utf8')
            )
            row = cursor.fetchone()
            if row:
                return row
            else:
                return None
        except Exception,e:
            self.logger.error(str(e), exc_info=True)
            return False
        finally:
            cursor.close()