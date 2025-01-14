import probounds.probounds as pb
from reactable import Reactable, embed_css

def create_probounds_table(raw_data, datatype):
    probounds_crosstab = pb.create_probounds_crosstab(raw_data, datatype=datatype)
    probounds_crosstab.columns = probounds_crosstab.columns.astype(str)
    embed_css()    
    return Reactable(probounds_crosstab)


import pandas as pd