"""
Makes a Batch Processing Request to Document AI using Document AI Toolbox
"""

import os

from dotenv import load_dotenv
from google.api_core.client_options import ClientOptions
from google.cloud import documentai, documentai_toolbox

# TODO(developer): Fill these variables before running the sample.
load_dotenv()
project_id = os.getenv("PROJECT_ID")
location = os.getenv("PROJECT_LOCATION")  # Format is 'us' or 'eu'
processor_id = os.getenv("PROCESSOR_ID")  # Create processor in Cloud Console
gcs_output_uri = os.getenv(
    "YOUR_OUTPUT_URI"
)  # Must end with a trailing slash `/`. Format: gs://bucket/directory/subdirectory/
processor_version_id = os.getenv(
    "YOUR_PROCESSOR_VERSION_ID"  # Optional. Example: pretrained-ocr-v1.0-2020-09-23
)

# TODO(developer): If `gcs_input_uri` is a single file, `mime_type` must be specified.
gcs_input_uri = "gs://ocr-example-d6f3f772/Winnie_the_Pooh.pdf"  # Format: `gs://bucket/directory/file.pdf` or `gs://bucket/directory/`
input_mime_type = "application/pdf"
field_mask = "text,entities,pages.pageNumber"  # Optional. The fields to return in the Document object.


def batch_process_toolbox(
    project_id: str,
    location: str,
    processor_id: str,
    gcs_input_uri: str,
    gcs_output_uri: str,
    processor_version_id: str = None,
    input_mime_type: str = None,
    field_mask: str = None,
):
    # You must set the api_endpoint if you use a location other than "us".
    opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")

    client = documentai.DocumentProcessorServiceClient(client_options=opts)

    if not gcs_input_uri.endswith("/") and "." in gcs_input_uri:
        # Specify specific GCS URIs to process individual documents
        gcs_document = documentai.GcsDocument(
            gcs_uri=gcs_input_uri, mime_type=input_mime_type
        )
        # Load GCS Input URI into a List of document files
        gcs_documents = documentai.GcsDocuments(documents=[gcs_document])
        input_config = documentai.BatchDocumentsInputConfig(gcs_documents=gcs_documents)
    else:
        # Specify a GCS URI Prefix to process an entire directory
        gcs_prefix = documentai.GcsPrefix(gcs_uri_prefix=gcs_input_uri)
        input_config = documentai.BatchDocumentsInputConfig(gcs_prefix=gcs_prefix)

    # Cloud Storage URI for the Output Directory
    gcs_output_config = documentai.DocumentOutputConfig.GcsOutputConfig(
        gcs_uri=gcs_output_uri, field_mask=field_mask
    )

    # Where to write results
    output_config = documentai.DocumentOutputConfig(gcs_output_config=gcs_output_config)

    if processor_version_id:
        # The full resource name of the processor version, e.g.:
        # projects/{project_id}/locations/{location}/processors/{processor_id}/processorVersions/{processor_version_id}
        name = client.processor_version_path(
            project_id, location, processor_id, processor_version_id
        )
    else:
        # The full resource name of the processor, e.g.:
        # projects/{project_id}/locations/{location}/processors/{processor_id}
        name = client.processor_path(project_id, location, processor_id)

    request = documentai.BatchProcessRequest(
        name=name,
        input_documents=input_config,
        document_output_config=output_config,
    )

    # BatchProcess returns a Long Running Operation (LRO)
    operation = client.batch_process_documents(request)

    # Operation Name Format: projects/{project_id}/locations/{location}/operations/{operation_id}
    documents = documentai_toolbox.document.Document.from_batch_process_operation(
        location=location, operation_name=operation.operation.name
    )

    for document in documents:
        # Read the text recognition output from the processor
        print("The document contains the following text:")
        # Truncated at 100 characters for brevity
        print(document.text[:100])


if __name__ == "__main__":
    batch_process_toolbox(
        project_id=project_id,
        location=location,
        processor_id=processor_id,
        gcs_input_uri=gcs_input_uri,
        gcs_output_uri=gcs_output_uri,
        input_mime_type=input_mime_type,
        field_mask=field_mask,
    )
