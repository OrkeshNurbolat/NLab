import NLab.Utils.common as cm ; cm.rl(cm) ;
import NLab.Utils.rwdata as rwdata ; cm.rl(rwdata) ;


from PyQt5.QtWidgets import QApplication 
from PyQt5 import QtWidgets
from PyQt5 import QtGui,QtCore  
from PyQt5 import QtWidgets  
from PyQt5.Qt import Qt  
import h5py

import os
import pathlib
import numpy as np

import pyqtgraph as pg
import pyqtgraph.console 
from pyqtgraph.examples.ExampleApp import *  ;

from pathlib import Path
import time ; 


# matplotlib
if QtCore.qVersion() >= "5.":
    from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
else:
    from matplotlib.backends.backend_qt4agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure

style = '''
QWidget {
    font: medium Ubuntu;
    background-color: #071527;
    font-size: 16px;
    color:#FFFFFF; 
} 
'''

theEnterKey = 16777220; 
leftKey = 16777234; 
rightKey = 16777236; 


FontVisible=QtGui.QFont("Ubuntu" , 10  ) ; 
FontNormal=QtGui.QFont("Ubuntu" , 12  ) ; 
FontValuable=QtGui.QFont("Ubuntu" , 13 , italic=True ) ; 
FontImportant=QtGui.QFont("Ubuntu" , 14 , italic=True ) ; 
FontImportant.setBold(True);

DispChoices  ={
    0: [FontImportant  , QtGui.QColor("#FF0000") ] , # important
    1: [FontValuable  , QtGui.QColor("#002FAF") ]  ,# valuable 
    2: [FontNormal  , QtGui.QColor("#000000") ]  , # normal 
}

def weight_item(a:QtWidgets.QListWidgetItem , w:int=2) :
  a.setFont(DispChoices[w][0]) ; a.setForeground(DispChoices[w][1]);

#
def valuable(path) :
  hasdata = False; 
  important  = False   ;
  for f in os.listdir(path):
    if( os.path.isfile(cm.os_slash(path) +  f) and f =="DATA.hdf5"):
      hasdata =  True ; 
      important = rwdata.get_attr( cm.os_slash(path) +  f ,  rwdata.IMPORTANT , False) ;
    if( os.path.isfile(cm.os_slash(path) +  f) and f =="plot.py"):hasplot =  True ; 
  return hasdata ,important ;  

def get_dirs(path):
  D =[".."]; 
  paths = sorted(Path(path).iterdir(), key=os.path.getmtime); 
  if(len(paths) > 0 ) :paths.reverse();
  for f in paths  : 
    if(f.is_dir() ) :
      D.append(str(f.name)) ;
  return D ; 

def create_new_item( name:str ) ->QtWidgets.QListWidgetItem : 
  a= QtWidgets.QListWidgetItem(name) ;   
  weight_item(a,2); 
  return a ;    



