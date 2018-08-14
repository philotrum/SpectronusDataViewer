# -*- coding: utf-8 -*
"""
Created 20140516

@author: G. Kettlewell
Plot Spectronus data
"""

import matplotlib.pyplot as plt
from tkinter import Tk, RIGHT, BOTH, RAISED, filedialog
from tkinter.ttk import Frame, Button, Style, Label, Entry
import datetime as dt
import sys

sys.path.append('c:/users/grahamk/Documents/Github/LibraryScripts')

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
        starttime = dt.datetime.now() - dt.timedelta(days=7)
        self.frame.startDateTXT.insert(0, dt.datetime.strftime(starttime, '%Y-%m-%d %H:%M'))
        self.frame.startDateTXT.grid(row=0,column=1)
        self.frame.finishDateLBL = Label(self, text="Finish date", justify=RIGHT, width=12)
        self.frame.finishDateLBL.grid(row=1,column=0)
        self.frame.finishDateTXT = Entry(self, width=25)
        self.frame.finishDateTXT.insert(0, "2030-12-31 24:00")
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
        options['initialdir'] = 'c:/users/grahamk/ownCloud/OooftiData/B1Darwin/Data'
        options['initialfile'] = '*.db'
        options['parent'] = self.frame
        options['title'] = 'Select the tracker controller log file'

    def openDatabase(self):

        # Get filename and dates
        databaseFilename = filedialog.askopenfilename(**self.file_opt)
        startDate = self.frame.startDateTXT.get()
        finishDate = self.frame.finishDateTXT.get()

        # Primary key and date/time from sysvariables
        selectSTR = 'SELECT  sysvariablesPK, Collection_Start_Time FROM sysvariables where Collection_Start_Time between '
        selectSTR += chr(39) + startDate + chr(39) + ' and ' + chr(39) +  finishDate + chr(39)
        rows1 = ReadDatabase(databaseFilename, selectSTR)
        sysvariablesPK = LoadData(rows1, 0)

        readStartPos = str(sysvariablesPK[0])
        readFinishPos = str(sysvariablesPK[len(sysvariablesPK) -1])

        # Uncorrected species.
        selectSTR = 'SELECT CO2, CO2_1, CO2_2, CH4, N2O, CO, H2O FROM analysisprimary '
        selectSTR += 'where analysisprimaryID between ' + readStartPos + ' and ' + readFinishPos
        rows2 = ReadDatabase(databaseFilename, selectSTR)

        # Calculated vals
        selectSTR = 'SELECT CV_del13C FROM calcvals where calcvalsID between ' + readStartPos + ' and ' + readFinishPos
        rows3 = ReadDatabase(databaseFilename, selectSTR)

        # AI averages
        selectSTR = 'SELECT Cell_Temperature_Avg,Room_Temperature_Avg,Cell_Pressure_Avg,Flow_In_Avg,Flow_Out_Avg,  '
        selectSTR += 'Tank_Hi_Avg, Tank_Lo_Avg, N2_Purge_Avg FROM aiaverages where aiaveragesID between '
        selectSTR += readStartPos + ' and ' + readFinishPos
        rows4 = ReadDatabase(databaseFilename, selectSTR)

        # Assemble all data into a single list
        fullData = []
        for i in range(0, len(rows1) -1):
            fullData.append(rows1[i] + rows2[i] + rows3[i] + rows4[i])

        # Filter out lines that don't have all the data
        filteredData = []
        for row in fullData:
            if (str(row).find('None') == -1):
                filteredData.append(row)

        Date = ConvertToDateTime(filteredData, 1)
        CO2 = LoadData(filteredData, 2)
        CO2_12 = LoadData(filteredData, 3)
        CO2_13 = LoadData(filteredData, 4)
        CH4 = LoadData(filteredData, 5)
        N2O = LoadData(filteredData, 6)
        CO = LoadData(filteredData, 7)
        H2O = LoadData(filteredData, 8)
        Del13C = LoadData(filteredData, 9)
        CellTemp = LoadData(filteredData, 10)
        RoomTemp = LoadData(filteredData, 11)
        CellPress = LoadData(filteredData, 12)
        FlowIn = LoadData(filteredData, 13)
        FlowOut = LoadData(filteredData, 14)
        Tank_Hi = LoadData(filteredData, 15)
        Tank_Lo = LoadData(filteredData, 16)
        N2Purge = LoadData(filteredData, 17)

        ConcentrationsFig = plt.figure('Concentration retrievals')
        ConcentrationsFig.subplots_adjust(hspace=0.1)
        ConcentrationsFig.suptitle(databaseFilename + '\n' + str(Date[0]) + ' to ' + str(Date[len(Date) -1]), fontsize=14, fontweight='bold')

        # CO2
        Ax1=ConcentrationsFig.add_subplot(611)
        Ax1.scatter(Date,CO2, marker='+', label='CO2',color='r')
        Ax1.scatter(Date,CO2_12, marker='+', label='12CO2', color='b')
        Ax1.scatter(Date,CO2_13, marker='+', label='13CO2', color='g')
        Ax1.set_ylabel("CO2")
        leg = plt.legend(loc=2,ncol=1, fancybox = True)
        leg.get_frame().set_alpha(0.5)
        Ax1.grid(True)
        Ax1.get_yaxis().get_major_formatter().set_useOffset(False)

        # Del13C
        Ax2=ConcentrationsFig.add_subplot(612, sharex=Ax1)
        Ax2.scatter(Date,Del13C, marker='+', label='Del13C', color='r')
        Ax2.set_ylabel('Del13C')
        leg = plt.legend(loc=2,ncol=1, fancybox = True)
        leg.get_frame().set_alpha(0.5)
        Ax2.yaxis.set_label_position("right")
        Ax2.yaxis.tick_right()
        Ax2.grid(True)
        Ax2.get_yaxis().get_major_formatter().set_useOffset(False)

        # CO
        Ax3=ConcentrationsFig.add_subplot(613, sharex=Ax1)
        Ax3.scatter(Date,CO, marker='+')
        Ax3.set_ylabel('CO')
        Ax3.grid(True)
        Ax3.get_yaxis().get_major_formatter().set_useOffset(False)

        # CH4
        Ax4=ConcentrationsFig.add_subplot(614, sharex=Ax1)
        Ax4.scatter(Date,CH4, marker='+')
        Ax4.set_ylabel('CH4')
        Ax4.yaxis.tick_right()
        Ax4.yaxis.set_label_position("right")
        Ax4.grid(True)
        Ax4.get_yaxis().get_major_formatter().set_useOffset(False)

        # N2O
        Ax5=ConcentrationsFig.add_subplot(615, sharex=Ax1)
        Ax5.scatter(Date,N2O, marker='+')
        Ax5.set_ylabel('N2O')
        Ax5.grid(True)
        #Ax5.set_ylim(300,400)
        Ax5.get_yaxis().get_major_formatter().set_useOffset(False)

        # H2O
        Ax6=ConcentrationsFig.add_subplot(616, sharex=Ax1)
        Ax6.scatter(Date,H2O, marker='+')
        Ax6.set_ylabel('H2O')
        Ax6.yaxis.set_label_position("right")
        Ax6.yaxis.tick_right()
        Ax6.grid(True)
        Ax6.get_yaxis().get_major_formatter().set_useOffset(False)

         # Set x axis range
        t0 = Date[0] - dt.timedelta(0,3600)
        t1= Date[len(Date) -1 ] + dt.timedelta(0,3600)
        Ax6.set_xlim(t0,t1)
        Ax6.grid(True)

        ConcentrationsFig.autofmt_xdate()

        SystemStateFig = plt.figure('System State')
        SystemStateFig.suptitle(databaseFilename + '\n' + str(Date[0]) + ' to ' + str(Date[len(Date) -1]), fontsize=14, fontweight='bold')

         # Cell Pressure
        Ax1=SystemStateFig.add_subplot(611)
        Ax1.scatter(Date, CellPress, marker='+')
        Ax1.set_ylabel('Cell Pressure')
        Ax1.grid(True)
        Ax1.get_yaxis().get_major_formatter().set_useOffset(False)

        # Cell Temperature
        Ax2=SystemStateFig.add_subplot(612, sharex=Ax1)
        Ax2.scatter(Date,CellTemp, marker='+', label='Cell Temp')
        Ax2.set_ylabel('Cell Temperature')
        Ax2.yaxis.set_label_position("right")
        Ax2.yaxis.tick_right()
        Ax2.grid(True)
        Ax2.get_yaxis().get_major_formatter().set_useOffset(False)

        # Room Temperature
        Ax3=SystemStateFig.add_subplot(613, sharex=Ax1)
        Ax3.scatter(Date,RoomTemp, marker='+', label='Room Temp')
        Ax3.set_ylabel('Room Temperature')
        Ax3.grid(True)
        Ax3.get_yaxis().get_major_formatter().set_useOffset(False)

        # Cell flow
        Ax4=SystemStateFig.add_subplot(614, sharex=Ax1)
        Ax4.scatter(Date,FlowIn, marker='+', label='Flow In',color='r')
        Ax4.scatter(Date,FlowOut, marker='+', label='Flow Out',color='b')
        Ax4.set_ylabel('Cell Flows')
        Ax4.yaxis.set_label_position("right")
        Ax4.yaxis.tick_right()
        Ax4.grid(True)
        leg = plt.legend(loc=2,ncol=1, fancybox = True)
        leg.get_frame().set_alpha(0.5)
        Ax4.get_yaxis().get_major_formatter().set_useOffset(False)

        # Cylinder high pressures
        Ax5=SystemStateFig.add_subplot(615, sharex=Ax1)
        Ax5.scatter(Date,Tank_Hi, marker='+', label='Tank_Hi')
        Ax5.set_ylabel('Cylinder Pressure\nHigh')
        Ax5.grid(True)
        leg = plt.legend(loc=2,ncol=1, fancybox = True)
        leg.get_frame().set_alpha(0.5)
        Ax5.get_yaxis().get_major_formatter().set_useOffset(False)

        # Cylinder low pressure
        Ax6=Ax5.twinx()
        Ax6.scatter(Date, Tank_Lo, marker='+', label='Tank_Lo', color='r')
        Ax6.set_ylabel('Cylinder Pressure\nLow')
        Ax6.yaxis.set_label_position("right")
        Ax6.yaxis.tick_right()
        Ax6.grid(True)
        leg = plt.legend(loc=3,ncol=1, fancybox = True)
        leg.get_frame().set_alpha(0.5)
        Ax6.get_yaxis().get_major_formatter().set_useOffset(False)

        # N2 purge
        Ax7=SystemStateFig.add_subplot(616, sharex=Ax1)
        Ax7.scatter(Date, N2Purge, marker='+')
        Ax7.set_ylabel('N2 Purge Flow')
        Ax7.grid(True)
        Ax7.get_yaxis().get_major_formatter().set_useOffset(False)

        # Set x axis range
        t0 = Date[0] - dt.timedelta(0,3600)
        t1= Date[len(Date) -1 ] + dt.timedelta(0,3600)
        Ax6.set_xlim(t0,t1)
        Ax6.grid(True)

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
