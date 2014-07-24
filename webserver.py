# -*- coding: utf-8 -*-
import ConfigParser
import hashlib
import logging, logging.handlers
import dateutil.parser
import simplejson as json
from flask import Flask, redirect, make_response, request
from flask.ext.restful import reqparse, Api, Resource, fields, marshal
from flask_swagger.flask_restful_swagger import swagger
from flask.ext.httpauth import HTTPBasicAuth
from werkzeug.contrib.fixers import ProxyFix
from models import MSDriver
from msorm.exceptions.QueryIntegrityException import QueryIntegrityException

app = Flask(__name__, static_url_path='/api/docs')
auth = HTTPBasicAuth()

# Initializes settings file.
settings = ConfigParser.SafeConfigParser()
settings_path = 'conf/settings.cfg'
settings.read(settings_path)

# Creates logging configuration.
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
# Assign handler to configure logger's format.
handler = logging.handlers.RotatingFileHandler(
    settings.get('Logging','logpath'),
    maxBytes=settings.get('Logging','maxBytes'),
    backupCount=settings.get('Logging','backupCount')
)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(mes***REMOVED***ge)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)

users = {
  'tigo':'94c6c2243936b5472836ac7077830f5e' #t3$tus3r
}

apiDescription = """<p>REST API description of insurance management. <br/> All responses abide to the format: </p>
  <pre>
  {
      'data': {},
      'errorCode': 'codigo',
      'errorMes***REMOVED***ge': 'men***REMOVED***je de error',
      'meta': {'status': 'success'} 
  }
  </pre>
  <br/>
  <p>
    The field <b>data</b> is replaced in every endpoint by its respective response.
    Fields <b>data</b>, <b>errorCode</b> and <b>errorMes***REMOVED***ge</b> are optional and rely on the <b>status</b> in the header <b>meta</b>
  </p>
  <p>
    The API relies on Basic Authentication via Request Headers descibed as:
      <pre>Authorization: Basic encodedString</pre>
      <br/>
    where encodedString represents the 64 base encoding of the concatenation of "username:password". All endpoints must receive this header.
    Test user and password are: <b>tigo</b> and <b>t3$tus3r</b>
    To set this header to test the endpoints in this api use the following inputs:
  </p>
  <form class='basic_auth_info'>
    <input placeholder="Username" id="input_username" name="username" type="text"/>
    <input placeholder="Password" id="input_password" name="password" type="text"/>
    <button id="addHeader">Add Header</button>
    <button id="verifyHeader">Verify Header</button>
  </form>
  <hr/>
  <p>
    <em>powered by <a href="http://swagger.wordnik.com">Swagger</a> </em>
  </p>
  """

# Initializes settings file.
settings = ConfigParser.SafeConfigParser()
settings.read('conf/settings.cfg')

# Instantiate a sql server driver
msdriver = MSDriver()
        
# Swagger generator wrapper
api = swagger.docs(
  Api(app),
  apiVersion='0.1.0',
  #***REMOVED***.200.34
  basePath='http://'+settings.get('API','DBG_HOST'),
  resourcePath='/',
  produces=["application/json"],
  api_spec_url='/api/specs',
  info=dict(
    title="© Grupo TIR, S.A.",
    description=apiDescription,
    contact="jdigherob@tir.com.gt",
  )
)


# Authentication Functions
@auth.get_password
def get_pw(username):
  if username in users:
    return users[username]
  return None


@auth.hash_password
def hash_pw(password):
  return hashlib.md5(password).hexdigest()

@auth.error_handler
def auth_error():
  response = BaseResponseFields(
    status='error',
    data=None,
    errorMes***REMOVED***ge=u'Las credenciales no son válidas. Acceso denegado.',
    errorCode='TE0002'
  )
  return wrap_response(response, 500, {'Content-Type':'application/json'})

############################
#####  Swagger models ######
# Properties are documented 
# for API description
############################

# Requests
@swagger.model
class SubscriptionBillingRequestFields:
  resource_fields = {
    'id':fields.Integer(default=None),
    'numeroTelefono':fields.String(),
    'numeroCertificado':fields.String(),
    'montoCobro':fields.Float(),
    'fechaHora':fields.String()
  }

@swagger.model
@swagger.nested(requests=SubscriptionBillingRequestFields.__name__)
class SubscriptionBillingRequest:
  """
  """
  resource_fields = {
    'requests':fields.List(fields.Nested(SubscriptionBillingRequestFields.resource_fields))
  }

@swagger.model
class SubscriptionCancellationRequestFields:
  resource_fields = {
    'id':fields.Integer(default=None),
    'numeroTelefono':fields.String(),
    'numeroCertificado':fields.String(),
    'fechaHora':fields.String(),
    'motivo':fields.String()
  }

