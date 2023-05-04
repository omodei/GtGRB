'''
*****************************************************
* WELCOME TO THE GLAST GRB QUICK ANALYSIS FRAMEWORK *
* BASED ON PYTHON and the GLAST ScienceTools        *
* For Question and Troubleshooting:                 *
*       nicola.omodei@slac.stanford.edu             *
*****************************************************
Testing loading UnbinnedAnalysis.... OK
Loaded module scripts
'''
#################################################
GRBs={ 'GRB080825C':{'RA':233.9,
                     'DEC': -4.5,
                     'ERR': 7.5e-01,
                     'GRBT05': 1.22,
                     'GRBT90': 22.21,
                     'GRBT90_ERR': 0.23,                     
                     'GRBTRIGGERDATE': 241366429.1050,
                     'REDSHIFT': 0.000,
                     'LOCINSTRUMENT':'LAT'},
       'GRB080916C':{'RA':119.85,
                     'DEC': -56.6400,
                     'ERR': 1.00e-04,
                     'GRBT05': 1.28,
                     'GRBT90': 64.26,
                     'GRBT90_ERR': 0.8,                     
                     'GRBTRIGGERDATE': 243216766.6140,
                     'REDSHIFT': 4.350,
                     'LOCINSTRUMENT':'XRT'},       
       'GRB081006':{'RA':136.32,
                    'DEC': -62.05,
                    'ERR': 0.52,
                    'GRBT05': -0.26,
                    'GRBT90': 6.14,
                    'GRBT90_ERR': 0.923,                    
                    'GRBTRIGGERDATE': 244996175.1730,
                    'REDSHIFT': 0.000,
                    'LOCINSTRUMENT':'LAT'},
       'GRB081024B':{'RA':322.95,
                     'DEC': 21.20,
                     'ERR': 2.2e-01,
                     'GRBT05': -0.06,
                     'GRBT90': 0.58,
                     'GRBT90_ERR': 0.2639,                     
                     'GRBTRIGGERDATE': 246576161.8640,
                     'REDSHIFT': 0.000,
                     'LOCINSTRUMENT':'LAT'},
       #'GRB081207':{'RA':103.52,
       #             'DEC': 70.5341,
       #             'ERR': 5.17e-01,
       #             'GRBT05': 5.89,
       #             'GRBT90': 103.17,
       #             'GRBT90_ERR': 2.3472,
       #             'GRBTRIGGERDATE': 250359527.9360,
       #             'REDSHIFT': 0.000,
       #             'LOCINSTRUMENT':'LAT'},
       #'GRB081215':{'RA':125.00,
       #'DEC': 53.8000,
       #             'ERR': 1.00e+00,
       #             'GRBT05': 1.22,
       #             'GRBT90': 6.78,
       #             'GRBT90_ERR': 0.1431,       
       #             'GRBTRIGGERDATE': 251059717.8460,
       #             'REDSHIFT': 0.000,
       #             'LOCINSTRUMENT':'GBM'},
       #'GRB081224':{'RA':201.7,
       #             'DEC': 75.1,
       #             'ERR': 1.0,
       #             'GRBT05': 0.74,
       #             'GRBT90': 17.18,
       #             'GRBT90_ERR': 1.15,
       #             'GRBTRIGGERDATE': 251846276.4140,
       #             'REDSHIFT': 0.000,
       #             'LOCINSTRUMENT':'GBM'},
       'GRB090217':{'RA':204.83,
                    'DEC': -8.4200,
                    'ERR': 3.50e-01,
                    'GRBT05': 0.83,
                    'GRBT90': 34.11,
                    'GRBT90_ERR': 0.7241,                    
                    'GRBTRIGGERDATE': 256539404.5600,
                    'REDSHIFT': 0.000,
                    'LOCINSTRUMENT':'LAT'},
       'GRB090227B':{'RA':10.48,
                     'DEC': 29.2400,
                     'ERR': 1.00e+00,
                     'GRBT05': -0.06,
                     'GRBT90': 1.22,
                     'GRBT90_ERR': 1.03,                     
                     'GRBTRIGGERDATE': 257452263.4100,
                     'REDSHIFT': 0.000,
                     'LOCINSTRUMENT':'IPN'},
       
       'GRB090323':{'RA':190.71,
                    'DEC': 17.0533,
                    'ERR': 1.00e-04,
                    'GRBT05': 8.19,
                    'GRBT90': 143.36,
                    'GRBT90_ERR': 1.45,                    
                    'GRBTRIGGERDATE': 259459364.6300,
                    'REDSHIFT': 3.570,
                    'LOCINSTRUMENT':'XRT'},
       'GRB090328':{'RA':90.67,
                    'DEC': -41.7152,
                    'ERR': 2.00e-04,
                    'GRBT05': 4.35,
                    'GRBT90': 66.05,
                    'GRBT90_ERR': 1.8102,                    
                    'GRBTRIGGERDATE': 259925808.5100,
                    'REDSHIFT': 0.736,
                    'LOCINSTRUMENT':'XRT'},
       'GRB090510':{'RA':333.55,
                    'DEC': -26.5827,
                    'ERR': 4.00e-04,
                    'GRBT05': 0.48,#-0.05,
                    'GRBT90': 0.38,#0.91,
                    'GRBT90_ERR': 0.14,                    
                    'GRBTRIGGERDATE': 263607781.9710,
                    'REDSHIFT': 0.900,
                    'LOCINSTRUMENT':'XRT'},
       'GRB090531B':{'RA':252.07,
                     'DEC': -36.0150,
                     'ERR': 3.50e-02,
                     'GRBT05': -0.20,
                     'GRBT90': 0.96,
                     'GRBT90_ERR': 0.23,                     
                     'GRBTRIGGERDATE': 265487758.4900,
                     'REDSHIFT': 0.000,
                     'LOCINSTRUMENT':'XRT'},
       'GRB090626':{'RA':170.03,
                    'DEC': -33.4900,
                    'ERR': 2.20e-01,
                    'GRBT05': 1.54,
                    'GRBT90': 50.43,
                    'GRBT90_ERR': 2.828,
                    'GRBTRIGGERDATE': 267683530.8800,
                    'REDSHIFT': 0.000,
                    'LOCINSTRUMENT':'LAT'},
       #'GRB090703A':{'RA':6.86,
       #              'DEC':5.55,
       #              'ERR':1.26e-01,
       #              'GRBT05': -2.3,
       #              'GRBT90': 8.83,
       #              'GRBT90_ERR': 1.0,  
       #              'GRBTRIGGERDATE': 268300444.5000,
       #              'REDSHIFT': 0.0000,
       #              'LOCINSTRUMENT':'LAT'},
       'GRB090720B':{'RA':202.99,
                     'DEC':-54.21,
                     'ERR':0.33,#3.35e-01,
                     'GRBT05': -0.256,
                     'GRBT90': 6.69,
                     'GRBT90_ERR': 0.7,                     
                     'GRBTRIGGERDATE': 269802178.9051,
                     'REDSHIFT': 0.0000,
                     'LOCINSTRUMENT':'LAT'},        
       'GRB090902B':{'RA':264.94,
                     'DEC': 27.3242,
                     'ERR': 1.00e-03,
                     'GRBT05': 2.82,
                     'GRBT90': 22.16,
                     'GRBT90_ERR': 0.2862,                     
                     'GRBTRIGGERDATE': 273582310.3130,
                     'REDSHIFT': 1.822,
                     'LOCINSTRUMENT':'XRT'},       
       '090924625':{'RA':69.73,
                    'DEC':-65.02,
                    'ERR':7.10e+00,
                    'GRBT05': -0.128,
                    'GRBT90': 0.512,
                    'GRBT90_ERR': 0.181,                    
                    'GRBTRIGGERDATE': 275497196.0000,
                    'REDSHIFT': 0.0000,
                    'LOCINSTRUMENT':'GBM'},       
       'GRB090926A':{'RA':353.40,
                     'DEC': -66.3200,
                     'ERR': 1.00e-02,
                     'GRBT05': 2.18,
                     'GRBT90': 15.94,
                     'GRBT90_ERR': 0.2862,                    
                     'GRBTRIGGERDATE': 275631628.9900,
                     'REDSHIFT': 2.106,
                     'LOCINSTRUMENT':'XRT'},
       'GRB091003':{'RA':251.52,
                    'DEC': 36.6252,
                    'ERR': 5.00e-04,
                    'GRBT05': 0.83,
                    'GRBT90': 21.06,
                    'GRBT90_ERR': 0.362,                    
                    'GRBTRIGGERDATE': 276237347.5850,
                    'REDSHIFT': 0.897,
                    'LOCINSTRUMENT':'XRT'},
       'GRB091031':{'RA':71.49,
                    'DEC': -57.6500,
                    'ERR': 2.35e-01,
                    'GRBT05': 1.41,
                    'GRBT90': 35.33,
                    'GRBT90_ERR': 0.46,                    
                    'GRBTRIGGERDATE': 278683230.8500,
                    'REDSHIFT': 0.000,
                    'LOCINSTRUMENT':'LAT'},
       'GRB091208B':{'RA':29.392,
                     'DEC': 16.8899,
                     'ERR': 0.0005,
                     'GRBT05': 0.26,
                     'GRBT90': 14.78,
                     'GRBT90_ERR': 1.54,                    
                     'GRBTRIGGERDATE': 281958599.9560,
                     'REDSHIFT': 1.063,
                     'LOCINSTRUMENT':'XRT'},       
       'GRB100116A':{'RA':305.01,
                     'DEC': 14.4300,
                     'ERR': 1.66e-01,
                     'GRBT05': 84.0,#0.58,
                     'GRBT90': 18.6,#103.11,
                     'GRBT90_ERR': 1.5,                     
                     'GRBTRIGGERDATE': 285370262.2400,
                     'REDSHIFT': 0.000,
                     'LOCINSTRUMENT':'LAT'},
       'GRB100225A':{'RA':310.30,
                     'DEC': -59.4000,
                     'ERR': 9.00e-01,
                     'GRBT05': -0.26,
                     'GRBT90': 12.74,
                     'GRBT90_ERR': 3.051,                     
                     'GRBTRIGGERDATE': 288758733.1470,
                     'REDSHIFT': 0.000,
                     'LOCINSTRUMENT':'GBM'},
       'GRB100325A':{'RA':330.24,
                     'DEC': -26.45,
                     'ERR': 6.00e-01,
                     'GRBT05': -0.38,
                     'GRBT90': 6.72,
                     'GRBT90_ERR': 1.6191,                     
                     'GRBTRIGGERDATE': 291191770.0200,
                     'REDSHIFT': 0.000,
                     'LOCINSTRUMENT':'LAT'},
       'GRB100414A':{'RA':192.11,
                     'DEC': 8.6930,
                     'ERR': 5.00e-04,
                     'GRBT05': 1.86,
                     'GRBT90': 28.35,
                     'GRBT90_ERR': 2.073,
                     'GRBTRIGGERDATE': 292904423.9900,
                     'REDSHIFT': 1.368,
                     'LOCINSTRUMENT':'XRT'},
       'GRB100620A':{'RA':86.90,
                     'DEC':-50.91,
                     'ERR':7.10e-01,
                     'GRBT05': 0.13,
                     'GRBT90': 41.1,
                     'GRBT90_ERR': 0.7,
                     'GRBTRIGGERDATE': 298695091.1000,
                     'REDSHIFT': 0.0000,
                     'LOCINSTRUMENT':'LAT'}, 
       #'GRB100707A':{'RA':358.02,
       #'DEC': -8.6580,
       #              'ERR': 4.00e-01,
       #              'GRBT05': 1.09,
       #              'GRBT90': 82.88,
       #              'GRBT90_ERR': 1.2,                     
       #              'GRBTRIGGERDATE': 300156400.9900,
       #              'REDSHIFT': 0.000,
       #              'LOCINSTRUMENT':'IPN'},
       'GRB100724B':{'RA':119.59,
                     'DEC': 75.86,
                     'ERR': 8.80e-01,
                     'GRBT05': 8.96,
                     'GRBT90': 118.59,
                     'GRBT90_ERR':5.25,                     
                     'GRBTRIGGERDATE': 301624927.9800,
                     'REDSHIFT': 0.000,
                     'LOCINSTRUMENT':'LAT'},
       'GRB100728A':{'RA':88.75839,
                     'DEC': -15.25531,
                     'ERR': 1.00e-04,
                     'GRBT05': 14.85,
                     'GRBT90': 177.73,
                     'GRBT90_ERR':0.9,                     
                     'GRBTRIGGERDATE': 301976252.6100,
                     'REDSHIFT': 0.000,
                     'LOCINSTRUMENT':'XRT'},
       'GRB100826A':{'RA':279.593, #286.43,
                     'DEC': -22.128, #-32.6300,
                     'ERR': 1.2,#3.85e+00,
                     'GRBT05': 8.19,
                     'GRBT90': 118.78,
                     'GRBT90_ERR': 10.443,                     
                     'GRBTRIGGERDATE': 304556304.8980,
                     'REDSHIFT': 0.000,
                     'LOCINSTRUMENT':'IPN'}, #GBM
       'GRB101014A':{'RA':27.206, #26.94, # 27.206,-50.819 THIS IS GTFINDSRC!!!
                     'DEC': -50.819, #-51.0700,
                     'ERR': 0.3, #1.00e+00,
                     'GRBT05': 1.41,
                     'GRBT90': 450.81,
                     'GRBT90_ERR': 1.41,                     
                     'GRBTRIGGERDATE': 308722314.6200,
                     'REDSHIFT': 0.000,
                     'LOCINSTRUMENT':'LATFS'}, #GBM
       'GRB101123A':{'RA':135.16,
                     'DEC': 1.9100,
                     'ERR': 1.00e+00,
                     'GRBT05': 40.26,
                     'GRBT90': 110.59,#145.41,
                     'GRBT90_ERR': 0.73,                     
                     'GRBTRIGGERDATE': 312245496.9730,
                     'REDSHIFT': 0.000,
                     'LOCINSTRUMENT':'GBM'},
       #'GRB101204':{'RA':191.75,
       #             'DEC':60.10,
       #             'ERR':7.23e-01,
       #             'GRBT05': -0.064,
       #             'GRBT90': 0.128000,
       #             'GRBT90_ERR': 0.0905097,
       #             'GRBTRIGGERDATE': 313143260.6000,
       #             'REDSHIFT': 0.0000,
       #             'LOCINSTRUMENT':'LAT'},       
       'GRB110120A':{'RA':61.5,
                     'DEC': -12.0,
                     'ERR': 3.60e-01,
                     'GRBT05': 0.26,
                     'GRBT90': 27.58,
                     'GRBT90_ERR': 9.79,                     
                     'GRBTRIGGERDATE': 317231981.2300,
                     'REDSHIFT': 0.000,
                     'LOCINSTRUMENT':'LAT'},
       'GRB110328B':{'RA':117.65,
                     'DEC': 43.1,
                     'ERR': 1.7e+00,
                     'GRBT05': 2.05,
                     'GRBT90': 124.93,
                     'GRBT90_ERR': 20.5060,                     
                     'GRBTRIGGERDATE': 323008161.1940,
                     'REDSHIFT': 0.000,
                     'LOCINSTRUMENT':'LAT'},
       'GRB110428A':{'RA':5.59,
                     'DEC': 64.8492,
                     'ERR': 1.00e-05,
                     'GRBT05': 2.69,
                     'GRBT90': 8.32,
                     'GRBT90_ERR': 0.18,                     
                     'GRBTRIGGERDATE': 325675112.4100,
                     'REDSHIFT': 0.000,
                     'LOCINSTRUMENT':'XRT'},
       'GRB110529A':{'RA':118.33,
                     'DEC': 67.9100,
                     'ERR': 1.50e+00,
                     'GRBT05': 0.00,
                     'GRBT90': 0.41,
                     'GRBT90_ERR': 0.028,                     
                     'GRBTRIGGERDATE': 328322924.8720,
                     'REDSHIFT': 0.000,
                     'LOCINSTRUMENT':'GBM'},
       'GRB110625A':{'RA':286.73,
                     'DEC': 6.7553,
                     'ERR': 1.00e-04,
                     'GRBT05': 3.07,
                     'GRBT90': 30.72,
                     'GRBT90_ERR': 1.4,                     
                     'GRBTRIGGERDATE': 330728900.2360,
                     'REDSHIFT': 0.000,
                     'LOCINSTRUMENT':'XRT'},
       'GRB110709A':{'RA':238.895,
                     'DEC':40.918,
                     'ERR': 0.0003,
                     'GRBT05': 1.1,
                     'GRBT90': 43.2,
                     'GRBT90_ERR': 0.4,
                     'GRBTRIGGERDATE': 331917869.4000,
                     'REDSHIFT': 0.0000,
                     'LOCINSTRUMENT':'XRT'},       
       'GRB110721A':{'RA':333.2,
                     'DEC': -38.5,
                     'ERR': 0.2,
                     'GRBT05': 0.45,
                     'GRBT90': 24.90,
                     'GRBT90_ERR':0.65,                     
                     'GRBTRIGGERDATE': 332916465.7600,
                     'REDSHIFT': 0.000,
                     'LOCINSTRUMENT':'IPN'},
       'GRB110731A':{'RA':280.50,
                     'DEC': -28.5372,
                     'ERR': 1.00e-04,
                     'GRBT05': 0.26,
                     'GRBT90': 7.56,
                     'GRBT90_ERR': 0.3,                     
                     'GRBTRIGGERDATE': 333803371.9540,
                     'REDSHIFT': 2.830,
                     'LOCINSTRUMENT':'XRT'},
       }




