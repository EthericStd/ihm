import tkinter as tk
from const import *


class Robot():

    def __init__(self, cav, circuit):
        self.cav = cav
        self.circuit = circuit
        self.circuit.robot = self


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
            print(motor, self.circuit.struct_val[motor])
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
                # Pop-up d'info que plus d'un moteur est allumé.
                return False
        return True

    def detect_murs(self, matrice):
        """
        Détecte les murs autour du robot et allume
        les capteurs en conséquence.
        """
        robot = self.detect_position()
        if (matrice[robot[1]-1][robot[0]] == 0):
            self.circuit.struct_val[2] = 1
        elif (matrice[robot[1]][robot[0]-1] == 0):
            self.circuit.struct_val[3] = 1
        elif (matrice[robot[1]][robot[0]+1] == 0):
            self.circuit.struct_val[4] = 1
        elif (matrice[robot[1]+1][robot[0]] == 0):
            self.circuit.struct_val[5] = 1

    def detect_position(self, matrice):
        """
        Détecte la position du robot dans le niveau.
        """
        for y in len(matrice):
            for x in len(matrice[y]):
                if (matrice[y][x] == 2):
                    return (x, y)
