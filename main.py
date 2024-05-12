#!/bin/python3

# import libraries
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

    # Draw bounding boxes around detected words with text
    for i in range(len(d['text'])):
        x, y, w, h = d['left'][i], d['top'][i], d['width'][i], d['height'][i]
        text = d['text'][i]
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(img, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 2)

    return recognized_text, img

def save_output_text(text, output_file_name):
    # Save the output to a text file
    with open(output_file_name + '.txt', 'w') as f:
        f.write(text)
    print(f"[green]Output text saved to {output_file_name}.txt[/]")

def save_output_image(image, output_image_path):
    # Save the output image
    cv2.imwrite(output_image_path, image)
    print(f"[green]Output image saved to {output_image_path}[/]")

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
        recognized_text, img = perform_ocr(full_image_path)
        progress.update(task, advance=1)

    # Display the recognized text
    print("[bold cyan]OCR Output:[/]\n")
    print("[center]" + recognized_text.strip() + "[/center]")

    # Ask whether to display the output image
    show_image = Prompt.ask("[cyan]Do you want to display the output image?[/]", choices=["y", "n"], default="n").lower()
    if show_image == 'y':
        cv2.imshow('Output', img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # Ask whether to save the output image
    save_image = Prompt.ask("[cyan]Do you want to save the output image?[/]", choices=["y", "n"], default="n").lower()
    if save_image == 'y':
        output_image_path = Prompt.ask("[cyan]Enter the path to save the output image:[/]", default="output.png")
        save_output_image(img, output_image_path)

    # Ask for output file name
    output_file_name = Prompt.ask("[cyan]Enter a name for the output file (without extension): [/]", default="output")

    # Save the output text to a file
    save_output_text(recognized_text, output_file_name)

if __name__ == "__main__":
    main()
