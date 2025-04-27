import http from 'k6/http';
import { check } from 'k6';
import { SharedArray } from 'k6/data';

/*
 * K6 Load Test for Multi-Modal LLM API
 *
 * This script performs a load test on the Multi-Modal LLM API using k6.
 * It sends requests with a base64-encoded image to test the model's image-to-text capabilities.
 * All request timeouts are disabled to prevent premature termination during load testing
 *
 * How to run:
 * 1. For local testing:
 *    k6 run loadtest.js
 *
 * 2. For testing against a deployed API:
 *    k6 run -e API_URL=https://multimodal-internvl3-38b-awq--serve.modal.run/v1 loadtest.js
 *
 * 3. To customize the number of VUs and iterations:
 *    k6 run -e API_URL=https://your-api-url.com/v1 --vus 10 --iterations 100 loadtest.js
 */

// Load the base64 data from the file
const base64Data = new SharedArray('base64Data', function() {
  const data = open('../test-files/test1_base64.txt');
  return [data.trim()];
});

export const options = {
  // Configure the load test to use X VUs (virtual users)
  vus: 30,
  // Make a total of X requests
  iterations: 150,
};

export default function() {
  // Get the base64 data
  const imageBase64 = base64Data[0];

  const payload = {
    "model": "internvl3-38b-awq",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "**ROLE:** You are an AI assistant specialized in converting document images into clean Markdown.\\n\\n**INPUT:** An image of a document page.\\n\\n**OBJECTIVE:** Analyze the input image and generate a complete and accurate Markdown representation of its content, following the rules below precisely.\\n\\n**PRIMARY TASK:** Convert the document image to Markdown.\\n\\n**OUTPUT FORMATTING:**\\n* **Strictly Markdown:** The output MUST be ONLY the Markdown text.\\n* **No Explanations:** Do NOT include any text before or after the Markdown content (no greetings, summaries, or comments).\\n* **No Delimiters:** Do NOT enclose the Markdown output in code fences (e.g., ```markdown) or any other wrapping characters.\\n\\n**DETAILED CONVERSION RULES:**\\n\\n1.  **Full Content Extraction:**\\n    * You MUST capture *all* textual information present on the page. This includes main text, headers, footers, captions, footnotes, labels, text inside tables, text within charts, etc.\\n    * Do not summarize or exclude any part.\\n\\n2.  **Layout & Structure:**\\n    * Use standard Markdown for structure (e.g., `#` for headings, `*` or `-` for bullet points, `1.` for numbered lists, paragraphs).\\n    * Maintain the original hierarchy and flow where possible.\\n\\n3.  **Specific Element Handling:**\\n    * **Tables:** Convert all tables into valid HTML table structures (`<table>`, `<thead>`, `<tbody>`, `<tr>`, `<th>`, `<td>`).\\n    * **Logos:** Identify and enclose logos using `<logo>...</logo>` tags (e.g., `<logo>Example Corp</logo>`).\\n    * **Watermarks:** Identify and enclose watermarks using `<watermark>...</watermark>` tags (e.g., `<watermark>CONFIDENTIAL</watermark>`).\\n    * **Page Numbers:** Identify and enclose page numbers using `<page_number>...</page_number>` tags (e.g., `<page_number>Page 5</page_number>`, `<page_number>12/30</page_number>`).\\n    * **Checkboxes:** Represent checkboxes using '☐' (unchecked) and '☑' (checked).\\n    * **Charts & Infographics:**\\n        * Extract ALL text found within the chart or infographic.\\n        * Represent the visual element itself with a descriptive placeholder tag, like `[Chart: Bar graph showing monthly sales]` or `[Infographic: Diagram illustrating the data flow]`. Place the extracted text immediately following or logically associated with this tag.\\n    * **Images/Photos (Non-Logo):** If there are relevant photos or complex diagrams not covered above, use a descriptive tag like `[Image: Photo of the new product prototype]` or `[Diagram: Network architecture overview]`. Extract any associated captions.\\n\\n**FINAL CHECK:** Ensure the output contains only the generated Markdown content as per these rules."
          },
          {
            "type": "image_url",
            "image_url": {
              "url": "data:image/jpeg;base64," + imageBase64
            }
          }
        ]
      }
    ],
    "temperature": 1,
    "top_p": 0.2,
    "tools": null,
    "tool_choice": "none",
    "logprobs": false,
    "top_logprobs": 0,
    "n": 1,
    "logit_bias": null,
    "max_tokens": null,
    "stop": null,
    "stream": false,
    "stream_options": null,
    "presence_penalty": 0,
    "frequency_penalty": 0,
    "user": "string",
    "response_format": null,
    "repetition_penalty": 1.1,
    "session_id": -1,
    "ignore_eos": false,
    "skip_special_tokens": true,
    "spaces_between_special_tokens": true,
    "top_k": 40,
    "seed": 0,
    "min_new_tokens": null,
    "min_p": 0.8
  };

  const headers = {
    'Content-Type': 'application/json',
  };

  const apiUrl = __ENV.API_URL || 'http://localhost:23333/v1';
  const response = http.post(`${apiUrl}/chat/completions`, JSON.stringify(payload), {
    headers: headers,
    timeout: '300s',
    connectTimeout: '300s',
    responseTimeout: '300s',
  });

  check(response, {
    'status is 200': (r) => r.status === 200,
    'has response': (r) => r.json().choices && r.json().choices.length > 0,
  });
}