@swagger.model
@swagger.nested(requests=SubscriptionCancellationRequestFields.__name__)
class SubscriptionCancellationRequest:
  """
  """
  resource_fields = {
    'requests':fields.List(fields.Nested(SubscriptionCancellationRequestFields.resource_fields))
  }

# Responses

@swagger.model
class MetaFields:
  """
    Nested properties of the 
    meta tag of the base response 
    format. 
  """
  resource_fields = {
    'status':fields.String()
  }

@swagger.model
@swagger.nested(meta=MetaFields.__name__)
class BaseResponseFields:
  """
    Properties of the base response
    format for all API responses.
  """
  resource_fields = {
    'meta':fields.Nested(MetaFields.resource_fields),
    'errorCode':fields.String,
    'errorMes***REMOVED***ge':fields.String,
    'data':fields.Raw
  }

  def __init__(self, status, data, errorCode=None, errorMes***REMOVED***ge=None):
    """
      Base response constructor.
      errorCode and errorMes***REMOVED***ge are only instatiated
      when an error has ocurred.
    """
    self.meta = {}
    self.meta['status'] = status
    self.data = data
    self.errorMes***REMOVED***ge = errorMes***REMOVED***ge
    self.errorCode = errorCode


@swagger.model
@swagger.nested(payload=BaseResponseFields.__name__)
class SubscriptionBillOperationsFields:
  """
    Every one of the operations received to be billed.
  """
  resource_fields = {
    'id':fields.String(),
    'payload':fields.Nested(BaseResponseFields.resource_fields)
  }

@swagger.model
@swagger.nested(results=SubscriptionBillOperationsFields.__name__)
class SubscriptionBillResponse:
  """
    The list of batch operations that were evaluated as 
    billing requests.
  """
  resource_fields = {
    'results':fields.List(fields.Nested(SubscriptionBillOperationsFields.resource_fields))
  }

@swagger.model
@swagger.nested(payload=BaseResponseFields.__name__)
class SubscriptionCancellationOperationsFields:
  """
    Every one of the operations received to be cancelled.
  """
  resource_fields = {
    'id':fields.String(),
    'payload':fields.Nested(BaseResponseFields.resource_fields)
  }

@swagger.model
@swagger.nested(results=SubscriptionCancellationOperationsFields.__name__)
class SubscriptionCancellationResponse:
  """
    The list of batch operations that were evaluated as 
    cancellation requests.
  """
  resource_fields = {
    'results':fields.List(fields.Nested(SubscriptionCancellationOperationsFields.resource_fields))
  }

@swagger.model
class SubscriptionStatusResponse:
  """
    Properties of the response when 
    querying the current status of a 
    subscription. 
  """
  resource_fields = {
    'codigoReclamo':fields.String(),
    'CUI':fields.String(),
    'nombreCompleto':fields.String(),
    'numeroCertificado':fields.String(),
    'numeroTelefono':fields.String(),
    'cobertura':fields.Float(),
  }

@swagger.model
class SubscriptionClaimResponse:
  """
    Properties of the response when 
    claiming a subscription.
  """
  resource_fields = {
    'cobertura':fields.Float(),
  }

@swagger.model
class SubscriptionChangeNumberResponse:
  """
  """
  resource_fields = {
    'mes***REMOVED***ge':fields.String()
  }

def wrap_response(response, status, headers):
  """
    Receives all responses and adds status codes and headers
    when filtered with marshal
  """
  return make_response(json.dumps(marshal(response, BaseResponseFields.resource_fields)), status, headers)

# Endpoints declaration

