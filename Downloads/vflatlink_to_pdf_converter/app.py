# from flask import Flask, render_template, request, send_file, flash
# import os
# import requests
# from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import img2pdf
# from PIL import Image
# import time

# app = Flask(__name__)
# app.secret_key = 'your_secret_key'  # Change this

# # Directory to store temporary PDFs
# UPLOAD_FOLDER = 'pdfs'
# if not os.path.exists(UPLOAD_FOLDER):
#     os.makedirs(UPLOAD_FOLDER)

# def scrape_vflat_images(url):
#     """Scrape images from VFlat share page using Selenium."""
#     chrome_options = Options()
#     # Uncomment for non-headless debugging
#     # chrome_options.add_argument("--headless")
#     chrome_options.add_argument("--no-sandbox")
#     chrome_options.add_argument("--disable-dev-shm-usage")
    
#     try:
#         print("Initializing ChromeDriver...")
#         driver = webdriver.Chrome(service=Service('/opt/homebrew/bin/chromedriver'), options=chrome_options)
#         print(f"Navigating to {url}...")
#         driver.get(url)
        
#         # Wait for thumbnail list and page list
#         WebDriverWait(driver, 20).until(
#             EC.presence_of_element_located((By.ID, "thumbnail-list"))
#         )
#         WebDriverWait(driver, 20).until(
#             EC.presence_of_element_located((By.ID, "page-list"))
#         )
        
#         # Get total pages
#         soup = BeautifulSoup(driver.page_source, 'html.parser')
#         try:
#             page_info = soup.find('div', id='page-info').find_all('span')[-1].text
#             total_pages = int(page_info)
#             print(f"Detected total pages: {total_pages}")
#         except:
#             total_pages = 100  # Default
#             print(f"Page count not found. Assuming {total_pages} pages.")
        
#         # Scroll thumbnail list to load all images
#         print("Scrolling thumbnail list to load all images...")
#         driver.execute_script("document.getElementById('thumbnail-list').scrollTop = document.getElementById('thumbnail-list').scrollHeight")
#         time.sleep(5)  # Wait for images to load
        
#         # Check initial page-list images
#         image_urls = []
#         soup = BeautifulSoup(driver.page_source, 'html.parser')
#         pages = soup.find('div', id='page-list').find_all('div', class_='page')
#         print(f"Found {len(pages)} pages in page-list")
#         for page in pages:
#             img = page.find('img')
#             if img and ('src' in img.attrs or 'data-src' in img.attrs or 'srcset' in img.attrs):
#                 src = img.get('src') or img.get('data-src') or img.get('srcset', '').split(',')[0].split()[0]
#                 high_res_src = src.replace('s=1024', 's=2048').replace('s=200', 's=2048')
#                 if high_res_src not in image_urls:
#                     image_urls.append(high_res_src)
#                     print(f"Extracted high-res URL for page {page['data-page-number']}: {high_res_src}")
        
#         # If insufficient images, try clicking thumbnails
#         if len(image_urls) < total_pages:
#             print(f"Only {len(image_urls)} images found in page-list. Trying thumbnails...")
#             thumbnails = driver.find_elements(By.CSS_SELECTOR, '#thumbnail-list .thumbnail')
#             print(f"Found {len(thumbnails)} thumbnails")
            
#             for i in range(min(len(thumbnails), total_pages)):
#                 retries = 3
#                 while retries > 0:
#                     try:
#                         thumbnails = driver.find_elements(By.CSS_SELECTOR, '#thumbnail-list .thumbnail')
#                         driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", thumbnails[i])
#                         time.sleep(0.5)  # Wait for scroll
#                         print(f"Clicking thumbnail {i+1}/{len(thumbnails)} (Attempt {4-retries}/3)...")
#                         thumbnails[i].click()
#                         time.sleep(2)  # Wait for main image
                        
#                         # Wait for main image
#                         WebDriverWait(driver, 10).until(
#                             EC.presence_of_element_located((By.CSS_SELECTOR, '#page-list .page[data-page-number="{}"] img'.format(i+1)))
#                         )
                        
