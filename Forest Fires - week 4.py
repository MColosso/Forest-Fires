# Regression Modeling in Practice Course
# Wesleyan University
# 
# Logistic Regression Model
# Mario Colosso V.
# 
# The sample comes from Cortez and Morais study about predicting forest fires using 
# metereological data [Cortez and Morais, 2007]. The study includes data from 517
# forest fires in the Natural Park Montesinho (Trás-os-Montes, in northeastern Portugal)
# January 2000 to December 2003, including meteorological data, the type of vegetation
# involved (which determines the six components of the Canadian Forest Fire Weather Index
# (FWI) system --see below--) and the total burned area in order to generate a model capable
# of predicting the burned area of small fires, which are more frequent.
# 
# Measures
# The data contains:
# * X, Y: location of the fire (x,y axis spatial coordinate within the Montesinho park map:
#   from 1 to 9)
# * month, day: month and day of the week the fire occurred (january to december and monday
#   to sunday)
# * FWI system components:
#   - FFMC: Fine Fuel Moisture Code (numeric rating of the moisture content of litter and
#     other cured fine fuels: 18.7 to 96.2)
#   - DMC: Duff Moisture Code (numeric rating of the average moisture content of loosely
#     compacted organic layers of moderate depth: 1.1 to 291.3)
#   - DC: Drought Code (numeric rating of the average moisture content of deep, compact
#     organic layers: 7.9 to 860.6)
#   - ISI: Initial Spread Index (numeric rating of the expected rate of fire spread: 0.0
#     to 56.1)
# * Meteorological variables:
#   - temp: temperature (2.2 to 33.3 °C)
#   - RH: relative humidity (15 to 100%)
#   - wind: wind speed (0.4 to 9.4 Km/h)
#   - rain: outside rain (0.0 to 6.4 mm/m^2)
# * area: the burned area of the forest as response variable (0.0 to 1090.84 Ha).

# Forest Fires

# Import required libraries and set global options
import pandas
import numpy
import matplotlib.pyplot as plt
import seaborn
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats import outliers_influence

pandas.set_option('display.float_format', lambda x:'%.3f'%x)


# TEST CATEGORICAL EXPLANATORY VARIABLES WITH MORE THAN TWO CATEGORIES

# Load Forest Fires .csv file
fires = pandas.read_csv('forestfires.csv')

# DATA MANAGEMENT

# Delete rows where any or all of the data are missing
fires = fires.dropna()

# Convert categorical variables (months and days) into numerical values
months_table = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 
                'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
days_table   = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat']

fires['month'] = [months_table.index(month) for month in fires['month'] ]
fires['day']   = [days_table.index(day)     for day   in fires['day']   ]

fires_attributes  = list(fires.columns.values)
number_of_columns = len(fires_attributes)

# Shift (X, Y) coordinates to origin
fires['X'] -= min(fires['X'])
fires['Y'] -= min(fires['Y'])

# Test categorical explanatory variables with more than two categories
model = smf.ols(formula = "area ~ C(X) + C(Y) + C(month) + C(day) + FFMC + DMC + " +
                          "       DC + ISI + temp + RH + wind + rain", 
                data = fires).fit()
print(model.summary())

# COMMENTS
# 
# * Only DC and DMC features (Drought Code and Duff Moisture Code) are statistically relevant to predict
#   burned area (p-values are 0.036 and 0.030 respectively)
# * No categorical variable (X, Y, month, day) are statistically relevant (p-values = 0.182+) but Y = 6
#   (p-value = 0.033)



# Data Management

# Load Forest Fires .csv file
fires = pandas.read_csv('forestfires.csv')

# Delete rows where any or all of the data are missing
fires = fires.dropna()

# Convert categorical variables (months and days) into numerical values
fires = pandas.get_dummies(fires, prefix_sep = '_')

# Shift (X, Y) coordinates to origin
fires['X'] -= min(fires['X'])
fires['Y'] -= min(fires['Y'])

