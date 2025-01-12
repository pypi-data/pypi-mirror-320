
# from dotenv import load_dotenv
import os
import json
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# load_dotenv()
# access_key = os.getenv("UNSPLASH_ACCESS_KEY")
query = "car"
import os
from .decorators import execution_time


def get_next_filename(name, path=None):
    # Separate the base name and the extension
    new_name, extension = os.path.splitext(name)
    if not path:
        path = os.getcwd()  # Use current working directory if no path is provided
    
    # Initialize the full file path
    n = 1
    p = os.path.join(path, f"{new_name}{extension}")
    
    # Check for file existence and append a number if it already exists
    while os.path.exists(p):
        p = os.path.join(path, f"{new_name}({n}){extension}")
        n += 1
    
    return os.path.basename(p)

def download_image(query, access_key=None):
    # Ensure access_key is provided before proceeding
    if not access_key:
        logger.error("Access key is missing.")
        raise RuntimeError("You have to add the access key.")
    
    # Construct the Unsplash API URL
    url = f"https://api.unsplash.com/photos/random?query={query}&client_id={access_key}"
    
    # Fetch the random image data from Unsplash API
    try:
        logger.info("Fetching image data from Unsplash")
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors
    except requests.RequestException as e:
        logger.error(f"Error fetching image data: {e}")
        return

    # Save the API response to a JSON file
    with open(f'{query}_response.json', "w") as f:
        json.dump(response.json(), f, indent=4)
    
    data = response.json()
    img_url = data['urls'].get("raw")
    description = data.get('description', query)
    
    if not img_url:
        logger.error("Image not url found")
        return

    # Create the directory for storing the images
    path = os.path.join("media", query)
    os.makedirs(path, exist_ok=True)  # Recursively create directories if they don't exist
    
    # Generate a unique filename
    title = get_next_filename(description if description else query + ".jpg", path)
    
    # Stream the image content (for handling large files efficiently)
    try:
        logger.info(f"Downloading image for query: {query}.")
        image_response = requests.get(img_url, stream=True)
        image_response.raise_for_status()  # Check for any image download issues
    except requests.RequestException as e:
        logger.error(f"Error downloading image: {e}")
        print(f"Error downloading image: {e}")
        return

    # Save the image to disk
    image_path = os.path.join(path, f"{title}.jpg")
    with open(image_path, "wb") as f:
        for chunk in image_response.iter_content(1024):  # Stream data in chunks
            f.write(chunk)
    
    logger.info(f"Image downloaded successfully to {image_path}!")


