import pandas as pd
from itertools import chain
import random


class Agent(object):
    def __init__(self, agent_name, base_model=None):
        self.q_table_loc = "./models/"
        self._verify_dir()
        self.agent_name = agent_name
        self.learning_rate = 0.7
        self.reward = {0: 1, 1: -1000}
        self.csv_loc = self.q_table_loc + agent_name + ".csv"
        self.move_list = []
        self.last_action = 0
        self.last_state = '420_240_0'
        self.count = 0
        if base_model is None:
            print("Attempting to import from file")
            self._import_q_table()
        else:
            print("Recieved data from constructor")
            self.base_model = base_model
        if self.base_model is None:
            print("Starting with an empty data set")
            self._generate_model()
            self._export_q_table()

    def _verify_dir(self):
        import os

        if not (os.path.isdir(self.q_table_loc)):
            os.makedirs(self.q_table_loc)

    def _import_q_table(self):
        import os

        if os.path.exists(self.csv_loc):
            self.base_model = pd.read_csv(self.csv_loc)

    def _export_q_table(self):
        # print(self.base_model)
        # if self.base_model != None:
        self.base_model.to_csv(self.csv_loc)

    def update_model(self, new_model):
        self.base_model = new_model

    def action(self, x_distance, y_distance, velocity):
        if x_distance < 140:
            x_distance = int(x_distance) - (int(x_distance) % 10)
        else:
            x_distance = int(x_distance) - (int(x_distance) % 70)

        if y_distance < 180:
            y_distance = int(y_distance) - (int(y_distance) % 10)
        else:
            y_distance = int(y_distance) - (int(y_distance) % 60)
        ident = [str(int(x_distance)), str(int(y_distance)), str(velocity)]
        state = "_".join(ident)
        # print(ident)
        self.move_list.append((self.last_state, self.last_action, state))
        self.last_state = state  # Update the last_state with the current state
        if len(self.base_model[self.base_model.id == state]) < 1:
            # print('appending')
            columns = [{"id": state, "x": x_distance, "y": y_distance, "v": velocity, "a0": 0, "a1": 0}]
            # columns = [{"id":'0_1_2', "x":0, "y":0, "v":0, "a0":0, "a1":0}]
            print(columns)
            self.base_model = self.base_model.append(columns)
            # self.last_action = int(random.randint(0, 1)>0.75)
            # self.last_action = 0
            # print(self.base_model[self.base_model.id == state])
            # return self.last_action
            # return 0
        if self.base_model[self.base_model.id == state].a0.values.tolist()[0] >= self.base_model[self.base_model.id == state].a1.values.tolist()[0]:
            # print("This is the better option")
            self.last_action = 0
            return 0
        else:
            self.last_action = 1
            return 1

    def update_scores(self, dump_base_model=False):
        history = list(reversed(self.move_list))
        hit_upper_pipe = float(history[0][2].split('_')[1]) > 120

        reward = 1

        for exp in history:
            # print("working with hist")
            state = exp[0]
            act = exp[1]
            res_state = exp[2]

            # Select reward
            if reward == 1 or reward == 2:
                cur_reward = self.reward[1]
            elif hit_upper_pipe and act:
                cur_reward = self.reward[1]
                hit_upper_pipe = False
            else:
                cur_reward = self.reward[0]
            # Update
            # print(res_state)
            row = self.base_model[self.base_model.id == res_state]
            # print(row[['a0', 'a1']].values.tolist())
            max_action = 0.7*max(row[['a0', 'a1']].values.tolist()[0])
            current_action = (self.base_model[self.base_model.id == state]['a'+str(act)])
            value = (1-self.learning_rate) * current_action + self.learning_rate * (cur_reward + max_action)
            # print(act)
            if act:
                self.base_model.loc[self.base_model.id == state, 'a1'] = value
            else:
                self.base_model.loc[self.base_model.id == state, 'a0'] = value
            # print(self.base_model[self.base_model.id == state])
            reward += 1
        self.count += 1  # increase game count
        # if dump_base_model:
        #     self._export_q_table()  # Dump q values (if game count % DUMPING_N == 0)
        self.move_list = []  # clear history after updating strategies

    def _generate_model(self):
        self.base_model = pd.DataFrame()
        print("Intitializing an emtpy model")
        output = []
        for x in chain(list(range(-40, 140, 10)), list(range(140, 421, 70))):
            for y in chain(list(range(-300, 180, 10)), list(range(180, 421, 60))):
                for v in range(-10, 11):
                    ident = [str(x), str(y), str(v)]
                    output.append(["_".join(ident), x, y, v, 0, 0])

        # ID = (x_y_v), x distance to next pipe,
        # y dist to next pipe, v = current vel, reward total for action =0, reward total for action =1
        self.base_model = pd.DataFrame(
            columns=["id", "x", "y", "v", "a0", "a1"], data=output
        )
