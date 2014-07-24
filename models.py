from msorm.QueryManager import QueryManager
from msorm.exceptions.QueryIntegrityException import QueryIntegrityException
import logging
import ConfigParser
import logging.handlers

class MSDriver():
    """

    """
    def __init__(self):
        # Initializes settings file.
        self.settings = ConfigParser.SafeConfigParser()
        self.settings_path = 'conf/settings.cfg'
        self.settings.read(self.settings_path)

        # Connects to mes***REMOVED***ges database.
        """self.segurosDB = pyodbc.connect(
            'DSN=%s;UID=%s;PWD=%s;DATABASE=%s' % 
            (
                self.settings.get('DBSeguros', 'dsn'),
                self.settings.get('DBSeguros', 'uid'),
                self.settings.get('DBSeguros', 'pwd'),
                self.settings.get('DBSeguros', 'database')
            ), 
            autocommit=True
        )"""
        
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

    def get_connection(self):
        return self.segurosDB.cursor()

    def get_response_mes***REMOVED***ge(self, state, motif):
        cursor = self.segurosDB.cursor()
        query = "exec %s ?, ?, ?" % self.settings.get('DBSeguros','getResponseMes***REMOVED***ge')
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
        qm = QueryManager(self.settings_path)
        try:
            query = "exec %s ?, ?, ?" % (self.settings.get('DBSeguros','isPaymentEnabled'))
            self.logger.debug('Executing query %s with param: %s, %s, %s' % (query, telephone, fechaBloqueo, estaBloqueado))
            row = qm.query_all('DBSeguros', query, params=[unicode(telephone).encode('utf8'), unicode(fechaBloqueo).encode('utf8'), estaBloqueado])
            if row:
                return row
            else:
                return None
        except Exception,e:
            self.logger.error(str(e), exc_info=True)
            return None
        finally:
            qm.disconnect()

    def is_blocked_IMEI(self, number):
        return False

    def exists_certificate(self, number, _type):
        qm = QueryManager(self.settings_path)
        try:
            query = "exec %s ?" % (self.settings.get('DBSeguros','getAllCertificates'))
            self.logger.debug('Executing query %s with param: %s' % (query, number))
            rows = qm.query_all('DBSeguros', query, params=[number])
            certificates = {}
            for row in rows:
                certificates[row['codigo']] = row['descripcion']
            if _type in certificates:
                return True
            else:
                return False
        except Exception,e:
            self.logger.error(str(e), exc_info=True)
            return False
        finally:
            qm.disconnect()

    def change_number(self, imei, number):
        qm = QueryManager(self.settings_path)
        try:
            query = "exec %s ?, ?" % (self.settings.get('DBSeguros','changeNumber'))
            self.logger.debug('Executing query %s with param: %s, %s' % (query, imei, number))
            row = qm.query_one('DBSeguros', query, params=[unicode(imei).encode('utf8'),unicode(number).encode('utf8')])
            if row:
                return row==1
            else:
                return False
        except QueryIntegrityException,qie:
            self.logger.error(str(qie), exc_info=True)
            raise QueryIntegrityException(str(qie))
        except Exception,e:
            self.logger.error(str(e), exc_info=True)
            return False
        finally:
            qm.disconnect()

    def claim_subscription(self, codigoReclamo):
        qm = QueryManager(self.settings_path)
        try:
            query = "exec %s ?" % (self.settings.get('DBSeguros','claimSubscription'))
            self.logger.debug('Executing query %s with param: %s' % (query, codigoReclamo))
            row = qm.query_one('DBSeguros', query, params=[unicode(codigoReclamo).encode('utf8')])
            if row:
                return row
            else:
                return False
        except QueryIntegrityException, qie:
            self.logger.error(str(qie), exc_info=True)
            raise QueryIntegrityException(str(qie))
        except Exception,e:
            self.logger.error(str(e), exc_info=True)
            return False
        finally:
            qm.disconnect()

    def scheduled_certificate_cancellation(self, noCertificado, noTelefono, motivo, fechaHora):
        cursor = self.segurosDB.cursor()
        try:
            query = "exec %s ?, ?, ?, ?" % (self.settings.get('DBSeguros','scheduledCertificateCancellation'))
            self.logger.debug('Executing query %s with param: %s, %s, %s, %s' % (query, noCertificado, noTelefono, motivo, fechaHora))
            cursor.execute(
                query,
                unicode(noCertificado).encode('utf8'),
                unicode(noTelefono).encode('utf8'),
                unicode(motivo).encode('utf8'),
                (str(fechaHora).split('+')[0]).encode('utf8')
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

    def scheduled_certificate_charge(self, noCertificado, noTelefono, montoCobro, fechaHora):
        cursor = self.segurosDB.cursor()
        try:
            query = "exec %s ?, ?, ?, ?" % (self.settings.get('DBSeguros','scheduledCertificateCharge'))
            self.logger.debug('Executing query %s with param: %s, %s, %s, %s' % (query, noCertificado, noTelefono, montoCobro, fechaHora))
            cursor.execute(
                query,
                unicode(noCertificado).encode('utf8'),
                unicode(noTelefono).encode('utf8'),
                montoCobro,
                (str(fechaHora).split('+')[0]).encode('utf8')
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