import cv2
import pytesseract

from pytesseract import Output
from rich.progress import Progress
from rich.prompt import Prompt
from rich import print

def perform_ocr(image_path):
    # Load the image
    img = cv2.imread(image_path)

    # Preprocess the image
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Perform OCR using Tesseract
    custom_config = r'-l eng --oem 3 --psm 6'
    d = pytesseract.image_to_data(thresh, output_type=Output.DICT, config=custom_config)

    # Extract the text and its corresponding bounding box
    recognized_text = ''
    for i in range(len(d['text'])):
        recognized_text += d['text'][i] + ' '

    return recognized_text, img, d

def save_output_text(text, output_file_name):
    # Save the output to a text file
    with open(output_file_name + '.txt', 'w') as f:
        f.write(text)
    print("Output saved to", output_file_name + '.txt')

def display_image_with_text(image, d):
    for i in range(len(d['text'])):
        x, y, w, h = d['left'][i], d['top'][i], d['width'][i], d['height'][i]
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(image, d['text'][i], (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    cv2.imshow('Output', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def main():
    # Ask for the image path
    image_path = Prompt.ask("[bold cyan]Enter the path to the image file: [/]")

    # Ask for the file extension
    file_extension = Prompt.ask("[bold cyan]Enter the file extension (e.g., png, jpg, etc.): [/]", default="png")

    # Path to the image
    full_image_path = f"{image_path}.{file_extension}"

    # Show loading progress
    with Progress() as progress:
        task = progress.add_task("[cyan]Performing OCR...", total=1)
        recognized_text, img, d = perform_ocr(full_image_path)
        progress.update(task, advance=1)

    # Display the recognized text
    print("[bold cyan]OCR Output:[/]\n")
    print("[center]" + recognized_text.strip() + "[/center]")

    # Ask whether to display the output image
    show_image = Prompt.ask("[cyan]Do you want to display the output image? (y/n): [/]", choices=["y", "n"], default="n").lower()
    if show_image == 'y':
        display_image_with_text(img, d)

    # Ask for output file name
    output_file_name = input("Enter a name for the output file (without extension): ")

    # Save the output text to a file
    save_output_text(recognized_text, output_file_name)

if __name__ == "__main__":
    main()