class SubscriptionBilling(Resource):
  @swagger.operation(
    notes="""These endpoint can receive from one two many batch requests within the ***REMOVED***me payload. <br/>
      fechaHora represented in ISO 8601 datetime string (e.g. 2014-05-08T23:41:54.000Z). <br/>
      <br/>
      <b>Note:</b> The field <b>id</b> in the response and request of batch operations is only used for mapping the result of each individual tran***REMOVED***ction. When there is only one tran***REMOVED***ction this field is optional.
      <br/>
      <br/>
      <b>Curl Example</b> (with test user and password):  <br/>
      $ curl -H "Authorization: Basic dGlnbzp0MyR0dXMzcg==" -H "Content-Type:application/json" <br/>
      -d "{'requests': [{'numeroCertificado': 'GT4958','montoCobro': 5.20,'numeroTelefono': '50255285798','fechaHora': '2014-05-08T23:41:54.000Z','id': 1}]}" <br/>
      localhost:5000/subscriptions/charge
    """,
    responseClass=SubscriptionBillResponse,
    nickname='billSubscription',
    parameters=[
      {
        "name": "request",
        "description": "Billing batch request",
        "required": True,
        "allowMultiple": True,
        "dataType": SubscriptionBillingRequest.__name__,
        "paramType": "body"
      },
    ],
    responseMes***REMOVED***ges=[
      {
        "code": 400,
        "mes***REMOVED***ge":"""<pre>
        {
          "data": {
            "results": [
              {
                "id": "0",
                "payload": {
                  "data": {
                    "mes***REMOVED***ge":"Validación de campos incorrecta."
                  },
                  "errorCode": null,
                  "errorMes***REMOVED***ge": null,
                  "meta": {
                    "status": "fail"
                  }
                }
              }
            ]
          },
          "errorCode": null,
          "errorMes***REMOVED***ge": null,
          "meta": {
            "status": "success"
          }
        }</pre>"""
      },
      {
        "code": 404,
        "mes***REMOVED***ge":"""<pre>
        {
          "data": {
            "results": [
              {
                "id": "0",
                "payload": {
                  "data": {
                    "mes***REMOVED***ge":"No existe certificado asignado a este número."
                  },
                  "errorCode": null,
                  "errorMes***REMOVED***ge": null,
                  "meta": {
                    "status": "fail"
                  }
                }
              }
            ]
          },
          "errorCode": null,
          "errorMes***REMOVED***ge": null,
          "meta": {
            "status": "success"
          }
        }</pre>"""
      },
      {
        "code": 500,
        "mes***REMOVED***ge": """<pre>
        {
          "data": null,
          "errorCode": "TE0001",
          "errorMes***REMOVED***ge": "El servicio no está disponible en este momento.",
          "meta": {
            "status": "error"
          }
        }</pre>"""
      }
    ]
  )
  @auth.login_required
  def post(self):
    """
      Evaluate one or more bill requests to be 
      charged to the given subscription.
    """
    response_codes = {
      2:'TF0002',
      3:'TF0003',
      4:'TF0004',
      0:'TF0005',
    }
    response_mes***REMOVED***ge = {
      1:u'Suscripción cobrada éxito***REMOVED***mente.',
      2:u'El número de certificado y número de teléfono no coinciden.',
      3:u'El certificado asociado al número no se encuentra en un estado válido para su cobro.',
      4:u'El certificado no existe.',
      0:u'La suscripción no pudo ser cobrada. Intente de nuevo o contacte a servicio técnico.',
    }
    responses = []
    requests = json.loads(request.data)
    operations = requests["requests"]
    for operation in operations:
      # If json payload from request 
      # isn't well formed return bad request
      try:
        noCertificado = operation["numeroCertificado"]
        noTelefono = operation["numeroTelefono"]
        montoCobro = operation["montoCobro"]
        _id = operation["id"]
      except Exception,e:
        print str(e)
        payload = {
          "data": {
            "mes***REMOVED***ge":"Campos inválidos. Todos los campos son nece***REMOVED***rios para realizar la operación.",
            "code":"TF0001"
          },
          "errorCode": "null",
          "errorMes***REMOVED***ge": "null",
          "meta": {
            "status": "fail"
          }
        }
        response = {
          "id":operation["id"],
          "payload":payload
        }
        responses.append(response)
        break

      # Validate that fields aren't empty
      if (not montoCobro) or (not noCertificado) or (not noTelefono) or (not _id):
        payload = {
          "data": {
            "mes***REMOVED***ge":"Campos inválidos. Todos los campos son nece***REMOVED***rios para realizar la operación.",
            "code":"TF0001"
          },
          "errorCode": "null",
          "errorMes***REMOVED***ge": "null",
          "meta": {
            "status": "fail"
          }
        }
      else:
        try:
          fechaHora = dateutil.parser.parse(operation["fechaHora"])
          try:
            result = msdriver.scheduled_certificate_charge(noCertificado, noTelefono, montoCobro, fechaHora)
            result = result[0]
            if result == 1:
              payload = {
                "data": {"mes***REMOVED***ge":response_mes***REMOVED***ge[result]},
                "errorCode": "null",
                "errorMes***REMOVED***ge": "null",
                "meta": {
                  "status": "success"
                }
              }
              status=200
            else:
              payload = {
                "data": {
                  "code":response_codes[result],
                  "mes***REMOVED***ge":response_mes***REMOVED***ge[result]
                },
                "errorCode": "null",
                "errorMes***REMOVED***ge": "null",
                "meta": {
                  "status": "fail"
                }
              }
              status=400
          except Exception,e:
            print str(e)
            response = BaseResponseFields(
              status='error',
              data=None,
              errorMes***REMOVED***ge=u'Error Interno.',
              errorCode='TE0001'
            )
            status = 500
            return wrap_response(response, status, {'Content-Type':'application/json'})
        except Exception, e:
          print str(e)
          payload = {
            "data": {
              "mes***REMOVED***ge":"Formato de fecha inválida. Validar que el formato de la fecha sea correspondiente al ISO8601.",
              "code":"TF0006"
            },
            "errorCode": "null",
            "errorMes***REMOVED***ge": "null",
            "meta": {
              "status": "fail"
            }
          }
         
      response = {
        "id":_id,
        "payload":payload
      }
      responses.append(response)
    compound_response = BaseResponseFields(
      status='success',
      data={
        "results":responses
      },
      errorMes***REMOVED***ge=None,
      errorCode=None
    )
    status = 200
    return wrap_response(compound_response, status, {'Content-Type':'application/json'})

