from datetime import datetime
from file_storage.models.file_storage_model import FileStorageModel


class SaveFileMetaService:
    @classmethod
    def create_files_meta_ref_id(
        cls,
        ref_type: str = None,
        ref_id: str = None,
        user_id: str = None,
        company_id=None,
        file_metadata_list: list = [],
    ):
        """
        Bulk creates FileStorageModel instances from a list of file metadata.

        Args:
            file_metadata_list (list): List of dictionaries containing file metadata.
                Example: [{"name": "file1.txt", "file_path": "/path/file1.txt", "size": 1024}, ...]

        Returns:
            list: file_metadata_list
        """
        if not file_metadata_list:
            raise ValueError("File metadata list cannot be empty.")

        # Prepare model instances
        file_instances = [
            FileStorageModel(
                create_date=datetime.now(),
                create_uid=user_id,
                ref_id=ref_id,
                ref_type=ref_type,
                company_id=company_id,
                original_file_name=file.get("original_file_name"),
                file_name=file.get("file_name"),
                file=file.get("file_key"),
                file_path=file.get("file_key"),
                file_size=file.get("file_size"),
                file_type=file.get("content_type"),
                description=file.get("description"),
            )
            # Mapping through file meta data list
            for file in file_metadata_list
        ]

        # Perform bulk create
        created_files = FileStorageModel.objects.bulk_create(file_instances)
        
        # Convert to JSON-like structure
        created_files_json = [
            {
                "id": file_record.id,
                "original_file_name": file_record.original_file_name,
                "file_name": file_record.file_name,
                "file_size": file_record.file_size,
                "file_type": file_record.file_type,
                "ref_type": file_record.ref_type,
                "ref_id": file_record.ref_id,
                "file": file_record.file.url,
                "description": file_record.description,
                "create_date": file_record.create_date,
                "create_uid": file_record.create_uid,
                "company": file_record.company.id,
                "hr_employee_id": file_record.hr_employee_id,
                "hr_employee_onbehalf_id": file_record.hr_employee_onbehalf_id,
            }
            for file_record in created_files
        ]

        return created_files_json
