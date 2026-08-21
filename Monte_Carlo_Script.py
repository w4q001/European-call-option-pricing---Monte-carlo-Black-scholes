from scipy.stats import norm
import matplotlib.pyplot as plt
import numpy as np


S0 = 100
K = 105
volatility = 0.15
time = 1
dtime = time / 252
r = 0.05


def BlackScholes(S, K, r, T, volatility):
    d1 = (np.log(S/K) + (r + 0.5*(volatility**2))*T) / (volatility*np.sqrt(T))
    d2 = d1 - volatility*np.sqrt(T)
    C = S*norm.cdf(d1) - K*np.exp(-r*T)*norm.cdf(d2)
    return C

bs_reference_price = BlackScholes(S0, K, r, time, volatility)


def montecarlo(n_sims):
    Z = np.random.normal(0, 1, size=(n_sims, 252))
    dWt = np.sqrt(dtime) * Z

    S = np.full(n_sims, S0, dtype=float)
    for day in range(252):
        S = S + (r * S * dtime) + (volatility * S * dWt[:, day])

    payoffs = np.maximum(S - K, 0)
    expected_payoff = np.mean(payoffs)
    standard_deviation = np.std(payoffs)
    standard_error = np.exp(-r * time) * standard_deviation / np.sqrt(n_sims)
    option_value = expected_payoff * np.exp(-r * time)
    lower_bound = option_value - 1.96 * standard_error
    upper_bound = option_value + 1.96 * standard_error

    return option_value, lower_bound, upper_bound


def montecarlo_antithetic(n_sims):
    n_pairs = n_sims // 2

    Z = np.random.normal(0, 1, size=(n_pairs, 252))
    dWt1 = np.sqrt(dtime) * Z
    dWt2 = np.sqrt(dtime) * (-Z)

    S1 = np.full(n_pairs, S0, dtype=float)
    S2 = np.full(n_pairs, S0, dtype=float)
    for day in range(252):
        S1 = S1 + (r * S1 * dtime) + (volatility * S1 * dWt1[:, day])
        S2 = S2 + (r * S2 * dtime) + (volatility * S2 * dWt2[:, day])

    payoff1 = np.maximum(S1 - K, 0)
    payoff2 = np.maximum(S2 - K, 0)
    pair_averages = (payoff1 + payoff2) / 2

    expected_payoff = np.mean(pair_averages)
    standard_deviation = np.std(pair_averages)
    standard_error = np.exp(-r * time) * standard_deviation / np.sqrt(n_pairs)
    option_value = expected_payoff * np.exp(-r * time)
    lower_bound = option_value - 1.96 * standard_error
    upper_bound = option_value + 1.96 * standard_error

    return option_value, lower_bound, upper_bound


sim_counts = [100, 500, 1000, 5000, 10000, 50000]

mc_prices, lower_bounds, upper_bounds = [], [], []
mc_prices_anti, lower_bounds_anti, upper_bounds_anti = [], [], []

for n in sim_counts:
    price, lower, upper = montecarlo(n)
    mc_prices.append(price)
    lower_bounds.append(lower)
    upper_bounds.append(upper)

    price_a, lower_a, upper_a = montecarlo_antithetic(n)
    mc_prices_anti.append(price_a)
    lower_bounds_anti.append(lower_a)
    upper_bounds_anti.append(upper_a)

plt.figure(figsize=(9, 5))

plt.plot(sim_counts, mc_prices, marker='o', label='Standard monte carlo', color='blue')
plt.fill_between(sim_counts, lower_bounds, upper_bounds, alpha=0.15, color='blue')

plt.plot(sim_counts, mc_prices_anti, marker='s', label='Antithetic monte carlo', color='orange')
plt.fill_between(sim_counts, lower_bounds_anti, upper_bounds_anti, alpha=0.15, color='orange')

plt.axhline(bs_reference_price, color='red', linestyle='--',
            label=f'Black-Scholes price = {bs_reference_price:.3f}')

plt.xscale('log')
plt.xlabel('Number of simulations')
plt.ylabel('Option price estimate')
plt.title('Standard vs Antithetic Monte Carlo Convergence to Black Scholes price')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()


n_test = 50000
_, low_std, up_std = montecarlo(n_test)
_, low_anti, up_anti = montecarlo_antithetic(n_test)

se_std = (up_std - low_std) / (2 * 1.96)
se_anti = (up_anti - low_anti) / (2 * 1.96)

variance_reduction_pct = (1 - (se_anti**2 / se_std**2)) * 100
print(f"Standard MC price:   {mc_prices[-1]:.4f}  (SE: {se_std:.4f})")
print(f"Antithetic MC price: {mc_prices_anti[-1]:.4f}  (SE: {se_anti:.4f})")
print(f"Variance reduction: {variance_reduction_pct:.1f}%")
