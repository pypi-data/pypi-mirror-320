import axinite.tools as axtools
import axinite as ax
from vpython import *
from itertools import cycle
from astropy.coordinates import CartesianRepresentation
import os, signal
  
def to_vec(v): 
    print(v)
    return vec(v[0], v[1], v[2])

def vpython_frontend(args: axtools.AxiniteArgs, mode: str, **kwargs):
    if mode == "live" or mode == "run":
        return vpython_live(args, **kwargs)
    elif mode == "show":
        return vpython_static(args, **kwargs)
    
def vpython_live(args: axtools.AxiniteArgs):
    if args.rate is None:
        args.rate = 100
    if args.radius_multiplier is None:
        args.radius_multiplier = 1
    if args.retain is None:
       args.retain = 200
    
    scene = canvas(title=args.name)
    scene.select()

    colors = cycle([color.red, color.blue, color.green, color.orange, color.purple, color.yellow])

    global pause
    pause = False
    def pause_handler():
        global pause
        pause = not pause

    global _rate
    _rate = args.rate
    def rate_hander(evt):
        global _rate
        _rate = evt.value
    button(text='Pause', bind=pause_handler, pos=scene.caption_anchor)
    slider(bind=rate_hander, min=1, max=1000, value=+_rate, step=1, right=15, length=200, pos=scene.caption_anchor)

    spheres = {}
    labels = {}
    lights = {}

    for body in args.bodies:
        body_color = axtools.string_to_color(body.color, "vpython") if body.color != "" else next(colors)
        body_retain = body.retain if body.retain != None else args.retain
        spheres[body.name] = sphere(pos=to_vec(body.r[0]), radius=body.radius.value * args.radius_multiplier, color=body_color, make_trail=True, retain=body_retain, interval=10)
        labels[body.name] = label(pos=spheres[body.name].pos, text=body.name, xoffset=15, yoffset=15, space=30, height=10, border=4, font='sans')
        if body.light == True: 
            lights[body.name] = local_light(pos=to_vec(body.r[0]), color=body_color)
            attach_light(spheres[body.name], lights[body.name])

    def fn(bodies, t, **kwargs):
        try:
            global _rate, pause
            rate(_rate)
            for body in bodies:
                print(body["r"][int(t / kwargs["delta"])] )
                print(int(t / kwargs["delta"]))
                spheres[body["n"]].pos = to_vec(body["r"][int(t / kwargs["delta"])])
                labels[body["n"]].pos = spheres[body["n"]].pos
                try: lights[body["n"]].pos = spheres[body["n"]].pos
                except: pass
            print(f"t = {t}", end='\r')
            if pause: 
                while pause: rate(10)
        except KeyboardInterrupt:
            os.kill(os.getpid(), signal.SIGINT)

    return fn, lambda: os.kill(os.getpid(), signal.SIGINT)

def vpython_static(args: axtools.AxiniteArgs):
    if args.rate is None:
        args.rate = 100
    if args.radius_multiplier is None:
        args.radius_multiplier = 1
    if args.retain is None:
       args.retain = 200
       
    scene = canvas(title=args.name)
    scene.select()

    colors = cycle([color.red, color.blue, color.green, color.orange, color.purple, color.yellow])

    def fn(body: axtools.Body):
        body_color = axtools.string_to_color(body.color, "vpython") if body.color != "" else next(colors)
        
        label(pos=to_vec(body.r[0]), text=body.name, xoffset=15, yoffset=15, space=30, height=10, border=4, font='sans', color=body_color)
        curve(pos=[to_vec(r) for r in body.r.values()], color=body_color)
        sphere(pos=to_vec(body.r[0]), radius=body.radius.value * args.radius_multiplier, color=body_color, opacity=0.2, make_trail=False)

    return fn, None, lambda: os.kill(os.getpid(), signal.SIGINT)