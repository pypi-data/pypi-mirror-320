# Energy Monitor

A Python package to monitor energy consumption and CO2 emissions for LLM models and other computational tasks. The package provides tools to track power usage of both CPU and GPU, as well as monitor system memory usage. It also estimates CO2 emissions based on energy consumption.

## Features

- Monitors CPU power usage
- Monitors GPU power usage (NVIDIA GPUs only)
- Monitors memory usage
- Estimates CO2 emissions based on energy consumption

## Installation

You can install the package using pip:

```bash
pip install python-energy-monitor
```
## Usage

You can use the EnergyMonitor class to start monitoring energy consumption and CO2 emissions:

```python
from energy_monitor import EnergyMonitor

# Initialize the energy monitor
monitor = EnergyMonitor()

# Log energy consumption data
monitor.log_energy_consumption()

# Stop the emissions tracker and get CO2 emissions
monitor.stop_tracker()

# Shutdown the monitor
monitor.shutdown()
```

## Requirements

- Python 3.6+
- psutil
- pynvml (for NVIDIA GPU monitoring)
- codecarbon (for CO2 emissions tracking)