# Very small keyword-based KB search for demo purposes.
KB = {
    'kitchen': 'Tips for kitchen: reuse RO water for cleaning, wash veggies in a bowl, run dishwasher only when full.',
    'bathroom': 'Bathroom tips: keep showers to 5-7 minutes, install low-flow showerheads, fix leaking taps and cisterns.',
    'garden': 'Garden tips: water early morning, use drip irrigation, mulch to reduce evaporation.',
    'rainwater': 'Rainwater harvesting basics: clean roof, first-flush, storage tank. Sizing: roof_area * rainfall * efficiency.',
    'leak': 'Leak detection: check meter, check cistern with dye, listen for dripping pipes.'
}

def kb_search(query: str):
    q = query.lower()
    for k,v in KB.items():
        if k in q:
            return v
    # fallback: return short help
    return "I can help with saving water in kitchen/bathroom/garden, rainwater harvesting, or run a water footprint calculation. Try: 'calculate my water use' or 'how to save water in kitchen' "
