import pandas as pd

load_cells = [1,2,3]
results = pd.DataFrame() 
fake_brdg = [i*10 for i in range(70)]
i=4
results['1bdrg'] = [i + j for j in fake_brdg]
i = -3
results['2bdrg'] = [i + j for j in fake_brdg]
results['3brdg'] = [j+5*(-1)**j for j in fake_brdg]
    

    