# X and Y are categorical variables, numerically coded 
#    -> Convert them in corresponding variables: X_0, X_1, ... Y_0, Y_1, ...
for x in range(min(fires['X']), max(fires['X'])+1):
    fires["X_{}".format(x)] = 1 * (fires['X'] == x)
fires.drop('X', axis=1, inplace=True)

for y in range(min(fires['Y']), max(fires['Y'])+1):
    fires["Y_{}".format(y)] = 1 * (fires['Y'] == y)
fires.drop('Y', axis=1, inplace=True)


# In[8]:

fires_attributes  = list(fires.columns.values)
number_of_columns = len(fires_attributes)


# Logistic regression [...] The binary logistic model is used to estimate the probability of a binary 
# response based on one or more predictor (or independent) variables (features). (Reference: Wikipedia
# (https://en.wikipedia.org/wiki/Logistic_regression)

# Convert target variable (burned area) into a categorical (binary) variable
# 0 = no burned area; 1 = some extension of the forest was burned
index_list = fires[fires['area'] > 0.].index.tolist()
fires['area'] = 0.
fires.loc[index_list, 'area'] = 1.

# Center each explanatory variables
#to_be_centered = fires_attributes[fires_attributes.index('FFMC') : 
#                                  fires_attributes.index('rain') + 1]
to_be_centered = [attr for attr in fires_attributes if attr != 'area']
for attr in to_be_centered:   #From FFMC to rain: Exclude categorical variables
    fires[attr] = fires[attr] - fires[attr].mean()

# Display general info about adjusted dataset
fires.describe().T


# Logistic regression

# Avoid explanatory variables equal to zero to avoid singular matrix
response_variable     = 'area'
explanatory_variables = [attr for attr in fires_attributes if attr != response_variable]

exp_variables_equal_zero = [attr for attr in explanatory_variables 
                            if sum(abs(fires[attr].values)) == 0]
print('Avoiding', exp_variables_equal_zero)
exp_variables_equal_zero += [response_variable]
explanatory_variables = [attr for attr in explanatory_variables 
                         if attr not in exp_variables_equal_zero]

import sys

def logistic_model(data, explanatory_variables, response_variable, 
                   maxiter = 35, verbose = True):
    explanatory_vars = ' + '.join(explanatory_variables)
    formula = response_variable + ' ~ ' + explanatory_vars

    try:
        model = smf.logit(formula = formula, data = data).fit(maxiter = maxiter)
    except:
        print('Error "' + str(sys.exc_info()[1]) + '" while processing model', formula)
        model = None
    
    if verbose and model != None:
        print()
        print('MODEL:', formula, '\n')
        print(model.summary())
        print()

        # odds ratios with 95% confidence intervals
        print ("Odds Ratios")
        params = model.params
        conf = model.conf_int()
        conf['OR'] = params
        conf.columns = ['Lower CI', 'Upper CI', 'Odds Ratios']
        print (numpy.exp(conf))
        
    return(model)

# Build Logistic Model
model = logistic_model(fires, explanatory_variables, response_variable, maxiter = 100)


# ------ The validity of the model fit is questionable ------
# 
# Even increasing the number of iterations to 2000, we got the message: "Warning: Maximum number of
# iterations has been exceeded."
# Occasionally when running a logistic/probit  regression we run into the problem of so-called complete
# separation or quasi-complete separation.
# 
# A complete separation happens when the outcome variable separates a predictor variable or a combination
# of predictor variables completely. Albert and Anderson (1984) define this as, "there is a vector α that
# correctly allocates all observations to their group."
# Complete separation or perfect prediction can occur for several reasons. One common example is when
# using several categorical variables whose categories are coded by indicators. For example, if one is
# studying an age-related disease (present/absent) and age is one of the predictors, there may be subgroups
# (e.g., women over 55) all of whom have the disease. Complete separation also may occur if there is a coding
# error or you mistakingly included another version of the outcome as a predictor. For example, we might have
# dichotomized a continuous variable X into a binary variable Y. We then wanted to study the relationship
# between Y and some predictor variables. If we would include X as a predictor variable, we would run into
# the problem of perfect prediction, since by definition, Y separates X completely. The other possible scenario
# for complete separation to happen is when the sample size is very small. In our example data above, there is
# no reason for why Y has to be 0 when X1 is <=3. If the sample were large enough, we would probably have some
# observations with Y = 1 and X1 <=3, breaking up the complete separation of X1.
# 
# Quasi-complete separation in a logistic/probit regression happens when the outcome variable separates a
# predictor variable or a combination of predictor variables to certain degree. 
# 
# (See http://www.ats.ucla.edu/stat/mult_pkg/faq/general/complete_separation_logit_models.htm)


