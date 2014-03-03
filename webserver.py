# -*- coding: utf-8 -*-
import random
from flask import Flask, redirect, make_response, json
from flask.ext.restful import reqparse, abort, Api, Resource, fields, marshal_with, marshal
from flask_swagger.flask_restful_swagger import swagger

app = Flask(__name__, static_url_path='/api/docs')

apiDescription = """<p>Descripción del API para gestión de seguros. <br/> Todas las respuestas se envían con el formato: </p>
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
      Los campos <b>data</b>, <b>codigo</b> y <b>men***REMOVED***je</b> son opcionales y dependen del <b>status</b> recibido en el header <b>meta</b>
  </p>
  <p>
    <em>powered by <a href="swagger.wordnik.com">Swagger</a> </em>
  </p>
  """

# Swagger generator wrapper
api = swagger.docs(Api(app), apiVersion='0.1.0',
                   basePath='http://localhost:5000',
                   resourcePath='/',
                   produces=["application/json"],
                   api_spec_url='/api/specs',
                   info=dict(
                    title="Seguros API © Grupo TIR, S.A.",
                    description=apiDescription,
                    contact="jdigherob@tir.com.gt",
                  ))


############################
#####  Swagger models ######
# Properties are documented 
# for API description
############################

# Requests
@swagger.model
class SubscriptionBillingOperationFields:
  resource_fields = {
    'id':fields.Integer(default=None),
    'numeroTelefono':fields.String(),
    'numeroCertificado':fields.String(),
    'montoCobro':fields.Float(),
    'fechaHora':fields.DateTime()
  }

@swagger.model
@swagger.nested(requests=SubscriptionBillingOperationFields.__name__)
class SubscriptionBillingRequest:
  """
  """
  resource_fields = {
    'requests':fields.List(fields.Nested(SubscriptionBillingOperationFields.resource_fields))
  }

@swagger.model
class SubscriptionCancellationOperationFields:
  resource_fields = {
    'id':fields.Integer(default=None),
    'numeroTelefono':fields.String(),
    'numeroCertificado':fields.String(),
    'montoCobro':fields.Float(),
    'fechaHora':fields.DateTime(),
    'motivo':fields.String()
  }

@swagger.model
@swagger.nested(requests=SubscriptionCancellationOperationFields.__name__)
class SubscriptionCancellationRequest:
  """
  """
  resource_fields = {
    'requests':fields.List(fields.Nested(SubscriptionCancellationOperationFields.resource_fields))
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
@swagger.nested(status=MetaFields.__name__)
class BaseResponseFields(object):
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
class SubscriptionBillResourceFields:
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
class SubscriptionCancellationResourceFields:
  """
    The list of batch operations that were evaluated as 
    cancelation requests.
  """
  resource_fields = {
    'results':fields.List(fields.Nested(SubscriptionCancellationOperationsFields.resource_fields))
  }

@swagger.model
class SubscriptionStatusResourceFields:
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
  return make_response(json.dumps(marshal(response, BaseResponseFields.resource_fields)), status, headers)


class SubscriptionBilling(Resource):
  @swagger.operation(
    notes="These endpoint can receive from one two many batch requests within the ***REMOVED***me payload. <br/> fechaHora represented in RFC822-formatted datetime string in UTC",
    responseClass=SubscriptionBillResourceFields,
    nickname='billSubscription',
    # Parameters can be automatically extracted from URLs (e.g. <string:id>)
    # but you could also override them here, or add other parameters.
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
                    "mes***REMOVED***ge":"Operación ingre***REMOVED***da éxito***REMOVED***mente."
                  },
                  "errorCode": null,
                  "errorMes***REMOVED***ge": null
                }
              }
            ]
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

  def put(self):
    """
      Evaluate one or more bill requests to be 
      charged to the given subscription.
    """
    pass

class SubscriptionCancellation(Resource):
  @swagger.operation(
    notes="These endpoint can receive from one two many batch requests within the ***REMOVED***me payload. <br/> fechaHora represented in RFC822-formatted datetime string in UTC",
    responseClass=SubscriptionCancellationResourceFields,
    nickname='cancelSubscription',
    # Parameters can be automatically extracted from URLs (e.g. <string:id>)
    # but you could also override them here, or add other parameters.
    parameters=[
      {
        "name": "request",
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
                  "errorMes***REMOVED***ge": null
                }
              }
            ]
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
  def put(self):
    """
      Evaluate one or more cancel requests to be 
      issued to the given subscription.
      args = parser.parse_args()
    
    """
    pass

class SubscriptionStatus(Resource):
  """
    Subscription get status documentation
  """

  """" def __init__(self):
    self.reqparse = reqparse.RequestParser()
    self.reqparse.add_argument('numeroTelefono', type=str, required=True, help='No se ha proporcionado ningún número de teléfono', location='path')
    super(SubscriptionStatus, self).__init__()"""

  @swagger.operation(
      notes="Inquiry on the status of a given telephone's subscription",
      responseClass=SubscriptionStatusResourceFields,
      nickname='getStatus',
      # Parameters can be automatically extracted from URLs (e.g. <string:id>)
      # but you could also override them here, or add other parameters.
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
  def put(self):
    pass
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
  def post():
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

if __name__ == '__main__':
  app.run(debug=True)