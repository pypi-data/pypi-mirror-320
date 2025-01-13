from playwright.sync_api import Page, sync_playwright, Browser
from PIL import Image
import requests
from typing import List
import io

from .utils import center_bbox, screenshot_to_image

BASE_URL = "https://u3mvtbirxf.us-east-1.awsapprunner.com"

class Simplex:
    def __init__(self, api_key: str, browser: Browser = None):
        """
        Initialize Simplex instance
        
        Args:
            api_key (str): API key for authentication
            browser (optional): Browser instance (for Hyperbrowser integration)
        """
        self.api_key = api_key
        self.browser = browser
        
        if browser is None:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=True)
            self.driver = self.browser.new_page()
        else:
            self.playwright = None
            if len(self.browser.contexts) > 0 and len(self.browser.contexts[0].pages) > 0:
                self.driver = self.browser.contexts[0].pages[0]
            else:
                self.driver = self.browser.new_page()

    def find_element(self, element_description: str, state: Image.Image | None = None, annotate: bool = True) -> List[int]:
        """
        Find an element in the screenshot using the element description

        Args:
            element_description (str): Description of the element to find
            screenshot (PIL.Image.Image): Screenshot of the page
        
        Returns:
            bounding_box (tuple): [x1, y1, x2, y2] bounding box of the found element
        """
        if state is None:
            state = self.take_stable_screenshot()

        endpoint = f"{BASE_URL}/find-element"
        
        # Convert PIL Image to bytes
        img_byte_arr = io.BytesIO()
        state.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        # Prepare multipart form data
        files = {
            'image_data': ('screenshot.png', img_byte_arr, 'image/png'),
            'element_description': (None, element_description),
            'api_key': (None, self.api_key)
        }        

        # Make the request
        response = requests.post(
            endpoint,
            files=files
        )


        # Print the results
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            res = response.json()
            bbox = [int(res['x1']), int(res['y1']), int(res['x2']), int(res['y2'])]

            # Add overlay directly to the page if driver exists
            if hasattr(self, 'driver') and annotate:
                # Create and inject overlay element
                self.driver.evaluate("""
                    (bbox) => {
                        // Remove any existing overlay
                        const existingOverlay = document.getElementById('simplex-bbox-overlay');
                        if (existingOverlay) {
                            existingOverlay.remove();
                        }
                        
                        // Create new overlay
                        const overlay = document.createElement('div');
                        overlay.id = 'simplex-bbox-overlay';
                        overlay.style.position = 'fixed';
                        overlay.style.border = '2px dashed rgba(74, 144, 226, 1)';
                        overlay.style.background = 'rgba(74, 144, 226, 0.1)';
                        overlay.style.animation = 'marching-ants 0.5s linear infinite';
                        overlay.style.left = bbox[0] + 'px';
                        overlay.style.top = bbox[1] + 'px';
                        overlay.style.width = (bbox[2] - bbox[0]) + 'px';
                        overlay.style.height = (bbox[3] - bbox[1]) + 'px';
                        overlay.style.pointerEvents = 'none';
                        overlay.style.zIndex = '10000';
                        overlay.style.margin = '0';
                        overlay.style.padding = '0';
                        
                        // Add marching ants animation keyframes
                        if (!document.querySelector('#marching-ants-keyframes')) {
                            const style = document.createElement('style');
                            style.id = 'marching-ants-keyframes';
                            style.textContent = `
                                @keyframes marching-ants {
                                    0% { border-style: dashed; }
                                    50% { border-style: solid; }
                                    100% { border-style: dashed; }
                                }
                            `;
                            document.head.appendChild(style);
                        }
                        
                        document.body.appendChild(overlay);

                        // Remove overlay after 3 second
                        setTimeout(() => {
                            overlay.remove();
                        }, 2000);
                    }
                """, bbox)
                self.driver.wait_for_selector('#simplex-bbox-overlay')
            return bbox 
        else:
            print("Error:", response.text)

    def step_to_action(self, step_description: str, state: Image.Image | None = None) -> List[List[str]]:
        """
        Convert a step description to an action

        Args:
            step_description (str): Description of the step to convert to action
            screenshot (PIL.Image.Image): Screenshot of the page
        
        Returns:
            action (List[List[str, str]]): List of actions to perform
        """
        if state is None:
            state = self.take_stable_screenshot()

        endpoint = f"{BASE_URL}/step_to_action"
        
        # Convert PIL Image to bytes
        img_byte_arr = io.BytesIO()
        state.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        # Prepare form data
        files = {
            'image_data': ('screenshot.png', img_byte_arr, 'image/png'),
            'step': (None, step_description),
            'api_key': (None, self.api_key)
        }
        
        # Make the request
        response = requests.post(
            endpoint,
            files=files
        )
        
        # Handle response
        if response.status_code == 200:
            res = response.json()
            actions = res.split('\n')
            actions = [action.split(',') for action in actions]
            actions = [[action.strip() for action in action_pair] for action_pair in actions]
            return actions
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return []
        
    def goto(self, url: str, new_tab: bool = False) -> None:
        """
        Navigate to a URL

        Args:
            url (str): URL to navigate to
            new_tab (bool): Whether to open a new tab or use the current tab
        """
        if new_tab:
            self.driver = self.browser.new_page()
        self.driver.goto(url)

    def execute_action(self, action: List[List[str]], state: Image.Image | None = None, annotate: bool = True) -> None:
        """
        Execute an action with playwright driver

        Args:
            action (List[List[str]]): List of actions to perform
        """
        action_type, description = action
        if state is None:
            state = self.take_stable_screenshot()

        try:
            if action_type == "CLICK":
                bbox = self.find_element(description, state, annotate=annotate)
                center_x, center_y = center_bbox(bbox)
                self.driver.mouse.click(center_x, center_y)

            elif action_type == "HOVER":
                bbox = self.find_element(description, state, annotate=annotate)
                center_x, center_y = center_bbox(bbox)
                self.driver.mouse.move(center_x, center_y)

            elif action_type == "TYPE":
                self.driver.keyboard.type(description)

            elif action_type == "ENTER":
                self.driver.keyboard.press("Enter")

            elif action_type == "SCROLL":
                self.driver.mouse.wheel(0, int(description))

            elif action_type == "WAIT":
                self.driver.wait_for_timeout(int(description))

        except Exception as e:
            print(f"Error executing action: {e}")
            return None
        
    def do(self, step_description: str, annotate: bool = True) -> None:
        """
        Execute a step description
        """
        state = self.take_stable_screenshot()
        actions = self.step_to_action(step_description, state)
        for action in actions:
            self.execute_action(action, annotate=annotate)
            
    def take_stable_screenshot(self) -> Image.Image:
        """
        Take a screenshot after ensuring the page is in a stable state.
        
        Returns:
            PIL.Image.Image: Screenshot of the current page
        """
        self.driver.wait_for_load_state('networkidle')
        return screenshot_to_image(self.driver.screenshot())
            
       