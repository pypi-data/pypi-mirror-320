if __name__ == "__main__":
    from src.monitor import EnergyMonitor
    
    monitor = EnergyMonitor()
    try:
        print("Starting energy monitoring...")
        monitor.log_energy_consumption()
    finally:
        monitor.stop_tracker()
        monitor.shutdown()
