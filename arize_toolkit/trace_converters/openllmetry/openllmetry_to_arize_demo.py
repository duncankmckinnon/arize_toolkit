import os
import openai

from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from arize_toolkit.trace_converters.openllmetry.map_openll_to_openinference import OpenLLMetryToOpenInferenceSpanProcessor

from opentelemetry.instrumentation.openai import OpenAIInstrumentor
from arize.otel import register  # convenience helper from Arize
import grpc  # for the Compression enum


# ✏️  Secrets
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

SPACE_ID = os.getenv("SPACE_ID")
API_KEY = os.getenv("API_KEY") 
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if __name__ == "__main__":
    provider = register(
        space_id=SPACE_ID,
        api_key=API_KEY,
        project_name="tracing-haiku-tutorial",
        set_global_tracer_provider=True,
    )

    provider.add_span_processor(OpenLLMetryToOpenInferenceSpanProcessor())

    provider.add_span_processor(
        BatchSpanProcessor(
            OTLPSpanExporter(
                endpoint="otlp.arize.com:443",
                headers={
                    "authorization": f"Bearer {API_KEY}",
                    "api_key": API_KEY,
                    "arize-space-id": SPACE_ID,
                    "arize-interface": "python",
                    "user-agent": "arize-python",
                },
                compression=grpc.Compression.Gzip,  # use enum instead of string
            )
        )
    )

    # ----------------------------------------------------------------------------------
    # Instrument OpenAI & make a quick test request
    # ----------------------------------------------------------------------------------
    OpenAIInstrumentor().instrument(tracer_provider=provider)
    openai_client = openai.OpenAI()

    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Write a haiku."}],
        max_tokens=20,
    )
    print("\nAssistant:\n", response.choices[0].message.content)

    # ----------------------------------------------------------------------------------
    # Resulting span attributes include:
    #   input.mime_type  = "application/json"
    #   input.value     ← JSON string of prompt + params
    #   llm.* / output.* / openinference.span.kind = "LLM"
    # ----------------------------------------------------------------------------------
