from google.cloud import bigquery

client = bigquery.Client()
datasets = list(client.list_datasets())
if datasets:
    print("Datasets encontrados en el proyecto:")
    for d in datasets:
        print(f"- {d.dataset_id}")
else:
    print("No se encontraron datasets.")