#                         # Get main image URL
#                         page = driver.find_element(By.CSS_SELECTOR, '#page-list .page[data-page-number="{}"]'.format(i+1))
#                         img = page.find_element(By.TAG_NAME, 'img')
#                         src = img.get_attribute('src') or img.get_attribute('data-src') or img.get_attribute('srcset', '').split(',')[0].split()[0]
#                         if src:
#                             high_res_src = src.replace('s=1024', 's=2048').replace('s=200', 's=2048')
#                             if high_res_src not in image_urls:
#                                 image_urls.append(high_res_src)
#                                 print(f"Extracted high-res URL for page {i+1}: {high_res_src}")
#                         else:
#                             print(f"No src/data-src/srcset for page {i+1}. Trying thumbnail...")
#                             thumb_img = thumbnails[i].find_element(By.TAG_NAME, 'img')
#                             src = thumb_img.get_attribute('src') or thumb_img.get_attribute('data-src') or thumb_img.get_attribute('srcset', '').split(',')[0].split()[0]
#                             high_res_src = src.replace('s=200', 's=2048')
#                             if high_res_src not in image_urls:
#                                 image_urls.append(high_res_src)
#                                 print(f"Extracted high-res URL from thumbnail for page {i+1}: {high_res_src}")
#                         break
#                     except Exception as e:
#                         print(f"Error processing page {i+1} (Attempt {4-retries}/3): {str(e)}")
#                         retries -= 1
#                         if retries == 0:
#                             with open(f'page_source_page_{i+1}.html', 'w') as f:
#                                 f.write(driver.page_source)
#                             print(f"Saved page source to page_source_page_{i+1}.html")
#                         time.sleep(1)
        
#         # Final attempt: Parse page-list again
#         if len(image_urls) < total_pages:
#             print(f"Only {len(image_urls)} images after thumbnail clicks. Parsing page-list again...")
#             soup = BeautifulSoup(driver.page_source, 'html.parser')
#             pages = soup.find('div', id='page-list').find_all('div', class_='page')
#             print(f"Found {len(pages)} pages in final page-list")
#             for page in pages:
#                 img = page.find('img')
#                 if img and ('src' in img.attrs or 'data-src' in img.attrs or 'srcset' in img.attrs):
#                     src = img.get('src') or img.get('data-src') or img.get('srcset', '').split(',')[0].split()[0]
#                     high_res_src = src.replace('s=1024', 's=2048').replace('s=200', 's=2048')
#                     if high_res_src not in image_urls:
#                         image_urls.append(high_res_src)
#                         print(f"Extracted high-res URL for page {page['data-page-number']}: {high_res_src}")
        
#         # Debug: Save final page source
#         if len(image_urls) < total_pages:
#             with open('page_source_final.html', 'w') as f:
#                 f.write(driver.page_source)
#             print(f"Saved final page source to page_source_final.html (only {len(image_urls)} images found).")
        
#         print(f"Extracted {len(image_urls)} high-res image URLs: {image_urls[:5]}...")  # Show first 5
#         driver.quit()
#         return image_urls
#     except Exception as e:
#         print(f"Error in scrape_vflat_images: {str(e)}")
#         if 'driver' in locals():
#             driver.quit()
#         raise e

# def download_images(image_urls, temp_dir='temp_images'):
#     """Download images to a temp folder."""
#     if not os.path.exists(temp_dir):
#         os.makedirs(temp_dir)
    
#     image_paths = []
#     for i, img_url in enumerate(image_urls):
#         try:
#             print(f"Downloading image {i+1}: {img_url}")
#             response = requests.get(img_url, timeout=15)
#             response.raise_for_status()
#             if not response.content:
#                 print(f"Empty content for {img_url}. Skipping.")
#                 continue
#             img_path = os.path.join(temp_dir, f'page_{i+1}.jpg')
#             with open(img_path, 'wb') as f:
#                 f.write(response.content)
            
#             with Image.open(img_path) as img:
#                 img.verify()
#             image_paths.append(img_path)
#         except Exception as e:
#             print(f"Failed to download {img_url}: {str(e)}")
#             continue
    
#     print(f"Downloaded {len(image_paths)} images")
#     return image_paths

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     pdf_path = None
#     if request.method == 'POST':
#         url = request.form['url']
#         print(f"Received URL: {url}")
#         if not url.startswith('https://share.vflat.com/'):
#             flash('Please provide a valid VFlat share URL.')
#             return render_template('index.html')
        
#         try:
#             image_urls = scrape_vflat_images(url)
#             if not image_urls:
#                 flash('No images found on the page. Check the URL or page structure.')
#                 return render_template('index.html')
            
