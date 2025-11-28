from flask_swagger_ui import get_swaggerui_blueprint
import json 


def mergeSwaggerFiles(files, output_file):
    # Merges multiple Swagger json files into a single file.
    final = {"openapi":"3.0.0","paths":{}, "components":{}}

    for file in files:
        with open(file) as f:
            data = json.load(f)
            final["paths"].update(data.get("paths", {}))
            final["components"].update(data.get("components", {}))

    with open(output_file, "w") as f:
        json.dump(final, f, indent=2)

mergeSwaggerFiles([
    "static/auth.json",
    #"static/user.json",
    #"static/product.json"
], "static/combined.json")

SWAGGER_URL = "/swagger"
API_URL = "/static/combined.json"
swagger = get_swaggerui_blueprint(SWAGGER_URL, API_URL) 



