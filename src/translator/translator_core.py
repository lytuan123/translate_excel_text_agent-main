"""
Advanced Translation Core Module
Combines the best of Translation Agent and Excel Translator
"""

import os
import time
from functools import wraps
from threading import Lock
from typing import List, Optional, Union, Dict, Any, Tuple

import tiktoken
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Load environment variables
load_dotenv()

# Global configuration
DEFAULT_CONFIG = {
    "endpoint": "OpenAI",
    "model": "gpt-4o",
    "temperature": 0.3,
    "rpm": 60,
    "max_tokens": 1000,
    "json_mode": False,
    "base_url": None
}

# Global client and configuration
client = None
current_config = DEFAULT_CONFIG.copy()

# Translation style options
TRANSLATION_STYLES = {
    "General": "Dịch văn bản một cách chính xác và rõ ràng, ưu tiên truyền đạt thông tin một cách trung lập và dễ hiểu cho đối tượng độc giả phổ thông.  Sử dụng ngôn ngữ tự nhiên, trôi chảy, và tránh các yếu tố phong cách đặc biệt. Tập trung vào việc truyền tải đúng ý nghĩa của văn bản gốc một cách hiệu quả nhất.",

    "Literary": "Dịch văn bản theo phong cách văn học, chú trọng truyền tải không chỉ ý nghĩa mà còn cả giá trị nghệ thuật và cảm xúc của tác phẩm gốc.  Sử dụng ngôn ngữ giàu hình ảnh, uyển chuyển, và chú ý đến nhịp điệu, âm điệu của câu văn.  Giữ gìn và tái tạo các phép tu từ (ẩn dụ, so sánh, nhân hóa...), hình ảnh, và giọng văn đặc trưng của tác giả.  Bản dịch cần mang lại trải nghiệm đọc tương tự như bản gốc về mặt thẩm mỹ và cảm xúc.",

    "Technical": "Dịch văn bản kỹ thuật với độ chính xác cao về mặt thuật ngữ và thông tin chuyên ngành.  Sử dụng ngôn ngữ chính xác, khách quan, và tuân thủ các quy ước, tiêu chuẩn trong lĩnh vực kỹ thuật.  Đảm bảo tính nhất quán trong việc sử dụng thuật ngữ và cấu trúc câu văn.  Mục tiêu là truyền đạt thông tin kỹ thuật một cách rõ ràng, dễ hiểu cho người đọc có chuyên môn.",

    "Financial": "Dịch văn bản tài chính với độ chính xác cao về các con số, thuật ngữ và khái niệm tài chính.  Sử dụng ngôn ngữ chuyên nghiệp, trang trọng, và tuân thủ các quy tắc, chuẩn mực trong lĩnh vực tài chính.  Đảm bảo tính bảo mật và chính xác của thông tin tài chính.  Bản dịch cần phù hợp với môi trường kinh doanh và tài chính chuyên nghiệp.",

    "Legal": "Dịch văn bản pháp lý với độ chính xác tuyệt đối về mặt ngôn ngữ và ý nghĩa pháp lý.  Sử dụng ngôn ngữ trang trọng, chính xác, và tuân thủ các quy ước, thuật ngữ pháp lý.  Đảm bảo tính rõ ràng, không mơ hồ, và tránh gây hiểu lầm về mặt pháp luật.  Bản dịch cần đáp ứng các yêu cầu về tính pháp lý và có thể sử dụng trong môi trường pháp lý.",

    "Medical": "Dịch văn bản y tế với độ chính xác cao về thuật ngữ y khoa và thông tin lâm sàng.  Sử dụng ngôn ngữ rõ ràng, chính xác, và tuân thủ các quy ước, tiêu chuẩn trong lĩnh vực y tế.  Đảm bảo tính chính xác và an toàn của thông tin y tế, đặc biệt là trong các văn bản liên quan đến chăm sóc bệnh nhân.  Bản dịch cần phù hợp với môi trường y tế chuyên nghiệp.",

    "Scientific": "Dịch văn bản khoa học với độ chính xác cao về thuật ngữ khoa học và thông tin nghiên cứu.  Sử dụng ngôn ngữ khách quan, logic, và tuân thủ các quy tắc, chuẩn mực trong văn phong khoa học.  Đảm bảo tính chính xác, minh bạch và có thể kiểm chứng của thông tin khoa học.  Bản dịch cần phù hợp với môi trường học thuật và nghiên cứu khoa học.",

    "Casual": "Dịch văn bản theo phong cách thân mật, tự nhiên như trong giao tiếp hàng ngày.  Sử dụng ngôn ngữ giản dị, gần gũi, và thoải mái.  Chú trọng đến ngữ điệu, cách diễn đạt tự nhiên và hài hước (nếu có) trong văn bản gốc.  Bản dịch cần tạo cảm giác thoải mái, thân thiện và phù hợp với các tình huống giao tiếp thông thường.",

    "Formal": "Dịch văn bản theo phong cách trang trọng, lịch sự, và chuyên nghiệp.  Sử dụng ngôn ngữ chuẩn mực, trang trọng, và tuân thủ các quy tắc giao tiếp lịch sự.  Tránh sử dụng tiếng lóng, từ ngữ suồng sã, hoặc cách diễn đạt quá thân mật.  Bản dịch cần phù hợp với các tình huống giao tiếp trang trọng, công việc, hoặc mang tính nghi thức.",

    "Marketing": "Dịch văn bản marketing với mục tiêu thuyết phục, thu hút sự chú ý và tạo ấn tượng tích cực với khách hàng.  Sử dụng ngôn ngữ sáng tạo, hấp dẫn, và có sức thuyết phục.  Chú trọng đến việc truyền tải thông điệp thương hiệu, lợi ích sản phẩm/dịch vụ, và kêu gọi hành động.  Bản dịch cần phù hợp với mục tiêu marketing và thu hút đối tượng mục tiêu.",

    "Educational": "Dịch văn bản giáo dục theo phong cách rõ ràng, dễ hiểu, và mang tính sư phạm.  Sử dụng ngôn ngữ đơn giản, mạch lạc, và dễ tiếp thu.  Chú trọng đến việc giải thích các khái niệm, thuật ngữ một cách chi tiết và dễ hiểu.  Bản dịch cần hỗ trợ người học tiếp thu kiến thức một cách hiệu quả và phù hợp với mục tiêu giáo dục.",

    "Creative": "Dịch văn bản sáng tạo với sự linh hoạt và tự do diễn đạt, nhưng vẫn đảm bảo truyền tải được ý tưởng cốt lõi và tinh thần của văn bản gốc.  Có thể sử dụng ngôn ngữ giàu hình ảnh, ẩn dụ, và các biện pháp tu từ để tăng tính sáng tạo và độc đáo cho bản dịch.  Phù hợp với các loại văn bản như thơ ca, lời bài hát, kịch bản, hoặc các tác phẩm nghệ thuật khác.  Bản dịch cần thể hiện được sự sáng tạo và mang đậm dấu ấn cá nhân của người dịch, đồng thời vẫn tôn trọng ý tưởng ban đầu của tác giả."
    }

