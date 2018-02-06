from vpython import *
import random as r
import numpy as np
from numba import jit
from collections import deque, namedtuple
from ast import literal_eval  
from copy import copy
from recordclass import recordclass 

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

Ball_num = 5
dt= 1/45
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

def copy_list(array):
    
    return list(map(copy,array))
    
def retarded_ballys(history, location):

        new_ballys = np.zeros(Ball_num, dtype = object)
        hist_len = len(history)
        
        if hist_len != 0:            
            for i in range(Ball_num):
    
                for j in  range(hist_len):
                    if norm(location-history[j][i].position)< c*(j+0.5)*dt:    
                        new_ballys[i]= history[j][i]
                        break
                                    
        else:
            new_ballys = ballys
        return np.array(new_ballys)    
    
def spheric(R):
    f = -1000*R
    return np.array([f,[0.,0.,0.]]) 
   
def tot_EM_field_at_charge(location):

    EM = np.array([[0.,0.,0.],[0.,0.,0.]], dtype = float)

    for q in ballys:#retarded_ballys(hist, location):

        EM = EM + q.EM_field(location)


    return EM + gwee.extra_field + spheric(location)


def Force_on_bally(field, charge):
    
    force = charge.ladung*(field[0] + np.cross(charge.velocity, field[1]))
    return force



class gui(object):
    
    def __init__(self):
        
        self.run_button = button(pos = scene.title_anchor, bind = self.run, text = 'stop')
        self.charge_button = button(pos = scene.title_anchor, bind = self.add_charge, text = 'add charge')
        self.cnum_display  = wtext( text = ''.join(str(len(ballys)) + ' charges'))
        self.text_field = wtext(pos = scene.title_anchor, text = 'm = 1; radius = 10; q = 0.0001; V = [10,0,0]; X = [-25, 0, 0]' )
        scene.bind('keydown', self.keyInput)
        
        self.trail_on = radio(bind = trail, text = 'show trail')       
        self.field_button = button(bind =self.add_field, text = 'add field ')
        scene.append_to_caption('\n\n')        
        self.extra_field   = np.array([[0.,0.,0.],[0.,0.,0.]], dtype = float)
        self.directions = ['x','y','z','-x','-y','-z','xy','xz','yz','-xy','-xz','-yz']        
        self.running = 1
        
    def run(self,b): 
        
        self.running = not self.running
        if self.running: b.text = "Pause"
        else: b.text = "Run"
        
    def keyInput(self,evt):
        s = evt.key
        
        if s == ')':
            s+= '='
            
        elif s == 'shift+,':
            s+= ';'
        elif s == 'shift+0':
            s+= '='
        elif len(s) == 1:
            self.call_values += s
        
            
        elif s == 'backspace' or s == 'delete':
                      
           self.call_values =  self.call_values[:-1]
           
        if s == ')':
            s+= '='
           
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
    
    __slots__ = ('length','position','position_2','show')
    
    def __init__(self, length, x, y,z):


        self.length = length
        self.position = np.array([x,y,z])
        self.position_2 = np.array([20,0,0])
        
        self.show = arrow(pos = vector(self.position[0],self.position[1],self.position[2] ), axis = vector(self.position_2[0],self.position_2[1],self.position_2[2] ))                
        

    def direction(self):
        
        field = tot_EM_field_at_charge(self.position)
        
        if show_magnetic == True:
            field_mag= norm(field[1])
        else:
            field_mag= norm(field[0])
        
        if field_mag == 0:            
            field_direction = np.zeros(3,)
        else:    
            if show_magnetic == True: 
                field_direction = -field[1]/field_mag       
                #self.field_direction = matrix_on_vector(rotation_matrix, self.field[1]/self.field_mag)
            else:
                field_direction = -field[0]/field_mag
                                        
        return field_direction      
    
    def dic_update(self):
        
        self.position_2 =  self.direction() * self.length
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
    radius = norm(R - position)
    
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

