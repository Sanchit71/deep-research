import os
import typer
import json
import re
from openai import AsyncOpenAI
import tiktoken
from typing import Optional
from rich.console import Console
from dotenv import load_dotenv
from .text_splitter import RecursiveCharacterTextSplitter
from deep_research_py.config import EnvironmentConfig
import asyncio
from deep_research_py.utils import logger

load_dotenv()


def clean_json_string(json_str: str) -> str:
    """Clean and fix common JSON formatting issues."""
    try:
        # Remove any leading/trailing whitespace
        json_str = json_str.strip()
        
        # Remove markdown code blocks if present
        if json_str.startswith('```json'):
            json_str = re.sub(r'^```json\s*', '', json_str)
        if json_str.endswith('```'):
            json_str = re.sub(r'\s*```$', '', json_str)
        
        # Ensure the JSON ends properly
        if not json_str.endswith('}'):
            json_str += '}'
            
        return json_str
        
    except Exception as e:
        logger.warning(f"Error cleaning JSON string: {e}")
        return json_str


def extract_json_from_response(response_text: str) -> dict:
    """Extract and parse JSON from AI response with multiple fallback strategies."""
    
    logger.debug(f"Attempting to parse JSON from response (length: {len(response_text)})")
    
    # Strategy 1: Try direct parsing
    try:
        result = json.loads(response_text)
        logger.debug("✅ Direct JSON parsing successful")
        return result
    except json.JSONDecodeError as e:
        logger.debug(f"Direct JSON parsing failed: {e}")
    
    # Strategy 2: Clean and try again
    try:
        cleaned = clean_json_string(response_text)
        result = json.loads(cleaned)
        logger.debug("✅ Cleaned JSON parsing successful")
        return result
    except json.JSONDecodeError as e:
        logger.debug(f"Cleaned JSON parsing failed: {e}")
    
    # Strategy 3: Extract JSON block if wrapped in markdown
    try:
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            json_content = json_match.group(1)
            result = json.loads(json_content)
            logger.debug("✅ Markdown JSON extraction successful")
            return result
    except json.JSONDecodeError as e:
        logger.debug(f"Markdown JSON extraction failed: {e}")
    
    # Strategy 4: Find JSON-like content between braces and fix common issues
    try:
        start = response_text.find('{')
        end = response_text.rfind('}')
        if start != -1 and end != -1 and end > start:
            json_content = response_text[start:end+1]
            
            # Fix the specific issue where reportText has an extra escaped quote at the start
            json_content = re.sub(r'("reportText"\s*:\s*")\\"', r'\1', json_content)
            json_content = re.sub(r'("reportMarkdown"\s*:\s*")\\"', r'\1', json_content)
            
            result = json.loads(json_content)
            logger.debug("✅ Brace extraction with fixes successful")
            return result
    except json.JSONDecodeError as e:
        logger.debug(f"Brace extraction with fixes failed: {e}")
    
    # Strategy 5: Manual extraction for reportText/reportMarkdown
    try:
        result = {}
        
        # Try reportText first (current prompt format)
        for field_name in ["reportText", "reportMarkdown"]:
            if f'"{field_name}"' in response_text:
                # Enhanced pattern to handle malformed quotes
                patterns = [
                    rf'"{field_name}"\s*:\s*"(.*?)"\s*\}}',  # Normal case
                    rf'"{field_name}"\s*:\s*\\"(.*?)"\s*\}}',  # Extra escaped quote at start
                    rf'"{field_name}"\s*:\s*"(.*)"$',  # End of string
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, response_text, re.DOTALL)
                    if match:
                        content = match.group(1)
                        # Unescape content properly
                        content = content.replace('\\"', '"')
                        content = content.replace('\\n', '\n')
                        content = content.replace('\\t', '\t')
                        content = content.replace('\\\\', '\\')
                        
                        result[field_name] = content
                        logger.info(f"✅ Successfully extracted {field_name} manually using pattern")
                        return result
        
        # Extract other common fields
        for field in ["learnings", "followUpQuestions", "queries", "questions"]:
            pattern = rf'"{field}"\s*:\s*\[(.*?)\]'
            match = re.search(pattern, response_text, re.DOTALL)
            if match:
                try:
                    array_content = '[' + match.group(1) + ']'
                    result[field] = json.loads(array_content)
                except Exception:
                    # Fallback: split by quotes and clean
                    items = re.findall(r'"([^"]*)"', match.group(1))
                    result[field] = items
        
        if result:
            logger.info(f"✅ Manual extraction successful, found fields: {list(result.keys())}")
            return result
            
    except Exception as e:
        logger.debug(f"Manual extraction failed: {e}")
    
    # Strategy 6: Last resort - try to extract any text content
    try:
        # Look for any substantial text content that might be the report
        text_patterns = [
            r'"reportText"\s*:\s*"([^"]{100,}.*?)"',
            r'"reportMarkdown"\s*:\s*"([^"]{100,}.*?)"',
            r'COMPREHENSIVE RESEARCH REPORT(.*?)(?:SOURCES|$)',
            r'RESEARCH REPORT(.*?)(?:SOURCES|$)',
        ]
        
        for pattern in text_patterns:
            match = re.search(pattern, response_text, re.DOTALL | re.IGNORECASE)
            if match:
                content = match.group(1).strip()
                if len(content) > 100:  # Ensure we have substantial content
                    content = content.replace('\\"', '"').replace('\\n', '\n').replace('\\t', '\t')
                    logger.warning(f"✅ Extracted text content using fallback pattern (length: {len(content)})")
                    return {"reportText": content}
    except Exception as e:
        logger.debug(f"Fallback text extraction failed: {e}")
    
    # Final fallback
    logger.warning("All JSON parsing strategies failed, returning empty structure")
    return {}


