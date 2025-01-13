## Project description

ECSEval is a Python package designed to evaluate AI-generated summaries against human-curated (SME) summaries and reference data. It focuses on metrics like factual accuracy, relevance, and completeness while leveraging Natural Language Inference (NLI) and Large Language Models (LLMs) for advanced text analysis.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install ECSEval.

```bash
pip install ECSEval
```

## Example Usage

```python
from ECSEval.summary_evaluator import SummaryEvaluator, Document

# invoking the LLM model
from langchain.chat_models import AzureChatOpenAI
from langchain.chains.question_answering import load_qa_chain

llm = AzureChatOpenAI(deployment_name=OPENAI_DEPLOYMENT_NAME,
                      model_name=OPENAI_MODEL_NAME,
                      openai_api_base=OPENAI_DEPLOYMENT_ENDPOINT,
                      openai_api_version=OPENAI_DEPLOYMENT_VERSION,
                      openai_api_key=OPENAI_API_KEY,
                      request_timeout=60)

# calling the SummaryEvaluator
evaluator = SummaryEvaluator(llm=llm)

# example Input data
reference_data = """The report discusses the presence of chemical contaminants, including lead and arsenic, 
in water samples from the region. It specifies the regulatory standards set by the Environmental Protection Agency (EPA), 
such as a maximum allowable lead level of 15 ppb. The analysis reveals that some samples exceed these regulatory thresholds, 
with lead levels reaching as high as 25 ppb in certain areas. Recommendations include immediate remediation efforts 
and stricter monitoring protocols."""
sme_summary = """The report highlights the presence of chemical contaminants like lead and arsenic in water samples. 
It mentions the EPA's regulatory standards, such as the maximum allowable lead level of 15 ppb, and states that some samples 
exceed these thresholds, with lead levels reaching 25 ppb. Remediation and monitoring efforts are recommended."""
ai_summary = """The report outlines water quality issues in the region, noting the presence of various chemicals. 
It emphasizes the need for better monitoring but does not provide details on contaminants, 
regulatory standards, or whether these standards are exceeded."""

# Evaluate summaries
metrics = evaluator.evaluate(reference_data, sme_summary, ai_summary)
print(metrics)

```
### Batch data processing
```python
import json
import pandas as pd
df = pd.read_excel('sample_data.xlsx') # dataframe containing Reference data, SME created summary and AI generated summary

metrics_list = []
for i in range(0, len(df)):
    metrics_dict  = evaluator.evaluate(df['reference text'].iloc[i], df['sme summary'].iloc[i], df['ai summary'].iloc[i])
    
    # to beautify the dict output in excel (optional)
    metrics_json = json.dumps(metrics_dict, indent=4)
    metrics_json = metrics_json.replace(r'\n', '\n')  
    
    metrics_list.append(metrics_json)

df['metrics'] = metrics_list

df.to_excel("sample_data_out.xlsx", index=False, engine='openpyxl')

```

## About

This package is built as part of our ongoing research on evaluating large language models for Environmental data. For more details about this work please refer to our research paper: "Evaluating the Evaluators: A Deep Dive into Metrics for Large Language Models on Environmental Data" which will be submitted to the MLDS 2025 Conference (https://mlds.analyticsindiamag.com/)

If you use this work, Please cite us and star at:https://github.com/dreji18/ECSEval

## License

[MIT](https://choosealicense.com/licenses/mit/)