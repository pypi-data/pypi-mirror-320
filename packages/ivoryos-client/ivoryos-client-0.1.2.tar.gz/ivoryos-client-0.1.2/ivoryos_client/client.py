import argparse
import requests

session = requests.Session()

def check_url_availability(url):
    try:
        response = session.get(url, timeout=5)
        if response.status_code != 200:
            raise ConnectionError(f"Server responded with status code {response.status_code}")
    except requests.RequestException as e:
        raise ConnectionError(f"Failed to connect to the server at {url}: Make sure to start the ivoryOS "
                              f"first and use the correct URL (http://xx.xx.xx.xx:port). Error: {e}")

# Function to create class and methods dynamically
def create_function(url, url_prefix, class_name, functions):
    class_template = f'class {class_name.capitalize()}:\n    url = "{url}/{url_prefix}/backend_control/deck.{class_name}"\n'

    for function_name, details in functions.items():
        signature = details['signature']
        docstring = details.get('docstring', '')

        # Creating the function definition
        method = f'    def {function_name}{signature}:\n'
        if docstring:
            method += f'        """{docstring}"""\n'

        # Generating the session.post code for sending data
        method += '        return session.post(self.url, data={'
        method += f'"hidden_name": "{function_name}"'

        # Extracting the parameters from the signature string for the data payload
        param_str = signature[6:-1]  # Remove the "(self" and final ")"
        params = [param.strip() for param in param_str.split(',')] if param_str else []

        for param in params:
            param_name = param.split(':')[0].strip()  # Split on ':' and get parameter name
            method += f', "{param_name}": {param_name}'

        method += '}).json()\n'
        class_template += method + '\n'

    return class_template

# Function to export the generated classes to a Python script
def export_to_python(class_definitions):
    with open('generated_classes.py', 'w') as f:
        # Writing the imports at the top of the script
        f.write('import requests\n\n')
        f.write('session = requests.Session()\n\n')

        # Writing each class definition to the file
        for class_name, class_def in class_definitions.items():
            f.write(class_def)
            f.write('\n')

        # Creating instances of the dynamically generated classes
        for class_name in class_definitions.keys():
            instance_name = class_name.lower()  # Using lowercase for instance names
            f.write(f'{instance_name} = {class_name.capitalize()}()\n')

def generate_proxy_script(url, url_prefix="ivoryos"):
    try:
        snapshot = session.get(f"{url}/{url_prefix}/backend_control").json()
    except requests.RequestException as e:
        raise ConnectionError(f"Failed to connect to the ivoryOS server at {url}: Make sure to start the ivoryOS "
                              f"first and use the correct URL.")
    class_definitions = {}
    for class_path, functions in snapshot.items():
        class_name = class_path.split('.')[-1]  # Extracting the class name from the path
        class_definitions[class_name.capitalize()] = create_function(url, url_prefix, class_name, functions)

    # Export the generated class definitions to a .py script
    export_to_python(class_definitions)

def main():
    parser = argparse.ArgumentParser(description="API generation from SDL snapshot on IvoryOS server")
    parser.add_argument('url', type=str, help='The URL to connect to the server')
    parser.add_argument('--url_prefix', type=str, help='The URL prefix.', default='ivoryos')
    args = parser.parse_args()

    # Now use the URL in your script
    url = args.url
    url_prefix = args.url_prefix

    try:
        # Check if the URL is active
        check_url_availability(url)

        generate_proxy_script(url, url_prefix=url_prefix)
    except ConnectionError as e:
        print(e)

if __name__ == "__main__":
    main()