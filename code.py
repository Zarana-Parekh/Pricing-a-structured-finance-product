##############################################################################
'''

Solution for TS-5
Zarana Parekh (201301177)
Mahima Achhpal (201301199)

We have not considered coupon values in the final settlement as given in 
the question.

An example has been included for code verification.

'''
##############################################################################


import pandas as pd
import numpy as np

# set equal to 1 for printing out specific day values for settlement
verbose = 0

# in this function we determine the returns and its volatility 
# from given data for each underlying
def find_parameters(filename):
	df = pd.read_csv(filename, sep=',')
	returns = []
	new_value = 0

	for idx, row in df.iterrows():
		old_value = new_value
		new_value = row['Close']
		
		if old_value != 0:
			r = (new_value - old_value)/old_value

			returns.append(r)

	return_values = np.array(returns)

	rate = np.mean(return_values)
	volatility = np.std(return_values)

	return [return_values, volatility]

T = 2 # maturity is 2 years
dt = 1/365 # for daily simulation
N = int(100000/2) # number of simulations 
numSteps = T*365 # number of steps per year 

# find returns and volatility for each underlying
ret1, sigma1 = find_parameters('BMW.csv')
ret2, sigma2 = find_parameters('DAIMLER.csv')
ret3, sigma3 = find_parameters('VW.csv')

corr_matrix = np.corrcoef([ret1,ret2,ret3]) # correlation matrix for the return values
vol = np.array([sigma1, sigma2, sigma3]) * np.sqrt(dt) # volatility 
cov = np.dot(np.dot(np.diag(vol) , corr_matrix) , np.diag(vol)) # covariance

ret1 = []
ret2 = []
ret3 = []

# generating correlated normal random variables
x = np.random.multivariate_normal([0, 0, 0], cov, (numSteps,N)) 
y = np.mean(x,axis=0) -x
x2 = np.concatenate((x,np.array(y)),axis=1)

x = []
y = []

rf = -0.251552 # risk-free rate

# simulating relative prices of the underlyings
price_relative1 = np.exp(np.cumsum((rf - 0.5 * sigma1 ** 2) * dt + x2[:,:,0],axis=1)) # BMW
price_relative2 = np.exp(np.cumsum((rf - 0.5 * sigma2 ** 2) * dt + x2[:,:,1],axis=1)) # DAIMLER
price_relative3 = np.exp(np.cumsum((rf - 0.5 * sigma3 ** 2) * dt + x2[:,:,2],axis=1)) # VW

x2 = []

strike = 1 # strike price
barrier = 0.65 # barrier price
underlying = np.array([10.68947, 12.00624, 5.05306]) # price of eah underlying
lock_in = 1.03 # lock-in value
nominal = 1000 # nominal value
lock_days = [99, 191, 282, 373, 467, 558, 649] # lock-in days taking 15/07/15 as first day indexing from 0

price_relatives = np.array([price_relative1, price_relative2,price_relative3])

price_relative1 = []
price_relative2 = []
price_relative3 = []

##############################################################################
# uncomment the following example to verify the code
##############################################################################

'''
#Following are the different settlement cases.

#Parameter values have been slightly modified for this case.

price_relatives = np.ones((3,6,4)) # relative prices for each underlying 
#its size = underlyings * numsteps * simulations

strike = 1.2 # strike price for each underlying
barrier = 0.65 # barrier price for each underlying
lock_in = 1.4 # lock-in price

#Case 1: If a Lock-in Event occurred during the term, 
#the repayment is in each case at the nominal value, in addition to the coupon.

price_relatives[0,1,0] = 1.5
price_relatives[0,2,0] = 1.5
price_relatives[1,2,0] = 1.5
price_relatives[2,2,0] = 1.5

#Case 2: If no Lock-in Event occurred and if none of the underlyings touches or 
#breaches its barrier during barrier monitoring, the
#nominal value is repaid – in addition to the coupon 
#(we have not considered coupons)

price_relatives[0,2,1] = 0.7
price_relatives[1,2,1] = 0.7
price_relatives[2,2,1] = 0.7


#Case 3: If no Lock-in Event occurred and if at least one of the underlyings touches
#or breaches its barrier during barrier monitoring, redemption is as follows – 
#in addition to the coupon, if all final fixings of the underlyings are higher than 
#or equal to the corresponding strike prices, the nominal value is repaid.

price_relatives[0,2,2] = 0.5
price_relatives[1,2,2] = 0.5
price_relatives[2,2,2] = 0.7
price_relatives[0,5,2] = 1.3
price_relatives[1,5,2] = 1.3
price_relatives[2,5,2] = 1.3


#Case 4: If no Lock-in Event occurred and if at least one of the underlyings touches
#or breaches its barrier during barrier monitoring, redemption is as follows – 
#in addition to the coupon, if the final fixing of at least one underlying is lower 
#than its strike price, a physical delivery of the indicated number of the underlying 
#with the poorest performance in percentage terms is made; fractions are not accumulated 
#and are paid out in cash.

price_relatives[0,2,3] = 0.5
price_relatives[1,2,3] = 0.5
price_relatives[2,2,3] = 0.7
price_relatives[0,5,3] = 1.3
price_relatives[1,5,3] = 1.3
price_relatives[2,5,3] = 1.1

lock_days = [2,3] # days considered for lock-in monitoring indexed from 0

numSteps = 6 # the above example is run on a smaller number of simulations to
# verify the validity of the results
verbose = 1
'''

##############################################################################

'''
we have determined the steps at which each condition is satisfied such as lock-in
event, barrier breach, etc. Then we update the payoff value in the final
results accordingly.
'''

locks = np.nonzero((price_relatives[:,lock_days,:]>lock_in).all(axis=0))[1]
if verbose:
	print("===============lock-in days==============")
	print(locks)

non_barrier_breaches = np.nonzero((price_relatives>barrier).all(axis=1).all(axis=0))[0]
if verbose:
	print("===============non-barrier breach days=======================")
	print(non_barrier_breaches)

above_strike = np.nonzero((price_relatives[:,numSteps-1,:]- strike >=0).all(axis = 0))[0]
if verbose:
	print("============above-strike days=================")
	print(above_strike)

min_indices = np.argmin(price_relatives[:,numSteps-1,:], axis = 0)
if verbose:
	print("===============min-underlying indices==============")
	print(min_indices)

payoff = np.zeros(N)

# setting the payoffs
p = np.swapaxes(price_relatives,0,2)
payoff = p[np.arange(p.shape[0]),numSteps-1,min_indices]*underlying[min_indices]
payoff[above_strike] = nominal
payoff[non_barrier_breaches] = nominal
payoff[locks] = nominal

print("================payoff details=============")
print('mean value of payoff: ', np.exp(-rf*T)*np.mean(payoff))
print('standard deviation of payoff: ',np.std(payoff))
    