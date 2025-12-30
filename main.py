from pokemon import Option, Context, apply_constraints, score, explain

# Define some options
options = [
    Option("Read book", {"time_taken": 5, "social_value": 2, "novelty_meter": 3, "learn_index": 5, "move_heart": 1, "challenge": 2, "fulfilment_value": 6}),
    Option("Go for walk", {"time_taken": 3, "social_value": 4, "novelty_meter": 2, "learn_index": 2, "move_heart": 3, "challenge": 1, "fulfilment_value": 4}),
    Option("Play game", {"time_taken": 8, "social_value": 1, "novelty_meter": 4, "learn_index": 1, "move_heart": 5, "challenge": 3, "fulfilment_value": 3})
]

# Set context
context = Context(device=5, pressing_matters=0)

# Filter options
options = apply_constraints(options)

# Compute scores
scores_dict = score(options, context)

# Show results
explain(scores_dict)