class dim1_widget(QtWidgets.QWidget) :
  def __init__(self ):
    QtWidgets.QWidget.__init__(self) ;
    self.layout = QtWidgets.QGridLayout() ;
    self.setLayout(self.layout) ;  
    self.executer = None ;

    self.vll_idx = 3 ; 
    
    self.LOG_LIST = QtWidgets.QListWidget() ; 
    self.VOL_LIST = QtWidgets.QListWidget() ; 
    #self.VOL_LIST.itemActivated.connect(self.vol_activated)
    self.LOG_LIST.itemSelectionChanged.connect(self.vol_activated)
    self.VOL_LIST.itemSelectionChanged.connect(self.vol_activated)

    self.CN_LIST = QtWidgets.QListWidget() ; 
    self.VOL_LIST_LIST =  [
     QtWidgets.QListWidget() , 
     QtWidgets.QListWidget() , 
     QtWidgets.QListWidget() , 
     QtWidgets.QListWidget() , 
    ]; 

    self.label_LOG_LIST  = QtWidgets.QLabel("LOG") ; 
    self.label_CN_LIST = QtWidgets.QLabel("CHANNELS") ; 
    self.label_VOL_LIST  = QtWidgets.QLabel("VOL") ; 
    
    self.label_VOL_LIST_LIST = [
      QtWidgets.QLabel("") ,  
      QtWidgets.QLabel("") , 
      QtWidgets.QLabel("") , 
      QtWidgets.QLabel("") , 
    ]; 
    
    self.layout.addWidget(self.label_LOG_LIST   , 0 , 0 , 1, 1); 
    self.layout.addWidget(self.label_CN_LIST   , 0 , 1 , 1, 1); 
    self.layout.addWidget(self.label_VOL_LIST   , 0 , 2 , 1, 1); 
    
    for i,l in enumerate(self.label_VOL_LIST_LIST) :
      self.layout.addWidget(l , 0 , self.vll_idx+i, 1, 1); 

    self.layout.addWidget(self.LOG_LIST , 1 , 0 , 1, 1); 
    self.layout.addWidget(self.CN_LIST , 1 , 1 , 1, 1); 
    self.layout.addWidget(self.VOL_LIST , 1 , 2 , 1, 1); 
    
    for i,l in enumerate(self.VOL_LIST_LIST):
      self.layout.addWidget(l , 1 , self.vll_idx+i, 5, 1); 
   
    # preview editor
    self.code= QtWidgets.QPlainTextEdit() ; 
    self.code.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap); 
    self.layout.addWidget(self.code,2,0,1,3);

    # buttons
    self.add = QtWidgets.QPushButton("add") ; 
    self.add.clicked.connect(self.add_func); 
    self.add_short_cut = QtWidgets.QShortcut(QtGui.QKeySequence('a'), self)
    self.add_short_cut.activated.connect(self.add_func) ;      


    self.clear = QtWidgets.QPushButton("clear") ; 
    self.clear.clicked.connect(self.clear_func); 
    self.clear_add_short_cut = QtWidgets.QShortcut(QtGui.QKeySequence('c'), self)
    self.clear_add_short_cut.activated.connect(self.clear_func) ;      



    self.run = QtWidgets.QPushButton("run") ; 
    self.run.clicked.connect(self.run_func); 
    self.run_add_short_cut = QtWidgets.QShortcut(QtGui.QKeySequence('r'), self)
    self.run_add_short_cut.activated.connect(self.run_func) ;      

    self.del_add_short_cut = QtWidgets.QShortcut(QtGui.QKeySequence('d'), self)
    self.del_add_short_cut.activated.connect(self.del_func) ;      
    
    self.layout.addWidget(self.clear,5,0,1,1);
    self.layout.addWidget(self.run,5,1,1,1);
    self.layout.addWidget(self.add,5,2,1,1);

  def connect_executer(self , executer_): 
    self.executer = executer_ ;

  def set_logs(self,LOGS=[]): 
    self.LOG_LIST.clear();  
    for i,name in enumerate(LOGS):
      slot =QtWidgets.QListWidgetItem(name)
      self.LOG_LIST.addItem( slot);   
      if(0 == i ) : self.LOG_LIST.setCurrentItem(slot) ;

  def set_vols(self, VOLS = [] ):
    self.VOL_LIST.clear();  
    for i,name in enumerate(VOLS):
      slot =QtWidgets.QListWidgetItem(name)
      self.VOL_LIST.addItem( slot);   
      if(0 == i ) : self.VOL_LIST.setCurrentItem(slot) ;

  def set_cns(self, CHANNELS = []):
    self.CN_LIST.clear();  
    for i,name in enumerate(CHANNELS):
      slot =QtWidgets.QListWidgetItem(name)
      self.CN_LIST.addItem( slot);   
      if(0 == i ) : self.CN_LIST.setCurrentItem(slot) ;


  def set_data(self, W  ,fn:str ): 
    self.W = W ;
    self.fn =fn  ;
    self.set_logs(W[rwdata.LOGS_NAME]);
    self.set_vols(W[rwdata.NAME_OF_VOL_NAMES]);
    self.set_cns(W[rwdata.NAME_OF_CN]);
    self.code.setPlainText(rwdata.get_attr(self.fn ,rwdata.DIM1_CODE, "") ) ; 

  def vol_activated(self, qmodelindex = None)  :
    citem = self.VOL_LIST.currentItem() ;
    clog = self.LOG_LIST.currentItem() ;  
    if(None == citem or  None == clog) : return ;
    assert(len(self.VOL_LIST) <=  5 ), "cant display more than 5 dimention"; 
    for i in range(4) :
      self.label_VOL_LIST_LIST[i].setText("");
      self.VOL_LIST_LIST[i].clear();

    i = 0 ;  
    for itemidx in range(len(self.VOL_LIST)): 
      ititem = self.VOL_LIST.item(itemidx) ;  
      if(citem.text() != ititem.text() ) :
        self.label_VOL_LIST_LIST[i].setText(ititem.text());
        V = ["{:.5e}".format(w) for w in self.W[clog.text()][rwdata.NAME_OF_VOLS][ititem.text()]  ]
        self.VOL_LIST_LIST[i].addItems(V);
        i+=1 ;
          

  def add_func(self):
    l = self.LOG_LIST.currentItem() ;
    c = self.CN_LIST.currentItem() ;
    v = self.VOL_LIST.currentItem() ;
    s = {}   ;  
    for i in range(4):
      sv =  self.VOL_LIST_LIST[i].currentItem() ;
      lb =  self.label_VOL_LIST_LIST[i].text() ;
      if( sv!=None ) : 
        s[lb] = self.VOL_LIST_LIST[i].currentRow();

    if(
      None != l 
      and None != c 
      and None != v
      and len(self.W[rwdata.NAME_OF_VOL_NAMES])-1 == len(s)
    ):
      idx_txt = "" ;  
      lw = len(self.W[rwdata.NAME_OF_VOL_NAMES])   ; 
      for i,x in enumerate(self.W[rwdata.NAME_OF_VOL_NAMES]) :
        if(x == v.text()): idx_txt+=":";
        elif(x in s) : idx_txt+=str(s[x]) ; 
        else :
          raise Exception("the volatile name \"{}\" is not set".format(s)) ; 
        if(i!=lw-1) :idx_txt+=",";
  
      w = "plt.plot("       ;
      w += "np.real(W[\"{}\"][\"{}\"][\"{}\"]) , "\
          .format(l.text(),rwdata.NAME_OF_VOLS , v.text()); 
      w += "np.abs(W[\"{}\"][\"{}\"][\"{}\"][{}])"\
          .format(l.text(),rwdata.DATA_MATRIX_DIM_NAME,c.text() , idx_txt); 
      w +=");\n"

      self.code.setPlainText(self.code.toPlainText() + w ) ; 

  def del_func(self): 
    tx = self.code.toPlainText().split("\n");
    if(tx[-1]==""):tx.pop();
    S="" ; 
    for x in tx[:-1] : S+=x ; S+="\n"; 
    self.code.setPlainText(S) ; 

  def clear_func(self):
    self.code.setPlainText("");

  def run_func(self):
    assert(self.fn!=None);
    the_code = self.code.toPlainText();
    rwdata.set_attr(self.fn , rwdata.DIM1_CODE, the_code ) ; 
    self.executer(the_code)  ;


