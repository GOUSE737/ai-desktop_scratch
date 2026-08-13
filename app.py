import sys
import os
from gui.dashboard import AssistantDashboard

def launch_gui():
    """Launches the desktop assistant GUI dashboard."""
    app = AssistantDashboard()
    app.mainloop()

if __name__ == "__main__":
    launch_gui()
