from datetime import datetime
from uuid import uuid4
from src.domain.models import Binary
from typing import List, Dict, Any
from src.infrastructure.json_repository import JsonRepository

class UploadBinaryUseCase:
    def __init__(self, file_repo, db_repo):
        self.file_repo = file_repo
        self.db_repo = db_repo
        
    def execute(self, file, enviroment: str) -> Binary:
        binary_id = str(uuid4())
        filename = self.file_repo.save_file(file, binary_id)
        binary = Binary(
            id =binary_id,
            filename=filename,
            enviroment=enviroment,
            status='pending' if enviroment == 'prod' else 'signed',
            uploaded_date=datetime.now()
        )
        self.db_repo.add(binary)
        return binary
        return binary

        class ListFilesUseCases:
            def __init__(self, db_repo: JsonRepository):
                self.db_repo = db_repo
            
            def execute(self) -> List[Dict[str, Any]]:
                try:
                    records = self.db_repo.list_records()
                    return records
                except Exception as e:
                    print(f"[ListFilesUseCase] Error retrieving records: {e}")
                    return []

        
        