from vpython import *
import random as r
import numpy as np
from collections import deque
import copy
import scipy 
 
class constants():
    def __init__(self):
        self.c = 3*10**6
        self.epsilon = 8.854187817 * 10**(-12)
        self.mu = 4*np.pi *10**(-7)
        
c = 3*10**6
epsilon = 8.854187817 * 10**(-12)
mu = 4*np.pi *10**(-7)

display_width = 200
display_height = 200
display_length = 200

wallR = box(pos= vector(display_width/2,0,0), size=vector(0.2,200,200), color=color.green)
wallL = box(pos=vector(-display_width/2,0,0), size= vector(0.2,200,200), color=color.green)
wallD = box(pos=vector(0,display_height/2,0), size= vector(200,0.2,200), color=color.red)
wallU = box(pos=vector(0,-display_height/2,0), size= vector(200,0.2,200), color=color.red)
wallF = box(pos=vector(0,0,-display_length/2), size= vector(200,200,0.2), color=color.yellow)

electrodynamics = True
show_field = False
show_magnetic = False
InfinitePlate = True
Magnet      = False
rotation_matrix = np.array([[0,0,1],
                            [0,1,0],
                            [1,0,0]], dtype = int)

Ball_num = 2
dt= 1/30
red = (255,0,0)
white = (255,255,255)




def normalized(a):
    b = np.linalg.norm(a)
    if not(b == 0):
        return a/b
    else:
        return np.zeros((1,3), dtype = float)



def matrix_on_vector(matrix, vector):
    
    new_vector = vector[0] * matrix[:,0] + vector[1] * matrix[:,1] + vector[2] * matrix[:,2]
    return new_vector
    
    
    
    
    
    
    
    
def tot_EM_field_at_charge(location):

    EM = np.array([[0.,0.,0.],[0.,0.,0.]], dtype = float)

    def retarded_ballys(history):

        new_ballys = np.zeros(Ball_num, dtype = object)

        for i in range(Ball_num):

            for j in  range(len(history)):

                if np.linalg.norm(location-history[j][i].position)< c*j*dt:
                    new_ballys[i]= history[j][i]                    
                    break
            new_ballys[i] = ballys[i]

        return new_ballys

    for q in retarded_ballys(hist):

        EM = EM + q.EM_field(location)
    
    if InfinitePlate == True:
        EM[0][0] = EM[0][0]+ 0.01
    if Magnet == True:
        EM[1][2] = EM[1][2]+ 0.1
        
    return EM

def Force_on_bally(field, charge):
    
    force = charge.ladung*(field[0] + np.cross(charge.velocity, field[1]))
    return force

def E_squared(location):
    return np.dot(tot_EM_field_at_charge(location)[0],tot_EM_field_at_charge(location)[0])

def electric_field_energy():
    
    return scipy.integrate.dblquad(E_squared,0,display_width, lambda y: 0, lambda y: display_height)





class arrow(object):
    
    def __init__(self, length, x, y):


        self.length = length
        self.position = np.array([x,y,0])
                        
        
    def relative_position(self, charges):
        pos = 0
        for q in charges:       
            pos += np.dot(q.position - self.position,q.position -self.position)
       
        return (pos)**0.5

    def field_update(self, charges):
        
        self.field = tot_EM_field_at_charge(self.position[0], self.position[1])
        
        if show_magnetic == True:
            self.field_mag= np.linalg.norm(self.field[1])
        else:
            self.field_mag= np.linalg.norm(self.field[0])
        
        if self.field_mag == 0:            
            self.field_direction = np.zeros(3,)
        else:    
            if show_magnetic == True: 
                #self.field_direction = self.field[1]/self.field_mag       
                self.field_direction = matrix_on_vector(rotation_matrix, self.field[1]/self.field_mag)
            else:
                self.field_direction = self.field[0]/self.field_mag
    def position_end(self):
        
        self.position_2 = self.position + self.field_direction * self.length

        return self.position_2

    def scaled_color(self):
        self.color = self.field_mag
        if self.color < 0.03:
            self.color = (46,120,255)
        elif self.color < 0.08:
            self.color = (147,145,252)
        elif self.color < 0.12:
            self.color = (249,23,28)
        elif self.color < 0.4:
            self.color =(251,139,33) 
        elif self.color < 0.8:
            self.color = (255,255,127)
        else:
            self.color = (255,255,255)
            
        
        return self.color
   
   # def show(self):
    #    pygame.draw.line(gameDisplay, self.scaled_color(),(int(self.position[0]), int(self.position[1])), (int(self.position_end()[0]), int(self.position_end()[1])))
        







