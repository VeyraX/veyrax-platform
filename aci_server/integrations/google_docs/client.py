from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from typing import Optional, Dict, Any, List

class GoogleDocsClient:
    def __init__(self, credentials: Credentials):
        self.service = build('docs', 'v1', credentials=credentials)
        self.drive_service = build('drive', 'v3', credentials=credentials)

    def get_document(self, document_id: str) -> Dict[str, Any]:
        return self.service.documents().get(
            documentId=document_id
        ).execute()

    def create_document(self, title: str) -> Dict[str, Any]:
        document = {
            'title': title
        }
        return self.service.documents().create(body=document).execute()

    def batch_update(self, document_id: str, requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        body = {
            'requests': requests
        }
        return self.service.documents().batchUpdate(
            documentId=document_id,
            body=body
        ).execute()

    def insert_text(self, document_id: str, location_index: int, text: str) -> Dict[str, Any]:
        requests = [
            {
                'insertText': {
                    'location': {
                        'index': location_index
                    },
                    'text': text
                }
            }
        ]
        return self.batch_update(document_id, requests)

    def replace_all_text(self, document_id: str, text_to_replace: str, replace_text: str) -> Dict[str, Any]:
        requests = [
            {
                'replaceAllText': {
                    'containsText': {
                        'text': text_to_replace,
                        'matchCase': True
                    },
                    'replaceText': replace_text
                }
            }
        ]
        return self.batch_update(document_id, requests)
        
    def search_text(self, document_id: str, search_term: str, case_sensitive: bool = False) -> Dict[str, Any]:
        document = self.get_document(document_id)
        result = {
            'matches': [],
            'total_found': 0
        }
        
        if 'body' in document and 'content' in document['body']:
            for element in document['body']['content']:
                if 'paragraph' in element:
                    for paragraph_element in element['paragraph']['elements']:
                        if 'textRun' in paragraph_element and 'content' in paragraph_element['textRun']:
                            content = paragraph_element['textRun']['content']
                            start_index = paragraph_element.get('startIndex', 0)
                            end_index = paragraph_element.get('endIndex', 0)
                            
                            found_text = False
                            if case_sensitive:
                                if search_term in content:
                                    found_text = True
                            else:
                                if search_term.lower() in content.lower():
                                    found_text = True
                            
                            if found_text:
                                result['matches'].append({
                                    'text': content,
                                    'start_index': start_index,
                                    'end_index': end_index
                                })
        
        result['total_found'] = len(result['matches'])
        return result

    def get_document_content(self, document_id: str) -> Dict[str, Any]:
        doc = self.service.documents().get(documentId=document_id).execute()
        
        full_text = ""
        if 'body' in doc and 'content' in doc['body']:
            for element in doc['body']['content']:
                if 'paragraph' in element:
                    for paragraph_element in element['paragraph']['elements']:
                        if 'textRun' in paragraph_element and 'content' in paragraph_element['textRun']:
                            full_text += paragraph_element['textRun']['content']
        
        doc['extractedContent'] = full_text
        
        return doc