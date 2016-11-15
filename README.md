# Pricing-a-structured-finance-product

Here a finance product has been priced. Details about the product can be found in the term sheet called TS-5.

1. Price the product using Monte Carlo simulation: using antithetic variates and the total simulation size as 100,000.

2. For estimating volatility and correlation we have used recent data for the underlyings in the term-sheet. 

3. The following featurs have been ignored for simplifying the problem:

 - It is assumed that payoff is in the same currency as that of the underlying (not Quanto).
 - Interim coupons paid by the product have been ignored.
 
4. The risk-free (spot) rate has been taken from the European Central Bank website. It has been used as the drift rate in GBM.
