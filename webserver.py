# -*- coding: utf-8 -*-
import random, hashlib
from flask import Flask, redirect, make_response, json
from flask.ext.restful import reqparse, request, Api, Resource, fields, marshal
from flask_swagger.flask_restful_swagger import swagger
from flask.ext.httpauth import HTTPBasicAuth
from werkzeug.contrib.fixers import ProxyFix

app = Flask(__name__, static_url_path='/api/docs')
auth = HTTPBasicAuth()

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
    <em>powered by <a href="swagger.wordnik.com">Swagger</a> </em>
  </p>
  """

# Swagger generator wrapper
api = swagger.docs(Api(app), apiVersion='0.1.0',
                   basePath='http://***REMOVED***.200.34',
                   resourcePath='/',
                   produces=["application/json"],
                   api_spec_url='/api/specs',
                   info=dict(
                    title="Seguros API © Grupo TIR, S.A.",
                    description=apiDescription,
                    contact="jdigherob@tir.com.gt",
                  ))


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
    'fechaHora':fields.DateTime()
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
    'montoCobro':fields.Float(),
    'fechaHora':fields.DateTime(),
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

@swagger.model
class SubscriptionClaimRequest:
  resource_fields = {
    'codigoReclamo':fields.String()
  }

@swagger.model
class SubscriptionChangeNumberRequest:
  resource_fields = {
    'IMEI':fields.String(),
    'numeroTelefono':fields.String()
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
    cancelation requests.
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
    notes="These endpoint can receive from one two many batch requests within the ***REMOVED***me payload. <br/> fechaHora represented in RFC822-formatted datetime string in UTC. " \
          "<br/><br/><b>Note:</b> The field <b>id</b> in the response and request of batch operations is only used for mapping the result of each individual tran***REMOVED***ction. When there is only one tran***REMOVED***ction this field is optional.",
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
    args = request.json
    print args
    choice = random.randint(1,10)
    if ( 1 <= choice < 4 ):
      response = BaseResponseFields(
        status='success',
        data={
          "results": [
            {
              "id": "0",
              "payload": {
                "data": {"mes***REMOVED***ge":"Subscription successfully billed."},
                "errorCode": "null",
                "errorMes***REMOVED***ge": "null",
                "meta": {
                  "status": "success"
                }
              }
            }
          ]
        }
      )
      status = 200
    elif (4 <= choice < 7):
      response = BaseResponseFields(
        status='success',
        data={
          "results": [
            {
              "id": "0",
              "payload": {
                "data": {"mes***REMOVED***ge":"No existe certificado para este número."},
                "errorCode": "null",
                "errorMes***REMOVED***ge": "null",
                "meta": {
                  "status": "fail"
                }
              }
            }
          ]
        }
      )
      status = 404
    elif (7 <= choice < 8):
      response = BaseResponseFields(
        status='success',
        data={
          "results": [
            {
              "id": "0",
              "payload": {
                "data": {"mes***REMOVED***ge":"Fecha de bloqueo no procede."},
                "errorCode": "null",
                "errorMes***REMOVED***ge": "null",
                "meta": {
                  "status": "fail"
                }
              }
            }
          ]
        }
      )
      status = 400  
    else:
      response = BaseResponseFields(
        status='error',
        data=None,
        errorMes***REMOVED***ge=u'El servicio no está disponible en este momento.',
        errorCode='TE0001'
      )
      status = 500
    return wrap_response(response, status, {'Content-Type':'application/json'})

class SubscriptionCancellation(Resource):
  """
  """
  @swagger.operation(
    notes="These endpoint can receive from one two many batch requests within the ***REMOVED***me payload. <br/> fechaHora represented in RFC822-formatted datetime string in UTC."  \
          "<br/><br/><b>Note:</b> The field <b>id</b> in the response and request of batch operations is only used for mapping the result of each individual tran***REMOVED***ction. When there is only one tran***REMOVED***ction this field is optional.",
    responseClass=SubscriptionCancellationResponse,
    nickname='cancelSubscription',
    # Parameters can be automatically extracted from URLs (e.g. <string:id>)
    # but you could also override them here, or add other parameters.
    parameters=[
      {
        "name": "requests",
        "description": "Cancelation batch request",
        "required": True,
        "allowMultiple": True,
        "dataType": SubscriptionCancellationRequest.__name__,
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
    args = request.json
    print args
    choice = random.randint(1,10)
    if ( 1 <= choice < 4 ):
      response = BaseResponseFields(
        status='success',
        data={
          "results": [
            {
              "id": "0",
              "payload": {
                "data": {"mes***REMOVED***ge":"Subscription successfully cancelled."},
                "errorCode": "null",
                "errorMes***REMOVED***ge": "null",
                "meta": {
                  "status": "success"
                }
              }
            }
          ]
        }
      )
      status = 200
    elif (4 <= choice < 7):
      response = BaseResponseFields(
        status='success',
        data={
          "results": [
            {
              "id": "0",
              "payload": {
                "data": {
                  "mes***REMOVED***ge":"Mótivo no definido."
                },
                "errorCode": "null",
                "errorMes***REMOVED***ge": "null",
                "meta": {
                  "status": "fail"
                }
              }
            }
          ]
        }
      )
      status = 404
    elif (7 <= choice < 8):
      response = BaseResponseFields(
        status='fail',
        data={
          "results": [
            {
              "id": "0",
              "payload": {
                "data": {
                  "mes***REMOVED***ge":"Fecha de bloqueo no procede."
                },
                "errorCode": "null",
                "errorMes***REMOVED***ge": "null",
                "meta": {
                  "status": "fail"
                }
              }
            }
          ]
        }
      )
      status = 400  
    else:
      response = BaseResponseFields(
        status='error',
        data=None,
        errorMes***REMOVED***ge=u'El servicio no está disponible en este momento.',
        errorCode='TE0001'
      )
      status = 500
    return wrap_response(response, status, {'Content-Type':'application/json'})

class SubscriptionStatus(Resource):
  """
    Subscription get status documentation
  """
  @swagger.operation(
      notes="Inquiry on the status of a given telephone's subscription",
      responseClass=SubscriptionStatusResponse,
      nickname='getStatus',
      parameters=[
        {
          "name": "numeroTelefono",
          "description": "Telephone number assigned to susbcription",
          "required": True,
          "allowMultiple": False,
          "dataType": str.__name__,
          "paramType": "path"
        },
      ],
      responseMes***REMOVED***ges=[
        {
          "code": 400,
          "mes***REMOVED***ge":"""<pre>
          {
            "data": {
              "mes***REMOVED***ge": "No existe bloqueo de IMEI para este número.",
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
              "mes***REMOVED***ge": "Fecha de bloqueo no procede.",
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
          "code": 404,
          "mes***REMOVED***ge":"""<pre>
          {
            "data": {
              "mes***REMOVED***ge": "No existe certificado para este número.",
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
        }
      ]
    )
  @auth.login_required
  def get(self, numeroTelefono):
    """
      Get the status of subcription of a telephone number.
    """ 
    choice = random.randint(1,10)
    if ( 1 <= choice < 4 ):
      response = BaseResponseFields(
        status='success',
        data={
          'numeroCertificado':'A15324',
          'numeroTelefono':'54612348',
          'nombreCompleto':'José Ordoñez',
          'CUI':'251061534862',
          'codigoReclamo':'3252',
          'cobertura':'2000.00'
        }
      )
      status = 200
    elif (4 <= choice < 7):
      response = BaseResponseFields(
        status='fail',
        data={
          'code':'TF0001',
          'mes***REMOVED***ge':u'No existe certificado para este número.',
        }
      )
      status = 404
    elif (7 <= choice < 8):
      response = BaseResponseFields(
        status='fail',
        data={
          'code':'TF0002',
          'mes***REMOVED***ge':u'Fecha de bloqueo no procede.',
        }
      )
      status = 400  
    else:
      response = BaseResponseFields(
        status='error',
        data=None,
        errorMes***REMOVED***ge=u'El servicio no está disponible en este momento.',
        errorCode='TE0001'
      )
      status = 500
    return wrap_response(response, status, {'Content-Type':'application/json'})

class SubscriptionClaim(Resource):
  """
  """
  def __init__(self):
    self.reqparse = reqparse.RequestParser()
    self.reqparse.add_argument('codigoReclamo', type=str, required=True, help='No se ha proporcionado ningún código de reclamo.')
    super(SubscriptionClaim, self).__init__()

  @swagger.operation(
      notes="Claim a subscription.",
      responseClass=SubscriptionClaimResponse,
      nickname='claimSubscription',
      parameters=[
        {
          "name": "request",
          "description": "Claim subscription request.",
          "required": True,
          "allowMultiple": False,
          "dataType": SubscriptionClaimRequest.__name__,
          "paramType": "body"
        },
      ],
      responseMes***REMOVED***ges=[
        {
          "code": 404,
          "mes***REMOVED***ge":"""<pre>
          {
            "data": {
              "mes***REMOVED***ge": "No existe código de reclamo.",
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
        }
      ]
    )
  @auth.login_required
  def post(self):
    """ Claim a subscription """
    args = self.reqparse.parse_args()
    choice = random.randint(1,10)
    if ( 1 <= choice < 5 ):
      response = BaseResponseFields(
        status='success',
        data={
          'cobertura':'2000.00'
        }
      )
      status = 200
    elif (6 <= choice < 8):
      response = BaseResponseFields(
        status='fail',
        data={
          'code':'TF0002',
          'mes***REMOVED***ge':u'El código de reclamo no existe.',
        }
      )
      status = 400  
    else:
      response = BaseResponseFields(
        status='error',
        data=None,
        errorMes***REMOVED***ge=u'El servicio no está disponible en este momento.',
        errorCode='TE0001'
      )
      status = 500
    return wrap_response(response, status, {'Content-Type':'application/json'})

class SubscriptionChangeNumber(Resource):
  """
  """
  def __init__(self):
    self.reqparse = reqparse.RequestParser()
    self.reqparse.add_argument('IMEI', type=str, required=True, help='No se ha proporcionado el valor para el IMEI.')
    self.reqparse.add_argument('numeroTelefono', type=str, required=True, help='No se ha proporcionado un número de teléfono válido.')
    super(SubscriptionChangeNumber, self).__init__()

  @swagger.operation(
      notes="Update IMEI assigned to a number.",
      responseClass=SubscriptionChangeNumberResponse,
      nickname='changeNumber',
      parameters=[
        {
          "name": "request",
          "description": "Change Number request",
          "required": True,
          "allowMultiple": False,
          "dataType": SubscriptionChangeNumberRequest.__name__,
          "paramType": "body"
        },
      ],
      responseMes***REMOVED***ges=[
        {
          "code": 400,
          "mes***REMOVED***ge":"""<pre>
          {
            "data": {
              "mes***REMOVED***ge": "No existe bloqueo de IMEI para este número.",
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
          "code": 404,
          "mes***REMOVED***ge":"""<pre>
          {
            "data": {
              "mes***REMOVED***ge": "Este número no existe.",
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
        }
      ]
    )
  @auth.login_required
  def post(self):
    """
      Change number assigned to IMEI.
    """
    args = self.reqparse.parse_args()
    choice = random.randint(1,10)
    if ( 1 <= choice < 4 ):
      response = BaseResponseFields(
        status='success',
        data={
          'mes***REMOVED***ge':'Datos actualizados éxito***REMOVED***mente',
        }
      )
      status = 200
    elif (4 <= choice < 7):
      response = BaseResponseFields(
        status='fail',
        data={
          'code':'TF0001',
          'mes***REMOVED***ge':u'El número de teléfono no existe.',
        }
      )
      status = 404
    else:
      response = BaseResponseFields(
        status='error',
        data=None,
        errorMes***REMOVED***ge=u'El servicio no está disponible en este momento.',
        errorCode='TE0001'
      )
      status = 500
    return wrap_response(response, status, {'Content-Type':'application/json'})

# Api description
api.add_resource(SubscriptionBilling, '/subscriptions/charge', endpoint='chargeSubscription')
api.add_resource(SubscriptionCancellation, '/subscriptions/cancel', endpoint='cancelSubscription')
api.add_resource(SubscriptionStatus,  '/subscription/<string:numeroTelefono>/status/', endpoint='getStatus')
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
    
    return response

@app.route('/api/docs/')
@app.route('/api/docs', endpoint='api-docs')
def api_webdocs():
  return redirect('/api/docs/index.html')

# Proxy setup that works with nginx
app.wsgi_app = ProxyFix(app.wsgi_app)

if __name__ == '__main__':
  app.run()