class AIClientFactory:
    """Factory for creating AI clients for different providers."""

    @classmethod
    def create_client(cls, api_key: str, base_url: str) -> AsyncOpenAI:
        """Create an AsyncOpenAI-compatible client for the specified provider."""
        return AsyncOpenAI(api_key=api_key, base_url=base_url)

    @classmethod
    def get_client(
        cls,
        service_provider_name: Optional[str] = None,
        console: Optional[Console] = None,
    ) -> AsyncOpenAI:
        """Get a configured AsyncOpenAI client using environment variables."""
        console = console or Console()

        try:
            # Get and validate the provider configuration
            config = EnvironmentConfig.validate_provider_config(
                service_provider_name, console
            )

            # Create the client
            return cls.create_client(api_key=config.api_key, base_url=config.base_url)

        except ValueError:
            raise typer.Exit(1)
        except Exception as e:
            console.print(
                f"[red]Error initializing {service_provider_name or EnvironmentConfig.get_default_provider()} client: {e}[/red]"
            )
            raise typer.Exit(1)

    @classmethod
    def get_model(cls, service_provider_name: Optional[str] = None) -> str:
        """Get the configured model for the specified provider."""
        config = EnvironmentConfig.get_provider_config(service_provider_name)
        if not config.model:
            raise ValueError(f"No model configured for {config.service_provider_name}")
        return config.model