# Common language codes mapping
LANGUAGE_CODES = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Russian": "ru",
    "Japanese": "ja",
    "Chinese": "zh",
    "Korean": "ko",
    "Arabic": "ar",
    "Hindi": "hi",
    "Vietnamese": "vi",
    "Thai": "th",
    "Dutch": "nl",
    "Greek": "el",
    "Turkish": "tr",
    "Polish": "pl",
    "Swedish": "sv",
    "Danish": "da",
    "Finnish": "fi",
    "Norwegian": "no",
    "Hungarian": "hu",
    "Czech": "cs",
    "Romanian": "ro",
    "Bulgarian": "bg",
    "Ukrainian": "uk",
    "Hebrew": "he",
    "Indonesian": "id",
    "Malay": "ms",
    "Urdu": "ur",
    "Persian": "fa",
    "Bengali": "bn",
    "Tamil": "ta",
    "Telugu": "te",
    "Marathi": "mr",
    "Gujarati": "gu",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Punjabi": "pa",
    "Sinhala": "si",
    "Nepali": "ne",
    "Khmer": "km",
    "Lao": "lo",
    "Myanmar": "my",
    "Amharic": "am",
    "Swahili": "sw",
    "Zulu": "zu",
    "Afrikaans": "af",
    "Albanian": "sq",
    "Armenian": "hy",
    "Azerbaijani": "az",
    "Basque": "eu",
    "Belarusian": "be",
    "Bosnian": "bs",
    "Catalan": "ca",
    "Croatian": "hr",
    "Estonian": "et",
    "Filipino": "fil",
    "Galician": "gl",
    "Georgian": "ka",
    "Icelandic": "is",
    "Irish": "ga",
    "Latvian": "lv",
    "Lithuanian": "lt",
    "Luxembourgish": "lb",
    "Macedonian": "mk",
    "Maltese": "mt",
    "Mongolian": "mn",
    "Montenegrin": "me",
    "Serbian": "sr",
    "Slovak": "sk",
    "Slovenian": "sl",
    "Welsh": "cy",
    "Yiddish": "yi",
}


