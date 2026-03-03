"""
Test script for brand intelligence website scraping
"""

from services.brand_intelligence import BrandIntelligenceService
import json

# Test URLs
test_urls = [
    "https://www.apple.com",
    "https://www.nike.com",
    "https://www.airbnb.com"
]

print("🧪 Testing Brand Intelligence Website Scraping\n")
print("=" * 60)

service = BrandIntelligenceService()

for url in test_urls:
    print(f"\n📍 Scraping: {url}")
    print("-" * 60)
    
    result = service.scrape_company_website(url, brand_id="test")
    
    if result['success']:
        data = result['data']
        print(f"✅ Success!")
        print(f"\n📝 Title: {data['title'][:100] if data['title'] else 'N/A'}")
        print(f"\n📄 Description: {data['description'][:150] if data['description'] else 'N/A'}...")
        print(f"\n📖 About: {data['about'][:200] if data['about'] else 'N/A'}...")
        print(f"\n🎯 Mission: {data['mission'][:150] if data['mission'] else 'N/A'}...")
        print(f"\n💎 Values: {data['values'][:3] if data['values'] else 'N/A'}")
        print(f"\n🛍️  Products: {data['products'][:3] if data['products'] else 'N/A'}")
    else:
        print(f"❌ Failed: {result['error']}")
    
    print("\n" + "=" * 60)

print("\n✅ Test complete!")
