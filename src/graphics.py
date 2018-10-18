from vpython import *
from planets import planet_list
import random

# center: Location at which the camera continually looks
scene = canvas(title='Space Simulator', align="left", width=600, height=600, center =vector(0,0,0))

planets = []

def planet_init(planetData):  # retrieves data from planet dictionary and creates a planet
    pTexture = 'textures/' + planetData['name'] + '.jpg'
    x = random.randint(-600, 600)

    pSphere = sphere(pos =vector(x,0,0), radius = x, texture=pTexture, make_trail = True)
    return pSphere  # return a sphere object

def planet_update(planets):
    x=random.randint(-600,600)
    print(x)
    for i in planets:
        i.pos=vector(x,0,0)



def main():
    for planet in planet_list:
        print(planet['name'])
        planets.append(planet_init(planet))

    Crahsed = False
    for i in range(3000):
        rate(100)
        planet_update(planets)


if __name__ == "__main__":
    main()

"""
sun = sphere(pos=vector(0,0,0), radius = 100, color= color.orange)

earth = sphere(pos=vector(-200,0,0), radius = 30, texture=textures.earth,
               make_trail = True)

mercury = sphere(pos=vector(-400, 0, 0), radius = 50, texture = textures.flower,
                make_trail = True)
"""

"""

#earthVelocity = vector(0,0,3)

#mercuryVelocity = vector(0,0, 6)


# create graph display
velocityGraph =graph(width=600, height=600, align="right",
          title= '<b>Earth Velocity</b>',
          xtitle = '<i>time</i>', ytitle='<i>velocity</i>',
          foreground = color.black, background = color.white,
          xmax = 3000, xmin =0 , ymax=20, ymin=0)

# crayon for drawing graph
f1 =gcurve(color= color.red, label="EarthVelocity")




t=0

for i in range(3000):
    #box(pos=vec(0, 0, 0), shininess=0, texture={'file': textures.stones, 'bumpmap': bumpmaps.stones})
    # only loop 100 times in a second
    rate(100)
    # earth rotate
    #earth.rotate(angle=pi/4)
    #stars = sphere(radius=30066790000, texture=textures.granite)
    # earth moving position
    earth.pos = earth.pos + earthVelocity
    #mercury.pos = mercury.pos = mercuryVelocity
    PHYSICS: add in the force gravity
    # distance between earth and the sun using Pythagorean Theorem in 3 dimensions
    earthDist = (earth.pos.x**2 + earth.pos.y**2 + earth.pos.z**2)**0.5
    #mercuryDist = (mercury.pos.x**2 + mercury.pos.y**2 + mercury.pos.z**2)**0.5
    # Unit radial vector (https://www.quora.com/What-are-the-radial-unit-vector-and-the-tangential-unit-vector-in-a-circular-motion)
    radial_vector = (earth.pos - sun.pos)/earthDist
    #radial_vector2 = (mercury.pos - sun.pos)/mercuryDist
    # Force of gravity from Newton's Law
    #fgravity = -G*m*M*radial_vector/dist**2
    fGravity = -10000*radial_vector/earthDist**2
    #fGravity2 = -10000*radial_vector2/mercuryDist**2
    # The Earth's velocity will be changed by the force of gravity
    earthVelocity= earthVelocity+fGravity
    #mercuryVelocity = mercuryVelocity + fGravity2
    # The earth position will be changed by it's velocity
    earth.pos += earthVelocity
    #mercury.pos += mercuryVelocity

    # plot the earth velocity
    #f1.plot(pos = (t, mag(earthVelocity))) # magninute of the vector
    t += 1

   # if mercuryDist <= sun.radius: break

"""