def model_load(
    endpoint: str,
    model: str,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    temperature: float = 0.3,
    rpm: int = 60,
    json_mode: bool = False,
) -> Dict[str, Any]:
    """
    Load and configure the language model client.
    
    Args:
        endpoint: The API provider (OpenAI, Groq, TogetherAI, Ollama, CUSTOM)
        model: The model name
        api_key: API key for authentication
        base_url: Custom base URL for API requests
        temperature: Temperature parameter for text generation
        rpm: Rate limit (requests per minute)
        json_mode: Whether to use JSON mode for responses
        
    Returns:
        Dictionary with current configuration
    """
    global client, current_config
    
    # Update configuration
    current_config["endpoint"] = endpoint
    current_config["model"] = model
    current_config["temperature"] = temperature
    current_config["rpm"] = rpm
    current_config["json_mode"] = json_mode
    
    if base_url:
        current_config["base_url"] = base_url
    
    try:
        # Dynamic import to avoid unnecessary dependencies
        import openai
        
        # Configure client based on endpoint
        match endpoint:
            case "OpenAI":
                client = openai.OpenAI(api_key=api_key if api_key else os.getenv("OPENAI_API_KEY"))
            case "Groq":
                client = openai.OpenAI(
                    api_key=api_key if api_key else os.getenv("GROQ_API_KEY"),
                    base_url="https://api.groq.com/openai/v1",
                )
            case "TogetherAI":
                client = openai.OpenAI(
                    api_key=api_key if api_key else os.getenv("TOGETHER_API_KEY"),
                    base_url="https://api.together.xyz/v1",
                )
            case "CUSTOM":
                if not base_url:
                    raise ValueError("Base URL is required for CUSTOM endpoint")
                client = openai.OpenAI(api_key=api_key, base_url=base_url)
            case "Ollama":
                client = openai.OpenAI(
                    api_key="ollama", base_url="http://localhost:11434/v1"
                )
            case _:
                # Default to OpenAI
                client = openai.OpenAI(
                    api_key=api_key if api_key else os.getenv("OPENAI_API_KEY")
                )
        
        return current_config
    
    except ImportError:
        raise ImportError(
            "OpenAI package is not installed. Please install with 'pip install openai'"
        )
    except Exception as e:
        raise RuntimeError(f"Failed to initialize language model client: {str(e)}")


def rate_limit(get_max_per_minute):
    """Rate limiting decorator to control API request rate"""
    def decorator(func):
        lock = Lock()
        last_called = [0.0]

        @wraps(func)
        def wrapper(*args, **kwargs):
            with lock:
                max_per_minute = get_max_per_minute()
                min_interval = 60.0 / max_per_minute
                elapsed = time.time() - last_called[0]
                left_to_wait = min_interval - elapsed

                if left_to_wait > 0:
                    time.sleep(left_to_wait)

                ret = func(*args, **kwargs)
                last_called[0] = time.time()
                return ret

        return wrapper
    return decorator


@rate_limit(lambda: current_config["rpm"])
def get_completion(
    prompt: str,
    system_message: str = "You are a helpful assistant.",
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    json_mode: Optional[bool] = None,
) -> Union[str, dict]:
    """
    Generate a completion using the configured language model.
    
    Args:
        prompt: The user's prompt or query
        system_message: Context for the assistant
        model: Optional model override
        temperature: Optional temperature override
        json_mode: Optional JSON mode override
        
    Returns:
        Generated text or JSON response
    """
    global client, current_config
    
    if client is None:
        raise RuntimeError("Model client not initialized. Call model_load() first.")
    
    # Use provided parameters or fallback to global config
    model = model or current_config["model"]
    temperature = temperature if temperature is not None else current_config["temperature"]
    json_mode = json_mode if json_mode is not None else current_config["json_mode"]
    
    try:
        if json_mode:
            response = client.chat.completions.create(
                model=model,
                temperature=temperature,
                top_p=1,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt},
                ],
            )
        else:
            response = client.chat.completions.create(
                model=model,
                temperature=temperature,
                top_p=1,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt},
                ],
            )
        
        return response.choices[0].message.content
    
    except Exception as e:
        raise RuntimeError(f"API request failed: {str(e)}")