class integriere(object):
    
    pred_vel_coef = (1/24)*np.array([55,
                                 -59,
                                 37,
                                 -9])

    pred_pos_coef = (1/360)*np.array([323,
                                      -264,
                                      159,
                                      -38])
    
    corr_vel_coef = (-1/720)*np.array([-251,
                                       -646,
                                       264,
                                       -106,
                                       19])
    
    corr_pos_coef = (-1/1440)*np.array([-135,
                                        -752,
                                        246,
                                        -96,
                                         17])
    def __init__(self,SSH):
    
        self.SSH = SSH
        self.hom_force = np.zeros(3)
    #SS system state: An array of states; SFH an array of force matrices with rg 4
    def pred(self,SS):        
        
        for state in SS:
            self.AM4(state)
        
    def AM4(self,state): 

        state.velocity = state.velocity + self.pred_vel_coef@state.fh*dt
        
        state.position = state.position +state.velocity*dt + self.pred_pos_coef@state.fh*dt**2
        
    def corr(self,SS):
        #doesnt work with retarded fields
        for state in SS:            
           state.fh_update()
          
        for state_n,state_n1 in zip(self.SSH[0], SS):
            
            self.AB5(state_n, state_n1)
            
    def AB5(self,state_n,state_n1):
        
        state_n1.velocity = state_n.velocity + self.corr_vel_coef@state_n1.fh*dt
        state_n1.position = state_n.position +state_n.velocity*dt + self.corr_pos_coef@state_n1.fh*dt**2
        state_n1.acceleration = state_n1.fh[0]
        
    @staticmethod     
    def  correct_f(SS):  
        
        for state in SS:
            
            state.fh.popleft()
            state.fh.pop()
            state.fh_update()
            
        for i, state in enumerate(SS):    
            state.acceleration = state.fh[0]
            stoss(i,state)
            #bally.Edgelord()
            state.manifest.pos = vector(state.position[0],state.position[1],state.position[2])
            
    def midpoint(self,ballys): 
        
        for bally in ballys:
            bally.fh_update()
            
        self.SSH.appendleft(list(map(copy,ballys)))
        
        for bally in ballys:
            bally.acceleration = bally.fh[0]
            bally.move()
            
        for i,bally in enumerate(ballys):
                        
            bally.corrected_move(self.hom_force)
            stoss(i,bally)
            bally.Edgelord()
            
        
        
    def __call__(self, ballys):
              
        self.SSH.appendleft(list(map(copy,ballys)))
                
        self.pred(ballys)        
        self.corr(ballys)
        self.correct_f(ballys)
        
class basic_Ball():
    
    __slots__ =('position','velocity','acceleration','mass','radius','ladung')
    
    def __init__(self, m , radius , q , X,V,A):
    
        self.position = X
        
        self.velocity = V
        
        self.acceleration = A
        self.mass = m
        self.radius = radius
        self.ladung = q
        
        
    def EM_field(self, R):       
       #reshape just costs 1 µs  
       return np.reshape((jit_EM_field(self.position,self.radius ,self.ladung,self.velocity,self.acceleration,R)),(2,3))
   
class Ball(basic_Ball):
    
    def __init__(self, m = 1, radius = 10, q = 0.0001,A = np.array([0,0,0], dtype = float) ,V = np.array([0,0,0], dtype = float), X = np.array([0,0,0],dtype = float), c = vector(255,0,0)):
        
        super().__init__(m , radius , q , X,V,A )
        self.position_2 = X
        
        self.velocity_2 = V
        self.color = c
        
        self.fh = deque(maxlen = 5)
        
        self.manifest= sphere(make_trail = 0, trail_radius = 1, pos = vector(self.position[0],self.position[1],self.position[2] ),radius = self.radius, color = self.color)
    
    @classmethod
    def from_string(cls, string):
        
        if string == '':
            return cls()
        
        args = dict(e.split(' =') for e in string.split('; '))
        
        for key, value in args.items():
            
            value = eval(value)
            args[key] = value 
            
            if isinstance(value,list):
                
                args[key] = np.array(value, dtype = float)
               
        return cls(**args)
    
    def __copy__(self):
                         
        return basic_Ball(self.mass, self.radius , self.ladung , self.position ,self.velocity ,self.acceleration)
    
    def force(self, hom_f):
        
        return (Force_on_bally(tot_EM_field_at_charge(self.position), self)+ hom_f)/self.mass  

    def fh_update(self, hom_f = np.zeros(3)):
        self.fh.appendleft(self.force(hom_f))
        
    def acceleration_compute(self,force):
        a = force/self.mass
        self.acceleration += a
        
    def move(self):
             
        self.velocity += self.acceleration*dt  
        self.position += self.velocity*dt 
           
        
    def corrected_move(self,hom_f):
        a = Force_on_bally(tot_EM_field_at_charge(self.position), self)/self.mass  +hom_f                      
        self.position -= self.velocity*dt
        self.velocity += (a-self.acceleration)*dt/2  
        self.position += self.velocity*dt
        
        self.acceleration = (a+self.acceleration)/2    
        
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
         


 
                
            
         
