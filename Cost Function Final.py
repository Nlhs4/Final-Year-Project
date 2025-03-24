import math
import random
from random import randint
import numpy as np
import scipy.stats as st
import pandas as pd
import openpyxl

# General parameters , can be changed for geometric variation
topArea = 1050
topRad = math.sqrt(topArea / math.pi)
botArea = 610
botRad = math.sqrt(botArea / math.pi)
depth = 2
volume = (1/3) * math.pi * depth * (topRad**2 + botRad**2 + (topRad * botRad)) # ~1640
berm = 3


#Used for the varying geometric parameters
"""
topRad = 25
topArea = math.pi * topRad ** 2
botRad = 20.629
botArea = math.pi * botRad ** 2
depth = 1
volume = (1/3) * math.pi * depth * (topRad**2 + botRad**2 + (topRad * botRad)) # ~1640
print (volume)
berm = 3
"""

# Maintenance parameters
# Inspection
employRate = 20  # £ per hour
litterRate = 30  # Additional capital cost
fixedInspec = employRate * 7 + litterRate

# Grass cutting
grassRate = 0.35  # £ per m2
grassArea = (math.pi * (topRad + berm + 1.5)**2) - topArea
fixedGrass = grassRate * grassArea

# Meadow grass cutting
tractorHire = 400  # £ for one day
tractorSpeed = 4000  # m per hour
tractorWidth = 1.2  # m working width 
meadowArea = (math.pi * (topRad + berm + 1.5 + 10)**2) - grassArea
fixedMeadow = ((((meadowArea / tractorWidth) / tractorSpeed) + 2) * employRate) + tractorHire

# Plant control
controlRate = 25
fixedControl = controlRate * 3.5

# Aquatic grass cutting
aquaticRate = 0.5  # £ per m2
aquaticArea = ((1/2) * ((2 * math.pi * topRad) + (2 * math.pi * botRad) * depth)) + (math.pi * botRad**2)   # Assume whole area is viable for maintenance
fixedAquatic = aquaticRate * aquaticArea

# Replanting / reseeding
seedCost = 0.0635  # per m2  
seedSpeed = 1/240  # hours per m2
fixedSeedGrass = ((seedSpeed * grassArea) * employRate) + (seedCost * grassArea)
aquaticReplant = 3  # per m2
fixedSeedAquatic = aquaticArea * aquaticReplant
fixedSeed = fixedSeedGrass + fixedSeedAquatic

def controlRun():
    """Calculate the total yearly cost without additional probability of maintenance tasks."""
    costs = []
    for month in [fixedInspec + fixedGrass, 
                  fixedInspec + fixedGrass + fixedControl, 
                  fixedInspec + fixedGrass + fixedMeadow, 
                  fixedInspec + fixedGrass, 
                  fixedInspec + fixedGrass, 
                  fixedInspec + fixedGrass + fixedControl, 
                  fixedInspec + fixedGrass, 
                  fixedInspec + fixedGrass, 
                  fixedInspec + fixedGrass + fixedMeadow + fixedAquatic, 
                  fixedInspec + fixedGrass + fixedControl, 
                  fixedInspec + fixedGrass, 
                  fixedInspec + fixedGrass]:
        costs.append(round(month, 3))
    return sum(costs)

def monthly(a, b, c, d, e, f, g):
    """Calculate the total yearly cost with additional probability of maintenance tasks."""
    probInspec = random.choices([0, 1, 2, 3, 4], cum_weights=(a, b, c, d, 100), k=12)
    probControl = random.choices([0, 1], cum_weights=(90, 100), k=12)
    probSilt = random.choices([0, 1], cum_weights=(e, 100), k=12)
    probDrain = random.choices([0, 1], cum_weights=(f, 100), k=12)
    probErode = random.choices([0, 1], cum_weights=(g, 100), k=12)
    probDrought = random.choices([0, 1], cum_weights=(99.5, 100), k=12)

    costs = []
    for i in range(12):
        month_cost = (fixedInspec + fixedGrass + 
                      probInspec[i] * fixedInspec + 
                      probControl[i] * fixedControl + 
                      probSilt[i] * fixedSilt + 
                      probDrain[i] * fixedDrain + 
                      probErode[i] * fixedErode + 
                      probDrought[i] * fixedSeed)
        
        # Additional costs in specific months
        if i == 1 or i == 5 or i == 9: # February, June, and October (Plant Control)
            month_cost += fixedControl
        if i == 2:  # March (Meadow Cutting)
            month_cost += fixedMeadow
        if i == 8:  # September (Meadow & Aquatic)
            month_cost += fixedMeadow + fixedAquatic

        costs.append(round(month_cost, 3))
    
    return sum(costs)

