# Module: PdfStudio

## Overview
The `PdfStudio` class is responsible for creating and managing PDF documents using various functionalities related to content generation, formatting and layout design. This module leverages other components of the SoftwareAI library to construct even more complex PDF documents.

## Installation
Ensure the SoftwareAI library is installed. You can install it via `pip`:
```bash
pip install softwareai
```

## Usage Example
To use the `PdfStudio` class, follow these steps:
```python
NamePdf = "Pyqt5"
Theme = "Py qt5"
Pages = 2
PdfStudioclass = PdfStudio(NamePdf, Theme, Pages)
PdfStudioclass.execute()
```

## Class: PdfStudio

### Description
The `PdfStudio` class offers features to create professional PDF documents with the help of AI functionalities, styling options, and user-friendly interface components.

### Attributes
- **NamePdf**: The name of the PDF file to be created.
- **Theme**: A string describing the theme of the PDF.
- **Pages**: Integer specifying the number of pages to generate.
- **Debug**: Boolean flag indicating if debug information should be printed.
- **DebugTokens**: Boolean flag to control token usage debug information.
- **lang**: Language setting for debug messages, defaults to Portuguese.

### Methods
#### `__init__(self, NamePdf, Theme, Pages, Debug=True, DebugTokens=True, lang="pt")`
Initializes a new `PdfStudio` instance with the specified parameters.

#### `load_keys(self)`
Loads environment variables from a `.env` file located two directories above the script.

#### `load_envwork(self)`
Loads environment configuration from a different `.env` file for workspace settings.

#### `save_TXT(self, string, filename, mode)`
Saves the provided string to a specified filename using the provided file mode.

#### `create_table(self, data)`
Creates a table using the provided data, formatted appropriately for PDF generation.

#### `process_text_with_styles(self, content)`
Processes text content to apply styles based on markdown-like syntax for appearance in the PDF.

#### `get_contrasting_color(self, bg_color)`
Calculates and returns a contrasting text color based on the given background color.

#### `set_background_and_text(self, canvas_obj, doc, bg_color)`
Sets the background and adjusts the text's color for optimal contrast.

#### `add_page_number(self, canvas_obj, doc)`
Adds a page number to the PDF layout, skipping certain pages as necessary.

#### `on_page(self, canvas, doc)`
Callback function for document pages; responsible for adding styled elements like margins and page numbers.

#### `get_color_by_title(self, title)`
Returns the appropriate color based on the title of the document section.

#### `draw_colored_margins(self, canvas, doc, color)`
Draws colored margins around the document pages based on the specified color.

#### `create_contents_page(self, doc, titles)`
Generates a contents page in the PDF based on the provided titles.

#### `get_random_image(self, image_folder)`
Selects a random image from the specified folder, to be used in the PDF.

#### `create_pdf(self, content, filename, image_folder=None)`
Main function that takes in content and generates a PDF file at the specified path.

#### `create_content(self)`
Handles the content generation using AI, incorporating various prompts and processing logic.

#### `compile_content(self, folder_path, output_pdf)`
Compiles content from multiple `.txt` files located in a specified folder into a single PDF.

#### `execute(self)`
Executes the main functionality of the `PdfStudio` class including content compilation and PDF creation.

## Conclusion
The `PdfStudio` class is a powerful tool for creating detailed, professional PDF documents with ease, enhanced by AI features and customizable layouts.
