from webapp import webApp
from urllib import parse

PAGE = """
<html>
    <body>
        {content}
        <hr>
        {form}
    </body>
</html>
"""

ERR = """
<html>
    <body>
        Error 404 NOT FOUND: {resource}
        <hr>
        {form}
    </body>
</html>
"""

NOT_ALLOWED = """
<html>
    <body>
        Method not found: {resource}
    </body>
</html>
"""

FORM = """
<form action='/' method="post">
    <div>
        <label>Resorce name: </label>
        <input type="text" name="resource" required>
    </div>
    <div>
        <label>Content: </label>
        <input type="text" name="content" required>
    </div>
    <div>
        <input type="submit" value="SEND">
    </div>

</form>
"""


class ContentApp(webApp):

    contents = {
        '/': "<p>Pagina principal<p>",
        "/hola": "<h1>Hola, te saludo</h1>",
        "/adios": "<h2>Adios que lo pases bien</h2>"
    }

    def parse(self, request):
        """Quedarme con el nombre del recurso"""
        data = {}
        body_start = request.find("\r\n\r\n")
        
        if body_start == -1:
            data['body'] = None
        else:
            data['body'] = request[body_start + 4:]  # Adjusted to skip "\r\n\r\n"

        parts = request.split(' ', 2)
        data['method'] = parts[0]
        data['resource'] = parts[1]

        return data

    def get(self, request_resource):
        http_code = "404 Not Found"
        html_pagina = ERR.format(resource=request_resource, form=FORM)
            
        if request_resource in self.contents:
            """Lo tengo en mi diccionario de contenidos"""
            contenido = self.contents[request_resource]
            html_pagina = PAGE.format(content=contenido, form=FORM)
            http_code = "200 OK"

        return http_code, html_pagina

    def put(self, resource, body):
        self.contents[resource] = body
        html_page = PAGE.format(content=body, form=FORM)
        http_code = "200 OK"
        return http_code, html_page
    
    def post(self, resource, body):
        field = parse.parse_qs(body)
        self.contents[field["resource"][0]] = field["content"][0]
        resource_url = field["resource"][0]
        http_code = f"307 Temporary Redirect\r\nLocation: http://localhost:1234{resource_url}"
        html_page = "<html></html>"
        return http_code, html_page

    def procces(self, request_data):
        """Procesa con el recurso la respuesta"""
        if request_data['method'] == 'GET':
            http_code, html_page = self.get(request_data['resource'])
        elif request_data['method'] == 'PUT':
            http_code, html_page = self.put(request_data['resource'], request_data['body'])
        elif request_data['method'] == 'POST':
            http_code, html_page = self.post(request_data['resource'], request_data['body'])
        else:
            http_code = "405 METHOD NOT ALLOWED"
            html_page = NOT_ALLOWED.format(resource=request_data['method'])
        
        return http_code, html_page

if __name__ == "__main__":
    contentapp = ContentApp('', 1234)
