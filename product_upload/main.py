import requests
import json

url = "http://localhost:8001/graphql/"
file_number = 43

operations = {
    "query": """
        mutation ProductUploadCreate($file: Upload!, $imagesZip: Upload!) {
            adminProductUploadCreate(file: $file, imagesZip:$imagesZip ) {
                success
                productUpload {
                    id
                    status  
                    uploadUuid
                    }
                errors {
                    field
                    message
                    code
                }
            }
        }
    """,
    "variables": {"file": None, "imagesZip": None},
}

map_ = {"0": ["variables.file"], "1": ["variables.imagesZip"]}

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwidHlwZSI6ImFjY2VzcyIsImV4cCI6MTc4NTI3NzkwNiwiaWF0IjoxNzgwMDkzOTA2LCJqdGkiOiJhMjYyMGJlOWVkMzQ0ZTJmOTU0ZTc2YmIyMTk3N2MyNCJ9.Kz_eeEHvJQKPjTVlhW4_2J9o-4_TGxy01ygxiarzEr4"
headers = {
    "Authorization": f"Bearer {token}",
}

files = {
    "operations": (None, json.dumps(operations), "application/json"),
    "map": (None, json.dumps(map_), "application/json"),
    "0": ("file.xlsx", open(f"./packages/{file_number}/file.xlsx", "rb")),
    "1": ("images.zip", open(f"./packages/{file_number}/drugs.zip", "rb")),

}

response = requests.post(url, files=files, headers=headers, verify=False)

print(response.status_code)
print(json.dumps(response.json(), indent=2))
