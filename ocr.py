import fitz
import pytesseract
from PIL import Image


class OCR:
    def __init__(self):
        pass

    def read_fitz_document(self, pdf_doc: fitz.Document) -> list[tuple[str, list[list[int]]]]:
        """
        take a fitz pdf and return (per page) the text and list of char rectangle coordinates
        :param pdf_doc: input document as read by fitz
        :return: list of text/coordinates pairs
        """
        pages_data = []
        pdf_images = self._convert_to_images(pdf_doc)
        for pdf_image in pdf_images:
            text, rects = self._handle_single_image(pdf_image)
            pages_data.append(self._language_model_handling(text, rects))
        return pages_data

    @staticmethod
    def _handle_single_image(image) -> tuple[str, list[list[int]]]:
        """
        decode a single pdf image
        :param image: pixel map
        :return: text string and list of rectangle coordinates of each char
        """
        # convert tessract pixelmap into a PIL image for ease of processing
        img = Image.frombytes("RGB", (image.width, image.height), image.samples)
        # decode text and coordinates, this can be combined into a single call
        # doing ocr twice might be slow if we scale up
        text = pytesseract.image_to_string(img).replace('\n', " ")[:-1]
        elementary_data = pytesseract.image_to_boxes(img, output_type=pytesseract.Output.DICT)
        # collect tdata, this can be optimized further
        rects = []
        counter = 0
        for char in text:
            # spaces do not have bboxes
            if char == " ":
                rects.append([])
            elif elementary_data['char'][counter] == char:
                rects.append(
                    [int(elementary_data['left'][counter]), image.height - int(elementary_data['top'][counter]),
                     int(elementary_data['right'][counter]), image.height - int(elementary_data['bottom'][counter])])
                counter += 1
        return text, rects

    @staticmethod
    def _convert_to_images(doc):
        """
        Convert a pdf document into a list of pixelmaps
        :param doc: pdf docment
        :return: list of images (pixel maps)
        """
        images = []
        for page_num in range(doc.page_count):
            page = doc[page_num]
            images.append(page.get_pixmap())
        return images

    @staticmethod
    def _language_model_handling(text: str, rects: list[list[int]]) -> tuple[str, list[list[int]]]:
        """ if we want to be fancier, we can add language correction here for example
         this will correct words and handle errors by tessarct """
        return text, rects