# Test collinearity
# 
# As stated in PennState, STATS 501-Regression Methods course
# (https://onlinecourses.science.psu.edu/stat501/node/348), one way to reduce data-based multicollinearity is
# to collect aditional data under different experimental or observational conditions, which is not the current
# case. We'll use `variance_inflation_factor()` to determinate highly collinear features and remove one or more
# violating predictors from the regression model.
# 
#   variance_inflation_factor(exog, exog_idx)
# 
#   The variance inflation factor (VIF) is a measure for the increase of the variance of the parameter estimates
#   if an additional variable, given by 'exog_idx' is added to the linear regression. It is a measure for
#   multicollinearity of the design matrix, 'exog'.
#   One recommendation is that if VIF is greater than 5, then the explanatory variable given by 'exog_idx' is
#   highly collinear with the other explanatory variables, and the parameter estimates will have large standard
#   errors because of this.

def test_collinearity(data, explanatory_variables):
    data = numpy.array(data)
    highly_collinear_attr = list()
    vif_list = list()
    for attr in explanatory_variables:
        vif = outliers_influence.variance_inflation_factor(data, 
                                                           explanatory_variables.index(attr))
        vif_list.append(vif)
        if(vif > 5):
            highly_collinear_attr.append(attr)

    print('\nVariance Inflation Factors:')
    print(pandas.DataFrame(vif_list, index=explanatory_variables, columns=['VIF']).T)

    print('\nHighly collinear features:')
    print(highly_collinear_attr)


# Test collinearity of full model
test_collinearity(fires, explanatory_variables)

# COMMENTS
# 
# * One of FWI system components: DC (Drought Code: numeric rating of the average moisture content of deep,
#   compact organic layers), all months variables but april, all days variables, all X coordinates and all
#   Y coordinates but Y = 7 appears as highly collinear features.

# Lets try a simple model: FWI system components plus meteorological variables:

# TEST A SIMPLE MODEL (FWI system components + meteorological variables)
fwi_and_meteo_vars = ['FFMC', 'DMC', 'DC', 'ISI', 'temp', 'RH', 'wind', 'rain']
model = logistic_model(fires, fwi_and_meteo_vars, response_variable, maxiter = 100)

# COMMENTS
# 
# * This model converges to a solution but it doesn't explain the output variable (just 1.5% of cases)
# 
# * The odds ratios (probability of an event occurring in one group compared to the probability of an event
#   occurring in another group) are all near 1, indicating that there's an equal probability of forest fires
#   with or without rain, wind or any other used features.

# Lets test collinearity of variables in this model:

# Test collinearity for simple model (FWI system components + meteorological variables)
test_collinearity(fires, fwi_and_meteo_vars)

# COMMENTS
# 
# * DC (Drought Code: numeric rating of the average moisture content of deep, compact organic layers) is
#   highly collinear with the rest of the features.
# * Removing repetidely highly collinear features from the simple model, leads to only two variables: FFMC
#   (Fine Fuel Moisture Code: numeric rating of the moisture content of litter and other cured fine fuels)
#   and DMC (Duff Moisture Code: numeric rating of the average moisture content of loosely compacted organic
#   layers of moderate depth)


