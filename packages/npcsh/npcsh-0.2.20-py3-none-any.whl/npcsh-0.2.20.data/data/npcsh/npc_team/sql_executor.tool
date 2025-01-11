# npcsh/npc_team/tools/sql_executor.tool

tool_name: sql_executor
inputs:
  - sql_query
preprocess:
  - engine: python
    code: |
      import pandas as pd
      df = pd.read_sql_query(inputs['sql_query'], npc.db_conn)
      context['df'] = df
prompt:
  engine: natural
  code: |
    The result of your SQL query is:
    ```
    {{ df }}
    ```
postprocess:
  - engine: natural
    code: |
      {{ llm_response }}