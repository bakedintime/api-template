from flask import Response
from jinja2 import Template

def render_endpoint(endpoint):
  template = Template(endpoint_html)
  return Response(template.render(endpoint.__dict__), mimetype='text/html')

def render_homepage(resource_list_url):
  template = Template(homepage_html)
  conf = {'resource_list_url': resource_list_url}
  return Response(template.render(conf), mimetype='text/html')

homepage_html = """
<!DOCTYPE html>
<html>
<head>
  <title>Seguros API</title>
  <link href='//fonts.googleapis.com/css?family=Droid+Sans:400,700' rel='stylesheet' type='text/css'/>
  <link href='docs/css/highlight.default.css' media='screen' rel='stylesheet' type='text/css'/>
  <link href='docs/css/screen.css' media='screen' rel='stylesheet' type='text/css'/>
  <style type="text/css">
    ul.links a {
      line-height: 25px;
      color: #fff;
      font-weight: bolder;
      text-decoration: none;
    }
    ul.links a:hover {
      text-decoration: underline;
    }
    ul.links li:before {
     color: #fff;
     content: "\00BB";
    }
  </style>
</head>
<body>
<div id='header'>
  <div class="swagger-ui-wrap">
    <a id="logo">Seguros API</a>
    <form id='api_selector'>
      <div class='input'><input placeholder="http://example.com/api" id="input_baseUrl" name="baseUrl" type="text"/></div>
      <div class='input'><input disabled='disabled' placeholder="api_key" id="input_apiKey" name="apiKey" type="text"/></div>
      <div class='input'><a id="explore" href="#">Explore</a></div>
    </form>
  </div>
</div>
<div id="message-bar" class="swagger-ui-wrap">&nbsp;</div>
<div id="swagger-ui-container" class="swagger-ui-wrap"></div>
  <script type="text/javascript" src="docs/lib/shred.bundle.js"></script>
  <script src='docs/lib/jquery-1.8.0.min.js' type='text/javascript'></script>
  <script src='docs/lib/jquery.slideto.min.js' type='text/javascript'></script>
  <script src='docs/lib/jquery.wiggle.min.js' type='text/javascript'></script>
  <script src='docs/lib/jquery.ba-bbq.min.js' type='text/javascript'></script>
  <script src='docs/lib/handlebars-1.0.0.js' type='text/javascript'></script>
  <script src='docs/lib/underscore-min.js' type='text/javascript'></script>
  <script src='docs/lib/backbone-min.js' type='text/javascript'></script>
  <script src='docs/lib/swagger.js' type='text/javascript'></script>
  <script src='docs/lib/swagger-ui.js' type='text/javascript'></script>
  <script src='docs/lib/highlight.7.3.pack.js' type='text/javascript'></script>
  <script type="text/javascript" src="docs/lib/jquery.noty.packaged.min.js"></script>
  <script type="text/javascript">
    $(function () {
      window.swaggerUi = new SwaggerUi({
      url: "{{resource_list_url}}",
      dom_id: "swagger-ui-container",
      supportedSubmitMethods: ['get', 'post', 'put', 'delete'],
      onComplete: function(swaggerApi, swaggerUi){
        $('pre code').each(function(i, e) {hljs.highlightBlock(e)});
      },
      onFailure: function(data) {
        if(console) {
          console.log("Unable to Load SwaggerUI");
          console.log(data);
        }
      },
      docExpansion: "none"
    });
    $('#input_apiKey').change(function() {
      var key = $('#input_apiKey')[0].value;
      console.log("key: " + key);
      if(key && key.trim() != "") {
        console.log("added key " + key);
        window.authorizations.add("key", new ApiKeyAuthorization("api_key", key, "query"));
      }
    });
    $(document).on('click', '#addHeader', function(){
      if ($('#input_username')[0].value==='' || $('#input_password')[0].value===''){
        var notySuccess = noty({
          text: '<p style="font-family:\\'PT Sans\\', Georgia, Palatino, \\'Palatino Linotype\\', Times, \\'Times New Roman\\', serif;">No username or password defined.</p>',
          type: 'warning',
          timeout: 1000,
          layout: 'top',
          closeWith: ['click']
        });
        return false;
      }
      var username = $('#input_username')[0].value;
      var password = $('#input_password')[0].value;
      var encodedString = 'Basic '+ btoa(username + ':' + password);
      window.authorizations.add("basicAuth", new ApiKeyAuthorization("Authorization", encodedString, "header"));
      var notySuccess = noty({
        text: '<p style="font-family:\\'PT Sans\\', Georgia, Palatino, \\'Palatino Linotype\\', Times, \\'Times New Roman\\', serif;">The authorization header has been successfully assigned - Authorization: '+encodedString+'</p>',
        type: 'success',
        timeout: 1000,
        layout: 'top',
        closeWith: ['click']
      });
      return false;
    });
    $(document).on('click', '#verifyHeader', function(){
      var _auth;
      if (window.authorizations.authz.basicAuth === undefined){
        _auth = ' not yet defined';
      }else{
        _auth = window.authorizations.authz.basicAuth.value;
      }
      var notySuccess = noty({
        text: '<p style="font-family:\\'PT Sans\\', Georgia, Palatino, \\'Palatino Linotype\\', Times, \\'Times New Roman\\', serif;">The authorization header is '+_auth+'</p>',
        type: 'success',
        timeout: 2500,
        layout: 'top',
        closeWith: ['click']
      });
      return false;
    });
    window.swaggerUi.load();
  });
  </script>
</body>
</html>
"""

