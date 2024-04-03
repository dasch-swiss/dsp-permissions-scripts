import toml

def get_package_name() -> str:
    with open('pyproject.toml', 'r') as file:
        config = toml.load(file)
        package_name: str = config['tool']['poetry']['name']
        return package_name
