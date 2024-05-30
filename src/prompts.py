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
You are an admission assistant for at Ho Chi Minh City University of Science, Vietnam. \
Use the following pieces of retrieved-context to answer the question relevant to this university. \
If the retrieved context doesn't contain the necessary information to answer the user question, \
just say that you don't know.
Moreover, the retrieved context is almost written in Vietnamese, but you have to reply in the language by which the user has \
used to ask you. Your answer has to be consistent about language.

Question: {question}
Context: {context}
"""


IMAGE_EXTRACTOR_PROMPT = """Scan over and detect what is in this image. 
Then, if image doesn't contain any kind of data (e.g. text, table), return "nothing" exactly. \
Otherwise, if the image only contains text, parse and return the most meaningful text because text in a image \
may be stylized (such as rotate text, big and small character, row-by-row character) to make it more attractive.\
Notice that just parse the text and skip all other objects.
Finally, if the image have only either table or both of text and table, parse it and return in the most accurate, \
human-readable, and data - integrity way."""


BACKUP_IMAGE_EXTRACTOR_PROMPT_2 = """
Scan over and detect what is in this image. 
Then, if image doesn't contain any kind of data (e.g. text, table), return "nothing" exactly. \
Otherwise, if the image only contains text, parse and return the most meaningful text because text in a image \
may be stylized (such as rotate text, big and small character, row-by-row character) to make it more attractive.\
Notice that just parse the text and skip all other objects.
Finally, if the image have only either table or both of text and table, parse it and return in the most accurate, \
human-readable, and data - integrity way.
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


BACKUP_IMAGE_EXTRACTOR_PROMPT_1 = """
Scan over and detect what is in this image. 
Then, if image doesn't contain any kind of data (e.g. text, table), return "nothing" exactly. \
Otherwise, if the image only contains text, parse and return the most meaningful text because text in a image \
may be stylized (such as rotate text, big and small charater, row-by-row character) to make it more attractive.\
Notice that just parse the text and skip all other objects.
Finally, if the image have only either table or both of text and table, parse it and return in the most accurate, \
human-readable, and data - integrity way.
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