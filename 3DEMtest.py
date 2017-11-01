from vpython import *
import random as r
import numpy as np
from numba import jit
from ast import literal_eval  
    

c = 3*10**8
epsilon = 8.854187817 * 10**(-12)
mu = 4*np.pi *10**(-7)


display = { 'width' : 200, 
            'height' : 200,
            'length' : 200}


wallR = box(pos= vector(display['width']/2,0,0), size=vector(0.2,200,200), color=color.green)
wallL = box(pos=vector(-display['width']/2,0,0), size= vector(0.2,200,200), color=color.green)
wallD = box(pos=vector(0,display['height']/2,0), size= vector(200,0.2,200), color=color.red)
wallU = box(pos=vector(0,-display['height']/2,0), size= vector(200,0.2,200), color=color.red)
wallF = box(pos=vector(0,0,-display['length']/2), size= vector(200,200,0.2), color=color.yellow)

electrodynamics = True
show_field = True
show_magnetic = False
InfinitePlate = False
Magnet      = False
rotation_matrix = np.array([[0,0,1],
                            [0,1,0],
                            [1,0,0]], dtype = int)
planelement = 1/sqrt(2)

Ball_num = 4
c = 100
dt= 1/60
step = 40
red = (255,0,0)
white = (255,255,255)





@jit(cache = True, nopython=True)
def matrix_on_vector(matrix, vector):
    
    return vector[0] * matrix[:,0] + vector[1] * matrix[:,1] + vector[2] * matrix[:,2]
     
@jit(cache = True, nopython=True)
def dot(vec1, vec2):
    
    return vec1[0] * vec2[0] + vec1[1] * vec2[1] + vec1[2] * vec2[2]    
    
    
    
@jit(cache = True, nopython=True)
def cross(vec1, vec2):
    
    result = np.array([0.,0.,0.])
    
    a1, a2, a3 = vec1[0],vec1[1], vec1[2]
    b1, b2, b3 = vec2[0], vec2[1], vec2[2]
    
    result[0] = a2 * b3 - a3 * b2
    result[1] = a3 * b1 - a1 * b3
    result[2] = a1 * b2 - a2 * b1  
          
    return result

@jit(cache = True, nopython=True)
def norm(vec):
    return sqrt(vec[0]*vec[0] + vec[1]*vec[1] + vec[2]*vec[2])   
    
    
    
def tot_EM_field_at_charge(location):

    EM = np.array([[0.,0.,0.],[0.,0.,0.]], dtype = float)

    for q in ballys:

        EM = EM + q.EM_field(location)


    return EM + gwee.extra_field


def Force_on_bally(field, charge):
    
    force = charge.ladung*(field[0] + np.cross(charge.velocity, field[1]))
    return force




