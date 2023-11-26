import requests
from bs4 import BeautifulSoup
from PIL import Image
from fpdf import FPDF
import re

# List of URLs to process
urls_to_process = [
    'https://readcomicfree.org/comic/justice-league-vs-godzilla-vs-kong/issue-1/all',
    'https://readcomicfree.org/comic/justice-league-vs-godzilla-vs-kong/issue-2/all',
    # Add more URLs here if needed
]

# Process each URL
for url in urls_to_process:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all elements with class 'page-chapter' and extract img src & alt
    image_tags = soup.find_all(class_='page-chapter')
    image_links = [img['data-original'] for tag in image_tags for img in tag.find_all('img')]
    image_alt_names = [img['alt'] for tag in image_tags for img in tag.find_all('img')]
    
    # Download images and save as PDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pageHeight = 0
    for i, img_url in enumerate(image_links):
        pageAsImage = Image.open(requests.get(img_url, stream=True).raw)
        pageAsImage.save(f"{image_alt_names[i]}.jpg")
        width, height = pageAsImage.size
        # print(f"{image_alt_names[i]}; height:{height}, width:{width}")
        
        if i == 0:
          pageHeight = height
          
        if width == pageHeight:
          half_width = width // 2
          left_half = pageAsImage.crop((0, 0, half_width, height))
          right_half = pageAsImage.crop((half_width, 0, width, height))
    
          # Split images
          left_half.save(f"{image_alt_names[i]}_left.jpg")
          right_half.save(f"{image_alt_names[i]}_right.jpg")
    
          # Adding pages for split images
          pdf.add_page()
          pdf.image(f"{image_alt_names[i]}_left.jpg", 0, 0, 210, 297)  # A4 size, adjust as needed
          pdf.add_page()
          pdf.image(f"{image_alt_names[i]}_right.jpg", 0, 0, 210, 297)  # A4 size, adjust as needed
        else:
          pdf.add_page()
          pdf.image(f"{image_alt_names[i]}.jpg", 0, 0, 210, 297)  # A4 size, adjust as needed

    pattern = r'/comic/(.*?)/all'
    match = re.search(pattern, url)
    if match:
      pdf.output(f"{match.group(1).replace('/', '-')}.pdf", 'F')