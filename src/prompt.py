prompt_str = """\
Give me a summary of the table with the following JSON format.

- The table name must be unique to the table and describe it while being concise.
- Do NOT output a generic table name (e.g. table, my_table).

Do NOT make the table name one of the following: {exclude_table_name_list}

Table:
{table_str}

Summary: """

REFINE_PROMPT = """\
You will be given a list of history messages and the current user question.\
Your task is to refine the user question based on the previous user question.\
If the current question is not related to the {num} previous user's questions, please return the original question.
Otherwise, you must use the previous user questions to make the current question more effective summarizing the user's intent.

Example:
History:
- user: Có bao nhiêu người ủng hộ trong ngày 2 tháng 9?

Question: Vậy trong ngày 5 tháng 9 thì sao?
After refining: Có bao nhiêu người ủng hộ trong ngày 5 tháng 9?

History:
- user: Nguyen Van A ủng hộ bao nhiêu?

Question: Nội dung chuyển khoản ?
After refining: Nội dung chuyển khoản của Nguyen Van A là gì?
"""