def num_tokens_in_string(
    input_str: str, encoding_name: str = "cl100k_base"
) -> int:
    """Count the number of tokens in a string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(input_str))
    return num_tokens


def calculate_chunk_size(token_count: int, token_limit: int) -> int:
    """Calculate chunk size based on token count and limit."""
    if token_count <= token_limit:
        return token_count

    # Start with a guess of 100 characters per token
    chars_per_token = 100
    
    # Calculate total characters based on this guess
    total_chars = token_count * chars_per_token
    
    # Calculate number of chunks needed (aiming for token_limit tokens per chunk)
    num_chunks = (token_count + token_limit - 1) // token_limit
    
    # Calculate characters per chunk
    chars_per_chunk = total_chars // num_chunks
    
    return chars_per_chunk


def load_custom_terminology(terminology_file: str) -> Dict[str, str]:
    """Load custom terminology from a file.
    
    Args:
        terminology_file: Path to the terminology file
        
    Returns:
        Dictionary mapping source terms to target terms
    """
    terminology = {}
    try:
        with open(terminology_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and '=' in line:
                    source, target = line.split('=', 1)
                    terminology[source.strip()] = target.strip()
        return terminology
    except Exception as e:
        print(f"Error loading terminology file: {e}")
        return {}


def get_style_prompt(style: str, custom_instructions: str = None) -> str:
    """Get the prompt for a specific translation style.
    
    Args:
        style: The translation style to use
        custom_instructions: Additional custom instructions for the style
        
    Returns:
        The complete style prompt
    """
    base_style = TRANSLATION_STYLES.get(style, TRANSLATION_STYLES["General"])
    if custom_instructions:
        return f"{base_style} Additional instructions: {custom_instructions}"
    return base_style


def simple_translator(
    source_lang: str,
    target_lang: str,
    source_text: str,
    country: str = None,
    max_tokens: int = 1000,
    full_response: bool = False,
    translation_style: str = "General",
    custom_style_instructions: str = None,
    terminology_file: str = None
) -> Union[str, Tuple[str, str, str]]:
    """Translate text with options for returning the final translation or all steps.
    
    Args:
        source_lang: Source language
        target_lang: Target language
        source_text: Text to translate
        country: Target country for localization
        max_tokens: Maximum tokens per chunk
        full_response: Whether to return all translation steps
        translation_style: Style of translation to use
        custom_style_instructions: Additional custom instructions for the style
        terminology_file: Path to custom terminology file
        
    Returns:
        If full_response is False, returns the final translation.
        If full_response is True, returns a tuple of (initial_translation, reflection, final_translation).
    """
    # Load custom terminology if provided
    terminology = {}
    if terminology_file:
        terminology = load_custom_terminology(terminology_file)
    
    # Get style prompt
    style_prompt = get_style_prompt(translation_style, custom_style_instructions)
    
    # Check if text exceeds max tokens
    if num_tokens_in_string(source_text) > max_tokens:
        # Split text into chunks
        chunks = split_text_into_chunks(source_text, max_tokens)
        
        # Translate each chunk
        translations = []
        for chunk in chunks:
            translation = one_chunk_initial_translation(
                source_lang=source_lang,
                target_lang=target_lang,
                source_text=chunk,
                country=country,
                style_prompt=style_prompt,
                terminology=terminology
            )
            translations.append(translation)
        
        # Combine translations
        initial_translation = " ".join(translations)
    else:
        # Translate the entire text at once
        initial_translation = one_chunk_initial_translation(
            source_lang=source_lang,
            target_lang=target_lang,
            source_text=source_text,
            country=country,
            style_prompt=style_prompt,
            terminology=terminology
        )
    
    if not full_response:
        return initial_translation
    
    # Get reflection on translation
    reflection = one_chunk_reflect_on_translation(
        source_lang=source_lang,
        target_lang=target_lang,
        source_text=source_text,
        initial_translation=initial_translation,
        country=country,
        translation_style=translation_style,
        custom_style_instructions=custom_style_instructions,
        terminology=terminology
    )
    
    # Get improved translation
    final_translation = one_chunk_improve_translation(
        source_lang=source_lang,
        target_lang=target_lang,
        source_text=source_text,
        initial_translation=initial_translation,
        reflection=reflection,
        style_prompt=style_prompt,
        terminology=terminology
    )
    
    return initial_translation, reflection, final_translation


def one_chunk_initial_translation(
    source_lang: str,
    target_lang: str,
    source_text: str,
    country: str = None,
    style_prompt: str = None,
    terminology: Dict[str, str] = None
) -> str:
    """Perform initial translation for a single chunk of text.
    
    Args:
        source_lang: Source language
        target_lang: Target language
        source_text: Text to translate
        country: Target country for localization
        style_prompt: Style instructions for translation
        terminology: Custom terminology dictionary
        
    Returns:
        Initial translation of the text
    """
    # Prepare terminology instructions
    terminology_instructions = ""
    if terminology:
        terminology_instructions = "\nUse the following custom terminology:\n"
        for source, target in terminology.items():
            terminology_instructions += f"- {source} → {target}\n"
    
    # Prepare the prompt
    prompt = f"""Translate the following text from {source_lang} to {target_lang}."""
    
    if country:
        prompt += f" Adapt the translation for {country}."
    
    if style_prompt:
        prompt += f"\n\n{style_prompt}"
    
    if terminology_instructions:
        prompt += terminology_instructions
    
    prompt += f"\n\nText to translate:\n{source_text}"
    
    # Get translation
    response = get_completion(prompt)
    return response.strip()


def one_chunk_reflect_on_translation(
    source_lang: str,
    target_lang: str,
    source_text: str,
    initial_translation: str,
    country: str = "",
    translation_style: str = "General",
    custom_style_instructions: str = "",
    terminology: Dict[str, str] = None
) -> str:
    """Reflect on a translation and provide suggestions for improvement."""
    # Get style description
    style_description = TRANSLATION_STYLES.get(translation_style, "general translation")
    
    # Prepare system message
    system_message = f"""You are an expert linguist, specializing in {style_description} translation from {source_lang} to {target_lang}."""
    
    # Add custom style instructions if provided
    style_prompt = ""
    if custom_style_instructions:
        style_prompt = f"\nAdditional style instructions: {custom_style_instructions}"
    
    if terminology:
        system_message += f"\nUse the following custom terminology for specialized terms:\n{terminology}"

    country_context = f"The final style and tone of the translation should match the style of {target_lang} colloquially spoken in {country}." if country else ""

    reflection_prompt = f"""Your task is to carefully read a source text and a translation from {source_lang} to {target_lang} in a {style_description} style, and then give constructive criticism and helpful suggestions to improve the translation. \
{country_context}

