from typing import Generator, Dict, Any
from vector_tools.data_sources.base_source import BaseDataSource
from vector_tools.utils import split_document

class GoogleDriveSource(BaseDataSource):
    def __init__(self, drive_client, user_id: str, doc_limit: int = 1000):
        self.drive_client = drive_client
        self.user_id = user_id
        self.doc_limit = doc_limit
    
    def get_source_name(self) -> str:
        return "google_drive"
    
    def get_documents(self) -> Generator[Dict[str, Any], None, None]:
        try:
            params = {
                'q': "mimeType='application/vnd.google-apps.document'",
                'orderBy': 'modifiedTime desc',
                'pageSize': self.doc_limit,
                'pageToken': None
            }
            
            document_count = 0
            while True and document_count < self.doc_limit:
                response = self.drive_client.list_files(**params)
                
                for file in response.get('files', []):
                    if document_count >= self.doc_limit:
                        break
                        
                    try:
                        content = self.drive_client.download_file(
                            file['id'],
                            mime_type='text/plain'
                        )
                        
                        if content:
                            content.seek(0)
                            text_content = content.read()
                            text_content = text_content.decode('utf-8') if isinstance(text_content, bytes) else text_content
                            
                            combined_content = f"{file['name']}\n\n{text_content}"

                            base_metadata = {
                                'source': self.get_source_name(),
                                'doc_id': file['id'],
                                'title': file['name'],
                                'modified_time': file['modifiedTime'],
                                'web_view_link': file.get('webViewLink'),
                                'parent_ids': file.get('parents', []),
                                'user_id': self.user_id
                            }

                            for content_part, part_num, total_parts in split_document(combined_content):
                                part_metadata = base_metadata.copy()
                                if total_parts > 1:
                                    part_metadata.update({
                                        'part': part_num,
                                        'total_parts': total_parts,
                                    })
                                part_metadata['content'] = content_part
                                yield {
                                    'content': content_part,
                                    'metadata': part_metadata
                                }
                        document_count += 1
                    except Exception as e:
                        print(f"Error processing file {file['name']}: {e}")
                        continue
                
                if document_count >= self.doc_limit or not response.get('nextPageToken'):
                    break
                
                params['pageToken'] = response.get('nextPageToken')
                    
        except Exception as e:
            print(f"Error fetching documents: {str(e)}")
            raise