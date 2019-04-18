import json
import os

import random


class Agent(object):
    def __init__(self, agent_name, b_model=None):
        self.q_table_loc = "./models/"
        self._verify_dir()
        self.last_state = '0_0_0'
        self.base_model = {self.last_state: [0, 0]}
        self.agent_name = agent_name
        self.learning_rate = 0.7
        self.reward = {0: 1, 1: -1000}
        self.output_file_loc = self.q_table_loc + agent_name + ".json"
        self.move_list = []
        self.last_action = 0
        self.count = 0
        self.epsilon = 0.001
        
        if b_model != None:
            print("Recieved data from constructor")
            self.base_model = b_model
        elif len(self.base_model) == 1:
            self._import_q_table()
        else:
            print("Starting with an empty data set")

    def _verify_dir(self):
        
        if not (os.path.isdir(self.q_table_loc)):
            print("Models Directory Doesn't exist...\n Creating Models/ Directory...")
            os.makedirs(self.q_table_loc)
        else: print("Models Directory Exists")

    def get_table(self):
        return self.base_model

    def _import_q_table(self):
        if os.path.exists(self.output_file_loc):
            with open(self.output_file_loc) as json_file:
                self.base_model = json.load(json_file)
                print("Succesfully to imported from file")


    def _export_q_table(self):
        # print(self.base_model)
        # if self.base_model != None:
        f = open(self.output_file_loc, "w")
        f.write(json.dumps(self.base_model))
        f.close()

    def set_table(self, table):
        self.base_model = table
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
        self.move_list.append((self.last_state, self.last_action, state))
        self.last_state = state

        # Check to see if this state exists
        if state not in self.base_model:
            # self.base_model = self.base_model.append(columns)
            self.base_model[state] = [0, 0]
            # print('appending')
            # columns = [{"id": state, "x": x_distance, "y": y_distance, "v": velocity, "a0": 0, "a1": 0}]
            # columns = [{"id":'0_1_2', "x":0, "y":0, "v":0, "a0":0, "a1":0}]
            # print(columns)
            # self.last_action = int(random.randint(0, 1)>0.75)
            # self.last_action = 0
            # print(self.base_model[self.base_model.id == state])
            # return self.last_action
            # return 0
        if random.uniform(0,1)<self.epsilon:
            self.last_action = int(random.uniform(0, 1)<0.5)
            # print("Picking a random action")
        elif self.base_model[state][0] >= self.base_model[state][1]:
            # if self.base_model[self.base_model.id == state].a0.values.tolist()[0] >= self.base_model[self.base_model.id == state].a1.values.tolist()[0]:
            # print("This is the better option")
            self.last_action = 0
        else:
            self.last_action = 1
        return self.last_action

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
           
            if state not in self.base_model:
                self.base_model[state] = [0, 0]

            # print('appending')
            prev_rew = (1-self.learning_rate) * (self.base_model[state][act])
            new_rew = self.learning_rate * (cur_reward + 0.7*max(self.base_model[res_state]))
            self.base_model[state][act] = new_rew+prev_rew
            reward += 1
        self.count += 1  # increase game count
        # if dump_base_model:
        #     self._export_q_table()  # Dump q values (if game count % DUMPING_N == 0)
        self.move_list = []  # clear history after updating strategies

    def _generate_model(self):
        # self.base_model = pd.DataFrame()
        print("Intitializing an emtpy model")
        # output = []
        # columns = [{"id": '0_0_0', "x": 0, "y": 0, "v": 0, "a0": 0, "a1": 0}]

        # ID = (x_y_v), x distance to next pipe,
        # y dist to next pipe, v = current vel, reward total for action =0, reward total for action =1
        # self.base_model = pd.DataFrame(
            # columns=["id", "x", "y", "v", "a0", "a1"], data=columns
        # )
