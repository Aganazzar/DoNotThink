import random
from statistics import mean, variance

# --------------------------
# Option class
# --------------------------
class Option:
    def __init__(self, name, params):
        self.name = name
        self.params = params

    def __repr__(self):
        return f"Option({self.name})"

    def __hash__(self):
        return hash(self.name)  # allows using Option as dict key

# --------------------------
# Constraints
# --------------------------
def time_constraint(option):
    return option.params.get('time_taken', 0) <= 35

CONSTRAINTS = [time_constraint]

def apply_constraints(options):
    return [opt for opt in options if all(c(opt) for c in CONSTRAINTS)]

# --------------------------
# Criteria
# --------------------------
def time_score(option):
    return -option.params.get("time_taken", 0)

def social_score(option):
    return option.params.get("social_value", 0)

def novelty_score(option):
    return option.params.get("novelty_meter", 0)

def learn_score(option):
    return option.params.get("learn_index", 0)

def emotional_score(option):
    return option.params.get("move_heart", 0)

CRITERIA = {
    "time_score": time_score,
    "social_score": social_score,
    "novelty_score": novelty_score,
    "learn_score": learn_score,
    "emotional_score": emotional_score,
    # Fulfilment is handled separately
}

# --------------------------
# Normalization
# --------------------------
def normalize(scores):
    min_s, max_s = min(scores), max(scores)
    if min_s == max_s:
        return [0.5 for _ in scores]
    return [(s - min_s) / (max_s - min_s) for s in scores]

def compute_normalized_scores(options):
    normalized = {}
    for crit_name, func in CRITERIA.items():
        raw = [func(opt) for opt in options]
        norm = normalize(raw)
        normalized[crit_name] = dict(zip(options, norm))
    return normalized

# --------------------------
# Context
# --------------------------
class Context:
    def __init__(self, device=0, pressing_matters=0):
        self.device = device
        self.pressing_matters = pressing_matters

def compute_weights(context):
    # time more important if pressing matters
    # other criteria have neutral weight
    return {
        "time_score": 1.0 + context.pressing_matters,
        "social_score": 1.0,
        "novelty_score": 1.0,
        "learn_score": 1.0,
        "emotional_score": 1.0
    }

# --------------------------
# Fulfilment-based simulation
# --------------------------
def simulate_fulfilment(option, context, n=100):
    """
    Fulfilment is scaled by context:
      - pressing_matters increases fulfilment
      - device presence increases fulfilment
    Small uncertainty added for realism.
    """
    base = option.params.get("fulfilment_value", 0)
    scaled = base * (1 + 0.5 * context.pressing_matters + 0.5 * context.device)
    sigma = 0.5  # small noise
    return [random.gauss(scaled, sigma) for _ in range(n)]

def expected_utility(values, risk_lambda=0.01):
    mu = mean(values)
    var = variance(values) if len(values) > 1 else 0
    return mu - risk_lambda * var

# --------------------------
# Combinational penalties
# --------------------------
def combinational_impact(option):
    """
    Compute combined effect of learn_index and novelty based on time_taken.
    - Shorter time for high learning/novelty increases impact.
    - Longer time reduces impact proportionally.
    """
    time = option.params.get("time_taken", 1)
    learn = option.params.get("learn_index", 0)
    novelty = option.params.get("novelty_meter", 0)
    fulfil = option.params.get("fulfilment_value", 0)
    
    # Learning impact: scale inversely with time
    learn_impact = learn / time  # high learn, low time → bigger
    
    # Novelty impact: scale inversely with time, similar idea
    novelty_impact = novelty / time
    
    # Optional: relative fulfilment adjustment
    fulfil_impact = fulfil / max(time, 1)
    
    total_impact = learn_impact + novelty_impact + fulfil_impact
    
    return total_impact

# --------------------------
# Aggregate scoring
# --------------------------
def score(options, context):
    normalized_scores = compute_normalized_scores(options)
    weights = compute_weights(context)
    scores = {}

    for opt in options:
        total = 0
        # Weighted sum of normalized criteria
        for crit in CRITERIA:
            total += normalized_scores[crit][opt] * weights.get(crit, 1.0)
        # Add expected fulfilment (scaled by context)
        fulfil_values = simulate_fulfilment(opt, context)
        total += expected_utility(fulfil_values)
        # Add combinational penalties
        total += combinational_impact(opt)
        scores[opt] = total

    return scores

# --------------------------
# Explanation
# --------------------------
def explain(scores):
    print("Scores for all options:")
    for opt, score_value in scores.items():
        print(f"{opt.name}: {score_value:.3f}")
    
    best = max(scores, key=scores.get)
    print("\nSelected option:")
    print(f"{best.name} with score: {scores[best]:.3f}")

# --------------------------
# Example usage
# --------------------------
if __name__ == "__main__":
    # Define available free-time options
    options = [
        Option(
            "Read book", 
            {
                "time_taken": 5,
                "social_value": 2,
                "novelty_meter": 3,
                "learn_index": 5,
                "move_heart": 1,
                "fulfilment_value": 6
            }
        ),
        Option(
            "Go for walk", 
            {
                "time_taken": 3,
                "social_value": 4,
                "novelty_meter": 2,
                "learn_index": 2,
                "move_heart": 3,
                "fulfilment_value": 4
            }
        ),
        Option(
            "Play game", 
            {
                "time_taken": 8,
                "social_value": 1,
                "novelty_meter": 4,
                "learn_index": 1,
                "move_heart": 5,
                "fulfilment_value": 3
            }
        )
    ]

    # Define the current context
    context = Context(device=1, pressing_matters=2)

    # Apply constraints to filter out infeasible options
    options = apply_constraints(options)

    # Compute scores for all options
    scores_dict = score(options, context)

    # Display scores and the selected option
    explain(scores_dict)

