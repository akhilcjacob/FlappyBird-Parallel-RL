import pandas as pd
import os
import matplotlib.pyplot as plt

class plotting_service:
    def __init__(self):
        self.data = pd.DataFrame(columns=['Iteration', 'distance', 'score', 'states'])
        self.data.set_index('Iteration')
        if not (os.path.isdir('Plots')):
            os.makedirs('Plots')


    def add_row(self, row):
        self.data = self.data.append({'Iteration': int(row[0]), 'distance': int(row[1]), 'score': int(row[2]), 'states':row[3]}, ignore_index=True)
    def to_file(self):
        if len(self.data)>5:
            # self.data.plot(x='Iteration', fontsize=16, subplots=True)
            self.data[['Iteration', 'distance']].plot(x='Iteration', fontsize=16, subplots=True)
            plt.savefig('Plots/distance.png')
            self.data[['Iteration', 'score']].rolling(window=10).mean().plot(x='Iteration', fontsize=16, subplots=True)
            plt.savefig('Plots/score.png')
            self.data[['Iteration', 'states']].plot(x='Iteration', fontsize=16, subplots=True)
            plt.savefig('Plots/states.png')


            plt.close('all')

            if(len(self.data)%200==0):
                self.data.to_csv('Plots/data.csv')
