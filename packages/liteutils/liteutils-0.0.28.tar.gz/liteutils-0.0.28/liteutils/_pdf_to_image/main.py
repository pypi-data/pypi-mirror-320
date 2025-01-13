import os
from pathlib import Path

from pdf2image import convert_from_path


def pdf_to_images(pdf_path, output_path=None, dpi=300, **kwargs):
    """
    Convert PDF to image(s). If output_path is 'output.png', saves only first page.
    Otherwise saves all pages in the specified directory.

    Args:
        pdf_path (str): Path to the input PDF file
        output_path (str, optional): Can be either:
                                   - 'output.png': saves only first page
                                   - directory path: saves all pages in this directory
                                   - None: creates and uses 'pdf_to_images' directory
        dpi (int, optional): DPI for the output image. Defaults to 200
        **kwargs: Additional arguments to pass to convert_from_path

    Returns:
        Union[str, List[str]]: Path or list of paths to saved image(s)
    """
    try:
        # Single page mode - save as output.png
        is_single_page_mode = output_path.rsplit(".",1)[-1] in ["png", "jpg", "jpeg"]

        if is_single_page_mode:
            pages = convert_from_path(
                pdf_path,
                dpi=dpi,
                first_page=1,
                last_page=1,
                **kwargs
            )
            if pages:
                pages[0].save(output_path, 'PNG')
                return 'output.png'

        # Multi-page mode - save all pages in directory
        else:
            # Use default directory if none provided
            save_directory = 'pdf_to_images' if output_path is None else output_path

            # Create output directory if it doesn't exist
            os.makedirs(save_directory, exist_ok=True)

            # Convert all pages
            pages = convert_from_path(
                pdf_path,
                dpi=dpi,
                **kwargs
            )

            # Save all pages with numbered filenames
            saved_paths = []
            for i, page in enumerate(pages):
                page_path = os.path.join(save_directory, f'page_{i + 1}.png')
                page.save(page_path, 'PNG')
                saved_paths.append(page_path)

            return saved_paths

    except Exception as e:
        raise Exception(f"Error converting PDF: {str(e)}")

    return None