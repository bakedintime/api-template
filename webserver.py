from flask import Flask, redirect
from flask.ext.restful import reqparse, abort, Api, Resource, fields, marshal_with
# -*- coding: utf-8 -*-
from flask_restful_swagger import swagger

app = Flask(__name__, static_url_path='/api/docs')

# Swagger generator wrapper
api = swagger.docs(Api(app), apiVersion='0.1.0',
                   basePath='http://localhost:5000',
                   resourcePath='/',
                   produces=["application/json"],
                   api_spec_url='/api/specs')


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

@swagger.model
class SubscriptionStatusResourceFields:
  """
    Properties of the response when 
    querying the current status of a 
    subscription. 
  """
  resource_fields = {
    'numeroCertificado':fields.String(),
    'numeroTelefono':fields.String,
    'nombreCompleto':fields.String,
    'CUI':fields.String,
    'codigoReclamo':fields.String,
    'cobertura':fields.Float
  }

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


class Todo(Resource):
  "My TODO API"
  @swagger.operation(
      notes='get a todo item by ID',
      responseClass=TodoItemWithResourceFields,
      nickname='get',
      # Parameters can be automatically extracted from URLs (e.g. <string:id>)
      # but you could also override them here, or add other parameters.
      parameters=[
          {
            "name": "todo_id_x",
            "description": "The ID of the TODO item",
            "required": True,
            "allowMultiple": False,
            "dataType": 'string',
            "paramType": "path"
          },
          {
            "name": "a_bool",
            "description": "The ID of the TODO item",
            "required": True,
            "allowMultiple": False,
            "dataType": 'boolean',
            "paramType": "path"
          }
      ])
  @marshal_with(TodoItemWithResourceFields.resource_fields)
  def get(self, todo_id):
    # This goes into the summary
    "Get a todo task"
    abort_if_todo_doesnt_exist(todo_id)
    return TODOS[todo_id]

  def delete(self, todo_id):
    abort_if_todo_doesnt_exist(todo_id)
    del TODOS[todo_id]
    return '', 204

  def put(self, todo_id):
    args = parser.parse_args()
    task = {'task': args['task']}
    TODOS[todo_id] = task
    return task, 201


# TodoList
#   shows a list of all todos, and lets you POST to add new tasks
class TodoList(Resource):

  def get(self):
    return TODOS

  @swagger.operation(
      notes='Creates a new TODO item',
      responseClass=TodoItem.__name__,
      nickname='create',
      parameters=[
          {
            "name": "body",
            "description": "A TODO item",
            "required": True,
            "allowMultiple": False,
            "dataType": TodoItem.__name__,
            "paramType": "body"
          }
      ],
      responseMes***REMOVED***ges=[
          {
              "code": 201,
              "mes***REMOVED***ge": "Created. The URL of the created blueprint should " +
              "be in the Location header"
          },
          {
              "code": 405,
              "mes***REMOVED***ge": "Invalid input"
          }
      ])
  def post(self):
    args = parser.parse_args()
    todo_id = 'todo%d' % (len(TODOS) + 1)
    TODOS[todo_id] = {'task': args['task']}
    return TODOS[todo_id], 201

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