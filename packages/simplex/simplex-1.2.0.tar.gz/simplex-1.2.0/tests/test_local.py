import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from simplex import Simplex

from PIL import ImageDraw

from playwright.sync_api import sync_playwright
from PIL import Image
import time
import os
from hyperbrowser import Hyperbrowser

from dotenv import load_dotenv


load_dotenv()


def screenshot_tests():
    simplex = Simplex(api_key=os.getenv("SIMPLEX_API_KEY"))
    image = "/home/ubuntu/supreme-waffle/images/netflix.png"
    screenshot = Image.open(image)

    start_time = time.time()
    bbox = simplex.find_element("dark mode icon", screenshot)
    end_time = time.time()
    print(f"Time taken: {end_time - start_time} seconds")
    print(bbox)

    start_time = time.time()
    action = simplex.step_to_action("click and enter email address", screenshot)
    end_time = time.time()
    print(f"Time taken: {end_time - start_time} seconds")
    print(action)


def execute_action_test():
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False)
    driver = browser.new_page()
    
    simplex = Simplex(api_key=os.getenv("SIMPLEX_API_KEY"), driver=driver)
    simplex.goto("https://www.netflix.com/")
    actions = [['CLICK', 'email field'], ['TYPE', 'email address']]
    simplex.execute_action(actions[0])


def cgtrader_test():
    assets = ["apple watch"]
    urls = []

    with sync_playwright() as p:
        driver = p.chromium.launch(headless=False).new_page()
        simplex = Simplex(api_key=os.getenv("SIMPLEX_API_KEY"), driver=driver)
        simplex.goto("https://www.cgtrader.com/")

        for asset in assets:
            simplex.goto("https://www.cgtrader.com")
            simplex.do(f"search for {asset}")  
            simplex.do("click on search button")
            simplex.do(f"click on the first product")
            driver.wait_for_timeout(3000)

            urls.append(simplex.driver.url)

    print(urls)


def test_find_element(): 
    simplex = Simplex(api_key=os.getenv("SIMPLEX_API_KEY"))
    simplex.goto("https://www.cgtrader.com/")

    state = simplex.take_stable_screenshot()
    bbox = simplex.find_element("search bar")

    copy_image = state.copy()
    draw = ImageDraw.Draw(copy_image)
    draw.rectangle(bbox, outline='red', width=2)
    copy_image.save("annotated_state.png")
    

    # Get the page HTML and device scale factor
    html = simplex.driver.content()
    scale_factor = simplex.driver.evaluate("window.devicePixelRatio")
    
    # Get viewport dimensions and other relevant settings
    viewport_size = simplex.driver.viewport_size
    zoom_level = simplex.driver.evaluate("document.documentElement.style.zoom || 1")
    
    # Debug print
    print(f"Original bbox: {bbox}")
    print(f"Scale factor: {scale_factor}")
    print(f"Viewport size: {viewport_size}")
    print(f"Zoom level: {zoom_level}")
    
    # Transform coordinates from screenshot to HTML
    html_bbox = [
        bbox[0] / scale_factor,
        bbox[1] / scale_factor,
        bbox[2] / scale_factor,
        bbox[3] / scale_factor
    ]
    print(f"Transformed bbox: {html_bbox}")
    
    # Create HTML wrapper with matching viewport settings and scaled overlay
    html_with_settings = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{
                margin: 0;
                width: {viewport_size['width']}px;
                height: {viewport_size['height']}px;
                zoom: {zoom_level};
            }}
            .viewport-container {{
                width: 100%;
                height: 100%;
                overflow: hidden;
                position: relative;
                transform-origin: top left;
                transform: scale({1/scale_factor});
            }}
            #page-content {{
                width: {viewport_size['width'] * scale_factor}px;
                height: {viewport_size['height'] * scale_factor}px;
                transform-origin: top left;
            }}
            #bbox-overlay {{
                position: absolute;
                border: 2px solid red;
                left: {bbox[0]}px;
                top: {bbox[1]}px;
                width: {bbox[2] - bbox[0]}px;
                height: {bbox[3] - bbox[1]}px;
                pointer-events: none;
                z-index: 10000;
            }}
        </style>
    </head>
    <body>
        <div class="viewport-container">
            <div id="page-content">
                {html}
            </div>
            <div id="bbox-overlay"></div>
        </div>
    </body>
    </html>
    """

    # Save the HTML with viewport settings
    with open('screenshot_with_viewport.html', 'w') as f:
        f.write(html_with_settings)


def test_find_element_2():
    with sync_playwright() as p:
        driver = p.chromium.launch(headless=False).new_page(viewport={"width": 1920, "height": 1080})
        simplex = Simplex(api_key=os.getenv("SIMPLEX_API_KEY"), driver=driver)
        simplex.goto("https://www.cgtrader.com/")

        state = simplex.take_stable_screenshot()
        bbox = simplex.find_element("search bar")

        print(bbox)

def test_hyperbrowser_integration():
    """Test Simplex integration with Hyperbrowser"""

    # Initialize Hyperbrowser client
    client = Hyperbrowser(api_key=os.getenv("HYPERBROWSER_API_KEY"))
    
    # Create a new session
    session = client.sessions.create()
    ws_endpoint = session.ws_endpoint

    try:
        with sync_playwright() as p:
            # Connect browser to Hyperbrowser session
            browser = p.chromium.connect_over_cdp(ws_endpoint)
            context = browser.new_context()
            page = context.new_page()
            
            # Initialize Simplex with the Hyperbrowser-connected page
            simplex = Simplex(api_key=os.getenv("SIMPLEX_API_KEY"), browser=browser)
            
            # Test basic functionality
            simplex.goto("https://www.cgtrader.com/")
            simplex.do("search for iphone")
            
            # Verify the search worked by finding the search results
            bbox = simplex.find_element("search results")
            assert bbox is not None, "Search results not found"
            
    finally:
        # Always stop the Hyperbrowser session
        client.sessions.stop(session.id)

if __name__ == "__main__":
    test_hyperbrowser_integration()
    
    
