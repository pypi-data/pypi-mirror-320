import re
import nltk
from nltk.tokenize import sent_tokenize
from sklearn.metrics import precision_score, recall_score, f1_score
from transformers import pipeline
from langchain.chat_models import AzureChatOpenAI
from langchain.chains.question_answering import load_qa_chain
from transformers import AutoTokenizer

nltk.download("punkt")
nltk.download('punkt_tab')

#%%
class SummaryEvaluator:
    def __init__(self, llm=None):
        self.llm = llm
        self.query_list = [
        "Are any contaminants present at the site? Respond with 1 for Yes and 0 for No.",
        "Are contaminants present in water, soil, or air? Respond with 1 for Yes and 0 for No.",
        "Are concentrations of each contaminant measurable? Respond with 1 for Yes and 0 for No.",
        "Are there any regulatory standards or guidelines mentioned? Respond with 1 for Yes and 0 for No.",
        "Are any contaminants exceeding the regulatory standards? Respond with 1 for Yes and 0 for No."
        ] 

    def retrieve_value(self, docs, query):
        if self.llm is None:
            raise ValueError("LLM is not initialized. Please provide an LLM instance.")
        
        chain = load_qa_chain(self.llm, chain_type="stuff")
        document_objects = [Document(doc) for doc in docs]
        res = chain.run(input_documents=document_objects, question=query)
        
        # Extract binary response
        try:
            match = re.search(r'\b[01]\b', res)
            if match:
                return int(match.group())
            else:
                return 0
        except Exception:
            return 0

    def compute_answer_metrics(self, sme_summary, ai_summary):
               
        sme_answer_list = [self.retrieve_value([sme_summary], query) for query in self.query_list]
        total_answer_count = sme_answer_list.count(1)

        ai_answer_list = [self.retrieve_value([ai_summary], query) for query in self.query_list]
        ai_answer_count = ai_answer_list.count(1)

        answer_relevance = ai_answer_count / total_answer_count if total_answer_count > 0 else 0
        answer_completeness = ai_answer_count / len(self.query_list)

        return answer_relevance, answer_completeness
    
    def verify_factual_accuracy_LLM(self, ai_summary, reference):
        sentences = sent_tokenize(ai_summary)
        ground_truth_labels = [1] * len(sentences)  # Assume all sentences should be factually correct
        explanations = []
        predicted_labels = []
        
        # Define valid NLI labels
        valid_labels = ["ENTAILMENT", "NEUTRAL", "CONTRADICTION"]
        valid_label_pattern = r"\b(?:ENTAILMENT|NEUTRAL|CONTRADICTION)\b"

        for sentence in sentences:
            # Construct the prompt for the LLM
            messages = [
                {"role": "system", "content": "You are an NLI expert. Your task is to evaluate the relationship between a reference text and a given sentence."},
                {"role": "user", "content": (
                    f"Determine the relationship between the following:\n\n"
                    f"Reference Text:\n{reference}\n\n"
                    f"Sentence:\n{sentence}\n\n"
                    f"Options:\n"
                    f"- ENTAILMENT: The sentence is factually supported by the reference.\n"
                    f"- NEUTRAL: The sentence's factual accuracy cannot be determined from the reference.\n"
                    f"- CONTRADICTION: The sentence conflicts with the reference.\n\n"
                    f"Answer with one of: ENTAILMENT, NEUTRAL, or CONTRADICTION."
                )}
            ]

            # Use the LLM to predict the label
            response = self.llm.invoke(input=messages)
            predicted_label = response.content.strip()
            
            # Check if the predicted label is valid using regex
            match = re.search(valid_label_pattern, predicted_label.upper())
            if match:
                predicted_label = match.group(0)  # Extract valid label
            else:
                predicted_label = "NEUTRAL"  # Default to NEUTRAL if no valid label is found

            explanation = f'Sentence: "{sentence}"\nPredicted Label: {predicted_label}'
            explanations.append(explanation)

            # Convert label to binary (ENTAILMENT -> 1, others -> 0)
            if predicted_label.upper() == "ENTAILMENT":
                predicted_labels.append(1)
            else:
                predicted_labels.append(0)

        # Calculate metrics
        precision = precision_score(ground_truth_labels, predicted_labels)
        recall = recall_score(ground_truth_labels, predicted_labels)
        f1 = f1_score(ground_truth_labels, predicted_labels)

        # Add metrics to explanations
        explanations.append(f"\nMetrics:\nPrecision: {precision:.2f}\nRecall: {recall:.2f}\nF1 Score: {f1:.2f}")

        # Overall summary status
        factual_correctness = all(label == 1 for label in predicted_labels)
        status = "Summary is factually correct (all sentences ENTAILMENT)." if factual_correctness else "Summary is factually incorrect (NEUTRAL/CONTRADICTION detected)."
        explanations.append(f"Status: {status}")

        explanations = "\n".join(explanations)

        return precision, recall, f1, factual_correctness, explanations

    def evaluate(self, page_data, sme_summary, ai_summary):

        answer_relevance, answer_completeness = self.compute_answer_metrics(sme_summary, ai_summary)
        precision, recall, f1, factual_correctness, explanations = self.verify_factual_accuracy_LLM(ai_summary, page_data)

        return {
            "answer_relevance": answer_relevance,
            "answer_completeness": answer_completeness,
            "factual_correctness": factual_correctness,
            "explanations": explanations,
            "precision": precision,
            "recall": recall,
            "f1": f1
        }

# Document class for LangChain compatibility
class Document:
    def __init__(self, page_content, metadata=None):
        self.page_content = page_content
        self.metadata = metadata if metadata is not None else {}