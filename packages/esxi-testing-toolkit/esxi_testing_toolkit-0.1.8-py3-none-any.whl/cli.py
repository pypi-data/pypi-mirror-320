# import base packages
import typer
import requests
import logging

# import core components
from core.connection import ESXiConnection
from core.config_manager import retrieve_secrets

# used to suppress insecure request warnings from requests
from urllib3.exceptions import InsecureRequestWarning

# suppress insecure request warning for self-signed SSL cert in ESXi hosts.
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# logging boilerplate
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,format='%(asctime)s | %(levelname)-5s | %(message)s')

# typer boilerplate
app = typer.Typer()

# Get secrets
secrets = retrieve_secrets()

# Attempt connection to ESXi host using provided information
logging.info(f'Attempting to connect to {secrets['host']} as {secrets['username']}')
# Create connection to ESXi Host
connection = ESXiConnection(
    host=secrets['host'],
    username=secrets['username'],
    password=secrets['password'],
    verify_ssl=False
)
connection.connect_api()

# Generic CLI command so Typer still works.
@app.command()
def hello_world(name: str):
    print(f"Hello {name}")

@app.command()
def delete_vm_snapshot(vm_id: str):
    """
    Deletes all snapshots for a given VM.
    
    :param: connection: ESXiConnection object.
    :param: vm_id
    :returns: True if successful, False is unsuccessful.
    """
    logger.info(f'Sending request to delete snapshots for vm: {vm_id}')
    with open('./payloads/delete_snapshots.xml') as f:
        payload = f.readlines()
    logging.info(f'Parsed {payload} from ./payloads/delete_snapshots.xml')
    request = connection.send_request(payload=payload)
    
    
# app entrypoint
def main():    
    # start Typer app
    app()
    
if __name__ == "__main__":
    main()