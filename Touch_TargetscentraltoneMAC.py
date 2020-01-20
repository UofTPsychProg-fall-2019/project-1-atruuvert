#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
The Gap Effect Replication Experiment
@author: annie truuvert
"""
# Required set up 
import numpy as np
import pandas as pd
import os, sys, csv
from psychopy import visual, core, event, gui, logging, sound
import random
from random import shuffle
from psychopy.hardware import keyboard
from psychopy.sound import Sound
import sounddevice as sd
from struct import pack
from math import sin, pi
import wave

defaultKeyboard = keyboard.Keyboard()

# Set up dialog for entering participant info

expInfo = {"SubjectNumber":'',"Age":'',"Gender":'',"Handedness":''}
subgui = gui.DlgFromDict(expInfo)

if subgui.OK == False:
    core.quit()  # user pressed cancel

# Save the data
subNum = expInfo["SubjectNumber"]
age = expInfo["Age"]
gend = expInfo["Gender"]
hand = expInfo["Handedness"]

# Open a grey full screen window
win = visual.Window(fullscr=True, allowGUI=False, color='grey', unit='height')

# Setting up instruction pages

welcome_text = visual.TextStim(win=win, name='welcome_text',
    text='Welcome to the experiment. \n\nIn this experiment, you will be using your index finger to move as quickly and accurately as possible to a target that appears on the left or right side of the screen.\n\nTouch the box to continue.',
    font='Arial',
    pos=(0, 0), height=0.04, wrapWidth=1, ori=0, 
    color='white', colorSpace='rgb', opacity=1, 
    languageStyle='LTR',
    depth=0.0);

instructions_part2 = visual.TextStim(win=win, name='instructions_part2',
    text='On every trial, a central fixation cross will appear. Place your finger on the home box below it, and keep your eyes on the cross, and the trial will begin. A sound will indicate that the target will appear. Do not move your finger from the home box until the target appears. Your task is to touch the target as quickly and accurately as possible.\n\nTouch the box to begin practice.',
    font='Arial',
    pos=(0, 0), height=0.04, wrapWidth=1, ori=0, 
    color='white', colorSpace='rgb', opacity=1, 
    languageStyle='LTR',
    depth=0.0);
    
# Setting up 'next' boxes

next_box = visual.Rect(win=win,
    width=0.05, height=0.05,
    lineWidth=5, lineColor='white',
    lineColorSpace='rgb', fillColor='white',
    pos=(0.3,-0.3), ori=0.0, opacity=1.0, 
    depth=0, interpolate=True, 
    autoDraw=False);

begin_practice_box = visual.Rect(win=win,
    width=0.05, height=0.05,
    lineWidth=5, lineColor='white',
    lineColorSpace='rgb', fillColor='white',
    pos=(0.0,-0.4), ori=0.0, opacity=1.0, 
    depth=0, interpolate=True, 
    autoDraw=False);

# Setting up end of practice mode

end_practice = visual.TextStim(win=win,
    text='Practice complete. Touch the box to begin the experiment.',
    font='Arial',
    pos=(0, 0), height=0.04, wrapWidth=1, ori=0, 
    color='white', colorSpace='rgb', opacity=1, 
    languageStyle='LTR',
    depth=0.0);

# Setting up early release warning screen

early_release = visual.TextStim(win=win,
    text='YOU MOVED TOO EARLY! You may move your finger ONLY once the target appears.',
    font='Arial',
    pos=(0, 0), height=0.04, wrapWidth=1, ori=0, 
    color='white', colorSpace='rgb', opacity=1, 
    languageStyle='LTR',
    depth=0.0);

# Setting up start of trial (fixation cross and home square)

fixation_start = visual.TextStim(win=win, name='fixation_start',
    text='+',
    font='Arial',
    pos=(0, 0), height=0.1, wrapWidth=None, ori=0, 
    color='black', colorSpace='rgb', opacity=1);
    
home_start = visual.Rect(win=win,
    width=0.05, height=0.05,
    lineWidth=5, lineColor='black',
    lineColorSpace='rgb', fillColor=None,
    pos=(0.0,-0.095), ori=0.0, opacity=1.0, 
    depth=0, interpolate=True, 
    autoDraw=False);
    
# Setting up central fixation dot
central_fixation_5 = visual.Circle(win=win,
    radius=0.01,
    lineWidth=5, lineColor='black',
    lineColorSpace='rgb', fillColor='black',
    pos=(0,0), opacity=1.0); 
    
central_fixation_7 = visual.Circle(win=win,
    radius=0.015,
    lineWidth=5, lineColor='black',
    lineColorSpace='rgb', fillColor='black',
    pos=(0,0), opacity=1.0); 

# Setting up target

# Right
target_R = visual.Circle(win=win,
    radius=0.01,
    lineWidth=5, lineColor='black',
    lineColorSpace='rgb', fillColor='black',
    pos=(0.35,0), opacity=1.0); 

# Left
target_L = visual.Circle(win=win,
    radius=0.01,
    lineWidth=5, lineColor='black',
    lineColorSpace='rgb', fillColor='black',
    pos=(-0.35,0), opacity=1.0); 
    

# Setting up landing pads to track target touches

left_box = visual.Rect(win=win,
    width=.8, height=1, 
    lineWidth=5, lineColor='black',
    lineColorSpace='rgb', fillColor=None,
    pos=(-0.45,0), ori=0.0, opacity=0, 
    depth=0, interpolate=True, 
    autoDraw=False)

right_box = visual.Rect(win=win,
    width=.8, height=1, 
    lineWidth=5, lineColor='black',
    lineColorSpace='rgb', fillColor=None,
    pos=(0.45,0), ori=0.0, opacity=0, 
    depth=0, interpolate=True, 
    autoDraw=False)

# Setting up auditory warning signal

sd.default.samplerate = 44100

time = 0.050
frequency = 500

samples = np.arange(44100 * time) / 44100.0  # Generate time of samples between 0 and 50ms
wave = 10000 * np.sin(2 * np.pi * frequency * samples) # Recall that a sinusoidal wave of frequency f has formula w(t) = A*sin(2*pi*f*t)
wav_wave = np.array(wave, dtype=np.int16) # Convert it to wav format (16 bits)

# Setting up mouse

mouse = event.Mouse(visible=True) # Visible for programming purposes only; CHANGE FOR ACTUAL EXPERIMENT !!!

# Setting up timer

trialClock = core.Clock()
expClock = core.Clock()

# **********************************************************************************************************************

with open('{}.csv'.format(subNum), 'w') as f:
    writer = csv.writer(f, delimiter=',')
    writer.writerow(['subNum', 'age', 'gend', 'hand','trial', 'cond', 'target_side', 'at home', 'tone time', 'offset time', 'target time','RT', 'MT', 'landing_position', 'early'])

    # DEFINING A TRIAL

    conditions = ['R0', 'L0', 'R0.100', 'L0.100', 'R0.150', 'L0.150', 'R0.200', 'L0.200', 'R0.250', 'L0.250', 'R0.300', 'L0.300']*40
    shuffle(conditions)
    central_dot_sizes = [central_fixation_5, central_fixation_7]*240
    shuffle(central_dot_sizes)
    
    def trial():
        
        expClock.reset()
        mouse.clickReset()
        
        cond = float(conditions[t][1:])
        target_side = conditions[t][0]
        central_fixation = central_dot_sizes[t]
        
        RT = 0
        MT = 0
        landing_position = (0,0)
        early = 0
        
        at_home = 0
        tone_plays = 0
        central_offsets = 0
        target_appears = 0
        
        if target_side == 'L':
            target = target_L
            box = left_box
        elif target_side == 'R':
            target = target_R
            box = right_box
        
        nothing_happening = True  # To keep everything as is until mouse has been pressed
        
        while nothing_happening:
            
            if event.getKeys(keyList = ['q']): # quit function
                core.quit() 
            
            fixation_start.draw()
            home_start.draw()
            left_box.draw()
            right_box.draw()
            win.flip()
            
            if mouse.isPressedIn(home_start, buttons=(0,1,2)):  # Participant placed finger in home box to begin trial
                nothing_happening = False
        
        at_home = expClock.getTime()
        check_for_release()
        
        # OVERLAP
        if cond == 0:  
            trial_begin = True
            while trial_begin:
                
                central_fixation.draw()  # If overlap condition, central fixation dot remains on screen
                home_start.draw()
                left_box.draw()
                right_box.draw()
                win.flip()
                core.wait(0.500)  # Wait 500ms after finger pressed in home box before trial begins
                
                trial_begin = False
                
            no_touch = True  # Keep target on screen until participant has tried to touch it
            while no_touch:
                
                check_for_release()
                
                sd.play(wav_wave)
                central_fixation.draw()
                home_start.draw()
                left_box.draw()
                right_box.draw()
                win.flip()
                
                no_touch = False
                
            tone_plays = expClock.getTime() - at_home
            
            # AFTER TARGET APPEARS: Timing the release
            mouse.clickReset()
            
            core.wait(0.200)  # Wait 200ms
            
            trialClock.reset()
            
            target_appears = (expClock.getTime() - tone_plays - at_home)
            target_on = True
            while target_on:
                
                central_fixation.draw()
                home_start.draw()
                left_box.draw()
                right_box.draw()
                target.draw()  # Target appears
                win.flip()
                
                while RT == 0:
                    if not mouse.isPressedIn(home_start, buttons=(0,1,2)): # If mouse was in the home box, but isn't anymore, this is the release time
                        RT = trialClock.getTime()
                    
                if mouse.isPressedIn(left_box, buttons=(0,1,2)): # If finger touches screen, get position and movement time
                    MT = trialClock.getTime()
                    landing_position = mouse.getPos()
                    target_on = False
                if mouse.isPressedIn(right_box, buttons=(0,1,2)): 
                    MT = trialClock.getTime()
                    landing_position = mouse.getPos()
                    target_on = False
        
        # GAP
        else:
            
            central_fixation.draw()
            home_start.draw() 
            left_box.draw()
            right_box.draw()
            win.flip()
            
            core.wait(0.500)  # Wait 500ms after finger pressed in home box before trial begins
            
            sd.play(wav_wave)  # If gap condition, central fixation offsets at the same time as the tone
            
            home_start.draw()  
            left_box.draw()
            right_box.draw()
            win.flip()
            
            tone_plays = expClock.getTime() - at_home
            
            central_offsets = (expClock.getTime() - tone_plays - at_home)

            no_touch = True  # Keep target on screen until participant has tried to touch it
            while no_touch:
                    
                home_start.draw()
                left_box.draw()
                right_box.draw()
                win.flip()
                
                check_for_release()
                
                no_touch = False
                
            # AFTER TARGET APPEARS: Timing the release
            mouse.clickReset()
            
            core.wait(cond)  # Wait condition gap duration
            
            trialClock.reset()
            
            target_appears = (expClock.getTime() - central_offsets - tone_plays - at_home)
            target_on = True
            while target_on:
                
                home_start.draw()
                left_box.draw()
                right_box.draw()
                target.draw()  # Target appears
                win.flip()
                
                while RT == 0:
                   if not mouse.isPressedIn(home_start, buttons=(0,1,2)): # If mouse was in the home box, but isn't anymore, this is the release time
                       RT = trialClock.getTime()
                    
                if mouse.isPressedIn(left_box, buttons=(0,1,2)): # If finger touches screen, get position and movement time
                    MT = trialClock.getTime()
                    landing_position = mouse.getPos()
                    target_on = False
                if mouse.isPressedIn(right_box, buttons=(0,1,2)): 
                    MT = trialClock.getTime()
                    landing_position = mouse.getPos()
                    target_on = False
        
        writer.writerow([subNum, age, gend, hand, t, cond, target_side, at_home, tone_plays, central_offsets, target_appears, RT, MT, landing_position, early])  # Save trial as row in participant file
        mouse.clickReset()
    
    def check_for_release():
        cond = float(conditions[t][1:])
        target_side = conditions[t][0]
        central_fixation = central_dot_sizes[t]
        RT = 0
        MT = 0
        landing_position = (0,0)
        early = 0
        at_home = 0
        tone_plays = 0
        central_offsets = 0
        target_appears = 0
        if not mouse.isPressedIn(home_start, buttons=(0,1,2)): # If mouse isn't in the home box, and the target not drawn, released too early
            early = 1
            show_warning = True
            while show_warning:
                early_release.draw()
                win.flip()
                core.wait(4)
                show_warning = False
            writer.writerow([subNum, age, gend, hand, t, cond, target_side, at_home, tone_plays, central_offsets, target_appears, RT, MT, landing_position, early]) # early note "1" added on end of every failed trial
            trial()  # Restart trial
    
    # EXPERIMENT BEGINS

    # Go through the instructions

    welcome_sequence = [welcome_text, instructions_part2]
    next = [next_box, begin_practice_box]
    i = 0
    while i in range(len(welcome_sequence)):
        mouse.clickReset()
        welcome_sequence[i].draw()
        next[i].draw()
        win.flip()
        if mouse.isPressedIn(next[i], buttons=(0,1,2)):
            i+=1
    win.flip()
    mouse.clickReset()
    
    # Loop through practice trials

    t = 0
    while t in range(30):
        trial()
        t+=1
    
    # End practice and prompt to begin experiment
    
    transition = True
    while transition:
        end_practice.draw()
        next_box.draw()
        win.flip()
        if mouse.isPressedIn(next_box, buttons=(0,1,2)):
            mouse.clickReset()
            transition = False
    
    # Loop through experiment trials
    
    shuffle(conditions)
    shuffle(central_dot_sizes)
    
    t = 0
    while t in range(480):
        trial()
        t+=1

# Clean up

core.wait(2)
win.close()