''' OLD POSITIONS 
GRBs={'GRB080825C': {'DEC': -4.95,
                     'ERR': 0.87,
                     'GRBT05': 1.216,
                     'GRBT90': 20.9923,
                     'GRBT90_ERR': 0.23,
                     'GRBTRIGGERDATE': 241366429.1050,
                     'RA': 234.65,
                     'REDSHIFT': 0.0,
                     'LOCINSTRUMENT':'LAT'},
      
      'GRB080916C': {'DEC': -56.64,
                     'ERR': 0.0001,
                     'GRBT05': 1.28,
                     'GRBT90': 62.98,
                     'GRBT90_ERR': 0.8,
                     'GRBTRIGGERDATE': 243216766.6140,
                     'RA': 119.85,
                     'REDSHIFT': 4.35,
                     'LOCINSTRUMENT':'XRT'},
      
      'GRB081006':  {'DEC': -61.9,
                     'ERR': 0.46,
                     'GRBT05': -0.256,
                     'GRBT90': 6.4,
                     'GRBT90_ERR': 0.923,
                     'GRBTRIGGERDATE': 244996175.1730,
                     'RA': 136.21,
                     'REDSHIFT': 0.0,
                     'LOCINSTRUMENT':'LAT'},
      
      'GRB081024B': {'DEC': 21.25,
                     'ERR': 0.22,
                     'GRBT05': -0.064,
                     'GRBT90': 0.64,
                     'GRBT90_ERR': 0.2639,
                     'GRBTRIGGERDATE': 246576161.8640,
                     'RA': 322.9,
                     'REDSHIFT': 0.0,
                     'LOCINSTRUMENT':'LAT'},
      'GRB081207':  {'DEC': 70.5,
                     'ERR': 1.2,
                     'GRBT05': 5.8880999999999997,
                     'GRBT90': 97.281499999999994,
                     'GRBT90_ERR': 2.3472,
                     'GRBTRIGGERDATE': 250359527.9364,
                     'RA': 112.4,
                     'REDSHIFT': 0,'LOCINSTRUMENT':'GBM'},
      'GRB081215':  {'DEC': 53.8, # THIS IS THE GBM LOCALIZATION
                     'ERR': 1.0,
                     'GRBT05': 1.216,
                     'GRBT90': 5.5681,
                     'GRBT90_ERR': 0.1431,
                     'GRBTRIGGERDATE': 251059717.8462,
                     'RA': 125.0, # THIS IS THE CENTER OF THE IPN TRIANGULATION
                     'REDSHIFT': 0,'LOCINSTRUMENT':'GBM'},
      'GRB081224':  {'DEC': 73.3, #72.9, # THIS IS A SLIGHTLY HIGH TS
                     'ERR': 1.0, #0.62,
                     'GRBT05': 0.736,
                     'GRBT90': 16.4482,
                     'GRBT90_ERR': 1.1591,
                     'GRBTRIGGERDATE': 251846276.4139,
                     'RA':  206.20, #201.8,
                     'REDSHIFT': 0.0,'LOCINSTRUMENT':'GBM'},
      'GRB090217':  {'DEC': -8.47, # LAT
                     'ERR': 0.360,
                     'GRBT05': 0.832,
                     'GRBT90': 33.2805,
                     'GRBT90_ERR': 0.7241,
                     'GRBTRIGGERDATE': 256539404.56,
                     'RA': 204.68,
                     'REDSHIFT': 0.0,'LOCINSTRUMENT':'LAT'},
      #'GRB090227': {   'DEC': -43.1, # GBM
      #              'ERR': 1.2,
      #              'GRBT05': 0.0035000000000000001,
      #              'GRBT90': 16.188700000000001,
      #              'GRBT90_ERR': 0.83069999999999999,
      #              'GRBTRIGGERDATE': 257412359.00310001,
      #              'RA': 3.2,
      #              'REDSHIFT': 0,'LOCINSTRUMENT':'GBM'},
      'GRB090227B': {'DEC': 29.24, # NEW LOCALIZATION FROM THE TSMAP
                     'ERR': 1.0,
                     'GRBT05': -0.064,
                     'GRBT90': 1.28,
                     'GRBT90_ERR': 1.03,
                     'GRBTRIGGERDATE': 257452263.41,
                     'RA': 10.48,
                     'REDSHIFT': 0.0,'LOCINSTRUMENT':'LAT'},
      'GRB090323':  {'DEC': 17.0533,
                     'ERR': 0.0001,
                     'GRBT05': 8.192,
                     'GRBT90': 135.17,
                     'GRBT90_ERR': 1.45,
                     'GRBTRIGGERDATE': 259459364.63,
                     'RA': 190.710,
                     'REDSHIFT': 3.57,'LOCINSTRUMENT':'XRT'},
      'GRB090328':  {'DEC': -41.7152,'LOCINSTRUMENT':'XRT',
                     'ERR': 0.0002,
                     'GRBT05': 4.352,
                     'GRBT90': 61.697,
                     'GRBT90_ERR': 1.8102,
                     'GRBTRIGGERDATE': 259925808.5100,
                     'RA': 90.67,
                     'REDSHIFT': 0.736},
      'GRB090510':  {'DEC': -26.5827,'LOCINSTRUMENT':'XRT',
                     'ERR': 0.0004,
                     'GRBT05': -0.048,
                     'GRBT90': 0.96,
                     'GRBT90_ERR': 0.14,
                     'GRBTRIGGERDATE': 263607781.97099999,
                     'RA': 333.55,
                     'REDSHIFT': 0.90},
      
      'GRB090531B': {'DEC': -36.015,'LOCINSTRUMENT':'XRT',
                     'ERR': 0.035,
                     'GRBT05': -0.2,
                     'GRBT90': 1.16,
                     'GRBT90_ERR': 0.23,
                     'GRBTRIGGERDATE': 265487758.4900,
                     'RA': 252.07,
                     'REDSHIFT': 0.0},
      
      'GRB090626':  {'DEC': -33.34,'LOCINSTRUMENT':'LAT',
                     'ERR': 0.23,
                     'GRBT05': 1.536,
                     'GRBT90': 48.897,
                     'GRBT90_ERR': 2.828,
                     'GRBTRIGGERDATE': 267683530.88,
                     'RA': 169.97,
                     'REDSHIFT': 0.0},
      
      'GRB090902B': {'DEC': 27.3242,'LOCINSTRUMENT':'XRT',
                     'ERR': 0.001,
                     'GRBT05': 2.816,
                     'GRBT90': 19.34,
                     'GRBT90_ERR': 0.2862,
                     'GRBTRIGGERDATE': 273582310.3130,
                     'RA': 264.94,
                     'REDSHIFT': 1.822},
      'GRB090926':  {'DEC': -66.32,'LOCINSTRUMENT':'XRT',
                     'ERR': 0.01,
                     'GRBT05': 2.176,
                     'GRBT90': 13.7602,
                     'GRBT90_ERR': 0.2862,
                     'GRBTRIGGERDATE': 275631628.9900,
                     'RA': 353.40,
                     'REDSHIFT': 2.106},
      'GRB091003': {'DEC': 36.6252,'LOCINSTRUMENT':'XRT',
                    'ERR': 0.0005,
                    'GRBT05': 0.832,
                    'GRBT90': 20.224,
                    'GRBT90_ERR': 0.362,
                    'GRBTRIGGERDATE': 276237347.5845,
                    'RA': 251.52,
                    'REDSHIFT': 0.897},
      'GRB091031': {'DEC': -57.7,'LOCINSTRUMENT':'LAT',
                    'ERR': 0.24,
                    'GRBT05': 1.41,
                    'GRBT90': 33.92,
                    'GRBT90_ERR': 0.46,
                    'GRBTRIGGERDATE': 278683230.8500,
                    'RA': 71.4,
                    'REDSHIFT': 0.0},
      'GRB100116A': {'DEC': 14.48,'LOCINSTRUMENT':'LAT',
                     'ERR': 0.17,
                     'GRBT05': 0.58,
                     'GRBT90': 102.53,
                     'GRBT90_ERR': 1.5,
                     'GRBTRIGGERDATE': 285370262.2400,
                     'RA': 304.96,
                     'REDSHIFT': 0.0},
      'GRB100225A':{'DEC': -59.4,'LOCINSTRUMENT':'LAT',
                    'ERR': 0.9,
                    'GRBT05': -0.256,
                    'GRBT90': 12.9922,
                    'GRBT90_ERR': 3.051,
                    'GRBTRIGGERDATE': 288758733.1468,
                    'RA': 310.3,
                    'REDSHIFT': 0.0},
      'GRB100325A': {'DEC': -26.4,'LOCINSTRUMENT':'LAT',
                     'ERR': 0.6,
                     'GRBT05': -0.384,
                     'GRBT90': 7.104,
                     'GRBT90_ERR': 1.6191,
                     'GRBTRIGGERDATE': 291191770.01999998,
                     'RA': 330.18,
                     'REDSHIFT': 0.0},
      'GRB100414A': {'DEC': 8.693,'LOCINSTRUMENT':'XRT',
                     'ERR': 0.0005,
                     'GRBT05': 1.856,
                     'GRBT90': 26.4965,
                     'GRBT90_ERR': 2.073,
                     'GRBTRIGGERDATE': 292904423.9900,
                     'RA':  192.112,
                     'REDSHIFT': 1.368},
      'GRB100707A': {'DEC': -8.658,'LOCINSTRUMENT':'IPN',
                     'ERR': 0.4,
                     'GRBT05': 1.088,
                     'GRBT90': 81.79,
                     'GRBT90_ERR': 1.2,
                     'GRBTRIGGERDATE': 300156400.9900,
                     'RA': 358.019, #350.4,
                     'REDSHIFT': 0.0},
      
      'GRB100724B': {'DEC': 76.7,'LOCINSTRUMENT':'LAT',
                     'ERR': 0.86,
                     'GRBT05': 8.96,
                     'GRBT90': 109.63,
                     'GRBT90_ERR':5.25,
                     'GRBTRIGGERDATE': 301624927.9800,
                     'RA': 120.1,
                     'REDSHIFT': 0.0},
      
      'GRB100728A': {'DEC': -15.2554,'LOCINSTRUMENT':'XRT',
                     'ERR': 0.0001,
                     'GRBT05': 14.8482,
                     'GRBT90': 162.882,
                     'GRBT90_ERR':0.9,
                     'GRBTRIGGERDATE': 301976252.6100,
                     'RA': 88.761,
                     'REDSHIFT': 0.0},
      'GRB100826A': {'DEC': -32.63,'LOCINSTRUMENT':'GBM',
                     'ERR': 3.85,
                     'GRBT05': 8.1921,
                     'GRBT90': 110.59,
                     'GRBT90_ERR': 10.443,
                     'GRBTRIGGERDATE': 304556304.89840001,
                     'RA': 286.43,
                     'REDSHIFT': 0},
      'GRB101014A': {'DEC': -51.07,'LOCINSTRUMENT':'GBM', #GBM
                     'ERR': 1.0,
                     'GRBT05': 1.41,
                     'GRBT90': 449.4,
                     'GRBT90_ERR': 1.41,                      
                     'GRBTRIGGERDATE': 308722314.62,
                     'RA': 26.94,
                     'REDSHIFT': 0.0},
      'GRB101123A': {'DEC': 1.91,'LOCINSTRUMENT':'GBM',
                     'ERR': 1.0,
                     'GRBT05': 40.2567,
                     'GRBT90': 105.154,
                     'GRBT90_ERR': 0.73,
                     'GRBTRIGGERDATE': 312245496.97349,
                     'RA': 135.16,
                     'REDSHIFT': 0.0},
      'GRB110120A': {'DEC': -11.950,'LOCINSTRUMENT':'LAT', # LAT
                     'ERR': 0.3,
                     'GRBT05': 0.256,
                     'GRBT90': 27.3285,
                     'GRBT90_ERR': 9.79,
                     'GRBTRIGGERDATE': 317231981.2300,
                     'RA': 61.447,
                     'REDSHIFT': 0.0},
      
      'GRB110328B': {'DEC': 43.2,'LOCINSTRUMENT':'LAT',
                     'ERR': 1.7,
                     'GRBT05': 2.04801,
                     'GRBT90': 122.882,
                     'GRBT90_ERR': 20.5060,
                     'GRBTRIGGERDATE': 323008161.194,
                     'RA': 117.6,
                     'REDSHIFT': 0.0},
      
      'GRB110428A': {'DEC': 64.849194,
                     'LOCINSTRUMENT':'XRT',
                     'ERR': 0.00001,
                     'GRBT05': 2.688,
                     'GRBT90': 5.63208,
                     'GRBT90_ERR': 0.18,
                     'GRBTRIGGERDATE': 325675112.41,
                     'RA': 5.592583,
                     'REDSHIFT': 0.0},
      
      'GRB110529A': {'DEC': 67.91,
                     'LOCINSTRUMENT':'LAT',
                     'ERR': 1.5,
                     'GRBT05': 0.0,
                     'GRBT90': 0.41,
                     'GRBT90_ERR': 0.028,
                     'GRBTRIGGERDATE': 328322924.8715080,
                     'RA': 118.3300,
                     'REDSHIFT': 0.0},
      
      'GRB110625A': {'DEC': 6.7553,
                     'ERR': 0.0001,
                     'LOCINSTRUMENT':'XRT',
                     'GRBT05': 3.07202,
                     'GRBT90': 27.6485,
                     'GRBT90_ERR': 1.4,
                     'GRBTRIGGERDATE': 330728900.236,
                     'RA': 286.7327,
                     'REDSHIFT': 0.0},
      
      'GRB110721A': {'DEC': -38.593417,
                     'LOCINSTRUMENT':'XRT',
                     'ERR': 0.0001,
                     'GRBT05': 0.45,
                     'GRBT90': 24.45,
                     'GRBT90_ERR':0.65,
                     'GRBTRIGGERDATE': 332916465.76,
                     'RA': 333.659458,
                     'REDSHIFT':0.0},
      
      'GRB110731A': {'DEC': -28.537167,
                     'ERR': 0.0001,
                     'GRBT05': 0.26,
                     'GRBT90': 7.3,
                     'GRBT90_ERR': 0.3,                  
                     'GRBTRIGGERDATE': 333803371.9540,
                     'LOCINSTRUMENT':'XRT',
                     'RA': 280.50413,
                     'REDSHIFT': 2.83}
      }'''
from ARR import ARRs
from BGO_Bright_GRBs_Betta import BGOs
from ASDC import ASDCs

GRBs.update(ASDCs)
GRBs.update(BGOs)
GRBs.update(ARRs)

#################################################
