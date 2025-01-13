import json
import openai
import pandas as pd
from openai import OpenAI

class ProductDataGenerator:
    def __init__(self, api_key, website_url):
        self.client = OpenAI(api_key=api_key)
        self.website_url = website_url
        self.product_data = None
        
    def load_data(self, file_path):
        self.product_data = pd.read_csv(file_path, encoding='utf-8')
    
    def write_data(self, file_path):
        self.product_data.to_csv(file_path, encoding='utf-8', index=False)
        
    def test_data(self, requested_data):
        print('Entering testing mode')
        for idx, row in self.product_data.iterrows():
            yield self.llm_api_request(requested_data=requested_data, product_row=row)
                    
    def get_data(self, requested_data):
        for key in requested_data.keys():
            if key not in self.product_data.columns:
                self.product_data[key] = None

        for idx, row in self.product_data.iterrows():
            print(f"Row {idx + 1}:")
            result = self.llm_api_request(requested_data=requested_data, product_row=row)
            print(f"SKU: {row['sku']}")
            print(f"Generated data: {result}")
            
            for key, value in result.items():
                self.product_data.at[idx, key] = value
            
    def llm_api_request(self, requested_data={}, product_row=None):
        if product_row is None:
            raise ValueError("product_row cannot be None")
            
        product_data = product_row.to_dict()
        product_href = product_data['href'] if 'href' in product_data else None
        product_data = json.dumps(product_data, indent=2)

        system_prompt = f'''
            Based on prompt engineering guidelines,
            your instructions are split into the following sections:
            Persona, Context, Task, Format, and Examples.

        ### **Persona**:
            You are an expert on e-commerce data and specifically about the website *{self.website_url}*
            You have vast knowledge about the products in this website (prices, product features, specifications, categories, etc.)

        ### **Context**:
            You will be generating data for the products in the website *{self.website_url}*.
            You will be receiving a product data as input.
            You may have access to the product href if it is provided in *{product_href}*.
            
        ### **Task**:
        
            **Product Data Generation**:
            Generate realistic product data based on the input product information.
            Return a JSON object with the requested data according to the required attributes and types.
            
            **IMPORTANT**:
            For prices:
                1. ALWAYS generate a realistic price in cents (multiply the dollar amount by 100)
                2. Format as "US-USD <price in cents>" (e.g., "US-USD 23499" for $234.99)
                3. Never return 0 as a price unless explicitly stated in the input
                4. Base the price on similar products in the market
                5. Ensure the price is appropriate for the product category and features
                6. List elements must not contain semicolons (;)
                
        ### **Format Example**:
            Input product data example:
            ```
            {{
                "name": "Front Assy- GB II Dgry Numero",
                "part_number": "40281",
                "category": "Portable Restrooms>Standard Restrooms>Global"
            }}
            ```
            Requested data example:
            ```
            {{
                "prices": "string",
                "features": "string",
                "schematic": "string",
                "specifications": "list"
            }}
            ```
            Expected output:
            {{
                "prices": "US-USD 23499",
                "features": "The product boasts several key features ...",
                "schematic": "The technical schematic ...",
                "specifications": ["Material: High-density polyethylene (HDPE)", "Color: Dark Grey", ...]
            }}
        '''
        try:
            response = self.client.chat.completions.create(
                model = "gpt-4o-mini",
                messages = [
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": f"Here is the product data:\n{product_data}\n\nGenerate data according to these requirements:\n{json.dumps(requested_data, indent=2)}"
                    }
                ],
                temperature = 0.2,
                response_format = {
                    "type": "json_object"
                }
            )

            # Access the response content
            message = response.choices[0].message.content
            finish_reason = response.choices[0].finish_reason
            usage = response.usage
            response_dict = json.loads(message)
            
            return response_dict
        
        except openai.APIConnectionError as e:
            # Cause: Issue connecting to the OpenAI services.
            # Solution: Check network settings, proxy configuration, SSL certificates, or firewall rules.
            print(f"Failed to connect to OpenAI API: {e}")

        except openai.APITimeoutError as e:
            # Cause: Request timed out.
            # Solution: Retry after a brief wait and contact OpenAI support if the issue persists.
            print(f"Request timed out: {e}")

        except openai.AuthenticationError as e:
            # Cause: API key or token is invalid, expired, or revoked.
            # Solution: Check your API key or token and ensure it's active. Generate a new one if needed.
            print(f"Authentication failed: {e}")

        except openai.BadRequestError as e:
            # Cause: The request was malformed or missing required parameters.
            # Solution: Check error message and API documentation to correct the request.
            print(f"Bad request: {e}")

        except openai.ConflictError as e:
            # Cause: The resource was updated by another request.
            # Solution: Retry the request ensuring no conflicting updates.
            print(f"Conflict error: {e}")

        except openai.APIError as e:
            # Cause: General server error from OpenAI's side.
            # Solution: Retry after a short wait, and if it persists, contact OpenAI support.
            print(f"OpenAI API error: {e}")

        except openai.NotFoundError as e:
            # Cause: The requested resource does not exist.
            # Solution: Check the resource identifier and ensure it's correct.
            print(f"Resource not found: {e}")

        except openai.PermissionError as e:
            # Cause: You don't have permission to access the requested resource.
            # Solution: Check if you have the correct API key, organization ID, and resource ID.
            print(f"Permission denied: {e}")

        except openai.RateLimitError as e:
            # Cause: You have hit your assigned rate limit.
            # Solution: Slow down your requests. Refer to OpenAI’s rate limit documentation.
            print(f"Rate limit exceeded: {e}")

        except openai.UnprocessableEntityError as e:
            # Cause: The request format was correct but could not be processed.
            # Solution: Retry the request. If the issue persists, review the request data.
            print(f"Unprocessable entity: {e}")

def main():
    API_KEY = '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'
    BASE_URL = 'https://www.bbraun.de'
    p_opath = 'Bbraun/products_upload.csv'
    p_rpath = 'Bbraun/products_with_prices.csv'
    requested_data = {"prices": "string"}
    
    pdg = ProductDataGenerator(api_key=API_KEY, website_url=BASE_URL)
    
    pdg.load_data(p_opath)
    
    """ Testing """
    # print("Method 1: Processing products one by one using a generator (NO CHANGES ON ORIGINAL DATA):")
    # for idx, result in enumerate(pdg.test_data(requested_data)):
    #     if pd.notna(pdg.product_data.iloc[idx]['href']):
    #         print('HTML:', pdg.product_data.iloc[idx]['href'])
    #     print("Line:", idx + 1, "SKU:", pdg.product_data.iloc[idx]['sku'], 'Result:', result)
    #     input("Continue...")
    
    print("Method 2: Processing all products at once (ALL CHANGES ON ORIGINAL DATA):")
    pdg.get_data(requested_data)
    
    print("Saving modified data to:", p_rpath)
    pdg.write_data(p_rpath)

if __name__ == '__main__':
    main()