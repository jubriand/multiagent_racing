import sys, math
import pygame
import pygame.draw
import time

__circuit__ = ((10,10),(20,20),(35,70),(600, 380),(550,40))
__screenSize__ = (640,480)

# Utility functions for handling points
# I should probably build a class of vectors
def vecDiff(v1,v2):
    return (v1[0]-v2[0],v1[1]-v2[1])
def vecAdd(v1,v2):
    return (v2[0]+v1[0],v2[1]+v1[1])
def vecScalarMult(v, s):
    return (v[0]*s, v[1]*s)
def vecDot(v1, v2):
    return v1[0]*v2[0]+v1[1]*v2[1];
def vecInter(scalar, v1, v2):
    return (v1[0]+scalar*(v2[0]-v1[0]), v1[1]+scalar*(v2[1]-v2[0]))
def approximateLength(v1):
    '''This should be rewritten with an approximate length function (approximating it with no sqrt calls)'''
    return math.sqrt(v1[0]**2+v1[1]**2)
def approximateDistance(v1,v2):
    return approximateLength(vecDiff(v1,v2))


# Handles Vehicules
class Vehicule:
    #faire une voiture qui répare les autres
    _coords = (0,0)   # vector
    _speed = (1,1)    # vector
    _maxspeed = 15 
    _force = (0,0)  # accelerating force
    _maxforce = 10
    _color = (200,100,100)
    _colorfg = tuple([int(c/2) for c in _color])
    _radius=5
    _seeInFuture = 3
    _collision=False

    def __init__(self, coords=(0,0), speed=(1,1), force =(1,1),radius= 5):
        self._radius=radius
        self._coords = coords
        self._speed = speed
        self._force = force
        self._collision=False

    def position(self): return self._pos

    def steerUpdate(self, track, vehicules):
        self._force = (0,0)
        self._force = vecAdd(self._force, self.steerPathFollow(track))
        #self.steerGroup( vehicules)

    def steerPathFollow(self, track):
        (s,p,l) = track._closestSegmentPointToPoint(self._coords) #bestLength, bestPoint, bestSegment
        # TODO: We should first add a force if l is too large (too far from the middle of the track) 
        if l > s :
            newForce=(50,50)
        # This is the future position
        (sf, futurePosition) = track._segmentPointAddLength(s, p, max(10,approximateLength(self._speed)) * self._seeInFuture) 
        
        
        # We just have to register a force to get to futurePosition !
        force = vecDiff(futurePosition, self._coords)
        force = vecScalarMult(force,self._maxforce/approximateLength(force))
        return force
       
        
    def steerGroup(self, vehicules):
        forceAtt = (4,4)
        
        for v in vehicules:
            if v is not self :
                v._force=forceAtt
                break
            break
                
                
    def steerSeparation(self, vehicules):
         forceAccu=(0,2) # starts with a fresh force #TODO mettre l'inverse de la vitesse
         #for v in vehicules:
# =============================================================================
# 
#          while self._collision==True:
#               
#               self._force=forceAccu
#               self._maxspeed=2
#               self._color=(100,200,100)
#               self._collision=False
#         
# =============================================================================
         


    def drawMe(self, screen):
        pygame.draw.circle(screen,self._color,   self._coords,self._radius,0)
        pygame.draw.circle(screen,self._colorfg, self._coords,self._radius,1)

class Ambulance(Vehicule):
        _color=(100,200,100)      
        _maxspeed=10
        _healingRadius=20
        def __init__(self,coords):
            super().__init__(coords=coords, radius=8)
        
        def drawMe(self, screen):
            pygame.draw.circle(screen,self._color,   self._coords,self._radius,0)
            pygame.draw.circle(screen,self._colorfg, self._coords,self._radius,1)
            pygame.draw.circle(screen, self._color, self._coords, 20, width=1)
           