class gui(object):
    
    def __init__(self):
        
        self.charge_button = button(pos = scene.title_anchor, bind = self.add_charge, text = 'add charge')
        self.cnum_display  = wtext( text = ''.join(str(len(ballys)) + ' charges'))
        self.text_field = wtext(pos = scene.title_anchor, text = 'm = 1; radius = 10; q = 0.0001 ; V = [10,0,0]; X = [-25, 0, 0]' )
        scene.bind('keydown', self.keyInput)
        
        self.field_button = button(bind =self.add_field, text = 'add field ')
        scene.append_to_caption('\n\n')        
        self.extra_field   = np.array([[0.,0.,0.],[0.,0.,0.]], dtype = float)
        self.directions = ['x','y','z','-x','-y','-z','xy','xz','yz','-xy','-xz','-yz']
        
    def keyInput(self,evt):
        s = evt.key
        
        if len(s) == 1:
            self.text_field.text += s
            
        elif s == 'backspace':
            
           try:
               del self.text_field.text [-1]
           except:#index out of bounds                        
               pass
           
    @property
    def call_values(self):
        return self.text_field.text
    
    @call_values.setter 
    def call_values(self, string):
        
        self.text_field.text = string
        
    def field_init(self):
        self.extra_field   = np.array([[0.,0.,0.],[0.,0.,0.]], dtype = float)
        
    def add_charge(self):
        
        try:
            ballys.append(Ball.from_string(self.call_values))
        #eval('ballys.append(Ball('+ self.call_values + ' ))')
            self.call_values = ''
        except:
            self.call_values = 'wrong format'
            
    def add_field(self):
              
        self.E_dic = slider(min = 0, max = 11, step = 1, value = 0,top = 10, bind = self.give_field)
        self.E_dic_tex = wtext(text = ''.join( 'E: ' + self.directions[self.E_dic.value]) )
        scene.append_to_caption('\n\n')
        
        self.B_dic = slider(min = 0, max = 11, step = 1, value = 0,top = 10, bind = self.give_field)
        self.B_dic_tex = wtext(text = ''.join('B: ' + self.directions[self.B_dic.value]) )
        scene.append_to_caption('\n\n')
        
        self.E_mag = slider(min = 0, max = 1000, step = 10, value = 0, top = 10, bind = self.give_field)
        self.E_mag_tex = wtext( text = ''.join('E_mag:' + str(self.E_mag.value)  ))
        scene.append_to_caption('\n\n')
        
        self.B_mag = slider(min = 0, max = 1000, step = 10, value = 0, top = 10,bind = self.give_field)
        self.B_mag_tex = wtext( text = ''.join('B_mag: ' + str(self.B_mag.value)))
        scene.append_to_caption('\n\n')
        
    def update_text(self):
        
        self.E_dic_tex.text = ''.join( 'E: ' + self.directions[self.E_dic.value] ) 
        self.B_dic_tex.text = ''.join('B: ' + self.directions[self.B_dic.value] ) 
        self.E_mag_tex.text = ''.join('E_mag:' + str(self.E_mag.value) )
        self.B_mag_tex.text= ''.join('B_mag: ' + str(self.B_mag.value) )
    
    def evaluate(self,dic, f, f_mag):
               
        if dic <= 2:
            self.extra_field[f][dic] = 1
            
        elif dic <= 5:
            self.extra_field[f][dic-3] = -1
                            
        def in_ebene(start):  
                  
            if dic == start:            
                self.extra_field[f][0] = planelement
                self.extra_field[f][1] = planelement
                                
            elif dic == start +1:
                self.extra_field[f][0] = planelement
                self.extra_field[f][2] = planelement
                       
            elif dic == start +2:
                self.extra_field[f][1] = planelement
                self.extra_field[f][2] = planelement
        in_ebene(6)  
        in_ebene(9)  
        
        if dic <9:        
            self.extra_field[f] *= f_mag 
                        
        else:
            self.extra_field[f] *= -f_mag        
                
    def give_field(self):
        
        self.field_init()
        self.update_text()                
       
        self.evaluate(self.E_dic.value, 0, self.E_mag.value)
        self.evaluate(self.B_dic.value, 1, self.B_mag.value)

        
        
        
        
        
        


class pointer(object):
    
    def __init__(self, length, x, y,z):


        self.length = length
        self.position = np.array([x,y,z])
        self.position_2 = np.array([20,0,0])
        
        self.show = arrow(pos = vector(self.position[0],self.position[1],self.position[2] ), axis = vector(self.position_2[0],self.position_2[1],self.position_2[2] ))                
        

    def field_update(self, charges):
        
        self.field = tot_EM_field_at_charge(self.position)
        
        if show_magnetic == True:
            self.field_mag= np.linalg.norm(self.field[1])
        else:
            self.field_mag= np.linalg.norm(self.field[0])
        
        if self.field_mag == 0:            
            self.field_direction = np.zeros(3,)
        else:    
            if show_magnetic == True: 
                self.field_direction = -self.field[1]/self.field_mag       
                #self.field_direction = matrix_on_vector(rotation_matrix, self.field[1]/self.field_mag)
            else:
                self.field_direction = -self.field[0]/self.field_mag
                
    def position_end(self):
        
        self.position_2 =  self.field_direction * self.length
        self.show.axis = vector(self.position_2[0],self.position_2[1],self.position_2[2])
        

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
        




