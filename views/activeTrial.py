import datetime as dt
import tkinter as tk
from tkinter import CENTER, StringVar

import matplotlib.animation as animation
import matplotlib.pyplot as plt
from async_tkinter_loop import async_handler
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import Data.SaveModelData as saveModelData


# Active Trial Frame
class ActiveTrial(tk.Frame):
    # Constructor for frame
    def __init__(self, parent, controller):
        super().__init__(parent)
        # Controller object to switch frames
        self.controller = controller
        #create our model controll names, frequently changed
        self.levelButtonName=StringVar()
        self.descendButtonName=StringVar()
        self.ascendButtonName=StringVar()
        self.modelButtonName=StringVar()
        self.deleteModelButtonName=StringVar()
        self.confirmation=0 #used as a flag to request second confirmation form user to delete model
        self.modelDataWriter = saveModelData.CsvWritter()
        

        self.create_widgets()

    # Frame UI elements
    def create_widgets(self):
        # Active Trial title label
        calibrationMenuLabel = tk.Label(
            self, text="Active Trial", font=("Arial", 40))
        calibrationMenuLabel.place(relx=0.5, rely=0.1, anchor=CENTER)
        
        batteryPercentLabel = tk.Label(
            self, textvariable=self.controller.deviceManager._realTimeProcessor._exo_data.BatteryPercent, font=("Arial", 12))
        batteryPercentLabel.place(relx=0.9, rely=0.1, anchor=CENTER)

        #Define Model Status
        modelStatusLabel = tk.Label(
            self, textvariable=self.controller.deviceManager._realTimeProcessor._predictor.modelStatus, font=("Arial", 12))
        modelStatusLabel.place(relx=0.75, rely=0.55)

        # Update torque button
        updateTorqueButton = tk.Button(
            self,
            text="Update Torque",
            command=lambda: self.controller.show_frame("UpdateTorque"),
        )
        updateTorqueButton.place(relx=0.75, rely=0.35)

        self.recalibrateFSRButton = tk.Button(
            self,
            text="Recalibrate FSRs",
            command=async_handler(self.on_recal_FSR_button_clicked),
        )
        self.recalibrateFSRButton.place(relx=0.75, rely=0.40)

        # End Trial Button
        endTrialButton = tk.Button(
            self,
            text="End Trial",
            command=async_handler(self.on_end_trial_button_clicked),
        )
        endTrialButton.place(relx=0.75, rely=0.8)

        # Mark Trial Button
        markButton = tk.Button(
            self,
            textvariable=self.controller.deviceManager._realTimeProcessor._exo_data.MarkLabel,
            command=async_handler(self.on_mark_button_clicked),
        )
        markButton.place(relx=0.85, rely=0.35)
        
        # Level Trial Button
        self.levelButtonName.set("Collect Level Data")
        levelTrialButton = tk.Button(
            self,
            textvariable=self.levelButtonName,
            command=async_handler(self.on_level_trial_button_clicked),
        )
        levelTrialButton.place(relx=0.75, rely=0.6)
        #Display Level Step Count 
        lvlstepsLabel = tk.Label(
            self, textvariable=self.controller.deviceManager._realTimeProcessor._predictor.levelStepsLabel, font=("Arial", 12))
        lvlstepsLabel.place(relx=0.7, rely=0.6)

        
        # Descend Trial Button
        self.descendButtonName.set("Collect Descend Data")
        descendTrialButton = tk.Button(
            self,
            textvariable=self.descendButtonName,
            command=async_handler(self.on_descend_trial_button_clicked),
        )
        descendTrialButton.place(relx=0.75, rely=0.65)
        #Display Descend Step Count 
        desstepsLabel = tk.Label(
            self, textvariable=self.controller.deviceManager._realTimeProcessor._predictor.descendStepsLabel, font=("Arial", 12))
        desstepsLabel.place(relx=0.7, rely=0.65)

        
        # Ascend Trial Button
        self.ascendButtonName.set("Collect Ascend Data")
        ascendTrialButton = tk.Button(
            self,
            textvariable=self.ascendButtonName,
            command=async_handler(self.on_ascend_trial_button_clicked),
        )
        ascendTrialButton.place(relx=0.75, rely=0.7)
        ascstepsLabel = tk.Label(
            self, textvariable=self.controller.deviceManager._realTimeProcessor._predictor.ascendStepsLabel, font=("Arial", 12))
        ascstepsLabel.place(relx=0.7, rely=0.7)

        #Create Model Button
        if (self.controller.deviceManager._realTimeProcessor._predictor.modelExists): #if there is no model
            self.modelButtonName.set("Stair Model Active " + str(self.controller.deviceManager._realTimeProcessor._predictor.optimizedscore) +"% Acc") #do nothing and request the user collect data first
        else:
            self.modelButtonName.set("Create Stair Model")
        createModelButton = tk.Button(
            self,
            textvariable=self.modelButtonName,
            command=async_handler(self.on_model_button_clicked),
        )
        createModelButton.place(relx=0.75, rely=0.75)

        #Delete Model Button 
        self.deleteModelButtonName.set("Delete Model")
        deleteModelButton = tk.Button(
            self,
            textvariable=self.deleteModelButtonName,
            command=async_handler(self.on_delete_model_button_clicked),
        )
        deleteModelButton.place(relx=0.1, rely=0.9)

    def initialize_plot(self):
        # plotter ########################################################
        fig = plt.Figure()
        self.ax = fig.add_subplot(1, 1, 1)
        self.xValues = []
        self.yValues = []

        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().place(relx=0.25, rely=0.5, anchor=CENTER)

        self.ani = animation.FuncAnimation(
            fig, self.animate, fargs=(
                self.xValues, self.yValues), interval=200
        )

    def animate(self, i, xValues, yValues):
        rightTorque = (
            self.controller.deviceManager._realTimeProcessor._chart_data.rightTorque
        )

        xValues.append(dt.datetime.now().strftime("%M:%S"))
        yValues.append(rightTorque)

        # Limit values to 20 items
        xValues = xValues[-20:]
        yValues = yValues[-20:]

        self.ax.clear()
        self.ax.plot(xValues, yValues)

        self.ax.set_title("Right Torque")

    def show(self):
        self.initialize_plot()

    async def on_level_trial_button_clicked(self):
        '''
        If not currently recording data, 
            record and label data as level
        If recording
            end the recording       
        '''
        if self.controller.deviceManager._realTimeProcessor._predictor.state ==0:#if not recording data
            self.controller.deviceManager._realTimeProcessor._predictor.state =1 #record and label as level
            self.levelButtonName.set("End Level Collection")
        elif self.controller.deviceManager._realTimeProcessor._predictor.state ==1: #if recording
            self.controller.deviceManager._realTimeProcessor._predictor.state =0 #stop
            self.levelButtonName.set("Collect Level Data")

    async def on_descend_trial_button_clicked(self):
        if self.controller.deviceManager._realTimeProcessor._predictor.state ==0:#if not recording data
            self.controller.deviceManager._realTimeProcessor._predictor.state =2 #record and label as descend
            self.descendButtonName.set("End Descend Collection")
        elif self.controller.deviceManager._realTimeProcessor._predictor.state ==2: #if recording
            self.controller.deviceManager._realTimeProcessor._predictor.state =0 #stop
            self.descendButtonName.set("Collect Descend Data")

    async def on_ascend_trial_button_clicked(self):
        if self.controller.deviceManager._realTimeProcessor._predictor.state ==0: #if not recording data
            self.controller.deviceManager._realTimeProcessor._predictor.state =3 #record and label as ascend
            self.ascendButtonName.set("End Ascend Collection")
        elif self.controller.deviceManager._realTimeProcessor._predictor.state ==3: #if recording
            self.controller.deviceManager._realTimeProcessor._predictor.state =0 #stop
            self.ascendButtonName.set("Collect Ascend Data")
    
    async def on_model_button_clicked(self):
        if not (self.controller.deviceManager._realTimeProcessor._predictor.modelExists): #if there is no model
            if len(self.controller.deviceManager._realTimeProcessor._predictor.database): #if there is data 
                self.controller.deviceManager._realTimeProcessor._predictor.createModel() #create the model
                self.modelButtonName.set("Stair Model Active " + str(self.controller.deviceManager._realTimeProcessor._predictor.optimizedscore) +"% Acc")
                if self.controller.deviceManager._realTimeProcessor._predictor.database: #if we collected data to generate a mode
                    #save the data, for trouble shooting, replication, or future use
                    self.modelDataWriter.writeToCsv(self.controller.deviceManager._realTimeProcessor._exo_data,self.controller.deviceManager._realTimeProcessor._predictor)
            else:
                self.modelButtonName.set("Collect Level, Descend, Ascend Data First") #do nothing and request the user collect data first
        else:
            self.modelButtonName.set("Stair Model Active " + str(self.controller.deviceManager._realTimeProcessor._predictor.optimizedscore) +"% Acc")
            
    
    async def on_delete_model_button_clicked(self):
        if self.confirmation==0: #flag
            self.deleteModelButtonName.set("Are you Sure?") #ask the user to confirm intentions to delete model
            self.confirmation=self.confirmation+1 
        else:
            self.controller.deviceManager._realTimeProcessor._predictor.deleteModel() #user indicated confirmation, delete model
            self.modelButtonName.set("Create Stair Model") #reset labels and flags
            self.deleteModelButtonName.set("Delete Model")
            self.confirmation=0

    async def on_mark_button_clicked(self):
        self.controller.deviceManager._realTimeProcessor._exo_data.MarkVal += 1
        self.controller.deviceManager._realTimeProcessor._exo_data.MarkLabel.set("Mark: " +str(self.controller.deviceManager._realTimeProcessor._exo_data.MarkVal))

    async def on_recal_FSR_button_clicked(self):
        await self.recalibrateFSR()

    async def recalibrateFSR(self):
        await self.controller.deviceManager.calibrateFSRs()

    async def on_end_trial_button_clicked(self):
        await self.endTrialButtonClicked()

    async def endTrialButtonClicked(self):
        await self.ShutdownExo()

        self.controller.show_frame("ScanWindow")

    async def ShutdownExo(self):
        # End trial
        await self.controller.deviceManager.motorOff()  # Turn off motors
        await self.controller.deviceManager.stopTrial()  # End trial
        # Disconnect from Exo
        self.controller.trial.loadDataToCSV(
            self.controller.deviceManager
        )  # Load data from Exo into CSV
