import json
import os
from multiprocessing import Queue, Lock
import time
from Plotting_Service import plotting_service
class Q_Table_Processor:
    def __init__(self, agents, file_save_rate=20):
        self.agents = agents
        self.total_n = sum(range(0, agents))
        self.master_q = {}
        self.output_file_loc = "./models/master.json"
        # self.manager = Manager()
        self._import_q_table()
        self.best_run = 0
        self.update = 0
        self.file_save_rate = file_save_rate
        # self.q = []
        self.q = Queue()
        self.run_server_on = True
        self.lock = Lock()
        self.plotter = plotting_service()

    def _import_q_table(self):
        if os.path.exists(self.output_file_loc):
            with open(self.output_file_loc) as json_file:
                print("Importing previous datafile")
                # self.master_q = self.manager.dict(json.load(json_file))
                self.master_q = json.load(json_file)
        else:
            print("Initializing new datafile")
            self.master_q = {'0_0_0': [0, 0]}

    def _export_q_table(self):
        f = open(self.output_file_loc, "w")
        f.write(json.dumps(self.master_q))
        f.close()

    def kill_server(self):
        self.run_server_on = False

    def run_server(self):
        try:
            while self.run_server_on:
                new_table, distance,score = self.q.get()
                self.lock.acquire()
                self.master_q = self.merge_tables(self.master_q, new_table, distance, self.best_run)
                self.update += 1
                self.plotter.add_row([self.update,distance,score,len(self.master_q)])
                if distance > self.best_run:
                    self.best_run = distance

                self.lock.release()

                if self.update % self.file_save_rate:
                    self._export_q_table()
                    self.plotter.to_file()
                # print(self.best_run)
                # self.update_line([self.update,score])

        except KeyboardInterrupt:
            print('Exiting Server')
            # for new_table, score in self.q.get():
                # print("recd new score")
                
                # self.master_q = self.merge_tables(self.master_q, new_table, score - self.best_run)
                # if score > self.best_run:
                #     self.best_run = score
                # self.update += 1

                # if self.update % self.file_save_rate:
                #     self._export_q_table()
                # self.q = []

    def process_table(self, q_table, distance, score):
        self.lock.acquire()
        self.q.put([q_table, distance, score])
        self.lock.release()

    def get_table(self):
        return self.master_q
        # self.master_q = self.merge_tables(self.master_q, q_table, score > self.best_run)






    def merge_tables(self, primary_q, secondary_q, dist,best_run):
        better = dist-best_run > 0
        weights = [0.8, 0.2]
        primary_q = primary_q.copy()
        if better:
            weights = weights[::-1]
            # weights[1] *=diff
        # combined_q = {'0_0_0':[0,0]}
        for key, value in secondary_q.items():
            if key in primary_q:
                for action in [0, 1]:
                    previous_mem = weights[0]*primary_q[key][action]*best_run
                    new_memory = weights[1]*secondary_q[key][action]*dist
                    # prim[key] = [0,0]
                    
                    # if previous_mem + new_memory > 0:
                    primary_q[key][action] = previous_mem+new_memory
            else:
                primary_q[key] = value
        return primary_q