class dim2_widget(QtWidgets.QWidget) :
  def __init__(self ):
    QtWidgets.QWidget.__init__(self) ;
    self.layout = QtWidgets.QGridLayout() ;
    self.setLayout(self.layout) ;  
    self.executer = None ;

    self.vll_idx = 4 ; 
    
    self.LOG_LIST = QtWidgets.QListWidget() ; 
    self.LOG_LIST.itemSelectionChanged.connect(self.vol_activated)
    
    self.VOL1_LIST = QtWidgets.QListWidget() ; 
    self.VOL2_LIST = QtWidgets.QListWidget() ; 
    self.VOL1_LIST.itemSelectionChanged.connect(self.vol_activated)
    self.VOL2_LIST.itemSelectionChanged.connect(self.vol_activated)

    self.CN_LIST = QtWidgets.QListWidget() ; 
    self.VOL_LIST_LIST =  [
     QtWidgets.QListWidget() , 
     QtWidgets.QListWidget() , 
     QtWidgets.QListWidget() , 
    ]; 

    self.label_LOG_LIST  = QtWidgets.QLabel("LOG") ; 
    self.label_CN_LIST = QtWidgets.QLabel("CHANNELS") ; 
    self.label_VOL1_LIST  = QtWidgets.QLabel("VOL-X") ; 
    self.label_VOL2_LIST  = QtWidgets.QLabel("VOL-Y") ; 
    
    self.label_VOL_LIST_LIST = [
      QtWidgets.QLabel("") ,  
      QtWidgets.QLabel("") , 
      QtWidgets.QLabel("") , 
    ]; 
    
    self.layout.addWidget(self.label_LOG_LIST   , 0 , 0 , 1, 1); 
    self.layout.addWidget(self.label_CN_LIST   , 0 , 1 , 1, 1); 
    self.layout.addWidget(self.label_VOL1_LIST   , 0 , 2 , 1, 1); 
    self.layout.addWidget(self.label_VOL2_LIST   , 0 , 3 , 1, 1); 
    
    for i,l in enumerate(self.label_VOL_LIST_LIST) :
      self.layout.addWidget(l , 0 , self.vll_idx+i, 1, 1); 

    self.layout.addWidget(self.LOG_LIST , 1 , 0 , 1, 1); 
    self.layout.addWidget(self.CN_LIST , 1 , 1 , 1, 1); 
    self.layout.addWidget(self.VOL1_LIST , 1 , 2 , 1, 1); 
    self.layout.addWidget(self.VOL2_LIST , 1 , 3 , 1, 1); 
    
    for i,l in enumerate(self.VOL_LIST_LIST):
      self.layout.addWidget(l , 1 , self.vll_idx+i, 5, 1); 
   
    # preview editor
    self.code= QtWidgets.QPlainTextEdit() ; 
    self.code.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap); 
    self.layout.addWidget(self.code,2,0,1,4);

    # buttons
    self.add = QtWidgets.QPushButton("add") ; 
    self.add.clicked.connect(self.add_func); 
    self.add_short_cut = QtWidgets.QShortcut(QtGui.QKeySequence('a'), self)
    self.add_short_cut.activated.connect(self.add_func) ;      


    self.clear = QtWidgets.QPushButton("clear") ; 
    self.clear.clicked.connect(self.clear_func); 
    self.clear_add_short_cut = QtWidgets.QShortcut(QtGui.QKeySequence('c'), self)
    self.clear_add_short_cut.activated.connect(self.clear_func) ;      



    self.run = QtWidgets.QPushButton("run") ; 
    self.run.clicked.connect(self.run_func); 
    self.run_add_short_cut = QtWidgets.QShortcut(QtGui.QKeySequence('r'), self)
    self.run_add_short_cut.activated.connect(self.run_func) ;      

    self.del_add_short_cut = QtWidgets.QShortcut(QtGui.QKeySequence('d'), self)
    self.del_add_short_cut.activated.connect(self.del_func) ;      
    
    self.layout.addWidget(self.clear,5,0,1,1);
    self.layout.addWidget(self.run,5,1,1,1);
    self.layout.addWidget(self.add,5,2,1,1);

  def connect_executer(self , executer_): 
    self.executer = executer_ ;

  def set_logs(self,LOGS=[]): 
    self.LOG_LIST.clear();  
    for i,name in enumerate(LOGS):
      slot =QtWidgets.QListWidgetItem(name)
      self.LOG_LIST.addItem( slot);   
      if(0 == i ) : self.LOG_LIST.setCurrentItem(slot) ;

  def set_vols(self, VOLS = [] ):
    self.VOL1_LIST.clear();  
    for i,name in enumerate(VOLS):
      slot =QtWidgets.QListWidgetItem(name)
      self.VOL_LIST.addItem( slot);   
      if(0 == i ) : self.VOL_LIST.setCurrentItem(slot) ;
  
  def set_cns(self, CHANNELS = []):
    self.CN_LIST.clear();  
    for i,name in enumerate(CHANNELS):
      slot =QtWidgets.QListWidgetItem(name)
      self.CN_LIST.addItem( slot);   
      if(0 == i ) : self.CN_LIST.setCurrentItem(slot) ;


  def set_data(self, W  ,fn:str ): 
    pass
    self.W = W ;
    self.fn =fn  ;
    #self.set_logs(W[rwdata.LOGS_NAME]);
    #self.set_vols(W[rwdata.NAME_OF_VOL_NAMES]);
    #self.set_cns(W[rwdata.NAME_OF_CN]);
    #self.code.setPlainText(rwdata.get_attr(self.fn ,rwdata.DIM1_CODE, "") ) ; 

  def vol_activated(self, qmodelindex = None)  :
    pass
    #citem = self.VOL_LIST.currentItem() ;
    #clog = self.LOG_LIST.currentItem() ;  
    #if(None == citem or  None == clog) : return ;
    #assert(len(self.VOL_LIST) <=  5 ), "cant display more than 5 dimention"; 
    #for i in range(4) :
    #  self.label_VOL_LIST_LIST[i].setText("");
    #  self.VOL_LIST_LIST[i].clear();

    #i = 0 ;  
    #for itemidx in range(len(self.VOL_LIST)): 
    #  ititem = self.VOL_LIST.item(itemidx) ;  
    #  if(citem.text() != ititem.text() ) :
    #    self.label_VOL_LIST_LIST[i].setText(ititem.text());
    #    V = ["{:.5e}".format(w) for w in self.W[clog.text()][rwdata.NAME_OF_VOLS][ititem.text()]  ]
    #    self.VOL_LIST_LIST[i].addItems(V);
    #    i+=1 ;
    #      

  def add_func(self):
    pass
    #l = self.LOG_LIST.currentItem() ;
    #c = self.CN_LIST.currentItem() ;
    #v = self.VOL_LIST.currentItem() ;
    #s = {}   ;  
    #for i in range(4):
    #  sv =  self.VOL_LIST_LIST[i].currentItem() ;
    #  lb =  self.label_VOL_LIST_LIST[i].text() ;
    #  if( sv!=None ) : 
    #    s[lb] = self.VOL_LIST_LIST[i].currentRow();

    #if(
    #  None != l 
    #  and None != c 
    #  and None != v
    #  and len(self.W[rwdata.NAME_OF_VOL_NAMES])-1 == len(s)
    #):
    #  idx_txt = "" ;  
    #  lw = len(self.W[rwdata.NAME_OF_VOL_NAMES])   ; 
    #  for i,x in enumerate(self.W[rwdata.NAME_OF_VOL_NAMES]) :
    #    if(x == v.text()): idx_txt+=":";
    #    elif(x in s) : idx_txt+=str(s[x]) ; 
    #    else :
    #      raise Exception("the volatile name \"{}\" is not set".format(s)) ; 
    #    if(i!=lw-1) :idx_txt+=",";
  
    #  w = "plt.plot("       ;
    #  w += "np.real(W[\"{}\"][\"{}\"][\"{}\"]) , "\
    #      .format(l.text(),rwdata.NAME_OF_VOLS , v.text()); 
    #  w += "np.abs(W[\"{}\"][\"{}\"][\"{}\"][{}])"\
    #      .format(l.text(),rwdata.DATA_MATRIX_DIM_NAME,c.text() , idx_txt); 
    #  w +=");\n"

    #  self.code.setPlainText(self.code.toPlainText() + w ) ; 

  def del_func(self): 
    pass
    #tx = self.code.toPlainText().split("\n");
    #if(tx[-1]==""):tx.pop();
    #S="" ; 
    #for x in tx[:-1] : S+=x ; S+="\n"; 
    #self.code.setPlainText(S) ; 

  def clear_func(self):
    pass
    #self.code.setPlainText("");

  def run_func(self):
    pass
    #assert(self.fn!=None);
    #the_code = self.code.toPlainText();
    #rwdata.set_attr(self.fn , rwdata.DIM1_CODE, the_code ) ; 
    #self.executer(the_code)  ;







