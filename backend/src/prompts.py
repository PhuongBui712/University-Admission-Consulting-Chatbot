LLAMA3_RAG_PROMPT = """
<|begin_of_text|>
<|start_header_id|>system<|end_header_id|>
You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the \
question. If you don't know the answer, just say that you don't know.
The question or even context can be written in Vietnamese or English. If user don't ask to reply by which language\
you have to primarily answer by Vietnamese. Otherwise, reply the question by requested language.
<|eot_id|>
<|start_header_id|>user<|end_header_id|>
Question: {question}
Context: {context}
<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""


ADMISSION_CONSULTANT_PROMPT = """\
You are an admission assistant for Ho Chi Minh City University of Science, Vietnam. \
Use the following pieces of retrieved-context to answer the question relevant to this university. \
If the retrieved context doesn't contain the necessary information to answer the user question, \
just say that you don't know.

Moreover, the retrieved context is almost written in Vietnamese, but you have to reply in the language by which the \
user has used to ask you. Your answer has to be consistent to user's question.
For example:
- User's question is in English:
    + Question: Who are you?
    + Answer: I am admission assistant Ho Chi Minh City University of Science, Vietnam
- Uer's question is in Vietnamese:
    + Question: Bạn là ai?
    + Answer: Tôi là trợ lý sinh viên của Trường Đại học Khoa học Tự nhiên TP.HCM, Việt Nam

Answer following questions using provided context:
Context: {context}
Question: {question}
"""

# Image extractor prompts
IMAGE_EXTRACTOR_PROMPT_5 = """You are given an image as input. Your task is to parse the image based on the following criteria:

1. If the image contains text or a table:
  - Parse the text or table (or both of them), even if it is stylized (e.g., rotated, varying font sizes, row-by-row characters) to make it more attractive.
  - Return the most meaningful text or table content.
  - The parsed table should be formatted as the example 1.

2. If the image contains any other kind of data (diagrams, graphs, etc.) or doesn't contain any kind of data.
  - Return the string "other".

Example 1 (Image containing a table or text ):
Input Image:
[Image contain a string "Điểm chuẩn" and a table]

Expected Output:
Điểm chuẩn
|----------|-------------------|-----------------------------------------------------------------------|-------|-------|-------|
| Mã ngành | Ngành, nhóm ngành | PTXT2                                                                 | PTXT3 | PTXT4 | PTXT6 |
|          |                   |-----------------------------------------------------------------------|       |       |       |
|          |                   | Ưu tiên xét tuyển thẳng (ĐHQG - HCM) | Ưu tiên xét tuyển (ĐHQG - HCM) |       |       |       |
|----------|-------------------|-----------------------------------------------------------------------|-------|-------|-------|
|12342     | Hải dương học     |  8.90                                |  8.39                          | 19.00 | 600   |   -   |
|----------|-------------------|-----------------------------------------------------------------------|-------|-------|-------|

Example 2 (Image containing a diagram):
Input Image:
[An image containing a diagram or graph]

Expected Output:
others

Example 3 (Image without any data):
Input Image:
[An image without any data, text, or tabular information]

Expected Output:
others

Please provide the parsed text, table, or the appropriate string based on the input image."""


IMAGE_EXTRACTOR_PROMPT = """You will be given an image as input. Your task is to analyze the image and follow these instructions:

1. If the image contains only text, parse the text and return the most meaningful text content. The text in the image may be stylized \
(e.g., rotated, varying font sizes, row-by-row characters) to make it more visually appealing. Your goal is to extract the meaningful \
text content while ignoring any stylistic elements.

2. If the image contains any kind of data such as tables, diagrams, graphs, or charts, or does not contain any meaningful \
text or data, return the string "others".

Here are some examples:

Example 1 (Image containing stylized text):
[Insert image of stylized text, e.g., text with varying font sizes and orientations - "Hello World"]
Expected output: "Hello World"

Example 2 (Image containing a table):
[Insert image containing a data table]
Expected output: "others"

Example 3 (Image containing a graph):
[Insert image containing a graph or chart]
Expected output: "others"

Example 4 (Image without any text or data):
[Insert image without any meaningful content, e.g., a solid color or abstract pattern]
Expected output: "others"