class SubscriptionCancellation(Resource):
  """
    Documentation of Subscription cancelation's endpoint
  """
  @swagger.operation(
    notes=
    """These endpoint can receive from one two many batch requests within the ***REMOVED***me payload. <br/>
      <em>fechaHora</em> represented in ISO 8601 datetime string (e.g. 2014-05-08T23:41:54.000Z).<br/><br/>
      <b>Note:</b> The field <b>id</b> in the response and request of batch operations is only used for mapping the result of each individual tran***REMOVED***ction.
      When there is only one tran***REMOVED***ction this field is optional.
      <br/>
      <br/>
      <b>Curl Example</b> (with test user and password):  <br/>
      $ curl -H "Authorization: Basic dGlnbzp0MyR0dXMzcg==" -H "Content-Type:application/json" <br/>
      -d "{'requests': [{'numeroCertificado': 'GT4958','motivo': 'M0003','numeroTelefono': '50255285798','fechaHora': '2014-05-08T23:41:54.000Z','id': 1}]}" <br/>
      localhost:5000/subscriptions/cancel
    """,
    responseClass=SubscriptionCancellationResponse,
    nickname='cancelSubscription',
    # Parameters can be automatically extracted from URLs (e.g. <string:id>)
    # but you could also override them here, or add other parameters.
    parameters=[
      {
        "name": "body",
        "description": "Cancellation batch request",
        "required": True,
        "allowMultiple": False,
        "dataType": SubscriptionCancellationRequest.__name__,
        "paramType": "body"
      },
    ],
    consumes =[
      "application/json"
    ],
    produces = [
      "application/json"
    ],
    responseMes***REMOVED***ges=[
      {
        "code": 400,
        "mes***REMOVED***ge":"""<pre>
        {
          "data": {
            "results": [
              {
                "id": "0",
                "payload": {
                  "data": {
                    "mes***REMOVED***ge":"Mótivo no definido."
                  },
                  "errorCode": null,
                  "errorMes***REMOVED***ge": null,
                  "meta": {
                    "status": "fail"
                  }
                }
              }
            ]
          },
          "errorCode": null,
          "errorMes***REMOVED***ge": null,
          "meta": {
            "status": "success"
          }
        }</pre>"""
      },
      {
        "code": 404,
        "mes***REMOVED***ge":"""<pre>
        {
          "data": {
            "results": [
              {
                "id": "0",
                "payload": {
                  "data": {
                    "mes***REMOVED***ge":"No existe certificado para este número."
                  },
                  "errorCode": null,
                  "errorMes***REMOVED***ge": null,
                  "meta": {
                    "status": "fail"
                  }
                }
              }
            ]
          },
          "errorCode": null,
          "errorMes***REMOVED***ge": null,
          "meta": {
            "status": "success"
          }
        }</pre>"""
      },
      {
        "code": 500,
        "mes***REMOVED***ge": """<pre>
        {
          "data": null,
          "errorCode": "TE0001",
          "errorMes***REMOVED***ge": "El servicio no está disponible en este momento.",
          "meta": {
            "status": "error"
          }
        }</pre>"""
      }
    ]
  )
  @auth.login_required
  def post(self):
    """
      Evaluate one or more cancel requests to be 
      issued to the given subscription.
    """
    response_codes = {
      2:'TF0002',
      3:'TF0003',
      4:'TF0004',
      0:'TF0005',
    }
    response_mes***REMOVED***ge = {
      1:u'Suscripción cancelada éxito***REMOVED***mente.',
      2:u'El número de certificado y número de teléfono no coinciden.',
      3:u'El certificado asociado al número no se encuentra en un estado válido para su cancelación. Puede haber sido cancelado anteriormente.',
      4:u'El certificado no existe.',
      0:u'La suscripción no pudo ser cancelada. Intente de nuevo o contacte a servicio técnico.',
    }
    responses = []
    requests = json.loads(request.data)
    operations = requests["requests"]
    for operation in operations:
      try:
        noCertificado = operation["numeroCertificado"]
        noTelefono = operation["numeroTelefono"]
        motivo = operation["motivo"]
        _id = operation["id"]
      except Exception,e:
        print str(e)
        payload = {
          "data": {
            "mes***REMOVED***ge":"Campos inválidos. Todos los campos son nece***REMOVED***rios para realizar la operación.",
            "code":"TF0001"
          },
          "errorCode": "null",
          "errorMes***REMOVED***ge": "null",
          "meta": {
            "status": "fail"
          }
        }
        response = {
          "id":operation["id"],
          "payload":payload
        }
        responses.append(response)
        break

      # Validate that fields aren't empty
      if (not motivo) or (not noCertificado) or (not noTelefono) or (not _id):
        payload = {
          "data": {
            "mes***REMOVED***ge":"Campos inválidos. Todos los campos son nece***REMOVED***rios para realizar la operación.",
            "code":"TF0001"
          },
          "errorCode": "null",
          "errorMes***REMOVED***ge": "null",
          "meta": {
            "status": "fail"
          }
        }
      else:
        try:
          fechaHora = dateutil.parser.parse(operation["fechaHora"])
          try:
            result = msdriver.scheduled_certificate_cancellation(noCertificado, noTelefono, motivo, fechaHora)
            result = result[0]
            if result == 1:
              payload = {
                "data": {"mes***REMOVED***ge":response_mes***REMOVED***ge[result]},
                "errorCode": "null",
                "errorMes***REMOVED***ge": "null",
                "meta": {
                  "status": "success"
                }
              }
              status=200
            else:
              payload = {
                "data": {
                  "code":response_codes[result],
                  "mes***REMOVED***ge":response_mes***REMOVED***ge[result]
                },
                "errorCode": "null",
                "errorMes***REMOVED***ge": "null",
                "meta": {
                  "status": "fail"
                }
              }
              status=400
          except Exception,e:
            print str(e)
            response = BaseResponseFields(
              status='error',
              data=None,
              errorMes***REMOVED***ge=u'Error Interno.',
              errorCode='TE0001'
            )
            status = 500
            return wrap_response(response, status, {'Content-Type':'application/json'})
        except Exception, e:
          print str(e)
          payload = {
            "data": {
              "mes***REMOVED***ge":"Formato de fecha inválida. Validar que el formato de la fecha sea correspondiente al ISO8601.",
              "code":"TF0006"
            },
            "errorCode": "null",
            "errorMes***REMOVED***ge": "null",
            "meta": {
              "status": "fail"
            }
          }
         
      response = {
        "id":_id,
        "payload":payload
      }
      responses.append(response)
    compound_response = BaseResponseFields(
      status='success',
      data={
        "results":responses
      },
      errorMes***REMOVED***ge=None,
      errorCode=None
    )
    status = 200
    return wrap_response(compound_response, status, {'Content-Type':'application/json'})

