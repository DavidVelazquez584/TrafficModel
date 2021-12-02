import numpy as np
import agentpy as ap
import matplotlib.pyplot as plt
import seaborn as sns
import IPython
import json
import os
import _thread
import time
from flask import Flask, render_template, request, jsonify
app = Flask(__name__, static_url_path="")
port = int(os.getenv("PORT", 8020))

class Vehicle(ap.Agent):
    def setup(self):
        self.grid = self.model.grid
        self.pos = [0, 0]
        self.road = 1
        self.side = [1, 0]
        self.speed = 1
        self.crossed = False
        self.id = 0
        new_Dict = {}
        new_Dict["id"] = self.id
        new_Dict["x"] = self.pos[0]
        new_Dict["y"] = 0
        new_Dict["z"] = self.pos[1]
        self.posDict = [new_Dict]

    def direction(self):
        self.pos = self.grid.positions[self]
        if self.pos[1] == 0:
            self.side = [0, 1]

    def movement(self):
        self.direction()
        new_Dict = {}
        new_Dict["id"] = self.id
        new_Dict["x"] = self.pos[0]
        new_Dict["y"] = 0
        new_Dict["z"] = self.pos[1]
        #if self.posDict.count==1:
        self.posDict[0]=new_Dict
        #else:
         #   self.posDict.append(new_Dict)
        return (self.speed * self.side[0], self.speed * self.side[1])

    def add_position(self):
        new_Dict = {}
        new_Dict["id"] = self.id
        new_Dict["x"] = self.pos[0]
        new_Dict["y"] = 0
        new_Dict["z"] = self.pos[1]
        #if self.posDict.count==1:
        self.posDict[0]=new_Dict
        #else:
         #   self.posDict.append(new_Dict)
        

    def route(self):
        self.pos = self.grid.positions[self]
        if self.pos[1] == 0:
            return 'Horizontal'
        return 'Vertical'

class StopSign(ap.Agent):
    def setup(self):
        self.status = 1
        self.road = 3
        self.grid = self.model.grid
        self.pos = [0, 0]
        self.route=''
        self.id = 0
        new_Dict = {}
        new_Dict["idSS"] = self.id
        new_Dict["state"] = self.status
        self.statusDict = [new_Dict]

    def positions(self):
        self.pos = self.grid.positions[self]

    def change_state(self):
        self.positions()
        tGrid = self.p['Grid']
        self.status = 2
        self.road=2
        if self.model.n_cars_1 > self.model.n_cars_2:
            if self.pos[0] == int((tGrid/2)+1):
                self.status = 0
                self.road=4
        elif self.model.n_cars_1 < self.model.n_cars_2:
            if self.pos[1] == int((tGrid/2)+1):
                self.status = 0
                self.road=4
        else:
            if self.pos[1] == int((tGrid/2)+1):
                self.status = 0
                self.road=4
        new_Dict = {}
        new_Dict["idSS"] = self.id
        new_Dict["state"] = self.status
        #if self.statusDict.count==1:
        self.statusDict[0]=new_Dict
        #else:
        #    self.statusDict.append(new_Dict)
        

class Grass(ap.Agent):
    def setup(self):
        self.road = 5
        self.condition = 1