class Ball(object):
    def __init__(self, m,q, V = np.array([0,0,0], dtype = float), X = np.array([0,0,0],dtype = float), c = vector(255,0,0)):
        self.position = X
        self.position_2 = X
        self.velocity = V
        self.velocity_2 = V
        self.acceleration = np.array([0.,0.,0.], dtype = float)
        self.mass = m
        self.ladung = q
        self.color = c
        self.manifest= sphere(pos = vector(self.position[0],self.position[1],self.position[2] ), radius = self.mass, color = self.color)

    def acceleration_compute(self,force):
        a = force/self.mass
        self.acceleration += a

    def move(self):
        self.velocity += self.acceleration*dt
       
        #if self.velocity.any() >= c/3:
         #   self.velocity -= self.acceleration*dt  

        self.position += self.velocity*dt
        self.acceleration *= 0
        self.manifest.pos = vector(self.position[0],self.position[1],self.position[2])
    
    def show(self):
        pygame.draw.circle(gameDisplay, self.color, [int(self.position[0]), int(self.position[1])], self.mass)

    def Edgelord(self):

        if ((self.position[0] + dt*self.velocity[0] >= display_width/2-self.mass) and dt*self.velocity[0] > 0):
            self.velocity[0] *= -1
            self.position[0] = display_width/2 - self.mass + dt*self.velocity[0]
            self.acceleration *= 0
             

        elif ((self.position[0] + dt*self.velocity[0] - self.mass  <= -display_width/2) and dt*self.velocity[0] < 0 ):

            self.velocity[0] *= -1
            self.position[0] = self.mass + dt*self.velocity[0] -display_width/2
            self.acceleration *= 0

        elif ((self.position[1] + dt*self.velocity[1] >= display_height/2 - self.mass) and dt*self.velocity[1] > 0):

            self.velocity[1] *= -1
            self.position[1] = display_height/2 - self.mass + dt*self.velocity[1]
            self.acceleration *= 0

        elif ((self.position[1] + dt*self.velocity[1] - self.mass  <= -display_height/2) and dt*self.velocity[1] < 0 ):

            self.position[1] = self.mass -dt*self.velocity[1] -display_height/2
            self.velocity[1] *= -1
            self.acceleration *= 0
            
        elif ((self.position[2] + dt*self.velocity[2] >= display_length/2-self.mass) and dt*self.velocity[2] > 0):
            self.velocity[2] *= -1
            self.position[2] = display_length/2 - self.mass + dt*self.velocity[2]
            self.acceleration *= 0 

        elif ((self.position[2] + dt*self.velocity[2] - self.mass  <= -display_length/2) and dt*self.velocity[2] < 0 ):

            self.velocity[2] *= -1
            self.position[2] = self.mass + dt*self.velocity[2] -display_length/2
            self.acceleration *= 0
            
    def EM_field(self, R):
       #using solutions to lienard wiechert potential
        
        radius = np.linalg.norm(R - self.position)
        if radius != 0:
            unitradius = (R - self.position)/radius
        else:
            unitradius = np.zeros(3)

        if np.linalg.norm(radius) != 0 and np.dot(unitradius, self.velocity)!=1:
            charge      = self.ladung / (1 - np.dot(unitradius, self.velocity) ** 3)
            

            if radius < self.mass:
                radius = self.ladung

            radius2     = radius ** 2

            velocity_in_c = self.velocity/c
            
            oneMinusV2  = 1 - np.dot(velocity_in_c, velocity_in_c)
            uMinusV     = unitradius - velocity_in_c            
            aCrossUmV   = np.cross(uMinusV, self.acceleration)
            Eleft       = (oneMinusV2 * (unitradius - velocity_in_c)) / radius2
            Eright      = np.cross(unitradius, aCrossUmV) / (radius*c**2)
            E           = (charge/(4*np.pi*epsilon)) * (Eleft - Eright)
            #E = np.zeros(3, )
            B           = np.cross(unitradius/c, ((mu*epsilon*charge*c**2) * (Eleft - Eright)))
            
            EM_field = np.array([E,B], dtype = float)
        else:
            EM_field = np.zeros((2,3), dtype = float)

        return EM_field

