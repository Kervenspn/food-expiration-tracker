from google.cloud import vision

client = vision.ImageAnnotatorClient()

def detect_food_name(image_path):
    with open(image_path, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    text_response = client.text_detection(image=image)
    label_response = client.label_detection(image=image)

    # Try text first (best for packaging like "Milk", "Eggs", etc.)
    if text_response.text_annotations:
        return text_response.text_annotations[0].description.split("\n")[0]

    # Fallback to labels
    if label_response.label_annotations:
        return label_response.label_annotations[0].description

    return ""