from transformers import pipeline
from src.monitor import EnergyMonitor

# Load LLM
llm = pipeline("text-generation", model="gpt2")

# Initialize energy monitor
monitor = EnergyMonitor()

try:
    # Monitor energy during inference
    print("Running LLM inference...")
    monitor.log_energy_consumption()
    result = llm("What is the capital of France?", max_length=10)
    print(result)
    monitor.log_energy_consumption()
finally:
    monitor.shutdown()
