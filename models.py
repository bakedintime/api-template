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

    def is_blacklisted(self, number):
        cursor = self.segurosDB.cursor()
        query = "exec %s ?" % (self.settings.get('SegurosDB','isBlacklisted'))
        self.logger.debug('Executing query %s with param: %s' % (query, number))
        cursor.execute(query, unicode(number).encode('utf8'))
        row = cursor.fetchone()
        cursor.close()
        if row and row[0] == 1:
            return True
        else:
            return False

    def is_user_already(self, identifier, _type, certificateType):
        cursor = self.segurosDB.cursor()
        query = "exec %s ?, ?, ?" % (self.settings.get('SegurosDB','isUserAlready'))
        self.logger.debug('Executing query %s with param: %s, %s, %s' % (query, identifier, _type, certificateType))
        cursor.execute(query, unicode(identifier).encode('utf8'), unicode(_type).encode('utf8'), unicode(certificateType).encode('utf8'))
        row = cursor.fetchone()
        cursor.close()
        if row and row[0] == 1:
            return True
        else:
            return False

    def is_time_limit_violation(self, number):
        cursor = self.segurosDB.cursor()
        query = "exec %s ?" % (self.settings.get('SegurosDB','isTimeLimitViolation'))
        self.logger.debug('Executing query %s with param: %s' % (query, number))
        cursor.execute(query, unicode(number).encode('utf8'))
        row = cursor.fetchone()
        cursor.close()
        if row and row[0] == 1:
            return True
        else:
            return False

    def getLineStatus(self, telephone):
        cursor = self.segurosDB.cursor()
        query = "exec %s ?" % (self.settings.get('SegurosDB','getLineStatus'))
        self.logger.debug('Executing query %s with param: %s' % (query, telephone))
        cursor.execute(query, unicode(telephone).encode('utf8'))
        row = cursor.fetchone()
        cursor.close()
        if row and row[0] != 0:
            return row
        else:
            return None
