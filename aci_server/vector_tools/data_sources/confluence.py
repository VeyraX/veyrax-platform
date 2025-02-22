from typing import Generator, Dict, Any
from vector_tools.data_sources.base_source import BaseDataSource
from vector_tools.utils import split_document
from integrations.confluence.service import ConfluenceService

class ConfluenceSource(BaseDataSource):
    def __init__(self, confluence_service: ConfluenceService, user_id: str, doc_limit: int = 5):
        self.confluence_service = confluence_service
        self.user_id = user_id
        self.doc_limit = doc_limit
    
    def get_source_name(self) -> str:
        return "confluence"

    def get_documents(self) -> Generator[Dict[str, Any], None, None]:
        try:
            processed_docs = 0
            spaces = self.confluence_service.get_spaces().results
            
            for space in spaces:
                if processed_docs >= self.doc_limit:
                    break
                    
                try:
                    pages = self.confluence_service.get_pages(space_id=space['id']).results
                    
                    for page in pages:
                        if processed_docs >= self.doc_limit:
                            break
                            
                        try:
                            page_content = self.confluence_service.get_page(page['id'])
                            text_content = page_content.body['storage']['value']
                            
                            if not text_content:
                                continue
                            
                            processed_docs += 1
                            combined_content = f"{page_content.title}\n\n{text_content}"
                            
                            base_metadata = {
                                'source': self.get_source_name(),
                                'doc_id': page_content.id,
                                'title': page_content.title,
                                'space_id': space['id'],
                                'space_name': space['name'],
                                'version': page_content.version['number'],
                                'user_id': self.user_id,
                                'url': f"{self.confluence_service.base_url}/wiki/spaces/{space['key']}/pages/{page_content.id}"
                            }

                            for content_part, part_num, total_parts in split_document(combined_content):
                                part_metadata = base_metadata.copy()
                                if total_parts > 1:
                                    part_metadata.update({
                                        'part': part_num,
                                        'total_parts': total_parts,
                                    })
                                yield {
                                    'content': content_part,
                                    'metadata': {
                                        **part_metadata,
                                        'content': content_part
                                    }
                                }
                                
                        except Exception as e:
                            print(f"Error processing page {page['id']}: {e}")
                            continue
                            
                except Exception as e:
                    print(f"Error processing space {space['id']}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error fetching documents: {str(e)}")
            raise