ballys = []
hist = deque(maxlen = int(1/dt))

for i in range(Ball_num):
    #ballys.insert(i, Ball(r.randrange(300,display['width'] - 5, 10),r.randrange(200,display['height']/2,1)   , r.randrange(5,10,1),(r.randint(1,255),r.randint(1,255),r.randint(1,255)), r.randint(-200,200)/1000, r.randint(-200,200)/1000))
    ballys.insert(i, Ball(1,10,0.008,V = np.array([0,0,5*(-1)**(2+i)], dtype = float), X = np.array([i*30*(-1)**(2+i) , i*30*(-1)**(1+i) , i*30*(-1)**(2+i)], dtype = float)))
    #ballys.insert(i, Ball(1,10,0.0001,V = np.array([10,0,0], dtype = float), X = np.array([-25, 0, 0], dtype = float)))
    #ballys.insert(i, Ball(1,10,-0.0001,V = np.array([0,0,3], dtype = float), X = np.array([25, 0, 0], dtype = float)))
#ballys.append(Ball(1,-0.0004,V = np.array([0,0,0], dtype = float), X = np.array([0,0,0], dtype = float))) 
ballys.append(Ball(1,10,0.008,V = np.array([0,2,0], dtype = float), X = np.array([50,50,0], dtype = float)))
ballys.append(Ball(1,10,0.008,V = np.array([0,0,0], dtype = float), X = np.array([-50,-50,0], dtype = float)))
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
                    pointers.append(pointer(20, pointer_grid_x[i], pointer_grid_y[j], pointer_grid_y[k]))
            
    pointers = np.array(pointers)        

grav = np.array([0.,-0.01,0.])
angularVector = np.array([0.,0.,2])
crashed = False
index = 0

@np.vectorize
def arrow_update(zeiger):                     
    zeiger.dic_update()
        
      
def stoss(i,bally):
    
    for bally2 in ballys[i+1:]:           
    #checks collisions
        if  norm(bally.position - bally2.position) <= bally.radius  + bally2.radius  :

            bally.velocity_2 = (bally.mass * bally.velocity + bally2.mass * bally2.velocity + bally2.mass *(bally2.velocity - bally.velocity))/ (bally.mass + bally2.mass)
            bally2.velocity_2 = (bally.mass * bally2.velocity + bally.mass * bally.velocity + bally.mass *(bally.velocity - bally2.velocity))/ (bally2.mass + bally.mass)

            #prevents balls getting stuck in each other and assignes new velocitys
            if not(norm(bally.position + bally.velocity_2  - (bally2.position + bally2.velocity_2) ) <= bally.radius + bally2.radius):
                    bally.velocity = bally.velocity_2
                    bally2.velocity = bally2.velocity_2
      
S = integriere(hist)  
     
def main(): 
    i = 0           
    while 1 :
             
        rate(1/dt) 
        if gwee.running:              
            if show_field == True :       
                arrow_update(pointers)
            S.midpoint(ballys)        
        i+=1
main()
for bally in ballys:
    bally.fh_update()
      
while 1:
       
    rate(1/dt)
          
    if show_field == True : 
        arrow_update(pointers)
    S(ballys) 
    
        
        
