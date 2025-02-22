from typing import Generator, Dict, Any
from vector_tools.data_sources.base_source import BaseDataSource
from vector_tools.utils import split_document
from integrations.notion.service import NotionService

class NotionSource(BaseDataSource):
    def __init__(self, notion_service: NotionService, user_id: str, doc_limit: int = 1000):
        self.notion_service = notion_service
        self.user_id = user_id
        self.doc_limit = doc_limit
    
    def get_source_name(self) -> str:
        return "notion"

    def get_documents(self) -> Generator[Dict[str, Any], None, None]:
        try:
            databases = self.notion_service.list_databases().items
            
            processed_docs = 0
            
            for db in databases:
                if processed_docs >= self.doc_limit:
                    break
                    
                try:
                    pages = self.notion_service.list_pages(db.id).items
                    
                    for page in pages:
                        if processed_docs >= self.doc_limit:
                            break
                            
                        try:
                            blocks = self.notion_service.client.get_block_children(page.id)
                            text_content = self._extract_content(blocks)
                            
                            if not text_content:
                                continue
                            
                            processed_docs += 1
                            combined_content = f"{page.title}\n\n{text_content}"
                                
                            base_metadata = {
                                'source': self.get_source_name(),
                                'doc_id': page.id,
                                'title': page.title,
                                'database_id': db.id,
                                'url': page.url,
                                'last_edited_time': page.last_edited_time,
                                'user_id': self.user_id
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
                            print(f"Error processing page {page.id}: {e}")
                            continue
                            
                except Exception as e:
                    print(f"Error processing database {db.id}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error fetching documents: {str(e)}")
            raise

    def _extract_title(self, page: dict) -> str:
        properties = page.get('properties', {})
        title_prop = next((prop for prop in properties.values() if prop['type'] == 'title'), None)
        
        if title_prop and title_prop.get('title'):
            return ' '.join(text.get('plain_text', '') for text in title_prop['title'])
        return 'Untitled'

    def _extract_content(self, blocks_response: dict) -> str:
        content = []
        
        for block in blocks_response.get('results', []):
            block_type = block.get('type', '')
            if block_type in ['paragraph', 'heading_1', 'heading_2', 'heading_3', 'bulleted_list_item', 'numbered_list_item']:
                text = block.get(block_type, {}).get('rich_text', [])
                content.extend(item.get('plain_text', '') for item in text)
        
        return ' '.join(content)