def stats1(allCumul):
    """Calculate and print the 90% and 99% confidence interval for the total yearly cost using t distibution."""
    confidence_interval = st.t.interval(confidence=0.90, df=len(allCumul)-1, 
                                        loc=np.mean(allCumul), 
                                        scale=st.sem(allCumul))
    print("90% Confidence Interval of Total Costs Utilsing t Distribution:", confidence_interval)

    confidence_interval = st.t.interval(confidence=0.99, df=len(allCumul)-1, 
                                        loc=np.mean(allCumul), 
                                        scale=st.sem(allCumul))
    print("99% Confidence Interval of Total Costs Utilsing t Distribution:", confidence_interval)
    return

def stats2(allCumul):
    """Calculate and print the 90% and 99% confidence interval for the total yearly cost using the normal distibution."""
    confidence_interval = st.norm.interval(confidence=0.90, 
                                        loc=np.mean(allCumul), 
                                        scale=st.sem(allCumul))
    print("90% Confidence Interval of Total Costs Utilising Normal Distribution:", confidence_interval)

    confidence_interval = st.norm.interval(confidence=0.99, 
                                        loc=np.mean(allCumul), 
                                        scale=st.sem(allCumul))
    print("99% Confidence Interval of Total Costs Utilising Normal Distribution:", confidence_interval)
    return

def yearReturn():
    """Simulate the yearly cost over 50 years with 50 iterations."""
    allCumul = []
    allResults = []

    for j in range(50):   
        allYears = []
        allControl = []

        #print("\n")
        for i in range(50):
            # Randomly determine bespoke repair costs
            global fixedDrain, fixedSilt, fixedErode
            fixedDrain = randint(2000, 6000)
            fixedSilt = randint(750, 1500)
            fixedErode = randint(2000, 6000)

            control = controlRun()

            if i < 10:
                totalYear = monthly(80, 95, 98, 99, 99, 99.5, 99.5)
            elif i < 20:
                totalYear = monthly(60, 90, 95, 99, 99, 99.5, 99.5)
            elif i < 30:
                totalYear = monthly(40, 80, 95, 99, 98, 99, 99.5)
            elif i < 40:
                totalYear = monthly(20, 60, 80, 95, 98, 99, 99)
            else:
                totalYear = monthly(5, 40, 70, 90, 98, 99, 99)

            # Every 3 years, add silt removal cost
            if i > 0 and i % 3 == 0:
                totalYear += fixedSilt
                control += 750  # Fixed minimum for control

            # Every 10 years, add major repairs (Drainage + Erosion)
            if i > 0 and i % 10 == 0:
                totalYear += fixedDrain + fixedErode
                control += 2000 + 2000  # Fixed minimum for control

            control *= 1.02 ** i        # Apply 2% inflation rate
            totalYear *= 1.02 ** i      # Apply 2% inflation rate

            allYears.append(totalYear)
            #print(round(sum(allYears),3))

            allControl.append(control)
            #print(round(sum(allControl),3))

            allResults.append({
                'Year': i + 2026,  # Year of simulation
                'Cumulative Yearly Cost': round(sum(allYears), 3),
                'Control Cost': round(sum(allControl),3)
            })
        


        allCumul.append(round(sum(allYears), 3))

        # Create a DataFrame from the results
        df = pd.DataFrame(allResults)

        # Export the DataFrame to Excel
        df.to_excel('Attenuation_Pond_Costing.xlsx', index=False, engine='openpyxl')

    #print(allCumul)
    stats1(allCumul)
    stats2(allCumul)

# Run the simulation
yearReturn()
