import tkinter as tk
from tkinter import CENTER, DISABLED, StringVar

from async_tkinter_loop import async_handler


# Frame to scan for exo
class ScanWindow(tk.Frame):
    # Initialize class
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.deviceNameText = StringVar()
        self.startTrialButton = None
        self.calTorqueButton = None
        self.create_widgets()

    # Holds all UI elements
    def create_widgets(self):
        titleLabel = tk.Label(
            self, text="ExoSkeleton Controller", font=("Arial", 40))
        titleLabel.place(relx=0.5, rely=0.1, anchor=CENTER)
        startScanLabel = tk.Label(self, text="Begin Scanning for Exoskeletons")
        startScanLabel.place(relx=0.5, rely=0.35, anchor=CENTER)
        startScanButton = tk.Button(
            self,
            text="Start Scan",
            command=async_handler(self.on_start_scan_button_clicked),
        )
        startScanButton.place(relx=0.5, rely=0.45, anchor=CENTER)
        self.deviceNameText.set("Not Connected")
        deviceNameLabel = tk.Label(self, textvariable=self.deviceNameText)
        deviceNameLabel.place(relx=0.5, rely=0.60, anchor=CENTER)
        self.startTrialButton = tk.Button(
            self,
            text="Start Trial",
            command=async_handler(self.on_start_trial_button_clicked),
            state=DISABLED,
        )
        self.startTrialButton.place(relx=0.75, rely=0.8)

        #Calibrate Torque
        self.calTorqueButton = tk.Button(
            self,
            text="Calibrate Torque",
            command=async_handler(self.on_calibrate_torque_button_clicked),
            state=DISABLED,
        )
        self.calTorqueButton.place(relx=0.75, rely=0.7, anchor=CENTER)

    # Async function to handle button click
    async def on_start_scan_button_clicked(self):
        self.deviceNameText.set("Scanning...")
        await self.startScanButtonClicked()

    # Start scanning for exo
    async def startScan(self):
        await self.controller.deviceManager.scanAndConnect()

    # Start scan and set device name flip start trial state
    async def startScanButtonClicked(self):
        await self.startScan()
        self.deviceNameText.set(self.controller.deviceManager.device)
        self.startTrialButton.config(state="normal")
        self.calTorqueButton.config(state="normal")

    # Handle start trial button clicked
    async def on_start_trial_button_clicked(self):
        await self.StartTrialButtonClicked()

    async def on_calibrate_torque_button_clicked(self):
        await self.controller.trial.calibrate(self.controller.deviceManager)

    # Switch frame to active trial and begin trial
    async def StartTrialButtonClicked(self):
        self.controller.show_frame("ActiveTrial")
        #wait self.controller.trial.calibrate(self.controller.deviceManager)
        await self.controller.trial.beginTrial(self.controller.deviceManager)
        #await self.controller.deviceManager.newStiffness(75)
