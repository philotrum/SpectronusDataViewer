# -*- coding: utf-8 -*
"""
Created 20140516

@author: G. Kettlewell

Plot Spectronus data
"""

import matplotlib.pyplot as plt
from Tkinter import Tk, RIGHT, BOTH, RAISED
from ttk import Frame, Button, Style, Label, Entry
import tkFileDialog
import datetime as dt
import sys

sys.path.append('c:/PythonScripts')

from DatabaseManipulation import ReadDatabase, LoadData, ConvertToDateTime

class SpectronusData_Dialog(Frame):

    def __init__(self, parent):

        Frame.__init__(self,parent)

        self.parent = parent

        self.initUI()

    def initUI(self):

        self.parent.title("Spectronus data")
        self.style = Style()
        self.style.theme_use("default")
        self.pack(fill=BOTH, expand=1)

        self.frame = Frame(self, relief=RAISED, borderwidth=1)

        self.frame.startDateLBL = Label(self, text="Start date", justify=RIGHT, width=12)
        self.frame.startDateLBL.grid(row=0,column=0)
        self.frame.startDateTXT = Entry(self, width=25)
        starttime = dt.datetime.now() - dt.timedelta(days=3)
        self.frame.startDateTXT.insert(0, dt.datetime.strftime(starttime, '%Y-%m-%d %H:%M'))
        self.frame.startDateTXT.grid(row=0,column=1)
        self.frame.finishDateLBL = Label(self, text="Finish date", justify=RIGHT, width=12)
        self.frame.finishDateLBL.grid(row=1,column=0)
        self.frame.finishDateTXT = Entry(self, width=25)
        self.frame.finishDateTXT.insert(0, "2015-12-31 24:00")
        self.frame.finishDateTXT.grid(row=1, column=1)

         # define buttons
        self.frame.selectDatabaseBTN = Button(self, text="Select the database", command=self.openDatabase, width=18)
        self.frame.selectDatabaseBTN.grid(row=4, column=1)
        self.frame.quitButton = Button(self, text="Quit", command=self.quit)
        self.frame.quitButton.grid(row=5, column=1)

        # define options for opening or saving a file
        self.file_opt = options = {}
        options['defaultextension'] = '.txt'
        options['filetypes'] = [('All files', '.*'), ('Database files', '.db')]
        options['initialdir'] = 'c:/users/grahamk/dropbox/oooftidata/Thomas/150305_Jenolan/Database'
        options['initialfile'] = '*.db'
        options['parent'] = self.frame
        options['title'] = 'Select the tracker controller log file'

    def openDatabase(self):

        # Get filename and dates
        databaseFilename = tkFileDialog.askopenfilename(**self.file_opt)
        startDate = self.frame.startDateTXT.get()
        finishDate = self.frame.finishDateTXT.get()

        # Primary key and date/time from sysvariables
        selectSTR = 'SELECT  sysvariablesPK, Collection_Start_Time, Inlet FROM sysvariables where Collection_Start_Time between '
        selectSTR += chr(39) + startDate + chr(39) + ' and ' + chr(39) +  finishDate + chr(39)
        rows1 = ReadDatabase(databaseFilename, selectSTR)
        sysvariablesPK = LoadData(rows1, 0)

        readStartPos = str(sysvariablesPK[0])
        readFinishPos = str(sysvariablesPK[len(sysvariablesPK) -1])

        # Uncorrected species.
        selectSTR = 'SELECT CO2, CO2_1, CO2_2, CH4, N2O, CO, H2O FROM analysisprimary where analysisprimaryID between '
        selectSTR += readStartPos + ' and ' + readFinishPos
        rows2 = ReadDatabase(databaseFilename, selectSTR)

        # Calculated vals
        selectSTR = 'SELECT CV_del13C FROM calcvals where calcvalsID between ' + readStartPos + ' and ' + readFinishPos
        rows3 = ReadDatabase(databaseFilename, selectSTR)

        # AI averages
        selectSTR = 'SELECT Cell_Temperature_Avg,Room_Temperature_Avg,Cell_Pressure_Avg,Flow_In_Avg,Flow_Out_Avg FROM aiaverages where aiaveragesID between '
        selectSTR += readStartPos + ' and ' + readFinishPos
        rows4 = ReadDatabase(databaseFilename, selectSTR)

        # Assemble all data into a single list
        fullData = []
        for i in range(0, len(rows1) -1):
            fullData.append(rows1[i] + rows2[i] + rows3[i] + rows4[i])
        rows1 = []
        rows2 = []
        rows3 = []
        rows4 = []

        # Filter out lines that don't have all the data
        filteredData = []
        for row in fullData:
            if (str(row).find('None') == -1):
                filteredData.append(row)
        fullData = []

        # Break the data into lists according to the inlet they are sampled from.
        numInlets = 4
        inletData = [[] for i in range(numInlets)]
        for row in filteredData:
            if (row[2] == 'Inlet_1'):
                inletData[0].append(row)
            elif (row[2] == 'Inlet_2'):
                inletData[1].append(row)
            elif (row[2] == 'Inlet_3'):
                inletData[2].append(row)
            elif (row[2] == 'Inlet_4'):
                inletData[3].append(row)
            else:
                # There is a problem!
                pass

        Date = [[] for i in range(numInlets)]
        CO2 =  [[] for i in range(numInlets)]
        CO2_12 = [[] for i in range(numInlets)]
        CO2_13 = [[] for i in range(numInlets)]
        CH4 = [[] for i in range(numInlets)]
        N2O = [[] for i in range(numInlets)]
        CO = [[] for i in range(numInlets)]
        H2O = [[] for i in range(numInlets)]
        Del13C = [[] for i in range(numInlets)]
        CellPress = [[] for i in range(numInlets)]
        FlowIn = [[] for i in range(numInlets)]
        FlowOut = [[] for i in range(numInlets)]

        for i in range(0, numInlets):
            Date[i] = ConvertToDateTime(inletData[i], 1)
            CO2[i] = LoadData(inletData[i], 3)
            CO2_12[i] = LoadData(inletData[i], 4)
            CO2_13[i] = LoadData(inletData[i], 5)
            CH4[i] = LoadData(inletData[i], 6)
            N2O[i] = LoadData(inletData[i], 7)
            CO[i] = LoadData(inletData[i], 8)
            H2O[i] = LoadData(inletData[i], 9)
            Del13C[i] = LoadData(inletData[i], 10)
            CellPress[i] = LoadData(inletData[i], 13)
            FlowIn[i] = LoadData(inletData[i], 14)
            FlowOut[i] = LoadData(inletData[i], 15)

        # I don't want to separate cell and room temperature data by inlet
        fullDates = ConvertToDateTime(filteredData, 1)
        CellTemp = LoadData(filteredData, 11)
        RoomTemp = LoadData(filteredData, 12)

        filteredData = []

        for i in range(numInlets):
            inletData[i] = []

        ConcentrationsFig = plt.figure('Concentration retrievals')
        ConcentrationsFig.subplots_adjust(hspace=0.1)
        ConcentrationsFig.suptitle(databaseFilename + '\n' + str(fullDates[0]) + ' to ' + str(fullDates[len(fullDates) -1]), fontsize=14, fontweight='bold')

        colours = ['b', 'k', 'g', 'r']

        # CO2
        Ax1=ConcentrationsFig.add_subplot(611)
        for i in range(numInlets):
            Ax1.scatter(Date[i],CO2[i], marker='+', label='Inlet ' + str(i + 1),color=colours[i])
        #Ax1.scatter(Date,CO2_12, marker='+', label='12CO2', color='b')
        #Ax1.scatter(Date,CO2_13, marker='+', label='13CO2', color='g')
        Ax1.set_ylabel("CO2")
        leg = plt.legend(loc=2,ncol=1, fancybox = True)
        leg.get_frame().set_alpha(0.5)
        Ax1.grid(True)
        Ax1.get_yaxis().get_major_formatter().set_useOffset(False)

        # Del13C
        Ax2=ConcentrationsFig.add_subplot(612, sharex=Ax1)
        for i in range(numInlets):
            Ax2.scatter(Date[i],Del13C[i], marker='+', label='Inlet ' + str(i + 1), color=colours[i])
        Ax2.set_ylabel('Del13C')
        leg = plt.legend(loc=2,ncol=1, fancybox = True)
        leg.get_frame().set_alpha(0.5)
        Ax2.yaxis.set_label_position("right")
        Ax2.yaxis.tick_right()
        Ax2.grid(True)
        Ax2.get_yaxis().get_major_formatter().set_useOffset(False)

        # CO
        Ax3=ConcentrationsFig.add_subplot(613, sharex=Ax1)
        for i in range(numInlets):
            Ax3.scatter(Date[i],CO[i], marker='+', label='Inlet ' + str(i + 1), color=colours[i])
        leg = plt.legend(loc=2,ncol=1, fancybox = True)
        leg.get_frame().set_alpha(0.5)
        Ax3.set_ylabel('CO')
        Ax3.grid(True)
        Ax3.get_yaxis().get_major_formatter().set_useOffset(False)

        # CH4
        Ax4=ConcentrationsFig.add_subplot(614, sharex=Ax1)
        for i in range(numInlets):
            Ax4.scatter(Date[i],CH4[i], marker='+', label='Inlet ' + str(i + 1), color=colours[i])
        Ax4.set_ylabel('CH4')
        leg = plt.legend(loc=2,ncol=1, fancybox = True)
        leg.get_frame().set_alpha(0.5)
        Ax4.yaxis.tick_right()
        Ax4.yaxis.set_label_position("right")
        Ax4.grid(True)
        Ax4.get_yaxis().get_major_formatter().set_useOffset(False)

        # N2O
        Ax5=ConcentrationsFig.add_subplot(615, sharex=Ax1)
        for i in range(numInlets):
            Ax5.scatter(Date[i],N2O[i], marker='+', label='Inlet ' + str(i + 1), color=colours[i])
        leg = plt.legend(loc=2,ncol=1, fancybox = True)
        leg.get_frame().set_alpha(0.5)
        Ax5.set_ylabel('N2O')
        Ax5.grid(True)
        #Ax5.set_ylim(300,400)
        Ax5.get_yaxis().get_major_formatter().set_useOffset(False)

        # H2O
        Ax6=ConcentrationsFig.add_subplot(616, sharex=Ax1)
        for i in range(numInlets):
            Ax6.scatter(Date[i],H2O[i], marker='+', label='Inlet ' + str(i + 1), color=colours[i])
        leg = plt.legend(loc=2,ncol=1, fancybox = True)
        leg.get_frame().set_alpha(0.5)
        Ax6.set_ylabel('H2O')
        Ax6.yaxis.set_label_position("right")
        Ax6.yaxis.tick_right()
        Ax6.grid(True)
        Ax6.get_yaxis().get_major_formatter().set_useOffset(False)

         # Set x axis range
        t0 = fullDates[0] - dt.timedelta(0,3600)
        t1= fullDates[len(fullDates) -1 ] + dt.timedelta(0,3600)
        Ax6.set_xlim(t0,t1)
        Ax6.grid(True)

        ConcentrationsFig.autofmt_xdate()


        SystemStateFig = plt.figure('System State')
        SystemStateFig.suptitle(databaseFilename + '\n' + str(fullDates[0]) + ' to ' + str(fullDates[len(fullDates) -1]), fontsize=14, fontweight='bold')

         # Cell Pressure
        Ax1=SystemStateFig.add_subplot(511)
        for i in range(numInlets):
            Ax1.scatter(Date[i],CellPress[i], marker='+', label='Inlet ' + str(i + 1), color=colours[i])
        leg = plt.legend(loc=2,ncol=1, fancybox = True)
        leg.get_frame().set_alpha(0.5)
        Ax1.set_ylabel('Cell Pressure')
        Ax1.grid(True)
        Ax1.get_yaxis().get_major_formatter().set_useOffset(False)

        # Cell Temperature
        Ax2=SystemStateFig.add_subplot(512, sharex=Ax1)
        Ax2.scatter(fullDates,CellTemp, marker='+', label='Cell Temp')
        Ax2.set_ylabel('Cell Temperature')
        Ax2.yaxis.set_label_position("right")
        Ax2.yaxis.tick_right()
        Ax2.grid(True)
        Ax2.get_yaxis().get_major_formatter().set_useOffset(False)

        # Room Temperature
        Ax3=SystemStateFig.add_subplot(513, sharex=Ax1)
        Ax3.scatter(fullDates,RoomTemp, marker='+', label='Room Temp')
        Ax3.set_ylabel('Room Temperature')
        Ax3.grid(True)
        Ax3.get_yaxis().get_major_formatter().set_useOffset(False)

        # Cell flow in
        Ax4=SystemStateFig.add_subplot(514, sharex=Ax1)
        for i in range(numInlets):
            Ax4.scatter(Date[i], FlowIn[i], marker='+', label='Inlet ' + str(i + 1), color=colours[i])
        leg = plt.legend(loc=2,ncol=1, fancybox = True)
        leg.get_frame().set_alpha(0.5)
        Ax4.set_ylabel('Cell Flow In')
        Ax4.yaxis.set_label_position("right")
        Ax4.yaxis.tick_right()
        Ax4.grid(True)
        Ax4.get_yaxis().get_major_formatter().set_useOffset(False)

        # Cell flow out
        Ax5=SystemStateFig.add_subplot(515, sharex=Ax1)
        for i in range(numInlets):
            Ax5.scatter(Date[i], FlowOut[i], marker='+', label='Inlet ' + str(i + 1), color=colours[i])
        leg = plt.legend(loc=2,ncol=1, fancybox = True)
        leg.get_frame().set_alpha(0.5)
        Ax4.set_ylabel('Cell Flow Out')
        Ax4.grid(True)
        Ax4.get_yaxis().get_major_formatter().set_useOffset(False)

        # Set x axis range
        t0 = fullDates[0] - dt.timedelta(0,3600)
        t1= fullDates[len(fullDates) -1 ] + dt.timedelta(0,3600)
        Ax4.set_xlim(t0,t1)
        Ax4.grid(True)

        SystemStateFig.autofmt_xdate()
        plt.show()

        def quit():
            self.quit()


def main():
    root = Tk()
    root.geometry("300x100+300+300")
    app = SpectronusData_Dialog(root)
    root.mainloop()

if __name__ == '__main__':
    main()
