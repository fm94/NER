# NER (Named Entity Recognition)

This repository implements a toy example on how to find sensitive information in a PDF and highlight it.

## Requirements
to install the requirements use `pip install -r requirments.txt`

## Install new NER models (spacy)

Spacy allows loading different pre-trained models. Before running the scrips in this repository you'd need to install the German package: `python -m spacy download de_core_news_sm`

## Run the algo
Simply have a PDF document ready and run `python process_document --input_pdf_path <you-path>`

This will generate an `output.pdf` document with sensitive information highlighted.
To extend the script (e.g., you want to blur/hide the sensitive information), modify the code in `_draw_rectangles_on_pdf(...)` 

## Examples
See `docs`

Have fun!