#             image_paths = download_images(image_urls)
#             if not image_paths:
#                 flash('Failed to download images.')
#                 return render_template('index.html')
            
#             print("Converting images to PDF...")
#             with open('temp.pdf', 'wb') as f:
#                 f.write(img2pdf.convert(image_paths))
#             print("PDF created: temp.pdf")
            
#             timestamp = int(time.time())
#             pdf_filename = f'vflat_pdf_{timestamp}.pdf'
#             pdf_path = os.path.join(UPLOAD_FOLDER, pdf_filename)
#             os.rename('temp.pdf', pdf_path)
#             print(f"PDF saved: {pdf_path}")
            
#             for path in image_paths:
#                 os.remove(path)
#             os.rmdir('temp_images')
            
#         except Exception as e:
#             print(f"Error in index route: {str(e)}")
#             flash(f'Error: {str(e)}')
    
#     return render_template('index.html', pdf_path=pdf_filename if pdf_path else None)

# @app.route('/download/<filename>')
# def download_pdf(filename):
#     print(f"Serving PDF: {filename}")
#     return send_file(os.path.join(UPLOAD_FOLDER, filename), as_attachment=True)

# # if __name__ == '__main__':
# #     app.run(debug=True)

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000, debug=True)



from flask import Flask, render_template, request, send_file, flash
import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import img2pdf
from PIL import Image
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this

# --- Use /tmp folders for cloud deployment ---
UPLOAD_FOLDER = '/tmp/pdfs'
TEMP_IMAGE_FOLDER = '/tmp/temp_images'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TEMP_IMAGE_FOLDER, exist_ok=True)

def scrape_vflat_images(url):
    """Scrape images from VFlat share page using Selenium."""
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # Headless for cloud
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    try:
        print("Initializing ChromeDriver...")
        driver = webdriver.Chrome(service=Service('/opt/homebrew/bin/chromedriver'), options=chrome_options)
        print(f"Navigating to {url}...")
        driver.get(url)
        
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "thumbnail-list"))
        )
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "page-list"))
        )
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        try:
            page_info = soup.find('div', id='page-info').find_all('span')[-1].text
            total_pages = int(page_info)
            print(f"Detected total pages: {total_pages}")
        except:
            total_pages = 100
            print(f"Page count not found. Assuming {total_pages} pages.")
        
        driver.execute_script("document.getElementById('thumbnail-list').scrollTop = document.getElementById('thumbnail-list').scrollHeight")
        time.sleep(5)
        
        image_urls = []
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        pages = soup.find('div', id='page-list').find_all('div', class_='page')
        print(f"Found {len(pages)} pages in page-list")
        for page in pages:
            img = page.find('img')
            if img and ('src' in img.attrs or 'data-src' in img.attrs or 'srcset' in img.attrs):
                src = img.get('src') or img.get('data-src') or img.get('srcset', '').split(',')[0].split()[0]
                high_res_src = src.replace('s=1024', 's=2048').replace('s=200', 's=2048')
                if high_res_src not in image_urls:
                    image_urls.append(high_res_src)
                    print(f"Extracted high-res URL for page {page['data-page-number']}: {high_res_src}")
        
        if len(image_urls) < total_pages:
            print(f"Only {len(image_urls)} images found in page-list. Trying thumbnails...")
            thumbnails = driver.find_elements(By.CSS_SELECTOR, '#thumbnail-list .thumbnail')
            print(f"Found {len(thumbnails)} thumbnails")
            
            for i in range(min(len(thumbnails), total_pages)):
                retries = 3
                while retries > 0:
                    try:
                        thumbnails = driver.find_elements(By.CSS_SELECTOR, '#thumbnail-list .thumbnail')
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", thumbnails[i])
                        time.sleep(0.5)
                        print(f"Clicking thumbnail {i+1}/{len(thumbnails)} (Attempt {4-retries}/3)...")
                        thumbnails[i].click()
                        time.sleep(2)
                        
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, '#page-list .page[data-page-number="{}"] img'.format(i+1)))
                        )
                        
                        page = driver.find_element(By.CSS_SELECTOR, '#page-list .page[data-page-number="{}"]'.format(i+1))
                        img = page.find_element(By.TAG_NAME, 'img')
                        src = img.get_attribute('src') or img.get_attribute('data-src') or img.get_attribute('srcset', '').split(',')[0].split()[0]
                        if src:
                            high_res_src = src.replace('s=1024', 's=2048').replace('s=200', 's=2048')
                            if high_res_src not in image_urls:
                                image_urls.append(high_res_src)
                                print(f"Extracted high-res URL for page {i+1}: {high_res_src}")
                        else:
                            thumb_img = thumbnails[i].find_element(By.TAG_NAME, 'img')
                            src = thumb_img.get_attribute('src') or thumb_img.get_attribute('data-src') or thumb_img.get_attribute('srcset', '').split(',')[0].split()[0]
                            high_res_src = src.replace('s=200', 's=2048')
                            if high_res_src not in image_urls:
                                image_urls.append(high_res_src)
                                print(f"Extracted high-res URL from thumbnail for page {i+1}: {high_res_src}")
                        break
                    except Exception as e:
                        print(f"Error processing page {i+1} (Attempt {4-retries}/3): {str(e)}")
                        retries -= 1
                        if retries == 0:
                            with open(f'page_source_page_{i+1}.html', 'w') as f:
                                f.write(driver.page_source)
                            print(f"Saved page source to page_source_page_{i+1}.html")
                        time.sleep(1)
        
        if len(image_urls) < total_pages:
            print(f"Only {len(image_urls)} images after thumbnail clicks. Parsing page-list again...")
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            pages = soup.find('div', id='page-list').find_all('div', class_='page')
            for page in pages:
                img = page.find('img')
                if img and ('src' in img.attrs or 'data-src' in img.attrs or 'srcset' in img.attrs):
                    src = img.get('src') or img.get('data-src') or img.get('srcset', '').split(',')[0].split()[0]
                    high_res_src = src.replace('s=1024', 's=2048').replace('s=200', 's=2048')
                    if high_res_src not in image_urls:
                        image_urls.append(high_res_src)
        
        if len(image_urls) < total_pages:
            with open('page_source_final.html', 'w') as f:
                f.write(driver.page_source)
            print(f"Saved final page source to page_source_final.html (only {len(image_urls)} images found).")
        
        print(f"Extracted {len(image_urls)} high-res image URLs: {image_urls[:5]}...")
        driver.quit()
        return image_urls
    except Exception as e:
        print(f"Error in scrape_vflat_images: {str(e)}")
        if 'driver' in locals():
            driver.quit()
        raise e

