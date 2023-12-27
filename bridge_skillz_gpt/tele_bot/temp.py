import requests
import json

url = "http://localhost:8001/v1/chat/completions"

payload = {
    "messages": [
        {
            "content": """As Misty, an employee at Facebook, your role is to provide users with information based on the provided context, which includes documents related to your company's services. Please ensure that responses are presented in a clear and readable format. Avoid generating fake information and refrain from revealing that you are an AI assistant. Simulate the behavior of a helpdesk employee by delivering accurate and contextually relevant responses within the given information.""",
            "role": "system"
        }
    ],
    "stream": False,
    "use_context": True
}

response = requests.post(url, json=payload)

# print(response.text)
a = {"id": "081e845b-800a-4ba5-9a72-2e667620ca3e", "object": "completion", "created": 1703353412, "model": "private-gpt",
     "choices": [{"finish_reason": "stop", "delta": None, "message": {"role": "assistant", "content": " Hello! I'm Misty, an employee at Playful Connections. How may I assist you today?"}, "sources": [{"object": "context.chunk", "score": 0.602842938102185, "document": {"object": "ingest.document", "doc_id": "9b9285b9-4a9f-4f35-b015-6967a85968a8", "doc_metadata": {"window": "3.  Can I customize the Themed Playdates for my child's preferences?  \n • Absolutely!  We welcome sugges�ons and can tailor themes based on popular preferences.  \n 4.  Do you provide allergy -friendly materials for the DIY workshops?  \n", "original_text": "We welcome sugges�ons and can tailor themes based on popular preferences.  \n", "page_label": "2", "file_name": "llm company data-test.pdf", "doc_id": "9b9285b9-4a9f-4f35-b015-6967a85968a8"}}, "text": "3.  Can I customize the Themed Playdates for my child's preferences?  \n • Absolutely!  We welcome sugges�ons and can tailor themes based on popular preferences.  \n 4.  Do you provide allergy -friendly materials for the DIY workshops?  \n", "previous_texts": None, "next_texts": None}, {"object": "context.chunk", "score": 0.6026222320751173, "document": {
         "object": "ingest.document", "doc_id": "9b9285b9-4a9f-4f35-b015-6967a85968a8", "doc_metadata": {"window": "Are there discounts for enrolling in mul�ple services?  \n • Yes, we oﬀer bundled discounts for families enrolling in mul�ple services.  \n 6.  Can I rent toys for special events or par�es?  \n • Yes, we oﬀer toy rental services for events, ensuring a unique and enjoyable experience for \nchildren.  \n \n About Playful Connec�ons: \nAt Playful Connec�ons, our commitment is to provide a diverse range of services that cater to the \nunique needs and preferences of every child. ", "original_text": "Can I rent toys for special events or par�es?  \n", "page_label": "2", "file_name": "llm company data-test.pdf", "doc_id": "9b9285b9-4a9f-4f35-b015-6967a85968a8"}}, "text": "Are there discounts for enrolling in mul�ple services?  \n • Yes, we oﬀer bundled discounts for families enrolling in mul�ple services.  \n 6.  Can I rent toys for special events or par�es?  \n • Yes, we oﬀer toy rental services for events, ensuring a unique and enjoyable experience for \nchildren.  \n \n About Playful Connec�ons: \nAt Playful Connec�ons, our commitment is to provide a diverse range of services that cater to the \nunique needs and preferences of every child. ", "previous_texts": None, "next_texts": None}], "index": 0}]}

print(a['choices'][0]['message'])