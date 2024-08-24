import os

from dotenv import load_dotenv
from google.api_core.client_options import ClientOptions
from google.cloud import documentai

load_dotenv()
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("PROJECT_LOCATION")  # Format is 'us' or 'eu'
PROCESSOR_ID = os.getenv("PROCESSOR_ID")  # Create processor in Cloud Console

# The local file in your current working directory
FILE_PATH = "sample.pdf"
# Refer to https://cloud.google.com/document-ai/docs/file-types
# for supported file types
MIME_TYPE = "application/pdf"

# Instantiates a client
docai_client = documentai.DocumentProcessorServiceClient(
    client_options=ClientOptions(api_endpoint=f"{LOCATION}-documentai.googleapis.com")
)

# The full resource name of the processor, e.g.:
# projects/project-id/locations/location/processor/processor-id
# You must create new processors in the Cloud Console first
RESOURCE_NAME = docai_client.processor_path(PROJECT_ID, LOCATION, PROCESSOR_ID)

# Read the file into memory
with open(FILE_PATH, "rb") as image:
    image_content = image.read()

# Load Binary Data into Document AI RawDocument Object
raw_document = documentai.RawDocument(content=image_content, mime_type=MIME_TYPE)

# Configure the process request
request = documentai.ProcessRequest(name=RESOURCE_NAME, raw_document=raw_document)

# Use the Document AI client to process the sample form
result = docai_client.process_document(request=request)

document_object = (
    result.document
)  # https://cloud.google.com/python/docs/reference/documentai/latest/google.cloud.documentai_v1beta3.types.Document

print("Document processing complete.")
print(f"Text: {document_object.text}")
print(document_object.document_layout)