def download_images(image_urls, temp_dir=TEMP_IMAGE_FOLDER):
    """Download images to a temp folder."""
    os.makedirs(temp_dir, exist_ok=True)
    image_paths = []
    for i, img_url in enumerate(image_urls):
        try:
            print(f"Downloading image {i+1}: {img_url}")
            response = requests.get(img_url, timeout=15)
            response.raise_for_status()
            if not response.content:
                continue
            img_path = os.path.join(temp_dir, f'page_{i+1}.jpg')
            with open(img_path, 'wb') as f:
                f.write(response.content)
            with Image.open(img_path) as img:
                img.verify()
            image_paths.append(img_path)
        except Exception as e:
            print(f"Failed to download {img_url}: {str(e)}")
            continue
    print(f"Downloaded {len(image_paths)} images")
    return image_paths

@app.route('/', methods=['GET', 'POST'])
def index():
    pdf_path = None
    if request.method == 'POST':
        url = request.form['url']
        if not url.startswith('https://share.vflat.com/'):
            flash('Please provide a valid VFlat share URL.')
            return render_template('index.html')
        
        try:
            image_urls = scrape_vflat_images(url)
            if not image_urls:
                flash('No images found on the page.')
                return render_template('index.html')
            
            image_paths = download_images(image_urls)
            if not image_paths:
                flash('Failed to download images.')
                return render_template('index.html')
            
            with open('/tmp/temp.pdf', 'wb') as f:
                f.write(img2pdf.convert(image_paths))
            
            timestamp = int(time.time())
            pdf_filename = f'vflat_pdf_{timestamp}.pdf'
            pdf_path = os.path.join(UPLOAD_FOLDER, pdf_filename)
            os.rename('/tmp/temp.pdf', pdf_path)
            
            for path in image_paths:
                os.remove(path)
            os.rmdir(TEMP_IMAGE_FOLDER)
            
        except Exception as e:
            flash(f'Error: {str(e)}')
    
    return render_template('index.html', pdf_path=pdf_filename if pdf_path else None)

@app.route('/download/<filename>')
def download_pdf(filename):
    return send_file(os.path.join(UPLOAD_FOLDER, filename), as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
