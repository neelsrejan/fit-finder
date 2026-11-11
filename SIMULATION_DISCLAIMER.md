# Simulation disclaimer

Shopper counts, clicks, purchases, returns, A/B arms, and dollar figures in this repository are simulated.

The data-generating process is `src/fit_finder/events/ab.py`, and the knobs are named constants in `src/fit_finder/events/assumptions.py`.

- A shopper has a latent size.
- The control arm orders that size, or one step off, with fixed probabilities.
- The treatment arm sometimes accepts a recommendation. The recommendation moves toward the latent size only with `P_POLICY_RIGHT_ABOUT_DIRECTION`. That probability is an assumption. It is not the held-out directional accuracy of the trained model.
- A return is recorded when the received size does not match the latent size, with a small noise flip.
- Dollars multiply avoided returns by `ASSUMED_COST_PER_RETURN`. That cost is not in the UCSD files.

Held-out fit metrics are a different thing. They compare the model's fit class to the reviewer's fit label. They are not returns, and they are not the A/B test.

Local events posted to `/events` are requests this process received, usually from the demo page. The response field `simulated` is false for those rows because they really happened on the machine. They are still not store traffic. The simulated experiment does not go through that endpoint. It writes `analytics/extracts/`.
