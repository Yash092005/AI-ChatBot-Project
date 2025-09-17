def calculate_usage():
    try:
        # Example calculation (you can adjust numbers later)
        taps = 5 * 10      # 5 taps × 10 liters/day
        showers = 2 * 50   # 2 showers × 50 liters/day
        toilets = 3 * 20   # 3 flushes × 20 liters/day

        total_usage = taps + showers + toilets
        return total_usage
    except Exception as e:
        return f"Error: {str(e)}"