The source text and initial translation, delimited by XML tags <SOURCE_TEXT></SOURCE_TEXT> and <TRANSLATION></TRANSLATION>, are as follows:

<SOURCE_TEXT>
{source_text}
</SOURCE_TEXT>

<TRANSLATION>
{initial_translation}
</TRANSLATION>

When writing suggestions, pay attention to whether there are ways to improve the translation's \n\
(i) accuracy (by correcting errors of addition, mistranslation, omission, or untranslated text),\n\
(ii) fluency (by applying {target_lang} grammar, spelling and punctuation rules, and ensuring there are no unnecessary repetitions),\n\
(iii) style (by ensuring the translations reflect the {style_description} style and take into account any cultural context),\n\
(iv) terminology (by ensuring terminology use is consistent and reflects the source text domain; and by only ensuring you use equivalent idioms {target_lang}).\n\

Write a list of specific, helpful and constructive suggestions for improving the translation.
Each suggestion should address one specific part of the translation.
Output only the suggestions and nothing else."""

    reflection = get_completion(reflection_prompt, system_message=system_message)
    return reflection


def one_chunk_improve_translation(
    source_lang: str,
    target_lang: str,
    source_text: str,
    initial_translation: str,
    reflection: str,
    style_prompt: str = None,
    terminology: Dict[str, str] = None
) -> str:
    """Improve the translation based on reflection.
    
    Args:
        source_lang: Source language
        target_lang: Target language
        source_text: Original text
        initial_translation: Initial translation
        reflection: Reflection on the translation
        style_prompt: Style instructions for translation
        terminology: Custom terminology dictionary
        
    Returns:
        Improved translation
    """
    # Prepare terminology instructions
    terminology_instructions = ""
    if terminology:
        terminology_instructions = "\nUse the following custom terminology:\n"
        for source, target in terminology.items():
            terminology_instructions += f"- {source} → {target}\n"
    
    # Prepare the prompt
    prompt = f"""Improve the following translation from {source_lang} to {target_lang} based on the reflection."""
    
    if style_prompt:
        prompt += f"\n\n{style_prompt}"
    
    if terminology_instructions:
        prompt += terminology_instructions
    
    prompt += f"""