class SetOfVehicules:
    _vehicules = []
    _ambulances = []
    for k in range (len(_vehicules)):
        if (isinstance(k,Ambulance)==True):
            _ambulances.append(_vehicules[k])

    def handleCollisions(self):
        " Simple collision checking. Not a very good one, but may do the job for simple simulations"
        for i,v1 in enumerate(self._vehicules):
            for v2 in self._vehicules[i+1:]:
                #if (v1 is Ambulance==False and v2 is Ambulance==False):
                    offset = vecDiff(v2._coords, v1._coords)
                    al = approximateLength(offset)
                    if al != 0 and al < v1._radius + v2._radius - 1: # collision
                            v1._coords=(int(v1._coords[0]+offset[0]/al*(v1._radius+v2._radius)),
                                        int(v2._coords[1]+offset[1]/al*(v1._radius+v2._radius))) 
                            
                            #if (v1 is Ambulance==True):
                            if (isinstance(v1,Ambulance)==True):
                                v1._collision=False
                                v2._collision=False
                            v1._collision=True
                            v2._collision=True  

                                
    def handleHealing(self):
        " Simple collision checking. Not a very good one, but may do the job for simple simulations"
        for i,v1 in enumerate(self._vehicules):
            if (isinstance(v1,Ambulance)==True):
                for v2 in self._vehicules[i+1:]:
                    #if (v1 is Ambulance==False and v2 is Ambulance==False):
                        offset = vecDiff(v2._coords, v1._coords)
                        al = approximateLength(offset)
                        if al != 0 and al <= v1._healingRadius: # collision
                                
                                v1._color=(200,200,100)                               
                                #v2._color=(200,200,100)
                                v2._maxspeed=10 
                                v2._collision=False
        
                        
    def lookAhead(self , car, distanceAfar=2):

        for v in self._vehicules:
            l_car = approximateLength(car._speed)*distanceAfar
            l_v = approximateLength(v._speed)
            if l_car<l_v:
                car._maxspeed=v._maxspeed
                car._color = (100,200,100)
    
    def updateCollisions(self):
        for v in self._vehicules:
            if v._collision==True:
                v._color=(100,100,200)
                v._speed=(0,0)
                v._maxspeed=0
            if (isinstance(v,Ambulance)==True):
                v._collision=False
                v._color=(100,200,100)
                v._maxspeed=10
            if v._collision==False:
                v._maxspeed=10
            #elif v._collision==False: 
            #     v._color=(100,100,100)
            #     if (v is Ambulance):
            #         v._maxspeed=Ambulance._maxspeed
            #     else:
            #         v._maxspeed=Vehicule._maxspeed
            

    def updatePositions(self):
        for v in self._vehicules:
            v._speed = vecAdd(v._speed, v._force)
            l = approximateLength(v._speed)
            if l > v._maxspeed:
                v._speed = vecScalarMult(v._speed, v._maxspeed / l)
            v._coords= (v._coords[0]+int(v._speed[0]), v._coords[1]+int(v._speed[1]))
            
            

    def append(self,item):
        self._vehicules.append(item)

    def drawMe(self, screen, scene = None):
        for v in self._vehicules: v.drawMe(screen)


