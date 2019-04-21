import pandas as pd
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class plotting_service:
    def __init__(self,agents):
        self.agents =agents
        self.folder = "Plots/"+str(agents)+"_agents/"
        self.data = pd.DataFrame(columns=['Iteration', 'distance', 'best_run', 'states', 'best_score'])
        self.data.set_index('Iteration')
        if not (os.path.isdir('Plots')):
            os.makedirs('Plots')
        if not os.path.isdir(self.folder):
            os.makedirs(self.folder)
        # if os.path.exists('Plots/data.csv'):
        #     self.data = pd.read_csv('Plots/data.csv')


    def add_row(self, row):
        self.data = self.data.append({'Iteration': int(row[0]), 'distance': int(row[1]), 'best_run': int(row[2]), 
        'states':row[3], 'best_score':row[4]}, ignore_index=True)
    def to_file(self):
        if len(self.data)>5:
            # self.data.plot(x='Iteration', fontsize=16, subplots=True)
            self.data[['Iteration', 'distance']].plot(x='Iteration', fontsize=16, subplots=True)
            plt.savefig(self.folder + 'distance.png')
            self.data[['Iteration', 'best_run']].plot(x='Iteration', fontsize=16, subplots=True)
            plt.savefig(self.folder + 'best_run.png')
            self.data[['Iteration', 'states']].plot(x='Iteration', fontsize=16, subplots=True)
            plt.savefig(self.folder + 'states.png')
            self.data[['Iteration', 'best_score']].plot(x='Iteration', fontsize=16, subplots=True)
            plt.savefig(self.folder + 'best_score.png')


            plt.close('all')

            if(len(self.data)%100==0):
                self.data.to_csv('Plots/data.csv')