Original text:
{source_text}

Initial translation:
{initial_translation}

Reflection:
{reflection}

Please provide an improved translation that addresses the issues identified in the reflection."""
    
    # Get improved translation
    response = get_completion(prompt)
    return response.strip()


def batch_translate(
    texts: Optional[List[str]] = None,
    source_texts: Optional[List[str]] = None,
    source_lang: str = "",
    target_lang: str = "",
    country: str = "",
    separator: str = "|||",
    translation_style: str = "General",
    custom_style_instructions: str = "",
    terminology_file: Optional[str] = None
) -> List[str]:
    """
    Translate a batch of texts at once to optimize API usage.
    
    Designed for Excel cells and other scenarios with multiple small texts.
    
    Args:
        texts: List of text strings to translate (legacy parameter)
        source_texts: List of text strings to translate (new parameter)
        source_lang: Source language of the texts
        target_lang: Target language for translation
        country: Optional country context for translation style
        separator: Separator used to join/split texts
        translation_style: Style of translation (e.g., "Literary", "Technical", "Financial")
        custom_style_instructions: Additional custom instructions for translation style
        terminology_file: Path to a file containing custom terminology
        
    Returns:
        List of translated texts
    """
    # Handle both parameter names for backward compatibility
    if texts is not None:
        input_texts = texts
    elif source_texts is not None:
        input_texts = source_texts
    else:
        return []
    
    if not input_texts:
        return []
    
    # Load custom terminology if provided
    custom_terminology = ""
    if terminology_file and os.path.exists(terminology_file):
        try:
            with open(terminology_file, 'r', encoding='utf-8') as f:
                custom_terminology = f.read()
        except Exception as e:
            print(f"Error loading terminology file: {e}")
    
    # Filter out empty texts
    filtered_texts = [text for text in input_texts if text and len(text.strip()) > 0]
    if not filtered_texts:
        return input_texts
    
    # Combine texts with separator
    combined_text = separator.join(filtered_texts)
    
    # Get style description
    style_description = TRANSLATION_STYLES.get(translation_style, "general translation")
    
    # Prepare system message
    system_message = f"""You are a professional translator from {source_lang} to {target_lang}, specializing in {style_description}. 
