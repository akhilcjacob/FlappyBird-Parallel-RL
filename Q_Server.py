import json
import os
from multiprocessing import Queue, Lock
import time
from Plotting_Service import plotting_service
from multiprocessing import Manager
import multiprocessing


class Q_Table_Processor:
    def __init__(self, agents, file_save_rate=20):
        self.agents = agents
        self.total_n = sum(range(0, agents))
        self.master_q = {}
        self.output_folder_loc = "./models/"+str(agents)+"_agents/"
        self.output_file_loc = self.output_folder_loc+"master.json"
        # self.manager = Manager()
        self._import_q_table()
        self.best_run = multiprocessing.Value('i', 0)
        self.best_score = multiprocessing.Value('i', 0)
        self.update = multiprocessing.Value('i',0)
        self.file_save_rate = file_save_rate
        # self.q = []
        self.q = Queue()
        self.run_server_on = True
        self.lock = Lock()
        self.plotter = plotting_service(agents)
        self.hist = []
        self.max_states=0
        self.lock2 = Lock()


    def _import_q_table(self):
        if os.path.exists(self.output_file_loc):
            with open(self.output_file_loc) as json_file:
                print("Importing previous datafile")
                # self.master_q = self.manager.dict(json.load(json_file))
                self.master_q = json.load(json_file)
        else:
            print("Initializing new datafile")
            self.master_q = {'0_0_0': [0, 0]}
            self._export_q_table()

    def _export_q_table(self):
        if not os.path.exists(self.output_folder_loc):
            os.makedirs(self.output_folder_loc)
        f = open(self.output_file_loc, "w")
        f.write(json.dumps(self.master_q))
        f.close()

    def kill_server(self):
        self.run_server_on = False

    def run_server(self):
        try:
            while self.run_server_on:
                new_table, distance, score = self.q.get()
                # print(self.update.value,  'is the real update num')
                self.hist.append([new_table, distance, score])
                self.max_states =max([self.max_states,len(new_table),len(self.master_q)])
                self.plotter.add_row([self.update.value, distance, self.best_run.value, self.max_states, self.best_score.value])
                if self.update.value % self.file_save_rate:
                    self._export_q_table()
                    self.plotter.to_file()
               
               
                self.lock.acquire()
                new_tables = [h[0] for h in self.hist]
                distances = [h[1] for h in self.hist]
                scores = [h[2] for h in self.hist]
                # scores.append(0)
                print('===== Update ', self.update.value, '======' )
                print('Distances in pixels: ',distances)
                print('Scores:',scores)

                new_tables.append(self.master_q)
                distances.append(self.best_run.value)
                scores.append(self.best_score.value)

                weights = [d**4 for d in distances]
                # weights = [w*((s+1)**2) for w, s in zip(weights, scores)]
                weights = [float(i)/sum(weights) for i in weights]
                
                # self.master_q
                # final_table = self.master_q.copy()
                ## Only do weighting function portion when there is more than 1 agent
                if self.agents != 1:
                    for tab in range(len(new_tables)-1):
                        table = new_tables[tab]
                        for k,v in table.items():
                            if k in self.master_q:
                                self.master_q[k] = [
                                    int((weights[-1])*self.master_q[k][0] + (weights[tab])*v[0]),
                                    int((weights[-1])*self.master_q[k][1] + (weights[tab])*v[1])
                                ]
                            else:
                                self.master_q[k] = v
                        # else:
                        #     self.master_q[k] = [0,0]
                            # print(self.master_q[k])
                # self.master_q = self.master_q.copy()
                else:
                    self.master_q = new_table
                
                with self.update.get_lock():
                    self.update.value += 1
                self.lock.release()
                if distance > self.best_run.value:
                    with self.best_run.get_lock():
                        self.best_run.value = distance
                    with self.best_score.get_lock():
                        self.best_score.value = score
                # print('------')

                if len(self.hist) < self.agents:
                    continue
                # del self.hist[-1]
                min_dist = min(x[1] for x in self.hist)
                for x in range(len(self.hist)):
                    if self.hist[x][1] == min_dist:
                        del self.hist[x]
                        break

                # print(self.hist)


                # print(len(self.hist),self.agents)
                # if len(self.hist) > self.agents/2:
                #     # new_table, distance, score
                #     print("hserre")
                #     new_tables = [h[0] for h in self.hist]
                #     new_tables.append(self.master_q)
                #     distances = [h[1] for h in self.hist]
                #     distances.append(self.best_run)
                #     scores = [h[2] for h in self.hist]
                #     scores.append(self.best_score)
                #     weights = [d**4 for d in distances]

                #     # Normalize the weights
                   
                #     # self.master_q = self.merge_tables(self.master_q, new_table, distance, self.best_run)
                    
                #     if distance > self.best_run:
                #         self.best_run = max(distances)
                #         self.best_score = max(scores)
                #     self.hist = []

               
                # print(self.best_run)
                # self.update_line([self.update,score])

        except KeyboardInterrupt:
            print('Exiting Server')
            # for new_table, score in self.q.get():
                # print("recd new score")
                
                # self.master_q = self.merge_tables(self.master_q, new_table, score - self.best_run)
                # self.update += 1

                # if self.update % self.file_save_rate:
                #     self._export_q_table()
                # self.q = []

    def process_table(self, q_table, distance, score):
        update_num = 0
        self.lock.acquire()
        self.q.put([q_table, distance, score])
        update_num = self.update.value
        self.lock.release()
        return update_num

    def get_table(self, prev_update):
        # with self.lock2:
        while prev_update == self.update.value: 
            # print('this is the update', self.update.value)
            time.sleep(0.01)
        with self.lock:
            return self.master_q
        # self.master_q = self.merge_tables(self.master_q, q_table, score > self.best_run)






    def merge_tables(self, primary_q, secondary_q, dist,best_run):
        better = dist-best_run > 0
        weights = [1, 1]
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
