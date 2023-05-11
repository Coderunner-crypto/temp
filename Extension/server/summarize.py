import os
import math
import time
import tiktoken
import backoff
import openai
import concurrent.futures
from youtube_transcript_api import YouTubeTranscriptApi
from bottle import post, request, run, response, static_file, route
from dotenv import load_dotenv

load_dotenv()


openai.api_key = os.getenv('OPENAI_API_KEY')

@backoff.on_exception(backoff.expo,
                      openai.error.RateLimitError,
                      max_tries=8)
def completions_with_backoff(**kwargs):
    return openai.Completion.create(**kwargs)

def split_text(text, chunk_size):
    text_split, n = text.split(), chunk_size
    chunks = math.ceil(len(text_split) / n)
    return [' '.join(text_split[i * n: (i + 1) * n]) for i in range(chunks)]

def num_tokens_from_string(string, encoding_name):
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def simple_summarize(text):
    # print(num_tokens_from_string(text, 'gpt2'))
    prompt = text + '\n\n' + 'Summarize the above text and return only the summary, nothing else. Also tell whether thr video is a clickbait or not. Separate the clickbait answer form the summary by $ symbol.'
    res = completions_with_backoff(
        model="text-davinci-002",
        prompt=prompt,
        max_tokens=250,
        temperature=0
    )
    # print(text, num_tokens_from_string(text, 'gpt2'), res.choices[0].text)
    return res.choices[0].text

def recursive_summarize(text):
    chunks = split_text(text, 2000)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(simple_summarize, chunk) for chunk in chunks]
        results = [f.result() for f in futures]
        summary = '\n'.join(results)
    n = num_tokens_from_string(summary, 'gpt2')
    # print(n)
    # print(summary)
    if n > 3700:
        return recursive_summarize(summary)
    return simple_summarize(summary)

def summarize(video_id):
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    transcript = transcript_list.find_transcript(['en', 'en-IN']).fetch()
    print(transcript)
    text = ' '.join(map(lambda x: x['text'], transcript))
    n = num_tokens_from_string(text, 'gpt2')
    if n > 3700:
        return recursive_summarize(text)
    return simple_summarize(text)

def enable_cors(fn):
    def _enable_cors(*args, **kwargs):
        # set CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

        if request.method != 'OPTIONS':
            # actual request; reply with the actual response
            return fn(*args, **kwargs)

    return _enable_cors