Follow these rules strictly:
1. Output ONLY the translation, nothing else
2. DO NOT include the original text in your response
3. DO NOT add any explanations or notes
4. Keep IDs, model numbers, and special characters unchanged
5. Use standard terminology for technical terms
6. Preserve the original formatting (spaces, line breaks)
7. Use proper grammar and punctuation
8. Only keep unchanged: proper names, IDs, and technical codes
9. Translate all segments separated by "{separator}" and keep them separated with the same delimiter"""
    
    if country:
        system_message += f"\n10. Use language style appropriate for {target_lang} as spoken in {country}"
    
    if custom_style_instructions:
        system_message += f"\n11. Follow these additional style instructions: {custom_style_instructions}"
    
    if custom_terminology:
        system_message += f"\n12. Use the following custom terminology for specialized terms:\n{custom_terminology}"
    
    # Prepare prompt
    user_prompt = f"""Translate the following text from {source_lang} to {target_lang} in a {style_description} style, keeping segments separated by '{separator}':\n\n{combined_text}"""
    
    try:
        # Call API
        translated_text = get_completion(
            prompt=user_prompt,
            system_message=system_message
        )
        
        # Split response
        translated_parts = translated_text.split(separator)
        
        # Handle mismatch in number of translated parts
        if len(translated_parts) != len(filtered_texts):
            # Fill with original text if parts are missing
            if len(translated_parts) < len(filtered_texts):
                translated_parts.extend(filtered_texts[len(translated_parts):])
            else:
                translated_parts = translated_parts[:len(filtered_texts)]
        
        # Map translations back to original text positions
        result = []
        translated_idx = 0
        
        for original_text in input_texts:
            if original_text and len(original_text.strip()) > 0:
                result.append(translated_parts[translated_idx])
                translated_idx += 1
            else:
                result.append("")
        
        return result
        
    except Exception as e:
        # Return original texts on error
        print(f"Error translating batch: {str(e)}")
        return input_texts


# --- Functions from Translation Agent for full translation pipeline ---

def one_chunk_initial_translation(
    source_lang: str, 
    target_lang: str, 
    source_text: str,
    country: str = "",
    style_prompt: str = None,
    terminology: Dict[str, str] = None
) -> str:
    """Initial translation for a single chunk of text."""
    # Get style description
    style_description = TRANSLATION_STYLES.get(style_prompt, "general translation")
    
    # Prepare system message
    system_message = f"""You are an expert linguist, specializing in {style_description} from {source_lang} to {target_lang}."""
    
    if style_prompt:
        system_message += f"\n{style_prompt}"
    
    if terminology:
        system_message += f"\nUse the following custom terminology for specialized terms:\n{terminology}"

    translation_prompt = f"""This is an {source_lang} to {target_lang} translation in a {style_description} style, please provide the {target_lang} translation for this text. \
Do not provide any explanations or text apart from the translation.
{source_lang}: {source_text}

{target_lang}:"""

    translation = get_completion(translation_prompt, system_message=system_message)
    return translation


def one_chunk_reflect_on_translation(
    source_lang: str,
    target_lang: str,
    source_text: str,
    initial_translation: str,
    country: str = "",
    translation_style: str = "General",
    custom_style_instructions: str = "",
    terminology: Dict[str, str] = None
) -> str:
    """Reflect on a translation and provide suggestions for improvement."""
    # Get style description
    style_description = TRANSLATION_STYLES.get(translation_style, "general translation")
    
    # Prepare system message
    system_message = f"""You are an expert linguist, specializing in {style_description} translation from {source_lang} to {target_lang}."""
    
    # Add custom style instructions if provided
    style_prompt = ""
    if custom_style_instructions:
        style_prompt = f"\nAdditional style instructions: {custom_style_instructions}"
    
    if terminology:
        system_message += f"\nUse the following custom terminology for specialized terms:\n{terminology}"

    country_context = f"The final style and tone of the translation should match the style of {target_lang} colloquially spoken in {country}." if country else ""

    reflection_prompt = f"""Your task is to carefully read a source text and a translation from {source_lang} to {target_lang} in a {style_description} style, and then give constructive criticism and helpful suggestions to improve the translation. \
{country_context}

The source text and initial translation, delimited by XML tags <SOURCE_TEXT></SOURCE_TEXT> and <TRANSLATION></TRANSLATION>, are as follows:

<SOURCE_TEXT>
{source_text}
</SOURCE_TEXT>

<TRANSLATION>
{initial_translation}
</TRANSLATION>

When writing suggestions, pay attention to whether there are ways to improve the translation's \n\
(i) accuracy (by correcting errors of addition, mistranslation, omission, or untranslated text),\n\
(ii) fluency (by applying {target_lang} grammar, spelling and punctuation rules, and ensuring there are no unnecessary repetitions),\n\
(iii) style (by ensuring the translations reflect the {style_description} style and take into account any cultural context),\n\
(iv) terminology (by ensuring terminology use is consistent and reflects the source text domain; and by only ensuring you use equivalent idioms {target_lang}).\n\