class LogBrowser(QtWidgets.QMainWindow): 
  def __init__(self , title_ = "Log Browser") :
    QtWidgets.QMainWindow.__init__(self) ;
    self.title = title_ ;  
    self.exec_id = 0;  

    self._main_ = QtWidgets.QWidget(); 
    self.setCentralWidget(self._main_) ;  
    
    #self.setStyleSheet(style) ;
    #layout = QtWidgets.QVBoxLayout(self._main)
    self.layout = QtWidgets.QGridLayout(self._main_) ;
   
    #self.layout = QtWidgets.QGridLayout() ;
    self.setLayout(self.layout) ;
  
    self.log_path = pathlib.Path(os.getcwd()); 
    #self.log_path =pathlib.Path( "/home/wmc/prog/tutorials/root_tut/1_mingle_tree/RUNS/") ;
    self.data_path = None;  

    # the log list
    self.layout.setColumnStretch(0,3) ;  
    self.layout.setColumnStretch(1,1) ;  
    self.layout.setRowStretch(1,3) ;  
    self.layout.setRowStretch(2,1) ;  
    
    # path enterring box :
    # self.save_path_maj = QtWidgets.QLineEdit(os.getcwd()) ; 
    # self.layout.addWidget(self.save_path_maj,0,1,1,1);

    # button
    # self.button = QtWidgets.QPushButton("PUSH") ; 
    # self.layout.addWidget(self.button,0,0,1,1);

    self.log_list = QtWidgets.QListWidget() ; 
    self.layout.addWidget(self.log_list,1,1,1,1);

    self.log_list.clicked.connect(self.log_list_left_click);
    #  self.log_list.addItem(create_new_item("{} + Blue".format(3*i+2))) ;   
    self.log_list.doubleClicked.connect(self.log_list_left_double_click) ; 
    self.log_list.keyPressEvent = self.list_key_event;
    self.fresh_log_list() ;

    ###################################
    # the tab bar maker
    self.tabBar = QtWidgets.QTabWidget() ;  
    self.layout.addWidget(self.tabBar  ,2,0,1,2 )
    self.tabBar.setFont(FontNormal) ;

    # the info bar 
    self.info= QtWidgets.QPlainTextEdit() ; 
    self.info.setFont(FontNormal) ;
    self.tabBar.addTab(self.info , "info") ;

    # the 1d bar 
    #self.dim1plot= QtWidgets.QWidget() ; 
    self.dim1plot= dim1_widget() ; 
    self.dim1plot.setFont(FontVisible) ;
    self.tabBar.addTab(self.dim1plot , "1d-quick-plot") ;

    # the 2d bar 
    self.dim2plot= dim2_widget() ; 
    self.dim2plot.setFont(FontVisible) ;
    self.tabBar.addTab(self.dim2plot , "2d-quick-plot") ;
    
    # the text editor
    self.editor  =  QtWidgets.QTextEdit() ; 
    hl = PythonHighlighter(self.editor.document());
    self.editor.setFont(FontNormal) ;
    self.editor.setTabStopWidth(20);
    self.tabBar.addTab(self.editor , "editor") ;

    # the plot
    self.canvas = FigureCanvas(Figure(figsize=(5,3) ,tight_layout=True )); 
    self.bar= NavigationToolbar(self.canvas, self)
    self.addToolBar(self.bar);
    self.layout.addWidget(self.canvas  ,1,0,1,1 )
    self.plt =self.canvas.figure.subplots();

    # the console  
    namespace= { 
        "self":self , 
        "canvas":self.canvas ,  
        "plt":self.plt , 
        "np" : np  , 
        "pwd":os.getcwd , 
        "rwdata": rwdata, 
      }  ;
    self.console = pyqtgraph.console.ConsoleWidget(namespace=namespace); 
    #self.layout.addWidget(self.console  ,2,1,1,1 )
    self.tabBar.addTab(self.console , "console") ;
    self.dim1plot.connect_executer(self.exec_console_plain);

    # setting up the shortcuts
    self.exec_file_short_cut = QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+R'), self.editor)
    self.exec_file_short_cut.activated.connect(self.exec_code) ;      

    self.exec_file_short_cut = QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+T'), self)
    self.exec_file_short_cut.activated.connect(self.editor.setFocus) ;      

    # refresh button
    self.exec_refresh = QtWidgets.QShortcut(QtGui.QKeySequence('F5'), self)
    self.exec_refresh.activated.connect(self. fresh_log_list) ;      

    self.exec_refresh = QtWidgets.QShortcut(QtGui.QKeySequence('F4'), self)
    self.exec_refresh.activated.connect(self.log_list_left_double_click) ;      
    
    self.save_file_short_cut = QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+S'), self.editor)
    self.save_file_short_cut.activated.connect(self.save_code) ;      

  def load_data(self):
    print("load data");
    assert(self.data_path!=None)     ;
    W = rwdata.load(self.data_path); 
    WK = list(W.keys()); 
    LG = W[rwdata.LOGS_NAME]; 
    CN = W[rwdata.NAME_OF_CN] ; 
    VN = W[rwdata.NAME_OF_VOL_NAMES] ; 
    # update globals
    
    G = self.console.globals() ; 
    G["W"] = W;
    G["WK"] = WK;
    G["LG"] = LG;
    G["CN"] = CN;
    G["VN"] = VN;

    # update info  
    s="";
    s+="CHANNEL NAMES: "
    lcn  = len(CN) ;
    for i,cn in enumerate(CN):
      s+=cn;
      if(i != lcn-1) : s+=" , "
    s+="\n" ;
    
    s+="VOLATILE NAMES: "
    lvn  = len(VN) ;
    for i,vn in enumerate(VN):
      s+=vn;
      if(i != lvn-1) : s+=" , "
    s+="\n" ;
    
    s+="LOGS: "
    llg  = len(LG) ;
    for i,ln in enumerate(LG):
      s+=ln;
      if(i != llg-1) : s+=" , "
    s+="\n" ;
    self.info.setPlainText(s);

    # setting up the 1d quick plot 
    self.dim1plot.set_data(W  , str(self.data_path));

  def load_code(self):
    print("load code");
    assert( self.data_path!=None); 
    c = rwdata.get_attr( str(self.data_path) ,rwdata.FREE_CODE  , "" );
    if(c == "") :
      c = rwdata.get_attr( str(self.data_path) ,rwdata.DIM1_CODE  , "" );
    if(c == "") :
      c = rwdata.get_attr( str(self.data_path) ,rwdata.DIM2_CODE  , "" );
    self.editor.setPlainText(c);

  def save_code(self):
    print("save code");
    assert( self.data_path!=None); 
    rwdata.set_attr( str(self.data_path) ,rwdata.FREE_CODE ,self.editor.toPlainText() );

  def exec_code(self) :
    self.save_code();
    self.exec_console(self.editor.document().toPlainText()) ; 

  def exec_console(self,content):
    self.load_data();
    self.exec_console_plain(content)

  def exec_console_plain(self,content):
    self.plt.cla(); 
    self.console.execSingle(content) ; 
    self.canvas.draw();
    self.console.write("\nExecuted[{}]\n".format(self.exec_id))  ;
    self.exec_id+=1;


  def list_key_event(self, ev):
    print(ev.key()) ;
    if( ev.key() in (theEnterKey , leftKey , rightKey ) ): 
      self.hit_action(self.log_list.currentItem()) ;
    elif( ev.key() in (QtCore.Qt.Key_Space, ) ): 
      item = self.log_list.currentItem(); 
      tx = item.text() ;
      fp = pathlib.Path(cm.os_slash(str(self.log_path)) + tx) ; 
      haveh5,important = valuable(str(fp))
      if(haveh5) :
        if(important) : weight_item(item,1);
        else : weight_item(item,0);
        rwdata.set_attr(cm.os_slash(str(fp))+"DATA.hdf5" , rwdata.IMPORTANT,not important )  ;
    QtWidgets.QListWidget.keyPressEvent(self.log_list ,ev) ;

  def fresh_log_list(self ) : 
    self.log_list.clear(); 
    p = str(self.log_path); 
    dirs = get_dirs(p) ; 
    for i,d in enumerate(dirs) : 
      slot = create_new_item(d) ;
      haveh5 ,important  = valuable(cm.os_slash(p) + d )
      if(important) :weight_item(slot, 0) ;
      elif(haveh5)    :weight_item(slot, 1) ;
      self.log_list.addItem(slot); 
      if(0 == i ) : self.log_list.setCurrentItem(slot)
   

  def log_list_left_click(self,  qmodelindex):
    #weight_item(self.log_list.currentItem(),2);
    pass ;

  def log_list_left_double_click(self,  qmodelindex = 0 ):
    self.hit_action(self.log_list.currentItem()) ;

  def hit_action(self,item): 
    tx = item.text() ;
    fp = pathlib.Path(cm.os_slash(str(self.log_path)) + tx) ; 
    haveh5,important = valuable(str(fp))
    if( tx == ".."):
      self.log_path = self.log_path.parent ; 
      self.fresh_log_list() ; 
    elif(haveh5):
      self.data_path = cm.os_slash(str(fp)) + "DATA.hdf5" ;
      self.load_data();
      self.load_code(); 
      self.exec_code(); 
    else : 
      self.log_path = fp ; 
      self.fresh_log_list();  