class Track:
    _circuit = None
    _cback = (128,128,128)
    _cfore = (10,10,10)
    _width = 30
    _screen = None
    _cachedLength = []
    _cachedNormals = []

    def __init__(self, screen):
        self._circuit = __circuit__
        self._screen = screen
        for i in range(0,len(self._circuit)):
            self._cachedNormals.append(vecDiff(self._circuit[i], self._circuit[len(self._circuit)-1 if i-1 < 0 else i-1]))
            self._cachedLength.append(approximateLength(self._cachedNormals[i]))
            self._cachedNormals[i] = (self._cachedNormals[i][0]/self._cachedLength[i], self._cachedNormals[i][1]/self._cachedLength[i] )


    def _segmentPointAddLength(self, segment, point, length):
        ''' get the segment and point (on it) after adding length to the segment and point (on it), by following the
        path'''
        nextStep = approximateDistance(point, self._circuit[segment])
        if nextStep > length: # We stay on the same segment
            nextPoint = vecAdd(point, vecScalarMult(self._cachedNormals[segment], length))
            return (segment, (int(nextPoint[0]), int(nextPoint[1])))
        length -= nextStep
        segment = segment+1 if segment+1<len(self._circuit) else 0
        while length > self._cachedLength[segment]:
            length -= self._cachedLength[segment]
            segment = segment+1 if segment+1<len(self._circuit) else 0
        nextPoint = vecAdd(self._circuit[segment-1 if segment > 0 else len(self._circuit)-1],
                vecScalarMult(self._cachedNormals[segment], length))
        return (segment, (int(nextPoint[0]), int(nextPoint[1])))
    
    def _closestSegmentPointToPoint(self,point):
        bestLength = None
        bestPoint = None
        bestSegment = None
        for i in range(0, len(self._circuit)):
            p = self._closestPointToSegment(i,point)
            l = approximateDistance(p,point)
            if bestLength is None or l < bestLength:
                bestLength = l
                bestPoint = p
                bestSegment = i
        return (bestSegment, bestPoint, bestLength)

    def _closestPointToSegment(self, numSegment, point):
        ''' Returns the closest point on the circuit segment from point'''
        p0 = self._circuit[len(self._circuit)-1 if numSegment-1 < 0 else numSegment-1]
        p1 = self._circuit[numSegment]
        local = vecDiff(point, p0)
        projection = vecDot(local, self._cachedNormals[numSegment])
        if projection < 0:
            return p0
        if projection > self._cachedLength[numSegment]:
            return p1
        return vecAdd(p0,vecScalarMult(self._cachedNormals[numSegment], projection))


        
        
        
    def drawMe(self, scene = None):

        for p in self._circuit: # Draw simple inner joins
            pygame.draw.circle(self._screen,self._cback,p,int(self._width/2),0)
        pygame.draw.lines(self._screen, self._cback, True, self._circuit, self._width)
        pygame.draw.lines(self._screen, self._cfore, True, self._circuit, 1)

        if True:
            for i,p in enumerate(self._circuit):
                pygame.draw.line(self._screen, (0,0,250), p, vecAdd(p,vecScalarMult(self._cachedNormals[i], 50)))

        # if scene is not None:
        #     for i,p in enumerate(self._circuit):
        #         scene.drawText(str(int(self._cachedLength[i])), p)

class Scene:
    _track= None
    _vehicules = None
    _screen = None
    _font = None

    _mouseCoords = (0,0)

    def __init__(self, screenSize = __screenSize__):
        pygame.init()
        self._screen = pygame.display.set_mode(screenSize)
        self._track = Track(self._screen)
        self._vehicules = SetOfVehicules()
        #self._font = pygame.font.SysFont('Arial', 25)

    def drawMe(self):
        self._screen.fill((0,0,0))
        self._track.drawMe(scene = self)
        self._vehicules.drawMe(self._screen, scene = self)

        # Illustrate the closestSegmentPointToPoint function
        (s,p,l) = self._track._closestSegmentPointToPoint(self._mouseCoords)
        pygame.draw.line(self._screen, (128,255,128),p, self._mouseCoords)
        #print(self._track._segmentPointAddLength(s,p,150))
        pygame.draw.circle(self._screen, (128,255,128),self._track._segmentPointAddLength(s,p,150)[1],20,1)

        pygame.display.flip()

    def drawText(self, text, position, color = (255,128,128)):
        self._screen.blit(self._font.render(text,1,color),position)

    def update(self):
        for v in self._vehicules._vehicules:
            v.steerUpdate(self._track, self._vehicules)
            v.steerSeparation(self._vehicules)
            #self._vehicules.lookAhead(v)
            #v.steerGroup(v)

        self._vehicules.updateCollisions()
        self._vehicules.updatePositions()
        self._vehicules.handleCollisions()
        self._vehicules.handleHealing()
        self.drawMe()

            

    def eventClic(self,coord,b,val):
        print("Adding Vehicule at ",coord[0],",",coord[1])
        print(val)
        if val==1:
            self._vehicules.append(Vehicule((coord[0],coord[1])))
        if val==3:
            self._vehicules.append(Ambulance((coord[0],coord[1])))
        
    def recordMouseMove(self, coord):
        self._mouseCoords = coord

def main():
    scene = Scene()
    done = False
    clock = pygame.time.Clock()
    while done == False:
        clock.tick(20)
        scene.update()
        scene.drawMe()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: done=True
            if event.type == pygame.KEYDOWN: done=True
            if event.type == pygame.MOUSEBUTTONDOWN:
                scene.eventClic(event.dict['pos'],event.dict['button'],event.button)
            elif event.type == pygame.MOUSEMOTION:
                scene.recordMouseMove(event.dict['pos'])

    pygame.quit()

if not sys.flags.interactive: main()