Write a list of specific, helpful and constructive suggestions for improving the translation.
Each suggestion should address one specific part of the translation.
Output only the suggestions and nothing else."""

    reflection = get_completion(reflection_prompt, system_message=system_message)
    return reflection


def one_chunk_improve_translation(
    source_lang: str,
    target_lang: str,
    source_text: str,
    initial_translation: str,
    reflection: str,
    style_prompt: str = None,
    terminology: Dict[str, str] = None
) -> str:
    """Improve translation based on reflection."""
    # Get style description
    style_description = TRANSLATION_STYLES.get(style_prompt, "general translation")
    
    # Prepare system message
    system_message = f"""You are an expert linguist, specializing in {style_description} editing from {source_lang} to {target_lang}."""
    
    if style_prompt:
        system_message += f"\n{style_prompt}"
    
    if terminology:
        system_message += f"\nUse the following custom terminology for specialized terms:\n{terminology}"

    prompt = f"""Your task is to carefully read, then edit, a translation from {source_lang} to {target_lang} in a {style_description} style, taking into
account a list of expert suggestions and constructive criticisms.

Please read the following:
1. Original {source_lang} text: {source_text}
2. Current {target_lang} translation: {initial_translation}
3. Suggestions for improvement: {reflection}

Please provide the improved {target_lang} translation of the original text. Return ONLY the improved translation, with no explanation or commentary."""

    improved_translation = get_completion(prompt, system_message=system_message)
    return improved_translation


def multichunk_initial_translation(
    source_lang: str, 
    target_lang: str, 
    source_text_chunks: List[str],
    translation_style: str = "General",
    custom_style_instructions: str = "",
    custom_terminology: str = ""
) -> List[str]:
    """Initial translation for multiple chunks of text."""
    translations = []
    
    for chunk in source_text_chunks:
        translation = one_chunk_initial_translation(
            source_lang, target_lang, chunk, translation_style, custom_style_instructions, custom_terminology
        )
        translations.append(translation)
    
    return translations


def multichunk_reflect_on_translation(
    source_lang: str,
    target_lang: str,
    source_text_chunks: List[str],
    translation_1_chunks: List[str],
    country: str = "",
    translation_style: str = "General",
    custom_style_instructions: str = ""
) -> List[str]:
    """Reflect on translations of multiple chunks."""
    reflections = []
    
    for src_chunk, trans_chunk in zip(source_text_chunks, translation_1_chunks):
        reflection = one_chunk_reflect_on_translation(
            source_lang, target_lang, src_chunk, trans_chunk, country, translation_style, custom_style_instructions
        )
        reflections.append(reflection)
    
    return reflections


def multichunk_improve_translation(
    source_lang: str,
    target_lang: str,
    source_text_chunks: List[str],
    translation_1_chunks: List[str],
    reflection_chunks: List[str],
    translation_style: str = "General",
    custom_style_instructions: str = "",
    custom_terminology: str = ""
) -> List[str]:
    """Improve translations of multiple chunks based on reflections."""
    improved_translations = []
    
    for src_chunk, trans_chunk, refl_chunk in zip(
        source_text_chunks, translation_1_chunks, reflection_chunks
    ):
        improved = one_chunk_improve_translation(
            source_lang, target_lang, src_chunk, trans_chunk, refl_chunk, translation_style, custom_style_instructions, custom_terminology
        )
        improved_translations.append(improved)
    
    return improved_translations 


@rate_limit(lambda: current_config["rpm"])
def detect_language(text: str) -> str:
    """
    Detect the language of a text using the language model.
    
    Args:
        text: The text to detect the language of
        
    Returns:
        The detected language name (e.g., "English", "Spanish")
    """
    if not text or len(text.strip()) < 10:
        return "Unknown"
    
    # Create a prompt for language detection
    prompt = f"""
    Detect the language of the following text. 
    Return ONLY the language name in English (e.g., "English", "Spanish", "French").
    Do not include any explanation or additional text.
    
    Text: {text[:500]}  # Limit text length to avoid token limits
    """
    
    try:
        # Get completion from the model
        response = get_completion(
            prompt=prompt,
            system_message="You are a language detection expert. Respond with only the language name.",
            temperature=0.1,  # Low temperature for more consistent results
            json_mode=False  # Disable JSON mode for language detection
        )
        
        # Clean up the response
        detected_lang = response.strip()
        
        # Check if the detected language is in our mapping
        if detected_lang in LANGUAGE_CODES:
            return detected_lang
        
        # Try to find a close match
        for lang in LANGUAGE_CODES:
            if lang.lower() in detected_lang.lower() or detected_lang.lower() in lang.lower():
                return lang
        
        # If no match found, return the raw response
        return detected_lang
        
    except Exception as e:
        print(f"Error detecting language: {str(e)}")
        return "Unknown" 