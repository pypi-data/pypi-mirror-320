from factory_sdk.datasets.hf import load as load_hf, fingerprint as fingerprint_hf
from tempfile import TemporaryDirectory
from datasets import load_from_disk, load_dataset
from tqdm_joblib import tqdm_joblib
from joblib import Parallel, delayed
from glob import glob
import os
from hashlib import md5
from uuid import uuid4
from typing import Optional
from factory_sdk.exceptions.api import *
from factory_sdk.dto.dataset import DatasetInitData, DatasetMeta, DatasetRevision, DatasetObject
from factory_sdk.dto.resource import FactoryRevisionState, FactoryMetaState
import json
from rich import print


class Datasets:
    def __init__(self, client):
        self.client = client

    def upload_dataset(self, factory_name, dataset_path, dataset: Optional[DatasetMeta], fingerprints={}, max_parallel_upload=8):
        if dataset is None:
            print("[green]🤖 Creating a new dataset in your factory instance...[/green]")
            dataset: DatasetMeta = self.client.post(
                f"datasets",
                DatasetInitData(name=factory_name),
                response_class=DatasetMeta
            )
        else:
            print("[cyan]🤖 Creating a new dataset revision in your factory instance...[/cyan]")

        revision: DatasetRevision = self.client.post(
            f"datasets/{dataset.id}/revisions",
            {}, response_class=DatasetRevision
        )

        files = glob(f"{dataset_path}/**", recursive=True)
        files = [file for file in files if os.path.isfile(file)]
        file_paths = [os.path.relpath(file, dataset_path) for file in files]

        print("[green]📦 Uploading files...[/green]")
        with tqdm_joblib(total=len(files)):
            Parallel(n_jobs=max_parallel_upload)(
                delayed(self.client.put_file)(
                    f"datasets/{dataset.id}/revisions/{revision.id}/files/{file_path}",
                    file
                )
                for file, file_path in zip(files, file_paths)
            )

        revision.state = FactoryRevisionState.READY
        revision.ext_fingerprints = fingerprints

        #put the updated revision
        revision:DatasetRevision=self.client.put(
            f"datasets/{dataset.id}/revisions/{revision.id}",
            revision, response_class=DatasetRevision
        )

        # Update the dataset state
        dataset.state = FactoryMetaState.READY
        dataset.last_revision = revision.id
        dataset:DatasetMeta=self.client.put(
            f"datasets/{dataset.id}",
            dataset,response_class=DatasetMeta
        )

        print("[bold green]🎉 Dataset uploaded to the Factory successfully![/bold green]")
        return dataset, revision

    def should_create_revision(self, hf_fingerprint: str, dataset: DatasetMeta, revision: DatasetRevision):

        if dataset is None:
            return True
        if revision is None:
            return True
        if revision.state == FactoryRevisionState.FAILED:
            return True
        if dataset.state != FactoryMetaState.READY:
            return True
        if "huggingface" not in revision.ext_fingerprints:
            return True
        if revision.ext_fingerprints["huggingface"] != hf_fingerprint:
            return True
        return False

    def from_huggingface(self, name, huggingface_name, huggingface_token=None, huggingface_config=None):

        hf_fingerprint = fingerprint_hf(huggingface_name, huggingface_token)

        try:
            dataset: DatasetMeta = self.client.get(
                f"tenants/{self.client._tenant.id}/projects/{self.client._project.id}/datasets/{name}", response_class=DatasetMeta,
                scope="names"
            )
            if dataset.last_revision is not None:
                revision: DatasetRevision = self.client.get(
                    f"datasets/{dataset.id}/revisions/{dataset.last_revision}",
                    response_class=DatasetRevision
                )
            else:
                revision = None
        except NotFoundException:
            dataset = None
            revision = None

        if self.should_create_revision(hf_fingerprint, dataset, revision):
            with TemporaryDirectory() as tempdir:
                hf_fingerprint = load_hf(
                    huggingface_name,
                    huggingface_token,
                    huggingface_config,
                    tempdir
                )
                dataset, revision = self.upload_dataset(
                    name,
                    tempdir,
                    dataset,
                    fingerprints={"huggingface": hf_fingerprint},
                    max_parallel_upload=8
                )
        else:
            print("[bold yellow]✅ Current dataset revision matches the HuggingFace fingerprint. No new revision needed.[/bold yellow]")

        return DatasetObject(meta=dataset, revision=revision)
