import json
from openai import OpenAI
import google.generativeai as genai
import openai
import loggerutility as logger 

class Email_CategoryDetector:
    def detect_category_openai(self, openai_api_key, categories, email_body):
        logger.log("Inside detect_category_openai::")
        try:
            categories_str = ', '.join(categories)
            message = [{
                "role": "user",
                "content": f"Classify the mail into one of the following categories: {categories_str} and Others. Based on the email content: {email_body}, provide ONLY the category in JSON format as {{\"category\": \"category\"}}."
            }]
            
            logger.log(f"Final GPT message for detecting category::: {message}")
            client = OpenAI(api_key=openai_api_key)
            result = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=message,
                temperature=0,
                max_tokens=1800,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
            )
            category = json.loads(result.choices[0].message.content)['category']
            logger.log(f"category:: {category}")
            return category
        except Exception as e:
            logger.log(f"Error detecting category with OpenAI: {str(e)}")
            raise

    def detect_category_gemini(self, gemini_api_key, categories, email_body, detect_email_category=True, signature=None):
        logger.log("Inside detect_category_gemini::")
        try:
            categories_str = ', '.join(categories) 
            if detect_email_category:
                message = [{
                    "role": "user",
                    "content": f"Classify the mail into one of the following categories: {categories_str} and Others. Based on the email content: {email_body}, provide ONLY the category in JSON format as {{\"category\": \"category\"}}."
                }]
            else:
                message = [{
                    "role": "user",
                    "content": f"Create a reply for the email received from a customer. Include the email signature as {signature}\nDo not include any instruction as the output will be directly in a program."
                }]

            logger.log(f"Final Gemini AI message for detecting category::: {message}")
            message_list = str(message)

            generation_config = {
                "temperature": 0,
                "top_p": 1,
                "top_k": 1,
                "max_output_tokens": 2048,
            }

            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel('gemini-1.0-pro')
            response = model.generate_content(message_list)

            logger.log(f"Input Question ::: {email_body}\ngemini-1.0-pro Response::: {response} {type(response)}")
            logger.log(f"\n\nResponse GeminiAI endpoint::::: {response} \n{type(response)}", "0")

            final_result = ""
            for part in response:
                final_result = part.text
                if final_result:
                    try:
                        final_result = final_result.replace("\\", "").replace('```', '').replace('json', '')
                        if final_result.startswith("{{") and final_result.endswith("}}"):
                            final_result = final_result[1:-1]
                        final_result = json.loads(final_result)
                        logger.log(f"finalResult:::  {final_result}")
                    except json.JSONDecodeError:
                        logger.log(f"Exception : Invalid JSON Response GEMINI 1.5: {final_result} {type(final_result)}")

            if detect_email_category:
                category = final_result.get('category', 'Others')
                return category
            else:
                logger.log(f"finalResult:::  {final_result}")
                return final_result

        except Exception as e:
            logger.log(f"Error with Gemini AI detection/generation: {str(e)}")
            raise

    def detect_category_local(self, openai_api_key, categories, email_body, detect_email_category=True, signature=None, local_ai_url=None):
        logger.log("Inside detect_category_local::")
        try:
            categories_str = ', '.join(categories)
            if detect_email_category:
                message = [{
                    "role": "user",
                    "content": f"Classify the mail into one of the following categories: {categories_str} and Others. Based on the email content: {email_body}, provide ONLY the category in JSON format as {{\"category\": \"category\"}}."
                }]
            else:
                message = [{
                    "role": "user",
                    "content": f"Create a reply for the email received from a customer. Include the email signature as {signature}\nDo not include any instruction as the output will be directly in a program."
                }]

            logger.log(f"Final Local AI message for detecting category::: {message}")
            openai.api_key = openai_api_key
            client = OpenAI(base_url=local_ai_url, api_key="lm-studio")
            completion = client.chat.completions.create(
                model="mistral",
                messages=message,
                temperature=0,
                stream=False,
                max_tokens=4096
            )

            final_result = str(completion.choices[0].message.content)
            logger.log(f"\n\nInput Question ::: {email_body}\nLocalAI endpoint finalResult ::::: {final_result} \n{type(final_result)}", "0")

            if detect_email_category:
                try:
                    json_start = final_result.find("{")
                    json_end = final_result.rfind("}") + 1
                    if json_start != -1 and json_end != -1:
                        json_str = final_result[json_start:json_end]
                        final_result = json.loads(json_str)
                        logger.log(f"finalResult:::  {final_result}")
                        category = final_result.get('category', 'Others')
                        logger.log(f"category::1037 {category}")
                        return category
                    else:
                        raise ValueError("No valid JSON object found in the response")
                except json.JSONDecodeError as e:
                    logger.log(f"JSON decode error: {e}")
                    raise
            else:
                logger.log(f"finalResult:1040  {final_result}")
                return final_result

        except Exception as e:
            logger.log(f"Error with LocalAI detection/generation: {str(e)}")
            raise