# TEST MODELS ADDING FEATURES TO SIMPLE MODEL (FWI system components + meteorological variables)
# Brute force attack. It may take a while
discarded_vars = ['area', 'Y_5']
vars_to_add    = [attr for attr in fires_attributes 
                  if attr not in fwi_and_meteo_vars + discarded_vars]
loop_indexes   = [0] * len(vars_to_add)
loop_index     = 0

results        = pandas.DataFrame(columns = ('Converge', 'Warnings', 'Pseudo_R_sq', 'Model'))
results_index  = 0

while (loop_index >= 0) and (results_index < 5000):   #Test only 5000 combinations
    exp_vars = []
    for idx in range(loop_index+1):
        exp_vars += [vars_to_add[loop_indexes[idx]]]
    formula = response_variable + ' ~ ' + ' + '.join(fwi_and_meteo_vars + exp_vars)
    model = logistic_model(fires, fwi_and_meteo_vars + exp_vars, 
                           response_variable, verbose = False)
    if model == None:
       results.loc[results_index] = [None, -1, None, 'Error: ' + formula]
    else:
        results.loc[results_index] = [model.mle_retvals['converged'], #Converge
                                      model.mle_retvals['warnflag'],  #Warnings
                                      model.prsquared,                #Pseudo R Squared
                                      formula]                        #Model
    results_index += 1
    if loop_indexes[loop_index] + 1 >= len(vars_to_add):
        loop_indexes[loop_index] = 0
        loop_index -= 1
        if loop_index < 0:
            break
        loop_indexes[loop_index] += 1
    elif loop_index < len(vars_to_add) - 1:
        loop_index += 1
        loop_indexes[loop_index] = loop_indexes[loop_index - 1] + 1
    else:
        print('Unknown condition')
        break

print('Total models:', len(results))
print('Total models which converged:', len(results[results['Converge'] == True]))
print('Total models with warnings:',   len(results[results['Warnings'] > 0]))
print('Total models on error:',        len(results[results['Warnings'] < 0]))
print()
print('Models which converged')
subset = results[results['Converge'] == True][['Pseudo_R_sq', 'Model']]
for idx in range(len(subset)):
    print('Pseudo R sq = %.3f, Model = %s' % (subset['Pseudo_R_sq'].ix[idx], 
                                              subset['Model'].ix[idx]))


# COMMENTS
# 
# * From a sample of 5000 models, only 3 converged to a solution, which are not explanatory of variance
#   on forest fires (pseudo R squared = 3.6% or less)
# * 4823 models finished with convergence warninigs: "Maximum Likelihood optimization failed to converge",
#   due to complete or quasi-complete separation.
# * The difference (174 models) finished with "Singular matrix" error while matrix inversion.

# Lets try the most promissing model (that one with biggest pseudo R squared):

# Take the formula of the most promissing model
r2_list = list(subset['Pseudo_R_sq'])
model_text = subset.ix[r2_list.index(max(r2_list))]['Model']

# Separate response variable from explanatory variables (separator = '~') and build a list of explanatory
# variables (separated by '+')
exp_vars = (model_text.split(' ~ ')[1]).split(' + ')
model = logistic_model(fires, exp_vars, response_variable)

# Test collinearity of most promissing model
test_collinearity(fires, exp_vars)


# CONCLUSIONS
# 
# * Probably, the highly collinearity of features along all models cause they do not converge to a solution
#   due to problems of a complete or quasi-complete separation.
# * The odds rates along all models indicate that there's equal probability of forest fires with or without
#   rain, wind or any other used features. In some cases, the obtained index may diverge highly.
# * As indicated in PennState, STATS 501-Regression Methods course
#   (https://onlinecourses.science.psu.edu/stat501/node/391), other possible cause of pitfalls is the
#   exclussion of important predictors: "the potential cost of excluding important predictors can be a
#   completely meaningless model containing misleading associations."
