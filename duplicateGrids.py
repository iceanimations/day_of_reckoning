### feed in these values ###

particleName = 'DOR_VFX_16_04_nParticle'
cache = [
        r"P:\external\Epic_Pictures\Day_of_Reckoning\Test\Junaid.Farooq\Jin_Dust_Cycle\Jinn2_Dust_Cycle_Cache\ver02\dust_.fxd",
        ]
cache_range = (1, 16)
name = "ffx_dup"
preset = "ffx_preset1"
lights = [
        "directionalLight1",
        ]
use_cycle = True

front_direction = (0,0,-1)

###########################


import pymel.core as pc
import math

def createFFX():
    before = set(pc.ls(type='ffxDyna'))
    pc.mel.ffx_createFFXNode(0)
    after = set(pc.ls(type='ffxDyna'))
    return list(after.difference(before))[0]

def eulerAnglesBetween(aim, start=None):
    if start is None:
        start = pc.dt.Vector(1, 0, 0)
    aim = aim.normal()
    start = start.normal()
    dot = aim.dot(start)
    anglebetween = math.acos(dot)
    vector = start.cross(aim).normal() * math.sin(anglebetween/2)
    scalar = math.cos(anglebetween/2)
    quat = pc.dt.Quaternion(vector.x, vector.y, vector.z, scalar)
    return quat.asEulerRotation()

def createFFXForParticles(particle, parent, use_cycle=True):
    frames  =16
    particleIds = pc.getParticleAttr(particle, at='id', array=True)
    if not particleIds:
        return

    myFrames = pc.getParticleAttr(particle, at='myFrame', array=True)
    charIds = pc.getParticleAttr(particle, at='charId', array=True)
    locations = pc.getParticleAttr(particle, at='position', array=True)
    velocities = pc.getParticleAttr(particle, at='velocity', array=True)

    for num in range( len(particleIds) ):
        charId = charIds[num]
        zeroFrame = charId * frames
        myFrame = myFrames[num]
        if myFrame != zeroFrame:
            continue

        myId = particleIds[num]
        myName = parent.name() + '|' + name + '_%d'%int(myId)
        time = pc.currentTime(q=True)

        tr = None
        if use_cycle and pc.objExists(myName):
            tr = pc.PyNode(myName)
            f = tr.getShape()
        else:
            f = createFFX()

            if preset:
                pc.mel.applyPresetToNode(f.name(), "", "", preset, 1)

            for idx, light in enumerate( lights ):
                if pc.objExists(light):
                    pc.connectAttr(light + '.message', f.light[idx])

            tr = f.firstParent()
            pc.parent(tr, parent)
            pc.rename(tr, myName)
            pc.setKeyframe(tr.v, t=time-1, v=0)
            cache_idx = 0
            cache_idx = int(charId % len(cache))
            f.output_path.set(cache[cache_idx].replace('\\', '\\\\'))
            f.start_frame.set(cache_range[0])
            f.end_frame.set(cache_range[1])
            f.playback_start_frame.set(cache_range[0])
            f.playback_end_frame.set(cache_range[1])
            f.playback_start_offset.set(time)
            if use_cycle:
                f.playback_after_end_type.set(2)

        pc.setKeyframe(tr.t, t=time-1)
        tr.tx.set(locations[num*3])
        tr.ty.set(locations[num*3+1])
        tr.tz.set(locations[num*3+2])
        pc.setKeyframe(tr.t, t=time)

        pc.setKeyframe(tr.r, t=time-1)
        rot = eulerAnglesBetween( pc.dt.Vector(*velocities[num*3:num*3+3]),
                start = pc.dt.Vector(*front_direction) )
        tr.rx.set(math.degrees( rot.x ))
        tr.ry.set(math.degrees( rot.y ))
        tr.rz.set(math.degrees( rot.z ))
        pc.setKeyframe(tr.r, t=time)

        pc.setKeyframe(tr.v, t=time, v=1)

def createFFXForRange():

    start = int ( round(pc.playbackOptions(min=True,query=True)) )
    end = int( round(pc.playbackOptions(max=True,query=True)) )

    gr = pc.createNode('transform', name='ffx_grp')
    for time in range(start, end+1):
        pc.currentTime(time, edit=True)
        createFFXForParticles( particleName, gr, use_cycle )

if __name__ == "__main__":
    createFFXForRange()