class SubscriptionStatus(Resource):
  """
    Subscription get status documentation
  """
  @swagger.operation(
    notes=
    """Inquiry on the status of a given telephone's subscription<br/>
      <b>Curl Example</b> (with test user and password):  <br/>
      $ curl --header "Authorization: Basic dGlnbzp0MyR0dXMzcg==" {apiUrl}/subscription/{numTel}/status
    """,
    responseClass=SubscriptionStatusResponse,
    nickname='getStatus',
    parameters=[
      {
        "name": "numeroTelefono",
        "description": "Número de teléfono asignado a suscripción.",
        "required": True,
        "allowMultiple": False,
        "dataType": str.__name__,
        "paramType": "path"
      },
    ],
    responseMes***REMOVED***ges=[
      {
        "code": 200,
        "mes***REMOVED***ge":"""<pre>
        {
          "data": {
            "numeroCertificado":'TST123',
            "numeroTelefono":'50212345678',
            "nombreCompleto":'Alan Fry',
            "CUI":'5234612345678',
            "codigoReclamo":'GT5167',
            "cobertura":500
          },
          "errorCode": null,
          "errorMes***REMOVED***ge": null,
          "meta": {
            "status": "success"
          }
        }</pre>"""
      },
      {
        "code": 400,
        "mes***REMOVED***ge":"""<pre>
        {
          "data": {
            "mes***REMOVED***ge": "No cumple con plazo mínimo de uso antes de reclamo.",
            "code": "TF0002"
          },
          "errorCode": null,
          "errorMes***REMOVED***ge": null,
          "meta": {
            "status": "fail"
          }
        }</pre>"""
      },
      {
        "code": 400,
        "mes***REMOVED***ge":"""<pre>
        {
          "data": {
            "mes***REMOVED***ge": "El certificado asociado al número no se encuentra en estado activo o cancelado.",
            "code": "TF0003"
          },
          "errorCode": null,
          "errorMes***REMOVED***ge": null,
          "meta": {
            "status": "fail"
          }
        }</pre>"""
      },
      {
        "code": 400,
        "mes***REMOVED***ge":"""<pre>
        {
          "data": {
            "mes***REMOVED***ge": "No existe bloqueo para último certificado de este número.",
            "code": "TF0004"
          },
          "errorCode": null,
          "errorMes***REMOVED***ge": null,
          "meta": {
            "status": "fail"
          }
        }</pre>"""
      },
      {
        "code": 400,
        "mes***REMOVED***ge":"""<pre>
        {
          "data": {
            "mes***REMOVED***ge": "Estatus: Reclamo inválido. Fecha de bloqueo no procede.",
            "code": "TF0005"
          },
          "errorCode": null,
          "errorMes***REMOVED***ge": null,
          "meta": {
            "status": "fail"
          }
        }</pre>"""
      },
      {
        "code": 404,
        "mes***REMOVED***ge":"""<pre>
        {
          "data": {
            "mes***REMOVED***ge": "No existe certificado para el número 50212345678.",
            "code": "TF0001"
          },
          "errorCode": null,
          "errorMes***REMOVED***ge": null,
          "meta": {
            "status": "fail"
          }
        }</pre>"""
      },
      {
        "code": 500,
        "mes***REMOVED***ge": """<pre>
        {
          "data": null,
          "errorCode": "TE0001",
          "errorMes***REMOVED***ge": "El servicio no está disponible en este momento.",
          "meta": {
            "status": "error"
          }
        }</pre>"""
      },
      {
        "code": 500,
        "mes***REMOVED***ge": """<pre>
        {
          "data": null,
          "errorCode": "TE0002",
          "errorMes***REMOVED***ge": "Error Interno.",
          "meta": {
            "status": "error"
          }
        }</pre>"""
      }
    ]
  )
  @auth.login_required
  def get(self, numeroTelefono):
    """
      Get the status of subcription of a telephone number.
    """ 
    response_codes = {
      2:'TF0002',
      3:'TF0003',
      4:'TF0004',
      0:'TF0005',
      5:'TE0002'
    }
    response_mes***REMOVED***ge = {
      2:u'No cumple con plazo mínimo de uso antes de reclamo.',
      3:u'El certificado asociado al número no se encuentra en estado activo o cancelado.',
      4:u'No existe bloqueo para último certificado de este número.',
      0:u'Estatus: Reclamo inválido. Fecha de bloqueo no procede.',
      5:u'Error Interno'
    }
    try:
      if not msdriver.exists_certificate(numeroTelefono,'robos'):
        response_mes***REMOVED***ge = u'No existe certificado para el número %s.' % (numeroTelefono)
        app.logger.info(response_mes***REMOVED***ge)
        response = BaseResponseFields(
          status='fail',
          data={
            'code':'TF0001',
            'mes***REMOVED***ge':response_mes***REMOVED***ge
          }
        )
        status = 404
        return wrap_response(response, status, {'Content-Type':'application/json'})
      # Obtener con el API si el telefono esta bloqueado y en que fecha se efectuo
      # para mandarlo al metodo de is_payment_enabled()
      # models.is_blocked_IMEI
      result = msdriver.is_payment_enabled(numeroTelefono, '2014/05/02', 1)[0]
      if result['response'] == 1:
        response = BaseResponseFields(
          status='success',
          data={
            'numeroCertificado':result['idCertificado'],
            'numeroTelefono':result['numeroTelefono'],
            'nombreCompleto':result['nombreCompleto'],
            'CUI':result['CUI'],
            'codigoReclamo':result['codigoReclamo'],
            'cobertura':result['cobertura']
          }
        )
        status = 200
      elif result['response'] == 0:
        response = BaseResponseFields(
          status='error',
          data=None,
          errorMes***REMOVED***ge= response_mes***REMOVED***ge[result['response']],
          errorCode= response_codes[result['response']]
        )
        status = 500
      else:
        response = BaseResponseFields(
          status='fail',
          data={
            'code': response_codes[result['response']],
            'mes***REMOVED***ge': response_mes***REMOVED***ge[result['response']],
          }
        )
        status = 400  
      return wrap_response(response, status, {'Content-Type':'application/json'})
    except Exception, e:
      app.logger.error(str(e), exc_info=True)
      response = BaseResponseFields(
        status='error',
        data=None,
        errorMes***REMOVED***ge= response_mes***REMOVED***ge[5],
        errorCode= response_codes[5]
      )
      status = 500
      return wrap_response(response, status, {'Content-Type':'application/json'})

