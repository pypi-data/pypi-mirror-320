from factory_sdk.datasets import Datasets
from factory_sdk.models import Models
from factory_sdk.adapters import Adapters
from factory_sdk.metrics import Metrics
from factory_sdk.preprocessors import Preprocessors
from factory_sdk.dto.project import Project
from factory_sdk.dto.tenant import Tenant
import requests
from pydantic import BaseModel
from factory_sdk.logging import logger
from typing import Optional, Type, Any
import os
from factory_sdk.exceptions.api import NotFoundException,GeneralAPIException,ConflictException,AuthenticationException
from factory_sdk.dto_old.state import FactoryState
import time
from rich import print
import math
from joblib import Parallel, delayed
from tqdm_joblib import tqdm_joblib
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial
from hashlib import sha256
from factory_sdk.exceptions.api import FileUploadException

import logging

logging.getLogger("requests").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)

# Import tqdm for progress bar
from tqdm.auto import tqdm

# Optional: If you can install external libraries
try:
    from requests_toolbelt.multipart.encoder import MultipartEncoder, MultipartEncoderMonitor
except ImportError:
    MultipartEncoder = None
    MultipartEncoderMonitor = None

class FactoryClient:
    def __init__(self,tenant:str, project: str, token:str, host: str="https://localhost:8443", verify_ssl: bool = True):
        """
        Initialize the FactoryClient with project, host, port, and SSL settings.
        """
        
        self._host = host
        self._token=token
        self.datasets = Datasets(client=self)
        self.models = Models(client=self)
        self.adapters = Adapters(client=self)
        self.metrics = Metrics(client=self)
        self.preprocessors = Preprocessors(client=self)
        self._session = requests.Session()  # Use a session for performance and connection pooling
        self._verify_ssl = verify_ssl
        
        tenant,project=self._init(tenant,project)
        self._tenant:Tenant=tenant
        self._project:Project=project

        #print sucessuffly connetced
        print(f"🛸 FactoryClient is successfully connected and starts working on project [bold blue]{project.name}[/bold blue]\n")


    def _init(self,tenant,project):
        #fetch project and tenant id
        tenant:Tenant=self.get(f"tenants/{tenant}",response_class=Tenant,scope="names")
        try:
            project=self.get(f"tenants/{tenant.id}/projects/{project}",response_class=Project,scope="names")
        except NotFoundException:
            #create project
            print(f"Project [bold blue]{project}[/bold blue] not found. Creating new project...")
            self._tenant=tenant
            project=self.post(f"projects",Project(name=project,tenant=tenant.id),response_class=Project,scope="tenant")
        return tenant,project

    def _api_url(self,scope="project") -> str:
        """
        Construct the base API URL based on the host, port, SSL, and project.
        """

        if scope=="names":
            return f"{self._host}/api/1/names"
        if scope=="tenant":
            return f"{self._host}/api/1/tenants/{self._tenant.id}"
        return f"{self._host}/api/1/tenants/{self._tenant.id}/projects/{self._project.id}"

    def _request(self, method: str, path: str,scope="project", **kwargs) -> Any:
        """
        Internal method to handle HTTP requests.

        Args:
            method (str): HTTP method ('GET', 'POST', 'PUT', etc.).
            path (str): API endpoint path.
            **kwargs: Additional arguments to pass to the request.

        Returns:
            Any: The response JSON or content.
        """
        url = f"{self._api_url(scope=scope)}/{path}"
        res = self._session.request(method, url,headers={
            "Authorization":f"Bearer {self._token}"
        },verify=self._verify_ssl,**kwargs)

        if res.status_code == 404:
            raise NotFoundException(f"Resource not found: {method} {path}")
        elif res.status_code == 409:
            raise ConflictException(f"Conflict: {method} {path}")
        elif res.status_code == 401:
            raise AuthenticationException(f"Authentication failed: {method} {path}")
        if res.status_code != 200 and res.status_code != 201:
            try:
                error_msg = res.json()
                logger.error(error_msg)
                raise GeneralAPIException(error_msg)
            except ValueError:
               raise GeneralAPIException(f"Failed to {method} {path}. Status code: {res.status_code}")

        try:
            return res.json()
        except ValueError:
            return res.content  # Return raw content if response is not JSON
        
    # def wait(self, path: str, timeout=360) -> None:
    #     start=time.time()
    #     while time.time()-start<timeout:
    #         url=f"{self._api_url}/{path}"
    #         res=self._session.get(url,headers={
    #             "Authorization":f"Bearer {self._token}"
    #         })
    #         if res.status_code==200:
    #             return
    #         elif res.status_code==408:
    #             time.sleep(1)
    #         else:
    #             raise GeneralAPIException(res.text)
    #             #raise GeneralAPIException(f"Failed to wait for {path}. Status code: {res.status_code}")
    #     raise Exception(f"Timeout waiting for {path}")

    def get(self, path: str, response_class: Optional[Type[BaseModel]] = None,scope="project") -> Any:
        """
        Perform a GET request to the specified path.

        Args:
            path (str): The API endpoint path.
            response_class (Type[BaseModel], optional): Pydantic model class to parse the response.

        Returns:
            Any: The parsed response or raw JSON.
        """
        res_json = self._request('GET', path,scope=scope)
        if response_class and res_json:
            return response_class(**res_json)
        return res_json

    def post(self, path: str, data: BaseModel, response_class: Optional[Type[BaseModel]] = None,scope="project") -> Any:
        """
        Perform a POST request to the specified path with the provided data.

        Args:
            path (str): The API endpoint path.
            data (BaseModel): The data to send in the POST request.
            response_class (Type[BaseModel], optional): Pydantic model class to parse the response.

        Returns:
            Any: The parsed response or raw JSON.
        """
        res_json = self._request('POST', path, json=data.model_dump() if data else None,scope=scope)
        if response_class and res_json:
            return response_class(**res_json)
        return res_json
    
    def put(self, path: str, data: BaseModel, response_class: Optional[Type[BaseModel]] = None,scope="project") -> Any:
        """
        Perform a PUT request to the specified path with the provided data.

        Args:
            path (str): The API endpoint path.
            data (BaseModel): The data to send in the PUT request.
            response_class (Type[BaseModel], optional): Pydantic model class to parse the response.

        Returns:
            Any: The parsed response or raw JSON.
        """
        res_json = self._request('PUT', path, json=data.model_dump(),scope=scope)
        if response_class and res_json:
            return response_class(**res_json)
        return res_json


    def upload_file(
        self, 
        url, 
        file_path, 
        scope="project", 
        buffer_size=64 * 1024 * 1024,  # 64MB
        max_workers=4
    ):
        """
        Uploads a file in parts to the specified URL using parallel uploads without
        loading all parts into memory at once.
        
        Parameters:
        - url (str): The endpoint URL for the upload.
        - file_path (str): The path to the file to be uploaded.
        - scope (str): The scope of the upload, default is "project".
        - buffer_size (int): The size of each upload chunk in bytes, default is 64MB.
        - max_workers (int): The maximum number of parallel upload threads.
        """
        try:
            file_size = os.path.getsize(file_path)
        except OSError as e:
            raise Exception(f"Failed to get file size: {e}")

        upload_url = f"{self._api_url(scope=scope)}/{url}"

        digest = sha256()

        with requests.Session() as session:
            # Initiate the upload session
            upload_id = None

            try:
            
                res = session.post(
                        upload_url,
                        headers={
                            "Authorization": f"Bearer {self._token}"
                        },
                        verify=self._verify_ssl
                )
                res.raise_for_status()
                upload_id = res.json()["upload_id"]

                part_url_base = f"{upload_url}/parts/{upload_id}"

                # Initialize the progress bar
                pbar = tqdm(total=file_size, unit="B", unit_scale=True, desc=os.path.basename(file_path))
                
                # Function to upload a single part
                def upload_part(part_number, part_data):
                    part_url = f"{part_url_base}/{part_number}"
                    try:
                        response = session.put(
                            part_url,
                            headers={
                                "Authorization": f"Bearer {self._token}"
                            },
                            data=part_data,
                            verify=self._verify_ssl
                        )
                        response.raise_for_status()
                        return len(part_data)
                    except requests.RequestException as e:
                        raise Exception(f"Upload failed at part {part_number}: {e}")

                # Manage concurrent uploads with limited memory usage
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    futures = {}
                    part_number = 0
                    try:
                        with open(file_path, "rb") as f:
                            while True:
                                part = f.read(buffer_size)
                                digest.update(part)
                                if not part:
                                    break
                                part_number += 1
                                # Submit the upload task
                                future = executor.submit(upload_part, part_number, part)
                                futures[future] = part_number

                                # If we reach max_workers, wait for the first to complete
                                if len(futures) >= max_workers:
                                    done = next(as_completed(futures))
                                    bytes_uploaded = done.result()
                                    pbar.update(bytes_uploaded)
                                    # Remove the completed future
                                    del futures[done]

                        # After submitting all parts, wait for remaining futures
                        for future in as_completed(futures):
                            bytes_uploaded = future.result()
                            pbar.update(bytes_uploaded)

                    except Exception as e:
                        pbar.close()
                        raise e

                pbar.close()

                fingerprint = digest.hexdigest()

                # Complete the upload
                complete_url = f"{upload_url}/complete/{upload_id}"
                res = session.post(
                        complete_url,
                        headers={
                            "Authorization": f"Bearer {self._token}"
                        },
                        json={"fingerprint": fingerprint},
                        verify=self._verify_ssl
                    )
                res.raise_for_status()
            except Exception as e:
                if upload_id is not None:
                    try:
                        cancel_url = f"{upload_url}/abort/{upload_id}"
                        res = session.post(
                            cancel_url,
                            headers={
                                "Authorization": f"Bearer {self._token}"
                            },
                            verify=self._verify_ssl
                        )
                        res.raise_for_status()
                        print("Upload cancelled.")
                    except Exception as e:
                        print(f"Failed to cancel upload: {e}")
                
                raise FileUploadException(f"Failed to upload file")
                
