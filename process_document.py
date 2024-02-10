from dataclasses import dataclass
from pathlib import Path
from typing import NoReturn
import argparse

import fitz

from ocr import OCR
from ner import NER


def parse_arguments():
    parser = argparse.ArgumentParser(description='Process PDFs with NER.')
    parser.add_argument('--input_pdf_path', type=str, help='Path to the input PDF file (required)')
    parser.add_argument('--output_pdf_path', type=str, default='output.pdf',
                        help='Path to the output PDF file (default: output.pdf)')
    return parser.parse_args()


@dataclass
class NERConfig:
    input_pdf_path: str | Path
    output_pdf_path: str | Path


@dataclass
class PwCSmartNERSystem:
    ner_model: str = "de_core_news_sm"

    _ocr_instance: OCR | None = None
    _ner_isstance: NER | None = None
    _doc: fitz.Document | None = None

    def __post_init__(self):
        self._ocr_instance = OCR()
        self._ner_instance = NER(self.ner_model)

    def process_single_document(self, config: NERConfig) -> None:
        """
        provide a single user config and handle the respective pdf document
        :param config: a NER system config
        """
        self._load_pdf(config.input_pdf_path)
        pages_data = self._ocr_instance.read_fitz_document(self._doc)
        ner_data = []
        for text, rects in pages_data:
            entities = self._ner_instance.perform_ner(text)
            ner_data.append((entities, rects))
        self._draw_rectangles_on_pdf(config.output_pdf_path, ner_data)

    def _draw_rectangles_on_pdf(self, output_pdf_path: str | Path, ner_data) -> None:
        """
        draw entity rectangles on the current pdf document
        :param output_pdf_path: where will the new pdf be stored
        :param ner_data: data containing entities and car bboxes
        """
        for page_number in range(self._doc.page_count):
            page = self._doc[page_number]
            for entity_text, start, end, label in ner_data[page_number][0]:
                containing_rect = self._construct_containing_rectangle(ner_data[page_number][1][start:end])
                if containing_rect is not None:
                    left, top, right, bottom = containing_rect
                    page.draw_rect(fitz.Rect(left, top, right, bottom), color=(1, 0, 0))
        self._doc.save(output_pdf_path)
        # finally close the file handle
        self._doc.close()

    def _load_pdf(self, input_pdf_path: str | Path) -> None | NoReturn:
        """ load a pdf and keep the handle open """
        try:
            self._doc = fitz.open(input_pdf_path)
        except (IOError, FileNotFoundError):
            raise Exception("File does not exist or corrupted, please make sure to provide a valid path!")

    @staticmethod
    def _construct_containing_rectangle(rectangles: list[list[int]]) -> list[int] | None:
        """
        given multiple rectangles representing a word (one per char), return the total rectangle of the word
        :param rectangles: list of char rectangles
        :return: word rectangle
        """
        # skip empty rectangles (representing spaces)
        rectangles = [rect for rect in rectangles if rect]
        if not rectangles:
            return None
        min_left, min_top, max_right, max_bottom = rectangles[0]
        for rect in rectangles[1:]:
            min_left = min(min_left, rect[0])
            min_top = min(min_top, rect[1])
            max_right = max(max_right, rect[2])
            max_bottom = max(max_bottom, rect[3])
        return [min_left, min_top, max_right, max_bottom]


if __name__ == "__main__":
    args = parse_arguments()
    s = PwCSmartNERSystem()
    user_config = NERConfig(input_pdf_path=args.input_pdf_path, output_pdf_path=args.output_pdf_path)
    s.process_single_document(user_config)
