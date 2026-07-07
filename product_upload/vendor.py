import requests
import json

url = "http://localhost:8001/graphql/"
file_number = 56

operations = {
    "query": """
        mutation ProductUploadCreate($file: Upload!, $imagesZip: Upload!) {
            vendorProductUploadCreate(file: $file, imagesZip:$imagesZip ) {
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

token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6InNWR0Q0NzdibjRxSk43VXhaMlBNa3RIUmExWW05aEVSRXI2c3hmZTNLb3cifQ.eyJleHAiOjE3ODM5ODM3NTEsImlhdCI6MTc4MjI1NTc1MSwianRpIjoiNjY5OWFlZWUtMTNjYy00NzZhLTk0ZWItZDExZWIyOWQ4MjFiIiwiaXNzIjoiaHR0cHM6Ly9hcGkuZGV2Mi53YXNmYXR5cGx1cy5jb20vYXV0aC9yZWFsbXMvamhpcHN0ZXIiLCJzdWIiOiJmMjY0ZDY4My0xNTI1LTRjOTctOTNmNy00NTBiMWZhZDM5ZDciLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJnYXRld2F5X3dlYl9hcHAiLCJzZXNzaW9uX3N0YXRlIjoiZGI1ODY5OGMtYzI5YS00N2I5LWIwZDEtM2NkY2M1NzIzNTdiIiwiYWNyIjoiMSIsImFsbG93ZWQtb3JpZ2lucyI6WyJodHRwczovL3dlYi5zZWhhY2l0eS5pbSIsImh0dHA6Ly8xMjcuMC4wLjE6ODc2MSIsImh0dHA6Ly9rZXljbG9hazo4NzYxIiwiaHR0cDovLzMuMjM0LjE1MC43Nzo4NzYxIiwiaHR0cDovL2xvY2FsaG9zdDo4MDgxIiwiaHR0cHM6Ly9pbS5zZWhhY2l0eS5jb20iLCIqIiwiaHR0cDovL2tleWNsb2FrOjgwODEiLCJodHRwOi8vMy4yMzQuMTUwLjc3OjgwODEiLCJodHRwczovL2ltLnRlc3Quc2VoYWNpdHkuY29tIiwiaHR0cDovL2xvY2FsaG9zdDo5MDAwIiwiaHR0cDovL2xvY2FsaG9zdDo4MTAwIl0sInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJkZWZhdWx0LXJvbGVzLWpoaXBzdGVyIl19LCJzY29wZSI6Im9wZW5pZCBqaGlwc3RlciBlbWFpbCBwcm9maWxlIiwic2lkIjoiZGI1ODY5OGMtYzI5YS00N2I5LWIwZDEtM2NkY2M1NzIzNTdiIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJyb2xlcyI6WyJkZWZhdWx0LXJvbGVzLWpoaXBzdGVyIl0sIm5hbWUiOiJ2ZW5kb3IgYWRtaW4iLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJ2OTY2NTU4OTYzMjc4IiwiZ2l2ZW5fbmFtZSI6InZlbmRvciIsImZhbWlseV9uYW1lIjoiYWRtaW4iLCJlbWFpbCI6InZlbmRvci5hZG1pNUBnbWFpbC5jb20iLCJ1c2VyX2lkIjoyMDY4LCJwYXRpZW50X2lkIjpudWxsLCJ2ZW5kb3JfaWQiOm51bGwsInByb3ZpZGVyX2lkIjpudWxsLCJwcm92aWRlcl9jb2RlIjpudWxsLCJhcHBfdHlwZSI6IlZlbmRvciIsImFwcF9yb2xlIjoiQWRtaW4iLCJuYXRpb25hbF9pZCI6Ijk2NjU1ODk2MzI3OCIsInBlcm1pc3Npb25zIjpbIm1hbmFnZV9icmFuY2hlcyIsIm1hbmFnZV9jaGVja291dHMiLCJtYW5hZ2Vfb3JkZXJzIiwibWFuYWdlX3Byb2R1Y3Rfc3RvY2tzIiwibWFuYWdlX2Rpc2NvdW50cyIsIm1hbmFnZV91c2VycyIsInZpZXdfY3VzdG9tZXJzIiwibWFuYWdlX2NoYXQiLCJtYW5hZ2VfaW52b2ljZXMiLCJtYW5hZ2VfbWVkaWNhbF9kZWxpdmVyeV9yZXF1ZXN0cyIsIm1hbmFnZV9waGFybWFjeV9jcmVkZW50aWFscyIsIm1hbmFnZV9wcmVzY3JpcHRpb25zIl19.dmqeEEcTb-VKJOz4l8UsqPI_5zyW7wexemByn8z8aJrW9zFciZfOeVc2nEAtAnlAGx7LcFywEAv6Ss8MvPERepmRAofpbgrn3hYK4HM0yFeztyvKswu8_p-cwInIVTZZgrw1UKrCIZzRl8tYsvXbJsN_D2-3-U-SeUkpvJLvXC1i0Z7cVUkyoX2Z0X9MXdDLax178i0H4qv5A-VflK4VwT3fx8Qz6AInLU88d5VIOmr1C-DfqSQd8gsv5X8yCXySHoFvZbaquvoi6veOFiUYpnaTBn4Bs2I8ghwsLGW6sHWdkqIbMvjBOIN9Kzzs94zT53uyrzJfCE29KQIEKQVcEpFu2Sgz3dnauUjRsvVMgqU5J8OCwScgGrkqR_3eB8vkGZ5uLBYDvaRXKEltgk6r5KxANE0uwg9NbN8ah_uQjXPx2lsnx3667M6-7WNkEbTfXfBrGPjJGVJnAdZ9oYsqV8grsPYViMkCulWBDHSM7ie0PGdrRwE6FFwR96W-xp80RSqkRIKa8AigNdxi2L0SfNIMSiIuRNFR98BQqVQzHDp6md3alGX19WaDCCgyv2wX5NQi7ViAM89dXHad1cBTSbI4KhtXoigxnf_7o2WHtTBCGS7TqMMvVcEnem3kuYtYMw7kld0Vj0QoM78vXIPH4Owj84nKaGtRTlDfImYVYKc"
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
