# Author: Cameron F. Abrams <cfa22@drexel.edu>

import pandas as pd
import os
from argparse import Namespace
from . import resources

datafile_path=os.path.join(os.path.split(resources.__file__)[0],'data','properties_database.csv')


class PropertiesDatabase:
    def __init__(self):
        D=pd.read_csv(datafile_path,header=0,index_col=0)
        self.D=D.rename(columns={'Tfp (K)':'Tfp','Tb (K)':'Tb','Tc (K)':'Tc','Pc (bar)':'Pc'})
        unitlist=['','','g/mol','K','K','K','bar','m3/mol','','','','J/mol-K','J/mol-K2','J/mol-K3','J/mol-K4','J/mol','J/mol','','','','','','K','K','','']
        self.properties=list(self.D.columns)
        unitdict={k:v for k,v in zip(self.properties,unitlist)}
        self.U=Namespace(**unitdict)

    def get_compound(self,name):
        row=self.D[self.D['Name']==name]
        if not row.empty:
            d=row.to_dict('records')[0]
            return Namespace(**d)
        return None
        
Properties=PropertiesDatabase()