ballys = [] 
for i in range(Ball_num):
    #ballys.insert(i, Ball(r.randrange(300,display_width - 5, 10),r.randrange(200,display_height/2,1)   , r.randrange(5,10,1),(r.randint(1,255),r.randint(1,255),r.randint(1,255)), r.randint(-200,200)/1000, r.randint(-200,200)/1000))
    ballys.insert(i, Ball(10,0.001,V = np.zeros(3, dtype = float), X = np.array([i*30-60, i*30 -60, i*30], dtype = float)))

#ballys.append(Ball(10,-0.001,V = np.zeros(3, dtype = float), X = np.array([0, 0,0 ], dtype = float))) 

if show_field == True:    
 #create arrow objects                  
    arrow_grid_x = np.arange(10, display_width, 20, dtype = int)
    arrow_grid_y = np.arange(10, display_height, 20, dtype = int)
    arrow_grid_z = np.arange(10, display_length, 20, dtype = int)
    arrow_grid_z = np.arange(10, display_length, 20, dtype = int)              
   
    dim_x = arrow_grid_x.shape[0]  
    dim_y = arrow_grid_y.shape[0]
    dim_z = arrow_grid_y.shape[0]

    arrows = []
    
    for i in range(dim_x):
        for j in range(dim_y):
            arrows.append(arrow(10, arrow_grid_x[i], arrow_grid_y[j]))
            
hist = deque(maxlen = int(1/dt))            

grav = np.array([0.,0.1,0.])
repulsion = np.array([0.,0.,0.])

crashed = False

while not crashed :

    rate(30)    
   

    hist.appendleft(copy.deepcopy(ballys))
            
    
    if electrodynamics == True:
        for bally in ballys:
            
            bally.acceleration_compute(Force_on_bally(tot_EM_field_at_charge(bally.position), bally))
    
    if show_field == True :       
        for i, zeiger in enumerate(arrows):
            #zeiger.relative_position(ballys) < 100:
            zeiger.field_update(ballys)
            zeiger.scaled_color()
            zeiger.position_end()
            #zeiger.show()
    
    for i, bally in enumerate(ballys):

        
        

       
        #ballys[i].acceleration_compute(grav * ballys[i].mass)
        
        for bally2 in ballys[i+1:]:
                
            #checks collisions
            if  np.linalg.norm(bally.position - bally2.position) <= bally.mass  + bally2.mass  :

                bally.velocity_2 = (bally.mass * bally.velocity + bally2.mass * bally2.velocity + bally2.mass *(bally2.velocity - bally.velocity))/ (bally.mass + bally2.mass)
                bally2.velocity_2 = (bally.mass * bally2.velocity + bally.mass * bally.velocity + bally.mass *(bally.velocity - bally2.velocity))/ (bally2.mass + bally.mass)

                #prevents balls getting stuck in each other and assignes new velocitys
                if not(np.linalg.norm(bally.position + bally.velocity_2  - (bally2.position + bally2.velocity_2) ) <= bally.mass  + bally2.mass):
                        bally.velocity = bally.velocity_2
                        bally2.velocity = bally2.velocity_2
        
        bally.Edgelord()
        
        bally.move()
        
        
    