class SubscriptionClaim(Resource):
  """
    Documentation for subscription's claim endpoint
  """
  def __init__(self):
    self.reqparse = reqparse.RequestParser()
    self.reqparse.add_argument('codigoReclamo', type=str, help='No se ha proporcionado ningún código de reclamo.')
    super(SubscriptionClaim, self).__init__()

  @swagger.operation(
    notes=
    """Claim a subscription. <br/>
       <b>Curl Example</b> (with test user and password):  <br/>
       $ curl --header "Authorization: Basic dGlnbzp0MyR0dXMzcg==" --data "codigoReclamo={codigoReclamo}" {apiUrl}/subscription/claim
    """,
    responseClass=SubscriptionClaimResponse,
    nickname='claimSubscription',
    parameters=[
      {
        "name": "codigoReclamo",
        "description": "Claim code associated to subscription.",
        "required": True,
        "allowMultiple": False,
        "dataType": str.__name__,
        "paramType": "form"
      }
    ],
    responseMes***REMOVED***ges=[
      {
        "code": 200,
        "mes***REMOVED***ge":"""<pre>
        {
          "data": {
            "cobertura": 500,
          },
          "errorCode": null,
          "errorMes***REMOVED***ge": null,
          "meta": {
            "status": "success"
          }
        }</pre>"""
      },
      {
        "code": 400,
        "mes***REMOVED***ge":"""<pre>
        {
          "data": {
            "mes***REMOVED***ge": "El campo de código de reclamo no debe estar vacío.",
            "code": "TF0001"
          },
          "errorCode": null,
          "errorMes***REMOVED***ge": null,
          "meta": {
            "status": "fail"
          }
        }</pre>"""
      },
      {
        "code": 404,
        "mes***REMOVED***ge":"""<pre>
        {
          "data": {
            "mes***REMOVED***ge": "El código de reclamo no existe.",
            "code": "TF0001"
          },
          "errorCode": null,
          "errorMes***REMOVED***ge": null,
          "meta": {
            "status": "fail"
          }
        }</pre>"""
      },
      {
        "code": 500,
        "mes***REMOVED***ge": """<pre>
        {
          "data": null,
          "errorCode": "TE0001",
          "errorMes***REMOVED***ge": "El servicio no está disponible en este momento.",
          "meta": {
            "status": "error"
          }
        }</pre>"""
      },
      {
        "code": 500,
        "mes***REMOVED***ge": """<pre>
        {
          "data": null,
          "errorCode": "TE0002",
          "errorMes***REMOVED***ge": "Error Interno.",
          "meta": {
            "status": "error"
          }
        }</pre>"""
      }
    ]
  )
  @auth.login_required
  def post(self):
    """ Claim a subscription """
    response_codes = {
      'a':'TF0002',
      'b':'TF0003',
    }
    response_mes***REMOVED***ge = {
      'a':u'El certificado ya ha sido pagado.',
      'b':u'El código de reclamo no existe.',
    }
    args = self.reqparse.parse_args()
    if not args.codigoReclamo:
      response = BaseResponseFields(
        status='fail',
        data={
          'code':'TF0002',
          'mes***REMOVED***ge':u'El campo de código de reclamo no debe estar vacío.'
        }
      )
      status = 400
      return wrap_response(response, status, {'Content-Type':'application/json'})
    try:
      result = msdriver.claim_subscription(args.codigoReclamo)
      if result != 'a' and result != 'b':
        response = BaseResponseFields(
          status='success',
          data={
            'cobertura': result
          }
        )
        status = 200
      else:
        response = BaseResponseFields(
          status='fail',
          data={
            'code':response_codes[result],
            'mes***REMOVED***ge':response_mes***REMOVED***ge[result],
          }
        )
        status = 400 
      return wrap_response(response, status, {'Content-Type':'application/json'})
    except QueryIntegrityException, qie:
      app.logger.error(str(qie), exc_info=True)
      response = BaseResponseFields(
        status='error',
        data={
          'code':'TE0002',
          'mes***REMOVED***ge':u'Error interno'
        }
      )
      status = 400
      return wrap_response(response, status, {'Content-Type':'application/json'})
    except Exception, e:
      app.logger.error(str(e), exc_info=True)
      response = BaseResponseFields(
        status='error',
        data=None,
        errorMes***REMOVED***ge= u'Error Interno',
        errorCode= 'TE0002'
      )
      status = 500
      return wrap_response(response, status, {'Content-Type':'application/json'})