class IntersectionModel(ap.Model):
    def setup(self):
        n_vehicles = self.p['Vehicles']
        self.carros_final=n_vehicles
        self.steps=0
        self.con=0
        self.tGrid = self.p['Grid']
        self.grid = ap.Grid(self, [self.tGrid] * 2, torus=False,track_empty=True)
        self.n_cars_1 = 0
        self.n_cars_2 = 0

        n_roads = (self.tGrid*self.tGrid)-(self.tGrid*2)-1

        self.vehicles = ap.AgentList(self, n_vehicles, Vehicle)
        self.road = ap.AgentList(self, n_roads, Grass)
        self.stop_sign = ap.AgentList(self, 2, StopSign)
        self.vehicles.grid = self.grid

        grass_pos = []
        for i in range(self.tGrid):
            for j in range(self.tGrid):
                if i != (self.tGrid/2) and j != (self.tGrid/2):
                    if i != (self.tGrid/2)+1 or j != (self.tGrid/2)-1:
                        if j != (self.tGrid/2)+1 or i != (self.tGrid/2)-1:
                            grass_pos.append((i,j))


        contador = 0
        for vehicle in self.vehicles:
            vehicle.id = contador
            contador+=1
            
        self.grid.add_agents(self.stop_sign, positions=[(int((self.tGrid/2)-1), int((self.tGrid/2)+1)), (int((self.tGrid/2)+1), int((self.tGrid/2)-1))])
        self.grid.add_agents(self.road, grass_pos)
        stop_lights = self.stop_sign
        contadorS = 0
        for semaforo in stop_lights:
            if self.grid.positions[semaforo][1]==0:
                semaforo.route='Vertical'
            else: 
                semaforo.route='Horizontal'
            semaforo.id = contadorS
            contadorS+=1
            vehicles_positions=[]
            positions=[(0, int(self.tGrid/2)), (int(self.tGrid/2), 0)]
            
        for i in range (n_vehicles):
            random_position = np.random.randint(0, 2)
            vehicles_positions.append(positions[random_position])
        #new_car=ap.AgentDList(self,1,Vehicle)
        self.grid.add_agents(self.vehicles,vehicles_positions)
        self.contador = 0
        self.jsonCollectData = {}
        self.start=0

    def step(self):
        if self.start==0:
            time.sleep(10)
            self.start+=1
        if self.carros_final!=0:
            self.steps+=1
        else:
            print(self.steps)
        self.contador += 1
        movimiento=True
        state=False
        moving_cars_1 = self.vehicles
        for car in moving_cars_1:
            agent_pos=self.grid.positions[car]
            for i in range(1,int((self.tGrid/2))):
                if (int(self.tGrid/2) == agent_pos[0])and(int(i) == agent_pos[1]):
                    self.n_cars_1 += 1
                    state=True
                if  (int(self.tGrid/2) == agent_pos[1])and(int(i) == agent_pos[0]):
                    self.n_cars_2 += 1
                    state=True
            if (int(self.tGrid/2) == agent_pos[0])and(int(self.tGrid)-1 == agent_pos[1]):
                #self.grid.remove_agents(self.vehicles) 
                self.grid.move_to(car,(0,self.tGrid))
                self.carros_final-=1
            elif (int(self.tGrid/2) == agent_pos[1])and(int(self.tGrid)-1 == agent_pos[0]):
                #self.grid.remove_agents(self.vehicles) 
                self.grid.move_to(car,(self.tGrid,self.tGrid))
                self.carros_final-=1

        if state:
            stop_light = self.stop_sign
            for semaforo in stop_light:    
                if state:
                    semaforo.change_state()
                else:
                    semaforo.status=1
                    semaforo.road=3

        for agents in self.grid.agents:
            agent_pos=self.grid.positions[agents]
            movimiento=True
            if agents.type == 'Vehicle':
                for neighbor in self.grid.neighbors(agents):
                    if agents.route() == 'Vertical':
                        if self.grid.positions[neighbor][1]==agent_pos[1]+1 and self.grid.positions[neighbor][0]==agent_pos[0]:
                            if   neighbor.type=='Vehicle':    
                                movimiento=False
                                break
                        if self.grid.positions[neighbor][1]==agent_pos[1] and self.grid.positions[neighbor][0]==agent_pos[0]+1:
                            if  neighbor.type=='StopSign':
                                if neighbor.status==2:
                                    movimiento=False
                                    break
                                else:
                                    self.n_cars_1-=1
                                    break
                        
                    if agents.route() == 'Vertical':
                        if self.grid.positions[neighbor][0]==agent_pos[0]+1 and self.grid.positions[neighbor][1]==agent_pos[1]:
                            if  neighbor.type=='Vehicle':
                                movimiento=False
                                break
                        if self.grid.positions[neighbor][0]==agent_pos[0] and self.grid.positions[neighbor][1]==agent_pos[1]+1:
                            if  neighbor.type=='StopSign':
                                if neighbor.status==2:
                                    movimiento=False
                                    break
                                else:
                                    self.n_cars_2-=1
                                    break
                if movimiento:
                    coordinates_move=agents.movement()
                    self.grid.move_by(agents,coordinates_move)
                else:
                    agents.add_position()

        jsonCollectData = {}
        vehicles = self.vehicles 
        arregloPos = []
        for car in vehicles:
            #id = f"{car.id}"
            #jsonCollectData[id] = car.posDict
            arregloPos = np.append(arregloPos, car.posDict)
 
        stopSigns = self.stop_sign
        arregloSS = []
        for stopSign in stopSigns:
            arregloSS = np.append(arregloSS, stopSign.statusDict)
        #print(arregloPos)
        arregloPos = arregloPos.tolist()
        arregloSS = arregloSS.tolist()
        jsonCollectData["data"] = arregloPos
        jsonCollectData["dataStopSign"] = arregloSS
        with open('archivoPosJson.json', 'w') as file:
            json.dump(jsonCollectData, file, indent=4)
        self.jsonCollectData = jsonCollectData
        time.sleep(1.5)
        if self.contador == self.p['steps'] - 1:
            IntersectionModel.end(self)

    def end(self):
        
        
        #requesting.post(url,data=model.jsonCollectData)

        pass

def runModel():
    parameters = {
        'Vehicles': 15,
        'steps': 500,
        'Grid':24,
    }
    # Perform experiment
    model = IntersectionModel(parameters)
    model.run()
    print(model.jsonCollectData)
    return model.jsonCollectData
_thread.start_new_thread(runModel,(),)
@app.route("/")
def root():
    with open('archivoPosJson.json') as file:
            data = json.load(file)
    #with open('archivoPosJson.json') as json_file:
     #       data = json.load(json_file)
            return jsonify(data)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port, debug=True)