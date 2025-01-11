from azure.storage.blob.aio import BlobServiceClient
from Helpers.CatalogDataHandler import CatalogDataHandler
from Exception.Exception import AzureException
from Helpers.Message import BLOB_STORAGE_SAVE_FAILED, BLOB_STORAGE_DELETE_FAILED, BLOB_STORAGE_DOWNLOAD_FAILED
from Helpers.Constant import STATUS_ERROR, CONNECTION_STRING, CONTAINER_NAME, BLOB_STORAGE

class BlobStorage: 

    def __init__(self):
        self.catalog = CatalogDataHandler().get_catalog_data(BLOB_STORAGE)
        self.blob_service_client = BlobServiceClient.from_connection_string(self.catalog.get(CONNECTION_STRING))
        self.container_client = self.blob_service_client.get_container_client(self.catalog.get(CONTAINER_NAME))

    async def get_file(self, file_path: str) -> bytes:
        try:
            blob_client = self.container_client.get_blob_client(file_path)
            blob_data = await blob_client.download_blob()
            file_bytes = await blob_data.readall()
            return file_bytes

        except Exception as e:
            raise AzureException(message=BLOB_STORAGE_DOWNLOAD_FAILED, error=str(e), status_code=STATUS_ERROR) from e


    async def store_file(self, file_bytes: bytes, file_path: str) -> None:
        try:
            blob_client = self.container_client.get_blob_client(file_path)
            await blob_client.upload_blob(file_bytes, overwrite=True)
        
        except Exception as e:
            raise AzureException(message=BLOB_STORAGE_SAVE_FAILED, error=str(e), status_code=STATUS_ERROR) from e
    

    async def delete_file(self, file_path: str) -> None:
        try:
            blob_client = self.container_client.get_blob_client(file_path)
            await blob_client.delete_blob()

        except Exception as e:
            raise AzureException(message=BLOB_STORAGE_DELETE_FAILED, error=str(e), status_code=STATUS_ERROR) from e