async def get_client_response(
    client: AsyncOpenAI, model: str, messages: list, response_format: dict, max_retries: int = 3
):
    # Log the full prompt being sent
    logger.info("🤖 Sending request to AI model")
    logger.info(f"   Model: {model}")
    logger.info(f"   Messages count: {len(messages)}")
    logger.info(f"   Response format: {response_format}")
    
    # Log each message with truncation for readability
    for i, message in enumerate(messages):
        role = message.get("role", "unknown")
        content = message.get("content", "")
        content_length = len(content)
        
        logger.info(f"   Message {i+1} ({role}): {content_length} characters")
        
        # Log first 500 and last 200 characters for context
        if content_length > 700:
            preview = content[:500] + "\n\n... [TRUNCATED] ...\n\n" + content[-200:]
            logger.debug(f"   Content preview:\n{preview}")
        else:
            logger.debug(f"   Full content:\n{content}")
    
    # Calculate and log token usage
    total_input_tokens = 0
    for message in messages:
        content = message.get("content", "")
        tokens = len(encoder.encode(content))
        total_input_tokens += tokens
    
    logger.info(f"   Estimated input tokens: {total_input_tokens:,}")
    
    for attempt in range(max_retries):
        try:
            logger.debug(f"   API call attempt {attempt + 1}/{max_retries}")
            
            response = await client.beta.chat.completions.parse(
                model=model,
                messages=messages,
                response_format=response_format,
            )

            result = response.choices[0].message.content
            
            # Log response details
            output_tokens = len(encoder.encode(result)) if result else 0
            logger.info(f"   ✅ Response received: {len(result)} characters, ~{output_tokens:,} tokens")
            
            # Log response preview
            if len(result) > 500:
                response_preview = result[:300] + "\n\n... [TRUNCATED] ...\n\n" + result[-200:]
                logger.debug(f"   Response preview:\n{response_preview}")
            else:
                logger.debug(f"   Full response:\n{result}")
            
            # Enhanced JSON parsing with multiple strategies
            try:
                parsed_response = extract_json_from_response(result)
                logger.debug("   ✅ JSON parsing successful")
                logger.debug(f"   Response keys: {list(parsed_response.keys()) if isinstance(parsed_response, dict) else 'Not a dict'}")
                return parsed_response
                
            except Exception as e:
                logger.error(f"   ❌ All JSON parsing strategies failed on attempt {attempt + 1}: {e}")
                logger.error(f"   Raw response (first 2000 chars): {result[:2000]}...")
                
                if attempt < max_retries - 1:
                    logger.warning("   ⚠️ Retrying with different approach...")
                    continue
                else:
                    # Last attempt - return a basic fallback based on expected content
                    logger.warning("   🔧 Creating fallback response structure")
                    
                    # Determine what type of response we expect based on content
                    if "reportText" in result.lower() or "reportMarkdown" in result.lower():
                        # Extract text content as best as possible
                        lines = result.split('\n')
                        text_lines = []
                        in_content = False
                        
                        for line in lines:
                            if 'reportText' in line.lower() or 'reportMarkdown' in line.lower():
                                in_content = True
                                continue
                            if in_content and line.strip():
                                # Clean the line
                                clean_line = line.strip()
                                if clean_line.startswith('"') and clean_line.endswith('"'):
                                    clean_line = clean_line[1:-1]
                                text_lines.append(clean_line)
                        
                        fallback_content = '\n'.join(text_lines) if text_lines else "RESEARCH REPORT\n\nTitle: Research Report\n\nReport generation encountered formatting issues. Please refer to the research learnings for detailed findings."
                        return {"reportText": fallback_content}
                    
                    elif "learnings" in result.lower():
                        return {"learnings": [], "followUpQuestions": []}
                    
                    elif "queries" in result.lower():
                        return {"queries": []}
                    
                    elif "questions" in result.lower():
                        return {"questions": []}
                    
                    else:
                        return {"error": "JSON parsing failed", "raw_content": result[:1000]}

        except Exception as e:
            if "429" in str(e) or "rate" in str(e).lower():
                wait_time = 2 ** attempt  # Exponential backoff
                logger.warning(f"   ⏳ Rate limit hit, waiting {wait_time} seconds before retry {attempt + 1}/{max_retries}")
                await asyncio.sleep(wait_time)
                if attempt == max_retries - 1:
                    logger.error("   ❌ Max retries exceeded due to rate limiting")
                    raise e
            else:
                logger.error(f"   ❌ API call failed: {e}")
                raise e

    logger.error("   ❌ All retry attempts failed")
    return {"error": "Max retries exceeded"}


MIN_CHUNK_SIZE = 140
encoder = tiktoken.get_encoding(
    "cl100k_base"
)  # Updated to use OpenAI's current encoding


def trim_prompt(
    prompt: str, context_size: int = int(os.getenv("CONTEXT_SIZE", "128000"))
) -> str:
    """Trims a prompt to fit within the specified context size."""
    if not prompt:
        return ""

    length = len(encoder.encode(prompt))
    if length <= context_size:
        return prompt

    overflow_tokens = length - context_size
    # Estimate characters to remove (3 chars per token on average)
    chunk_size = len(prompt) - overflow_tokens * 3
    if chunk_size < MIN_CHUNK_SIZE:
        return prompt[:MIN_CHUNK_SIZE]

    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=0)

    trimmed_prompt = (
        splitter.split_text(prompt)[0] if splitter.split_text(prompt) else ""
    )

    # Handle edge case where trimmed prompt is same length
    if len(trimmed_prompt) == len(prompt):
        return trim_prompt(prompt[:chunk_size], context_size)

    return trim_prompt(trimmed_prompt, context_size)