endpoint_html = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Api Docs for {{path}}</title>
    <link rel="stylesheet" href="//netdna.bootstrapcdn.com/bootstrap/3.0.3/css/bootstrap.min.css">
    <style>
      body {margin-top: 60px;}
    </style>
  </head>
  <body>
    <nav class="navbar navbar-inverse navbar-fixed-top" role="navigation">
      <div class="container">
        <div class="navbar-header">
          <button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-ex1-collapse">
            <span class="sr-only">Toggle navigation</span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </button>
        </div>
        <!-- Collect the nav links, forms, and other content for toggling -->
        <div class="collapse navbar-collapse navbar-ex1-collapse">
          <ul class="nav navbar-nav">
            {% for operation in operations %}
              <li><a href="#{{operation.method}}">{{operation.method}}</a></li>
            {% endfor %}
          </ul>
        </div><!-- /.navbar-collapse -->
      </div><!-- /.container -->
    </nav>
    <div class="container">
      <div class="row">
        <div class="col-lg-12">
          <h1>{{path}}</h1>
          <p class='lead'>{{description if description != None}}</p>
        </div>
        <div class="col-lg-12">
        {% for operation in operations %}
          <div class="panel panel-success" id='{{operation.method}}'>
            <div class="panel-heading">
              <h3 class="panel-title">{{operation.method}}</h3>
              <p>{{operation.summary if operation.summary != None}}</p>
            </div>
            <div class="panel-body">
              {% if operation.parameters %}
                <h4>Parameters</h4>
                <dl>
                  {% for parameter in operation.parameters %}
                    <dt>
                      {{parameter.name}}
                      {% if parameter.description %}
                        - {{parameter.description}}
                      {% endif %}
                    </dt>
                    <dd>Type: {{parameter.dataType}}</dd>
                    <dd>Allow Multiple: {{parameter.allowMultiple}}</dd>
                    <dd>Required: {{parameter.required}}</dd>
                  {% endfor %}
                </dl>
              {% endif %}
              {% if operation.notes %}
                <p><strong>Implementation notes</strong>: {{operation.notes}}</p>
              {% endif %}
              {% if operation.responseClass %}
                <p><strong>Response Class</strong>: {{operation.responseClass}}</p>
              {% endif %}
            </div>
          </div>
        {% endfor %}
      </div>
    </div><!-- /.container -->
    <script src="docs/lib/jquery.min.js"></script>
    <script src="docs/lib/bootstrap.min.js"></script>
  </body>
</html>
"""
