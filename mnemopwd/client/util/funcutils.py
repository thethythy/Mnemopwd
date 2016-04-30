# -*- coding: utf-8 -*-

# Copyright (c) 2015-2016, Thierry Lemeunier <thierry at lemeunier dot net>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this 
# list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# ---------------------------------------------------------
# Singleton class

def singleton(the_class):
    instances = {} # Dictionary of singleton objects
    def get_instance():
        if the_class not in instances:
            # Create a singleton object and store it
            instances[the_class] = the_class()
        return instances[the_class]
    return get_instance
    
# ---------------------------------------------------------
# Design pattern Observer

class Subject():
    """
    Subject of observation
    """
    
    def __init__(self):
        """Initiliaze the attribut self.observers = []"""
        self.observers = [] # List of observers
        
    def addObserver(self, obs):
        """Add a new observer"""
        if isinstance(obs, Observer):
            self.observers.append(obs)
    
    def delObserver(self, obs):
        """Delete an observer"""
        if isinstance(obs, Observer):
            self.observers.remove(obs)
            
    def update(self, property, value):
        """Update all the observers"""
        for obs in self.observers: obs.update(property, value)

class Observer():
    """
    An observer of the subject
    """
    
    def update(self, property, value):
        """Update the observer"""
        pass

# ---------------------------------------------------------
# sfill(n) : fill a string of n space character

def sfill(n):
    string = ''
    for i in range(n): string += ' '
    return string

