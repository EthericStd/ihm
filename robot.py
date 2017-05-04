import tkinter as tk
from const import *


class Robot():

    def __init__(self, cav, circuit):
        self.cav = cav
        self.circuit = circuit
        self.circuit.robot = self
        self.path_matrix = None
        self.matrix = None


    def read_structure(self):
        """
        Permet la lecture de la structure
        de donnée pour le robot.
        """
        for motor in self.circuit.struct_motor:
            l_entrees_motor = []
            for wire in self.circuit.struct_motor[motor]:
                l_id = self.circuit.struct_wire[wire]
                if (l_id[0] != motor):
                    if (self.cav.gettags(l_id[0])[0] in ["gate_and", "gate_or", "gate_xor", "gate_not"]):
                        self.calc_gate(l_id[0])
                    l_entrees_motor.append(l_id[0])
                else:
                    if (self.cav.gettags(l_id[1])[0] in ["gate_and", "gate_or", "gate_xor", "gate_not"]):
                        self.calc_gate(l_id[1])
                    l_entrees_motor.append(l_id[1])
            self.circuit.struct_val[motor] = self.ou(l_entrees_motor)
            # print(motor, self.circuit.struct_val[motor])
        return self.check_structure()

    def calc_gate(self, gate_id):
        """
        Calcule la valeure résultante d'une porte.
        """
        val_entree = []
        for i in range(2):
            res = []
            entree = self.circuit.struct_gate[gate_id][i]
            for wire in entree:
                l_id = self.circuit.struct_wire[wire]
                if (l_id[0] != gate_id):
                    if (self.cav.gettags(l_id[0])[0] in ["gate_and", "gate_or", "gate_xor", "gate_not"]):
                        self.calc_gate(l_id[0])
                    res.append(l_id[0])
                else:
                    if (self.cav.gettags(l_id[1])[0] in ["gate_and", "gate_or", "gate_xor", "gate_not"]):
                        self.calc_gate(l_id[1])
                    res.append(l_id[1])
            val_entree.append(self.ou(res))
            if (self.cav.gettags(gate_id)[0] == "gate_not"):
                val_entree.append(None)
                break
        self.circuit.struct_val[gate_id] = self.ope_gate(gate_id, val_entree[0], val_entree[1])

    def ou(self, l_id):
        """
        Retourne 1 si la valeur d'un des composants
        de la liste vaut 1, retourne 0 sinon.
        """
        for i in range(len(l_id)):
            if (self.circuit.struct_val[l_id[i]] == 1):
                return 1
        return 0

    def ope_gate(self, gate_id, val_entree1, val_entree2):
        """
        Fait l'opération de la porte entre les
        valeurs finales de ses deux entrées.
        """
        tag = self.cav.gettags(gate_id)[0]
        if (tag == "gate_and"):
            return (val_entree1 and val_entree2)
        elif (tag == "gate_or"):
            return (val_entree1 or val_entree2)
        elif (tag == "gate_xor"):
            if val_entree1 and val_entree2:
                return 0
            return (val_entree1 or val_entree2)
        elif (tag == "gate_not"):
            return (not val_entree1)

    def check_structure(self):
        """
        Vérifie que seuleument un moteur est allumé à la fois.
        """
        sum_val = 0
        for motor in self.circuit.struct_motor:
            sum_val += self.circuit.struct_val[motor]
            if (sum_val >= 2):
                return False
        return True

    def detect_murs(self, robot):
        """
        Détecte les murs autour du robot et allume
        les capteurs en conséquence.
        """
        if (self.matrix[robot[1]-1][robot[0]] == 1):
            self.circuit.struct_val[self.circuit.l_sensor[0]] = 1
        else:
            self.circuit.struct_val[self.circuit.l_sensor[0]] = 0

        if (self.matrix[robot[1]][robot[0]-1] == 1):
            self.circuit.struct_val[self.circuit.l_sensor[1]] = 1
        else:
            self.circuit.struct_val[self.circuit.l_sensor[1]] = 0

        if (self.matrix[robot[1]][robot[0]+1] == 1):
            self.circuit.struct_val[self.circuit.l_sensor[2]] = 1
        else:
            self.circuit.struct_val[self.circuit.l_sensor[2]] = 0

        if (self.matrix[robot[1]+1][robot[0]] == 1):
            self.circuit.struct_val[self.circuit.l_sensor[3]] = 1
        else:
            self.circuit.struct_val[self.circuit.l_sensor[3]] = 0

    def detect_position(self):
        """
        Détecte la position du robot dans le niveau.
        """
        for y in range(len(self.matrix)):
            for x in range(len(self.matrix[y])):
                if (self.matrix[y][x] == 2):
                    return [x, y]

    def create_matrix(self):
        """
        Crée la matrice correspondante
        à la carte choisie.
        """
        with open(self.path_matrix, "r") as fd:
            matrix = []
            i = 0
            for line in fd:
                line = line.strip()
                line = line.split(" ")
                for i in range(len(line)):
                    line[i] = int(line[i])
                # print(line)
                matrix.append(line)
        self.matrix = matrix

    def move_robot(self):
        """
        Permet au robot de bouger sur la carte.
        """
        robot_position = self.detect_position()
        self.detect_murs(robot_position)
        if (self.read_structure()):
            for i in range(self.circuit.l_motor[0], self.circuit.l_motor[3]+1):
                if (self.circuit.struct_val[i] == 1):
                    self.matrix[robot_position[1]][robot_position[0]] = 0
                    if (i == self.circuit.l_motor[0]):
                        robot_position[1] -= 1
                    elif (i == self.circuit.l_motor[1]):
                        robot_position[0] -= 1
                    elif (i == self.circuit.l_motor[2]):
                        robot_position[0] += 1
                    elif (i == self.circuit.l_motor[3]):
                        robot_position[1] += 1
                    if (self.matrix[robot_position[1][robot_position[0]]] == 3):
                        return True
                    self.matrix[robot_position[1][robot_position[0]]] = 2
        else:
            # Pop-up d'info que plus d'un moteur est allumé.
            return False

    def simulation(self):
        """
        Effectue la simulation du robot.
        """
        self.create_matrix()
        win = False
        while (not win):
            pos_deb = self.detect_position()
            win = self.move_robot()
            if (pos_deb == self.detect_position()):
                # Pop-up signalant que le robot est bloqué.
                break
        if (win):
            print("\n!!!!!!!!!!!!!!!!!!!!!! GAGNÉ !!!!!!!!!!!!!!!!!!!!!!!\n")
        else:
            print("\nBloqué  en ", pos_deb, ":(\n")