Your response should be a string containing either the parsed meaningful text content or the string "nothing" based on the instructions above."""


IMAGE_EXTRACTOR_PROMPT_4 = """Scan over and detect what is in this image. 
Then, if image doesn't contain any kind of data (e.g. text, table), return "nothing" exactly. \
Otherwise, if the image only contains text, parse and return the most meaningful text because text in a image \
may be stylized (such as rotate text, big and small character, row-by-row character) to make it more attractive.\
Notice that just parse the text and skip all other objects.
Finally, if the image have only either table or both of text and table, return "nothing" too."""


IMAGE_EXTRACTOR_PROMPT_3 = """Scan over and detect what is in this image. 
Then, if image doesn't contain any kind of data (e.g. text, table), return "nothing" exactly. \
Otherwise, if the image only contains text, parse and return the most meaningful text because text in a image \
may be stylized (such as rotate text, big and small character, row-by-row character) to make it more attractive.\
Notice that just parse the text and skip all other objects.
Finally, if the image have only either table or both of text and table, parse it and return in the most accurate, \
human-readable, and test_data - integrity way."""


IMAGE_EXTRACTOR_PROMPT_2 = """
Scan over and detect what is in this image. 
Then, if image doesn't contain any kind of test_data (e.g. text, table), return "nothing" exactly. \
Otherwise, if the image only contains text, parse and return the most meaningful text because text in a image \
may be stylized (such as rotate text, big and small character, row-by-row character) to make it more attractive.\
Notice that just parse the text and skip all other objects.
Finally, if the image have only either table or both of text and table, parse it and return in the most accurate, \
human-readable, and test_data - integrity way.
For example: an image has a title is text and a table could be parsed like following
TRƯỜNG ĐẠI HỌC KHOA HỌC TỰ NHIÊN
Điểm chuẩn các phương thức xét tuyển năm 2023
Lĩnh vực khoa học tự nhiên
|----------|-------------------|-----------------------------------------------------------------------|-------|-------|-------|
| Mã ngành | Ngành, nhóm ngành | PTXT2                                                                 | PTXT3 | PTXT4 | PTXT6 |
|          |                   |-----------------------------------------------------------------------|       |       |       |
|          |                   | Ưu tiên xét tuyển thẳng (ĐHQG - HCM) | Ưu tiên xét tuyển (ĐHQG - HCM) |       |       |       |
|----------|-------------------|-----------------------------------------------------------------------|-------|-------|-------|
|12342     | Hải dương học     |  8.90                                |  8.39                          | 19.00 | 600   |   -   |
|----------|-------------------|-----------------------------------------------------------------------|-------|-------|-------|
Lĩnh vực khoa học sự sống
|----------|-------------------|-----------------------------------------------------------------------|-------|-------|-------|
|12343     | Sinh học          |  8.50                                |  8.16                          | 21.50 | 650   |   -   |
|----------|-------------------|-----------------------------------------------------------------------|-------|-------|-------|
"""


IMAGE_EXTRACTOR_PROMPT_1 = """
Scan over and detect what is in this image. 
Then, if image doesn't contain any kind of test_data (e.g. text, table), return "nothing" exactly. \
Otherwise, if the image only contains text, parse and return the most meaningful text because text in a image \
may be stylized (such as rotate text, big and small charater, row-by-row character) to make it more attractive.\
Notice that just parse the text and skip all other objects.
Finally, if the image have only either table or both of text and table, parse it and return in the most accurate, \
human-readable, and test_data - integrity way.
For example: an image have content like following
TRƯỜNG ĐẠI HỌC KHOA HỌC TỰ NHIÊN
Điểm chuẩn các phương thức xét tuyển năm 2023

Lĩnh vực khoa học tự nhiên
|----------|-------------------|-----------------------------------------------------------------------|-------|-------|-------|
| Mã ngành | Ngành, nhóm ngành | PTXT2                                                                 | PTXT3 | PTXT4 | PTXT6 |
|          |                   |-----------------------------------------------------------------------|       |       |       |
|          |                   | Ưu tiên xét tuyển thẳng (ĐHQG - HCM) | Ưu tiên xét tuyển (ĐHQG - HCM) |       |       |       |
|----------|-------------------|-----------------------------------------------------------------------|-------|-------|-------|
|12342     | Hải dương học     |  8.90                                |  8.39                          | 19.00 | 600   |   -   |
|----------|-------------------|-----------------------------------------------------------------------|-------|-------|-------|
Lĩnh vực khoa học sự sống
|----------|-------------------|-----------------------------------------------------------------------|-------|-------|-------|
|12343     | Sinh học          |  8.50                                |  8.16                          | 21.50 | 650   |   -   |
|----------|-------------------|-----------------------------------------------------------------------|-------|-------|-------|

The result you have to return could be like that:
TRƯỜNG ĐẠI HỌC KHOA HỌC TỰ NHIÊN
Điểm chuẩn các phương thức xét tuyển năm 2023
-----------------------------Start Table-----------------------------
I. Lĩnh vực khoa học tự nhiên
1. Mã ngành: 12342
    - Ngành, nhóm ngành: Hải dương học
    - PTXT2:
        + Ưu tiên xét tuyển thẳng (ĐHQG - HCM): 8.90
        + Ưu tiên xét tuyển (ĐHQG - HCM): 8.39
    - PTXT3: 19.00
    - PTXT4: 600
    - PTXT6: không có
II. Lĩnh vực khoa học sự sống
1. Mã ngành: 12343
    - Ngành, nhóm ngành: Sinh học
    - PTXT2:
        + Ưu tiên xét tuyển thẳng (ĐHQG - HCM): 8.50
        + Ưu tiên xét tuyển (ĐHQG - HCM): 8.16
    - PTXT3: 21.50
    - PTXT4: 650
    - PTXT6: không có
------------------------------End Table------------------------------
"""


# Summarize prompt
TEXT_SUMMARIZE_PROMPT = """You are an assistant tasked with summarizing tables and texts for retrieval. \
These summaries will be embedded and used to retrieve the raw text or table elements.

Your task is to provide a concise summary of the given table or text in the same language as the input. \
The summary should be well-optimized for retrieval purposes, capturing the essential information while being concise and relevant.

Table or text: {input}
"""


IMAGE_SUMMARIZE_PROMPT = """You are an assistant tasked with summarizing images for retrieval. \
These summaries will be embedded and used to retrieve the raw image. \
Give a concise summary of the image that is well optimized for retrieval.
If it's a table, extract all elements of the table.
If it's a graph, explain the findings in the graph.
Do not include any numbers that are not mentioned in the image.
"""