@jit( nopython = True)
def jit_EM_field(position,length,ladung,velocity,acceleration,R):
    #using solutions to lienard wiechert potential
    EM_field = np.array([0.,0.,0.,0.,0.,0.])
    radius = np.linalg.norm(R - position)
    
    if radius != 0:        
        unitradius = (R - position)/radius
                     
        if np.dot(unitradius, velocity) != 1:
            charge = ladung / ( (1 - np.dot(unitradius, velocity)/c)** 3)
            
            if radius < length:
                radius = length
                
            radius2 = radius ** 2
            velocity_in_c = velocity/c
            oneMinusV2 = 1 - np.dot(velocity_in_c, velocity_in_c)
            uMinusV = unitradius - velocity_in_c            
            aCrossUmV = cross(uMinusV, acceleration)
            Eleft = (oneMinusV2 * (unitradius - velocity_in_c)) / radius2
            Eright = cross(unitradius, aCrossUmV) / (radius*c**2)
            
            E = (charge/(4*np.pi*epsilon)) * (Eleft - Eright)
            B = cross(unitradius/c, ((mu*epsilon*charge*c**2) * (Eleft - Eright)))
            
            EM_field = np.array([E[0],E[1],E[2],B[0],B[1],B[2]])
            
    return EM_field


class Ball(object):
    
    def __init__(self, m = 1, radius = 10, q = 0.0001, V = np.array([0,0,0], dtype = float), X = np.array([0,0,0],dtype = float), c = vector(255,0,0)):
        
        self.position = X
        self.position_2 = X
        self.velocity = V
        self.velocity_2 = V
        self.acceleration = np.array([0.,0.,0.], dtype = float)
        self.mass = m
        self.radius = radius
        self.ladung = q
        self.color = c
        
        self.manifest= sphere(pos = vector(self.position[0],self.position[1],self.position[2] ),radius = self.radius, color = self.color)
    
    @classmethod
    def from_string(cls, string):
        
        args = dict(e.split(' =') for e in string.split('; '))
        
        for key, value in args.items():
            
            value = eval(value)
            args[key] = value 
            
            if isinstance(value,list):
                
                args[key] = np.array(value, dtype = float)
               
        return cls(**args)
    
    def acceleration_compute(self,force):
        a = force/self.mass
        self.acceleration += a
        
    def move(self):
             
        self.velocity += self.acceleration*dt  
        self.position += self.velocity*dt 
        

        
    def corrected_move(self):
        a = Force_on_bally(tot_EM_field_at_charge(self.position), self)/self.mass                          
        self.position -= self.velocity*dt
        self.velocity += (a-self.acceleration)*dt/2  
        self.position += self.velocity*dt
        
        self.acceleration *= 0
        
        self.manifest.pos = vector(self.position[0],self.position[1],self.position[2])
        
        

    def Edgelord(self):

        if ((self.position[0] + dt*self.velocity[0] >= display['width']/2-self.mass) and dt*self.velocity[0] > 0):
            self.velocity[0] *= -1
            self.position[0] = display['width']/2 - self.mass + dt*self.velocity[0]
             

        elif ((self.position[0] + dt*self.velocity[0] - self.mass  <= -display['width']/2) and dt*self.velocity[0] < 0 ):

            self.velocity[0] *= -1
            self.position[0] = self.mass + dt*self.velocity[0] -display['width']/2
            

        elif ((self.position[1] + dt*self.velocity[1] >= display['height']/2 - self.mass) and dt*self.velocity[1] > 0):

            self.velocity[1] *= -1
            self.position[1] = display['height']/2 - self.mass + dt*self.velocity[1]
            

        elif ((self.position[1] + dt*self.velocity[1] - self.mass  <= -display['height']/2) and dt*self.velocity[1] < 0 ):

            self.position[1] = self.mass -dt*self.velocity[1] -display['height']/2
            self.velocity[1] *= -1
        
        elif ((self.position[2] + dt*self.velocity[2] >= display['length']/2-self.mass) and dt*self.velocity[2] > 0):
            self.velocity[2] *= -1
            self.position[2] = display['length']/2 - self.mass + dt*self.velocity[2]
             

        elif ((self.position[2] + dt*self.velocity[2] - self.mass  <= -display['length']/2) and dt*self.velocity[2] < 0 ):

            self.velocity[2] *= -1
            self.position[2] = self.mass + dt*self.velocity[2] -display['length']/2
                         
         
    def EM_field(self, R):
       
       #reshape just costs 1 µs  
       return np.reshape((jit_EM_field(self.position,self.radius ,self.ladung,self.velocity,self.acceleration,R)),(2,3))

    @staticmethod
    def trial_integrate():
        
        for bally in ballys:
            bally.acceleration_compute(Force_on_bally(tot_EM_field_at_charge(bally.position), bally))
            bally.move()
            
        for i,bally in enumerate(ballys):
                        
            bally.corrected_move()
            stoss(i,bally)
            bally.Edgelord()
            
