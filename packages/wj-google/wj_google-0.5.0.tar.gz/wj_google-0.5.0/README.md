# wj_google
## Connection to GCP
In order to use the client, you need a json [credentials](https://cloud.google.com/docs/authentication/application-default-credentials?hl=es-419) from the google project. The first time to connect to a service, It is necessary to authorize the app through the browser.

It is possible to use an environment variable as credentials. If you need to use credentials as environment variables, add the environment variable `GCP_CREDENTIALS` and as the value, place the values of the json file in a single line within brackets.

```
# .env file
GCP_CREDENTIALS={"type":"service_account","project_id":"your-project-id",...}
```

## Supported services

The currently supported services are:
- Google Drive
- Buckets
- BigQuery

## Google Drive
The GCP account must have Google Drive API enabled, and make sure that you have a OAuth 2.0 application created, in Google Cloud console, you can see the [documentation](https://developers.google.com/drive/api/guides/about-sdk?hl=es-419).

The following methods are currently supported:
- Upload files
- Download files
- Create directory
You must The package must be instantiated as follows:
```
from wj_google.google_api.google_api import GoogleApi

googleApi = GoogleApi(
    client_secret_file=CLIENT_SECRET_FILE, -> Json file must be configured in GCP
    api_name=API_NAME, -> drive in this case
    api_version=API_VERSION, -> Current version, 3 in this case
    scopes=GOOGLE_DRIVE_SCOPES, -> Scope of drive see doc
)
```
There are diferent scopes, as you can see in the [documentation](https://developers.google.com/drive/api/guides/api-specific-auth?hl=es-419).

## Google Drive
The GCP account must have Google Drive API enabled, and make sure that you have a OAuth 2.0 application created, in Google Cloud console, you can see the [documentation](https://developers.google.com/drive/api/guides/about-sdk?hl=es-419).

The following methods are currently supported:
- Upload files
- Download files
- Create directory

To use the library, it is necessary to prepare the credentials, and then instantiate the service that will be used.
```
from wj_google.google_api.google_api import GoogleApi

googleApi = GoogleApi(
    client_secret_file=CLIENT_SECRET_FILE, -> Json file must be configured in GCP
    api_name=API_NAME, -> drive in this case
    api_version=API_VERSION, -> Current version, 3 in this case
    scopes=GOOGLE_DRIVE_SCOPES, -> Scope of drive see doc
)
```
There are diferent scopes, as you can see in the [documentation](https://developers.google.com/drive/api/guides/api-specific-auth?hl=es-419).

### Uploading a file:
```
googleApi.upload_files_to_drive(
    folder_id, -> Id from the drive of the directory 
    file_paths, -> Path of yur file
    mime_types -> Type of file
)
```
### Downloading a file:
```
googleApi.download_files_drive(
    file_ids -> Google Drive id file, you can find it in the uri
    file_names -> Name given in your local
)
```
### Creating a directory:
```
googleApi.create_directory_drive(
    directory_name
)
```

## Google storage buckets

This resource can be used with the credentials of a service user, you see de [documentation](https://cloud.google.com/iam/docs/manage-access-service-accounts?hl=es).

The following methods are currently supported:
- Upload files
- Download files
- Create directory

As in the previous case, credentials are required. After which the resource is instantiated.
```
from wj_google.google_cloud.cloud_connector import GoogleStorage
googleStorageClient = GoogleStorage(
    service -> STORAGE in this case and for now***
    credentials
)
```
### Uploading a file:
```
googleStorageClient.upload_file(
    bucket_name -> Destination bucket 
    source_file_name -> Path of the file to upload
    destination_file_name Name of the file in bucket
)
```
### Downloading a file:
```
googleStorageClient.download_file(
    bucket_name -> bucket file
    file_name -> name and path in the bucket
    destination_file -> name and path in your local of the file
)
```
### Creating a bucket:
```
googleStorageClient.create_bucket(
    bucket_name,
    storage_class, -> Optional, to define the type of bucket to use
    location, -> Optional, to define in which region the bucket is hosted 
)
```
### Listing bucket's files:
```
googleStorageClient.list_files(bucket_name)
```

## Google BigQuery
This resource can be used with the credentials of a service user, you see de [documentation](https://cloud.google.com/python/docs/reference/bigquery/latest).


With the credentials are required. After which the resource is instantiated, in this case just execute the query.
```
from google_cloud.cloud_connector import GoogleBigQuery

bigquery = GoogleBigQuery(
    service=BIGQUERY,
    credentials=GOOGLE_BIGQUEY_CREDENTIALS,
    scopes=scopes -> To use services like Google Drive
)

```
### Do a consult:

```
query = 'YOUR_SQL_QUERY'
sql_job = bigquery.sql_query(query=query)
```

You can iterate over the sql_job:
```
for item in sql_job:
    print(item.name)
```

### Add label to bigquery table:

```
labels = {
    "type": "social_media",
    "category": "cloud",
}
bigquery = GoogleBigQuery(service=BIGQUERY, credentials=GOOGLE_BIGQUEY_CREDENTIALS)
bigquery.add_table_labels(
    labels=labels, dataset_name=dataset_name, table_name=table_name
)

```
### Delete label to bigquery table:
```
bigquery.delete_labels_in_table(dataset_name, table_name)
```

### Add rows to a Bigquery table:
Errors can be conslts in the list of errors returned by the method, if the list is empty, all the insertion was ok.
```
errors = bigquery.insert_row_in_table(
    table_id=table_id,
    rows=list_of_rows
)
```

## Google Firestore (New)

This new resource is in the testing phase and uses firebase-admin version 6.6.0 as the basis for communication with Firestore. For more information, check the [documentation](https://firebase.google.com/docs/firestore?hl=en).

Similarly to Google Cloud, credentials can be added through the GCP_CREDENTIALS environment variable, with the values enclosed in brackets.

```
# .env file
GCP_CREDENTIALS={"type":"service_account","project_id":"your-project-id",...}
```
To use the resource, import it and instantiate the client.

```
from wj_google.google_cloud.firestone import Firestore

firestore_db = Firebase(service_account_json=CREDENTIALS)
```
If the GCP credentials are configured as an environment variable, it is not necessary to provide them in the `service_account_json` field.
### Add a New Document

Returns the document ID if it was successfully inserted.

```
data = {
    "name": "John Doe",
    "email": "john@example.com",
    "age": None
}
id = firestore_db.add_document(collection=collection, data=data)
```

### Update a Document 

A document can be updated if it has the same ID as follows:

```
id = firestore_db.add_document(
    collection=collection, 
    data={"name": "Jane Doe", "age": 25},
    document_id=id
)
```

### Retrieve a Document by ID
With the same id, it is possible to return the complete document as a dictionary.

```
user = firestore_db.get_document(
    collection=collection,
    document_id=id
)
```

### Retrieve All Documents

It is also possible to retrieve the entire collection as a list:

```
users_list = firestore_db.get_all_documents(collection=collection)
```

### Delete a Document

It is possible to delete a document using its ID:

```
firestore_db.delete_document(collection=collection, document_id=id)
```

## Atlas Mongo (New)
It is now possible to perform operations for Atlas Mongo. For this, a user and password with permissions to the cluster to be worked on are required.

To start, it is necessary to use a URI, in which the user and password fields are replaced:

```
uri = mongodb://<USER>:<PASSWORD>@cluster0-shard-00-00.vubve.mongodb.net:27017,cluster0-shard-00-01.vubve.mongodb.net:27017,cluster0-shard-00-02.vubve.mongodb.net:27017/?ssl=true&replicaSet=atlas-n1rss5-shard-0&authSource=admin&retryWrites=true&w=majority&appName=Cluster0
```
Here we can see a URI configured for cluster0, it is recommended that USER and PASSWORD be assigned through environment variables. Similarly, DB_NAME and COLLECTION_NAME.

To start using this client, instantiate the functionality as follows:

```
from wj_google.google_cloud.atlas_mongo import AtlasMongo
mongo_db = AtlasMongo(uri=uri, db_name=COLLECTION_NAME, collection_name=COLLECTION_NAME)
```

### Create a document

Given a dictionary with the data to be inserted, simply create the document in the db.

```
id = mongo_db.create(document=document)
```

As in Firestore, it is possible to obtain the ID of the inserted document if data manipulation is required.

### Find a data with a value or values coincidences

It is possible to find matches in a general search performed on a collection. To do this, you can assign the fields for which you are looking for matches in the collection to a dictionary and use the find function with them.

```
query = {#Search all results with Age 26
    "Age": 26
}
result = mongo_db.find(
    query=query
)
```
The result will be an empty list [] or contain all documents that match the query.

# Update the inserted data
You can use a query to update documents that match the assigned parameters:

```
# Params to match in the update
query = {
    "Age": 27
}

#Data that will be update/added to documents
update_data = {
    "Age": 20
}
result = mongo_db.update(query=query, update_data=update_data)
```

It is also possible to search for a document by its ID, for this use the `_id` field in the query.

```
# Params to match in the update
query = {
    "_id: "7ffa286f-cac9-47cb-b095-505c601d7b4e"
}

#Data that will be update/added to documents
update_data = {
    "Age": 20
}
result = mongo_db.update(query=query, update_data=update_data)
```

# Given a query, deletes the match documents
Similarly, it is possible to use a function to delete documents using a query, and as in the previous section, it is possible to use the _id field and any search parameter(s).

```
deleted_count = mongo_db.delete(query=update_data)
```
The function returns the number of documents that matched the search and were deleted.
