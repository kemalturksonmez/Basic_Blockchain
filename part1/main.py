#!/usr/bin/env python3
"""
    @author: Kemal Turksonmez
"""
from ui import UI
import threading

lock = threading.Lock()
minerNum = 1
ui = UI(minerNum, lock)