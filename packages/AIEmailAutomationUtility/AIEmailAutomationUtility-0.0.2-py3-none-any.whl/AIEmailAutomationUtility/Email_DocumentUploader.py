import os
import json
import shutil
import requests
import loggerutility as logger


class Email_DocumentUploader:
    def upload_document(self, upload_config, file_data):
        try:
            # Create temp directory if needed
            temp_dir = "temp"
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
                
            # Save file temporarily
            file_path = os.path.join(temp_dir, file_data['filename'])
            with open(file_path, 'wb') as f:
                f.write(file_data['content'])
            
            # Prepare headers and parameters
            headers = {"TOKEN_ID": upload_config["token_id"]}
            params = {}
            
            param_fields = {
                "DOCUMENT_TYPE": "document_type",
                "OBJ_NAME": "obj_name",
                "FILE_TYPE": "file_type",
                "APP_ID": "app_id"
            }
            logger.log(f"param_fields:: {param_fields}")
            
            for api_key, config_key in param_fields.items():
                if config_key in upload_config and upload_config[config_key]:
                    params[api_key] = upload_config[config_key]
            
            # Upload file
            with open(file_path, 'rb') as file:
                files = {'file': file}
                response = requests.request(
                    upload_config["method"],
                    upload_config["url"],
                    headers=headers,
                    files=files,
                    data=params
                )
            
            if response.status_code == 200:
                result = json.loads(response.text)
                document_id = result["ID"]["Document_Id"]
                return str(response.status_code), document_id
            else:
                return str(response.status_code), f"Upload failed: {response.text}"
                
        except Exception as e:
            print(f"Error uploading document: {str(e)}")
            raise
        finally:
            # Cleanup
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)