class SubscriptionChangeNumber(Resource):
  """
    Documentation for subscription's change of number endpoint
  """
  def __init__(self):
    self.reqparse = reqparse.RequestParser()
    self.reqparse.add_argument(
      'IMEI',
      type=str,
      help='No se ha proporcionado el valor para el IMEI.'
    )
    self.reqparse.add_argument(
      'numeroTelefono',
      type=str,
      help='No se ha proporcionado un número de teléfono válido.'
    )
    super(SubscriptionChangeNumber, self).__init__()

  @swagger.operation(
    notes=
    """Update IMEI assigned to a number. <br/>
      <b>Curl Example</b> (with test user and password):  <br/>
      $ curl --header "Authorization: Basic dGlnbzp0MyR0dXMzcg==" --data "IMEI={imei}&numeroTelefono={numTel}" {apiUrl}/subscription/changeNumber
    """,
    responseClass=SubscriptionChangeNumberResponse,
    nickname='changeNumber',
    parameters=[
      {
        "name": "IMEI",
        "description": "IMEI associated to mobile device",
        "required": True,
        "allowMultiple": False,
        "dataType": str.__name__,
        "paramType": "form"
      },
      {
        "name": "numeroTelefono",
        "description": "Telephone number associated to mobile device",
        "required": True,
        "allowMultiple": False,
        "dataType": str.__name__,
        "paramType": "form"
      }
    ],
    responseMes***REMOVED***ges=[
      {
        "code": 200,
        "mes***REMOVED***ge":"""<pre>
        {
          "data": {
            "mes***REMOVED***ge": "Datos actualizados éxito***REMOVED***mente.",
          },
          "errorCode": null,
          "errorMes***REMOVED***ge": null,
          "meta": {
            "status": "success"
          }
        }</pre>"""
      },
      { 
        "code":400,
        "mes***REMOVED***ge":"""<pre>{
          "data": {
            "mes***REMOVED***ge": "El número enviado ya tiene otro IMEI asignado",
            "code": "TF0002"
          },
          "errorCode": null,
          "errorMes***REMOVED***ge": null,
          "meta": {
            "status": "fail"
          }
        }</pre>"""
      },
      {
        "code": 400,
        "mes***REMOVED***ge":"""<pre>
        {
          "data": {
            "mes***REMOVED***ge": "Los campos de IMEI y numeroTelefono no deben estar vacíos.",
            "code": "TF0001"
          },
          "errorCode": null,
          "errorMes***REMOVED***ge": null,
          "meta": {
            "status": "fail"
          }
        }</pre>"""
      },
      {
        "code": 500,
        "mes***REMOVED***ge": """<pre>
        {
          "data": null,
          "errorCode": "TE0001",
          "errorMes***REMOVED***ge": "El servicio no está disponible en este momento.",
          "meta": {
            "status": "error"
          }
        }</pre>"""
      },
      {
        "code": 500,
        "mes***REMOVED***ge": """<pre>
        {
          "data": null,
          "errorCode": "TE0002",
          "errorMes***REMOVED***ge": "Error Interno.",
          "meta": {
            "status": "error"
          }
        }</pre>"""
      }
    ]
  )
  @auth.login_required
  def post(self):
    """
      Change number assigned to IMEI.
    """
    args = self.reqparse.parse_args()
    if (not args.IMEI) or (not args.numeroTelefono):
      response = BaseResponseFields(
        status='fail',
        data={
          'code':'TF0002',
          'mes***REMOVED***ge':u'Los campos de IMEI y numeroTelefono no deben estar vacíos.'
        }
      )
      status = 400
      return wrap_response(response, status, {'Content-Type':'application/json'})
    try:
      was_success = msdriver.change_number(args.IMEI, args.numeroTelefono)
      if was_success:
        response = BaseResponseFields(
          status='success',
          data={
            'mes***REMOVED***ge':'Datos actualizados éxito***REMOVED***mente.',
          }
        )
        status = 200
      else:
        response = BaseResponseFields(
          status='fail',
          data={
            'code':'TF0001',
            'mes***REMOVED***ge':u'El IMEI no existe en la base de datos.',
          }
        )
        status = 404
      return wrap_response(response, status, {'Content-Type':'application/json'})
    except QueryIntegrityException, qie:
      app.logger.error(str(qie), exc_info=True)
      response = BaseResponseFields(
        status='fail',
        data={
          'code':'TF0002',
          'mes***REMOVED***ge':u'El número enviado ya tiene otro IMEI asignado'
        }
      )
      status = 400
      return wrap_response(response, status, {'Content-Type':'application/json'})
    except Exception, e:
      app.logger.error(str(e), exc_info=True)
      response = BaseResponseFields(
        status='error',
        data=None,
        errorMes***REMOVED***ge= u'Error Interno',
        errorCode= 'TE0002'
      )
      status = 500
      return wrap_response(response, status, {'Content-Type':'application/json'})

# Api description
api.add_resource(SubscriptionBilling, '/subscriptions/charge', endpoint='chargeSubscription')
api.add_resource(SubscriptionCancellation, '/subscriptions/cancel', endpoint='cancelSubscription')
api.add_resource(SubscriptionStatus,  '/subscription/<string:numeroTelefono>/status', endpoint='getStatus')
api.add_resource(SubscriptionClaim, '/subscription/claim', endpoint='ClaimSubscription')
api.add_resource(SubscriptionChangeNumber, '/subscription/changeNumber', endpoint='ChangeNumber')

# App routing

@app.after_request
def after(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods',
                         'POST, GET, PUT, PATCH, DELETE, OPTIONS')
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type, X-Requested-With')
    response.headers.add('Access-Control-Max-Age', '1728000')
    response.headers.add('Server', 'X-Server')
    return response

@app.route('/api', endpoint='api-docs')
def api_webdocs():
  return redirect('/api/specs.html#!/specs.json')

# Proxy setup that works with nginx
app.wsgi_app = ProxyFix(app.wsgi_app)

if __name__ == '__main__':
  app.run()
