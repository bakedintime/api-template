# -*- coding: utf-8 -*-
import random
from flask import Flask, redirect, make_response, json
from flask.ext.restful import reqparse, abort, Api, Resource, fields, marshal_with, marshal
from flask_swagger.flask_restful_swagger import swagger

app = Flask(__name__, static_url_path='/api/docs')

# Swagger generator wrapper
api = swagger.docs(Api(app), apiVersion='0.1.0',
                   basePath='http://localhost:5000',
                   resourcePath='/',
                   produces=["application/json"],
                   api_spec_url='/api/specs',
                   info=dict(
                    title="Seguros API © Grupo TIR, S.A.",
                    description="This is a ***REMOVED***mple server Petstore server.  You can find out more about Swagger \n    at <a href=\"http://swagger.wordnik.com\">http://swagger.wordnik.com</a> or on irc.freenode.net, #swagger.  For this ***REMOVED***mple,\n    you can use the api key \"special-key\" to test the authorization filters",
                    contact="apiteam@tir.com.gt",
                    license="Apache 2.0",
                    licenseUrl="http://www.apache.org/licenses/LICENSE-2.0.html"
                  ))


TODOS = {
    'todo1': {'task': 'build an API'},
    'todo2': {'task': '?????'},
    'todo3': {'task': 'profit!'},
}


def abort_if_todo_doesnt_exist(todo_id):
  if todo_id not in TODOS:
    abort(404, mes***REMOVED***ge="Todo {} doesn't exist".format(todo_id))

parser = reqparse.RequestParser()
parser.add_argument('task', type=str)


@swagger.model
class TodoItem:
  """This is an example of a model class that has parameters in its constructor
  and the fields in the swagger spec are derived from the parameters
  to __init__.
  In this case we would have args, arg2 as required parameters and arg3 as
  optional parameter."""
  def __init__(self, arg1, arg2, arg3='123'):
    pass


@swagger.model
class ModelWithResourceFields:
  resource_fields = {
      'a_string': fields.String()
  }

@swagger.model
@swagger.nested(
   a_nested_attribute=ModelWithResourceFields.__name__,
   a_list_of_nested_types=ModelWithResourceFields.__name__)
class TodoItemWithResourceFields:
  """This is an example of how Output Fields work
  (http://flask-restful.readthedocs.org/en/latest/fields.html).
  Output Fields lets you add resource_fields to your model in which you specify
  the output of the model when it gets sent as an HTTP response.
  flask-restful-swagger takes advantage of this to specify the fields in
  the model"""
  resource_fields = {
      'a_string': fields.String(attribute='a_string_field_name'),
      'a_formatted_string': fields.FormattedString,
      'an_int': fields.Integer,
      'a_bool': fields.Boolean,
      'a_url': fields.Url,
      'a_float': fields.Float,
      'an_float_with_arbitrary_precision': fields.Arbitrary,
      'a_fixed_point_decimal': fields.Fixed,
      'a_datetime': fields.DateTime,
      'a_list_of_strings': fields.List(fields.String),
      'a_nested_attribute': fields.Nested(ModelWithResourceFields.resource_fields),
      'a_list_of_nested_types': fields.List(fields.Nested(ModelWithResourceFields.resource_fields)),
  }

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


def wrap_response(response, status, headers):
  return make_response(json.dumps(marshal(response, BaseResponseFields.resource_fields)), status, headers)


  @swagger.operation(
          }
          },
          }

  def put(self):
    """
      Evaluate one or more bill requests to be 
      charged to the given subscription.
    """
    pass

class SubscriptionCancellation(Resource):
  def patch(self):
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
      description='Operations about things',
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
            "errorCode": "null",
            "errorMes***REMOVED***ge": "null",
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
            "errorCode": "null",
            "errorMes***REMOVED***ge": "null",
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
            "errorCode": "null",
            "errorMes***REMOVED***ge": "null",
            "meta": {
              "status": "fail"
            }
          }</pre>"""
        },
        {
          "code": 500,
          "mes***REMOVED***ge": """<pre>
          {
            "data": "null",
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

api.add_resource(SubscriptionBilling, '/subscriptions/charge', endpoint='chargeSubscription')
api.add_resource(SubscriptionCancellation, '/subscriptions/cancel', endpoint='cancelSubscription')
api.add_resource(SubscriptionStatus,  '/subscriptions/status/<string:numeroTelefono>', endpoint='getStatus')
api.add_resource(SubscriptionClaim, '/subscriptions/claim', endpoint='ClaimSubscription')


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
  TodoItemWithResourceFields()
  TodoItem(1, 2, '3')
  app.run(debug=True)