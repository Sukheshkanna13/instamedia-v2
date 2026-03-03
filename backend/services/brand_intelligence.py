"""
Brand Intelligence Service
Scrapes company websites to extract brand information for RAG context
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import re


class BrandIntelligenceService:
    """Service for scraping and analyzing brand websites"""
    
    def __init__(self, collection=None):
        """
        Initialize the service
        
        Args:
            collection: ChromaDB collection for storing brand knowledge
        """
        self.collection = collection
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
    
    def scrape_company_website(self, url: str, brand_id: str = "default") -> dict:
        """
        Scrape a company website to extract brand information
        
        Args:
            url: Company website URL
            brand_id: Brand identifier
            
        Returns:
            dict with extracted information
        """
        try:
            # Validate URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Fetch the homepage
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract information
            extracted_data = {
                'url': url,
                'brand_id': brand_id,
                'title': self._extract_title(soup),
                'description': self._extract_description(soup),
                'about': self._extract_about(soup, url),
                'mission': self._extract_mission(soup),
                'values': self._extract_values(soup),
                'products': self._extract_products(soup),
                'scraped_at': time.strftime("%Y-%m-%dT%H:%M:%SZ")
            }
            
            # Store in ChromaDB if collection provided
            if self.collection:
                self._store_in_chromadb(extracted_data)
            
            return {
                'success': True,
                'data': extracted_data,
                'message': f'Successfully scraped {url}'
            }
            
        except requests.RequestException as e:
            return {
                'success': False,
                'error': f'Failed to fetch website: {str(e)}',
                'data': None
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Scraping error: {str(e)}',
                'data': None
            }
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        
        h1_tag = soup.find('h1')
        if h1_tag:
            return h1_tag.get_text().strip()
        
        return ""
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content'].strip()
        
        meta_og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if meta_og_desc and meta_og_desc.get('content'):
            return meta_og_desc['content'].strip()
        
        return ""
    
    def _extract_about(self, soup: BeautifulSoup, base_url: str) -> str:
        """Extract about section"""
        # Look for about page link
        about_keywords = ['about', 'about-us', 'who-we-are', 'our-story']
        
        for link in soup.find_all('a', href=True):
            href = link['href'].lower()
            link_text = link.get_text().lower()
            
            if any(keyword in href or keyword in link_text for keyword in about_keywords):
                try:
                    about_url = urljoin(base_url, link['href'])
                    about_response = requests.get(about_url, headers=self.headers, timeout=10)
                    about_soup = BeautifulSoup(about_response.content, 'html.parser')
                    
                    # Extract main content
                    main_content = about_soup.find('main') or about_soup.find('article') or about_soup.find('div', class_=re.compile('content|about'))
                    if main_content:
                        text = main_content.get_text(separator=' ', strip=True)
                        return self._clean_text(text)[:1000]  # Limit to 1000 chars
                except:
                    pass
        
        # Fallback: extract from homepage
        main_content = soup.find('main') or soup.find('article')
        if main_content:
            text = main_content.get_text(separator=' ', strip=True)
            return self._clean_text(text)[:500]
        
        return ""
    
    def _extract_mission(self, soup: BeautifulSoup) -> str:
        """Extract mission statement"""
        mission_keywords = ['mission', 'our mission', 'purpose', 'why we exist']
        
        for keyword in mission_keywords:
            # Look for headings containing mission keywords
            for heading in soup.find_all(['h1', 'h2', 'h3', 'h4']):
                if keyword in heading.get_text().lower():
                    # Get the next paragraph or div
                    next_elem = heading.find_next(['p', 'div'])
                    if next_elem:
                        text = next_elem.get_text(strip=True)
                        if len(text) > 20:  # Ensure it's substantial
                            return self._clean_text(text)[:500]
        
        return ""
    
    def _extract_values(self, soup: BeautifulSoup) -> list:
        """Extract company values"""
        values = []
        values_keywords = ['values', 'our values', 'core values', 'principles']
        
        for keyword in values_keywords:
            for heading in soup.find_all(['h1', 'h2', 'h3', 'h4']):
                if keyword in heading.get_text().lower():
                    # Look for list items after the heading
                    parent = heading.find_parent()
                    if parent:
                        list_items = parent.find_all('li')
                        for item in list_items[:5]:  # Max 5 values
                            value_text = item.get_text(strip=True)
                            if len(value_text) > 5:
                                values.append(self._clean_text(value_text))
        
        return values
    
    def _extract_products(self, soup: BeautifulSoup) -> list:
        """Extract product/service information"""
        products = []
        product_keywords = ['products', 'services', 'solutions', 'offerings']
        
        for keyword in product_keywords:
            for heading in soup.find_all(['h1', 'h2', 'h3', 'h4']):
                if keyword in heading.get_text().lower():
                    parent = heading.find_parent()
                    if parent:
                        # Look for product names in headings or list items
                        for elem in parent.find_all(['h3', 'h4', 'li'])[:5]:
                            product_text = elem.get_text(strip=True)
                            if len(product_text) > 5 and len(product_text) < 100:
                                products.append(self._clean_text(product_text))
        
        return products
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters
        text = re.sub(r'[^\w\s\.,!?-]', '', text)
        return text.strip()
    
    def _store_in_chromadb(self, data: dict):
        """Store extracted data in ChromaDB"""
        if not self.collection:
            return
        
        brand_id = data['brand_id']
        
        # Store different sections as separate documents
        documents = []
        metadatas = []
        ids = []
        
        # Store title + description
        if data['title'] or data['description']:
            doc = f"Company: {data['title']}. {data['description']}"
            documents.append(doc)
            metadatas.append({
                'brand_id': brand_id,
                'type': 'overview',
                'url': data['url']
            })
            ids.append(f"{brand_id}_overview")
        
        # Store about section
        if data['about']:
            documents.append(data['about'])
            metadatas.append({
                'brand_id': brand_id,
                'type': 'about',
                'url': data['url']
            })
            ids.append(f"{brand_id}_about")
        
        # Store mission
        if data['mission']:
            documents.append(f"Mission: {data['mission']}")
            metadatas.append({
                'brand_id': brand_id,
                'type': 'mission',
                'url': data['url']
            })
            ids.append(f"{brand_id}_mission")
        
        # Store values
        if data['values']:
            values_text = "Core Values: " + ", ".join(data['values'])
            documents.append(values_text)
            metadatas.append({
                'brand_id': brand_id,
                'type': 'values',
                'url': data['url']
            })
            ids.append(f"{brand_id}_values")
        
        # Store products
        if data['products']:
            products_text = "Products/Services: " + ", ".join(data['products'])
            documents.append(products_text)
            metadatas.append({
                'brand_id': brand_id,
                'type': 'products',
                'url': data['url']
            })
            ids.append(f"{brand_id}_products")
        
        # Add to ChromaDB (with embeddings generated automatically)
        if documents:
            try:
                # Note: In production, you'd generate embeddings here
                # For now, we'll use mock embeddings
                embeddings = [[0.0] * 384 for _ in documents]
                
                self.collection.add(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas,
                    embeddings=embeddings
                )
            except Exception as e:
                print(f"Error storing in ChromaDB: {e}")


def get_brand_context(brand_id: str, query: str, collection=None) -> str:
    """
    Retrieve brand context from ChromaDB for RAG
    
    Args:
        brand_id: Brand identifier
        query: Query to search for relevant context
        collection: ChromaDB collection
        
    Returns:
        Relevant brand context as string
    """
    if not collection or collection.count() == 0:
        return ""
    
    try:
        # Query ChromaDB for relevant brand knowledge
        # Note: In production, you'd generate query embedding
        query_embedding = [0.0] * 384  # Mock embedding
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=3,
            where={"brand_id": brand_id},
            include=["documents", "metadatas"]
        )
        
        if results and results['documents'] and results['documents'][0]:
            context_parts = []
            for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
                context_parts.append(f"[{meta['type'].title()}] {doc}")
            
            return "\n\n".join(context_parts)
        
        return ""
        
    except Exception as e:
        print(f"Error retrieving brand context: {e}")
        return ""