ballys = [] 

for i in range(Ball_num):
    #ballys.insert(i, Ball(r.randrange(300,display['width'] - 5, 10),r.randrange(200,display['height']/2,1)   , r.randrange(5,10,1),(r.randint(1,255),r.randint(1,255),r.randint(1,255)), r.randint(-200,200)/1000, r.randint(-200,200)/1000))
    ballys.insert(i, Ball(1,10,0.001,V = np.array([0,0,3], dtype = float), X = np.array([i*30, i*30 , i*30*0], dtype = float)))
    #ballys.insert(i, Ball(1,10,0.0001,V = np.array([10,0,0], dtype = float), X = np.array([-25, 0, 0], dtype = float)))
    #ballys.insert(i, Ball(1,10,-0.0001,V = np.array([0,0,3], dtype = float), X = np.array([25, 0, 0], dtype = float)))
#ballys.append(Ball(1,-0.0004,V = np.array([0,0,0], dtype = float), X = np.array([0,0,0], dtype = float))) 
gwee = gui()
    
if show_field == True:    
 #create pointer objects                  
    pointer_grid_x = np.arange((-display['width']+10)/2, display['width']/2, step, dtype = int)
    pointer_grid_y = np.arange((-display['height']+10)/2, display['height']/2, step, dtype = int)
    pointer_grid_z = np.arange((-display['length']+10)/2, display['length']/2, step, dtype = int)
                 
   
    dim_x = pointer_grid_x.shape[0]  
    dim_y = pointer_grid_y.shape[0]
    dim_z = pointer_grid_y.shape[0]
    
    
    
    pointers = []
    
    for i in range(dim_x):
        for j in range(dim_y):
                for k in range(dim_z):
                    pointers.append(pointer(10, pointer_grid_x[i], pointer_grid_y[j], pointer_grid_y[k]))
            
    pointers = np.array(pointers)        

grav = np.array([0.,0.1,0.])
angularVector = np.array([0.,0.,2])
crashed = False
index = 0

@np.vectorize
def arrow_update(zeiger):
    
        zeiger.field_update(ballys)
        zeiger.scaled_color()
        zeiger.position_end() 
        
      
def stoss(i,bally):
    
        for bally2 in ballys[i+1:]:           
        #checks collisions
            if  np.linalg.norm(bally.position - bally2.position) <= bally.radius  + bally2.radius  :
    
                bally.velocity_2 = (bally.mass * bally.velocity + bally2.mass * bally2.velocity + bally2.mass *(bally2.velocity - bally.velocity))/ (bally.mass + bally2.mass)
                bally2.velocity_2 = (bally.mass * bally2.velocity + bally.mass * bally.velocity + bally.mass *(bally.velocity - bally2.velocity))/ (bally2.mass + bally.mass)
    
                #prevents balls getting stuck in each other and assignes new velocitys
                if not(np.linalg.norm(bally.position + bally.velocity_2  - (bally2.position + bally2.velocity_2) ) <= bally.mass  + bally2.mass):
                        bally.velocity = bally.velocity_2
                        bally2.velocity = bally2.velocity_2
                        
def main(): 
    i = 0           
    while i<400 :
            
        rate(60) 
                
        if show_field == True :       
            arrow_update(pointers)
        Ball.trial_integrate()        
        i+=1
    
        
