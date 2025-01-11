"""This module contains the functions to extract data from an Excel file."""
import json
from collections import defaultdict

import numpy as np
import pandas as pd

from src.io import logger
from src.llm import prompt_excel_extraction
from src.postprocessing.common import remove_none_values
from src.utils import generate_schema_structure, get_excel_sheets


async def extract_data_from_excel(
    params,
    input_doc_type,
    file_content,
    schema_client,
    mime_type,
):
    """Extract data from the Excel file.

    Args:
        params (dict): Parameters for the data extraction process.
        input_doc_type (str): The type of the document.
        file_content (bytes): The content of the Excel file to process.
        schema_client (DocumentSchemaClient): Client for the Document AI schema.
        mime_type (str): The MIME type of the file.

    Returns:
        formatted_data (list): A list of dictionaries containing the extracted data.
        result (list): The extracted data from the document.
        model_id (str): The ID of the model used for extraction.

    """
    # Generate the response structure
    response_schema = await generate_schema_structure(
        params, input_doc_type, schema_client
    )

    # Load the Excel file and get ONLY the "visible" sheet names
    sheets, workbook = get_excel_sheets(file_content, mime_type)

    # Store the extracted data from multiple worksheets
    extracted_data = defaultdict(dict)
    stored_data = defaultdict(dict)

    # Excel files may contain multiple sheets. Extract data from each sheet
    for sheet in sheets:
        logger.info(f"Processing sheet: {sheet}")
        excel_content = pd.DataFrame(workbook[sheet].values)
        # Convert to Markdown format for the LLM model
        worksheet = (
            "This is from a excel. Pay attention to the cell position:\n"
            + excel_content.replace(np.nan, "").to_markdown(index=False, headers=[])
        )

        # Prompt for the LLM JSON
        prompt_docai = prompt_excel_extraction(worksheet)

        # Extract the data from the Excel file
        # parameters = params["gemini_params"] if "gemini_params" in params else None
        try:
            result = params["LlmClient"].get_unified_json_genai(
                prompt_docai,
                response_schema=response_schema,
            )
        except Exception as e:
            logger.error(f"Error extracting data from LLM: {e}")
            continue

        # Filter None values
        filtered_result = remove_none_values(result)

        # Append the extracted data to the dictionary. Couldn't use defaultdict(list) due to the logs storage d_type
        extracted_data[sheet] = filtered_result
        stored_data[sheet] = result

    stored_data = json.dumps(dict(stored_data))

    return dict(extracted_data), stored_data, params["gemini_params"]["model_id"]
