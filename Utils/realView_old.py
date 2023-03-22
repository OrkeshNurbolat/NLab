import NLab.Utils.common as cm ;  cm.rl(cm);
from NLab.Instruments.Instrument import INSTR 
import multiprocessing as mp
try: mp.set_start_method("spawn");
except : pass ; 

from PyQt5 import QtGui,QtCore  
from PyQt5 import QtWidgets  
from PyQt5.Qt import Qt  

import pyqtgraph as pg
import numpy as np

style = '''
QWidget {
    font: medium Ubuntu;
    background-color: #011F2F;
    font-size: 16px;
    font-size: 16px;
    color:#FFFFFF; 
} 
'''



class Clear:pass;
class PRoll:pass; # message to mark the point rolling

class XYFM:
  def __init__(self , xname_ , yname_ , fx_ , fy_ , mode_='P'):
    self.mode = mode_; #P fore points , T for traces 
    self.xname = xname_;
    self.yname = yname_;
    self.fx = fx_;
    self.fy = fy_;

class CN:
  def __init__(self,mode_, arg_):
    self.mode = mode_ ; 
    self.arg  = arg_ ;

class Angle:
  def __init__(self, arg_):
    self.arg  = arg_

class Points:
  def __init__(self ,arg_):
    self.arg = arg_ ;

class Traces:
  def __init__(self, arg_):
    self.arg  = arg_

class SNAP:
  def __init__(self):
    self.depth = 7 ; # plot memory depth 
    self.Forms = { 
        "mag"  :np.abs ,
        "phase":np.angle ,
        "real" :np.real,
        "imag" :np.imag ,
        "rot"  :self.rotate
    };
    self.D = [] ; # temporal data
    self.CN = []  ; # channel names
    self.clear() ; 
  
  def clear(self):
    self.initD(); 
    self.ix = -1 ; # selected axis on x
    self.iy = -1 ; # selected axis on y 
    self.fx = list(self.Forms.keys())[0]; # selexted part on x 
    self.fy = list(self.Forms.keys())[0]; # selected part on y 
    self.ang = 0.0  ; #rotating angle in complex plane before project to real axis 
  
  def initD(self): 
    self.D= [] ; 
    for i in range(self.depth):
      DP = []; 
      for i in range(len(self.CN)):
        DP.append([]);
      self.D.append(DP);
  
  def setCN(self, lst_): # set the channel names
    if(self.CN != lst_):
      self.CN= lst_.copy(); 
      self.initD();

  def setXYFM(self , xyfm_):
    assert(xyfm_.xname in self.CN) ;
    assert(xyfm_.yname in self.CN) ;
    assert(xyfm_.fx in self.Forms) ;
    assert(xyfm_.fy in self.Forms) ;
    self.ix = self.CN.index(xyfm_.xname); 
    self.iy = self.CN.index(xyfm_.yname); 
    self.fx = xyfm_.fx;
    self.fy = xyfm_.fy;
  
  def roll(self):
    DP = []; 
    for i in range(len(self.CN)):
      DP.append([]);
    self.D =  [ DP  ]  + self.D[:-1] ;
    

  def rotate(self, dat ):
    return np.real(np.exp(1j * self.ang )*np.array(dat)); 

  def getData(self , i ):
    if( self.ix >= 0 and  self.iy >= 0 ) :
      return (self.Forms[self.fx](self.D[i][self.ix]) , self.Forms[self.fy]( self.D[i][self.iy]));
    else :  return None , None ;



class RTP(QtWidgets.QWidget):
  colors=[ 
    (200,0,0),  
    (55,100,180),  
    (40,80,150),  
    (30,50,110),  
    (25,40,70),  
    (25,30,50),  
    (25,30,40),  
  ];
  widths =[3,2,2,2,1,1,1];
  SymSize =[7,0,0,0,0,0,0];

  def __init__(self , title_ ="Real time measurement") :
    self.title = title_; 
    self.P = SNAP() ; #points mem 
    self.T = SNAP() ; #trace  mem
    self.clear();
  
  def clear(self):
    self.P.clear() ;  
    self.T.clear() ; 
    self.mode='P';

  def initGui(self):
    QtWidgets.QWidget.__init__(self);
    self.setStyleSheet(style);
    # button for points
    self.pb = QtWidgets.QRadioButton('Points');
    self.pb._n = 'P';
    self.pb.setChecked(True);
    self.pb.toggled.connect(self.RadioClick);
    
    # button for Traces 
    self.tb = QtWidgets.QRadioButton('Traces');
    self.tb._n = 'T';
    self.tb.toggled.connect(self.RadioClick);

    # selection for X axis
    self.xcb_lb = QtWidgets.QLabel("X");
    self.xcb_lb.setAlignment(QtCore.Qt.AlignRight);
    self.xcb    = QtWidgets.QComboBox();
    self.xcb.activated[str].connect(self.xcbOnChanged);
    
    # selection for Y axis
    self.ycb_lb = QtWidgets.QLabel("Y");
    self.ycb_lb.setAlignment(QtCore.Qt.AlignRight);
    self.ycb    = QtWidgets.QComboBox();
    self.ycb.activated[str].connect(self.ycbOnChanged);

    # format 
    self.fx_lb = QtWidgets.QLabel("fx");
    self.fx_lb.setAlignment(QtCore.Qt.AlignRight);
    self.fy_lb = QtWidgets.QLabel("fy");
    self.fy_lb.setAlignment(QtCore.Qt.AlignRight);
  
    self.fx = QtWidgets.QComboBox();
    self.fx.addItem("mag");
    self.fx.addItem("phase");
    self.fx.addItem("real");
    self.fx.addItem("imag");
    self.fx.addItem("rot");
    self.fx.activated[str].connect(self.fxOnChanged);

    self.fy = QtWidgets.QComboBox();
    self.fy.addItem("mag");
    self.fy.addItem("phase");
    self.fy.addItem("real");
    self.fy.addItem("imag");
    self.fy.addItem("rot");
    self.fy.activated[str].connect(self.fyOnChanged);

    # rotation 
    self.ang_lb = QtWidgets.QLabel("Rotate X : ") ;
    self.ang_lb.setAlignment(QtCore.Qt.AlignRight);
    self.ang = QtWidgets.QSlider(Qt.Horizontal);
    self.ang.setMinimum(0) ;
    self.ang.setMaximum(3600) ;
    self.ang.valueChanged.connect(self.angOnChanged) ;


    # plot widget
    self.plt =  pg.PlotWidget() ;  
    self.plt.showGrid(x = True , y=True);
    # here setup the layouts
    self.layout = QtWidgets.QGridLayout() ;
    self.setLayout(self.layout) ;
    
    self.layout.addWidget(self.pb     , 0 , 0 );
    self.layout.addWidget(self.tb     , 0 , 1 );
    
    self.layout.addWidget(self.xcb_lb , 0 , 2 );
    self.layout.addWidget(self.xcb    , 0 , 3 );
    self.layout.addWidget(self.ycb_lb , 0 , 4 );
    self.layout.addWidget(self.ycb    , 0 , 5 );
    
    self.layout.addWidget(self.fx_lb  , 0 , 6 );
    self.layout.addWidget(self.fx     , 0 , 7 );
    self.layout.addWidget(self.fy_lb  , 0 , 8 );
    self.layout.addWidget(self.fy     , 0 , 9 );
  
    self.layout.addWidget(self.ang_lb  , 0 , 10 );
    self.layout.addWidget(self.ang     , 0 , 11 );
    self.layout.addWidget(self.plt , 1 , 0 , 1 , 12);

    self.plots={}; 
    for i in [6,5,4,3,2,1,0]:
      self.plots[i] = \
        self.plt.plot([],[] ,pen={"color":self.colors[i]  ,"width":self.widths[i]} ,  
            symbolBrush = (255,0,0), 
            symbolPen = { "width":0 ,"color":(255,0,0) }   , 
            symbolSize =self.SymSize[i] ,  
        );
    self.plt.update();  

  def keyPressEvent(self, event):
    modifiers = QtWidgets.QApplication.keyboardModifiers() ;
    if modifiers == QtCore.Qt.ShiftModifier:
      pass


  def RadioClick(self):
    rb = self.sender()  ;
    TCB = None ; 
    if(rb.isChecked()):
      assert(rb._n in ['P', 'T']) ;
      if(rb._n == 'P'): 
        self.mode ='P' ;
        TCB = self.P.CN ; 
      elif(rb._n == 'T'): 
        self.mode ='T' ;
        TCB = self.T.CN ; 
      if(TCB != None):
        self.xcb.clear() ; 
        self.ycb.clear();
        for nm in TCB:
          self.xcb.addItem(nm);
          self.ycb.addItem(nm);
        self.xcb.adjustSize(); 
        self.ycb.adjustSize(); 
      self.updatePlot(True);

  def xcbOnChanged(self, text):
    if(self.mode=='P') : self.P.ix = self.P.CN.index(text) ;
    elif(self.mode=='T') : self.T.ix = self.T.CN.index(text) ;
    self.updatePlot(True);
  
  def ycbOnChanged(self, text):
    if(self.mode=='P') : self.P.iy = self.P.CN.index(text) ;
    elif(self.mode=='T') : self.T.iy = self.T.CN.index(text) ;
    self.updatePlot(True);

  def fxOnChanged(self, text):
    if(self.mode=='P') : self.P.fx = text;
    elif(self.mode=='T') : self.T.fx = text;
    self.updatePlot(True);

  def fyOnChanged(self, text):
    if(self.mode=='P') : self.P.fy = text;
    elif(self.mode=='T') : self.T.fy = text;
    self.updatePlot(True);
    
  def angOnChanged(self , v):
    v =((2*np.pi*v/3600));
    if(self.mode=='P') : self.P.ang = v;
    elif(self.mode=='T') : self.T.ang = v;
    self.updatePlot(True);
  
  def update(self):
    while(not self.fifo.empty()):
      W = self.fifo.get() ; 
      TPW =  type(W)
      rolled = False ;  
      if(Clear == TPW): 
        self.clear();
        self.clear_plot();
      elif(PRoll == TPW): 
        rolled = True ;
        self.P.roll();
      elif(CN == TPW):
        if('P' == W.mode ) :
          self.P.setCN(W.arg);
        elif('T' == W.mode ) :
          self.T.setCN(W.arg);
      elif(Points == TPW):
        assert( len(W.arg) == len(self.P.CN)) ; 
        for i,w in enumerate(W.arg):
          self.P.D[0][i].append(w);
      elif(Traces == TPW):
        assert( len(W.arg) == len(self.T.CN) ) ; 
        self.T.D = [W.arg]+self.T.D[:-1];
      elif(Angle == TPW):
        if(self.mode =='P'):
          self.P.ang = W.arg ; 
        if(self.mode =='T'):
          self.T.ang = W.arg ; 
      elif(XYFM == TPW):
        if(W.mode=='P') :
          self.P.setXYFM(W);
          self.mode  = 'P' ;
        elif(W.mode=='T') :
          self.T.setXYFM(W);
          self.mode  = 'T' ;
      self.updatePlot(rolled);
 
  def clear_plot(self): 
    for i in [6,5,4,3,2,1,0]:
      self.plots[i].setData([],[]);

  def updatePlot(self , rolled): 
    DX = None ;
    DY = None ; 
    if(self.mode == 'P') : 
      if(rolled) :  
        for i in [6,5,4,3,2,1 ] :
          DX,DY  = self.P.getData(i); 
          if(type(DX) != type(None) and type(DY) !=  type(None) ):
            self.plots[i].setData(DX,DY) ;
      DX,DY  = self.P.getData(0); 
      #print(DX, DY)  ;
      if(type(DX) != type(None) and type(DY) !=  type(None) ):
        self.plots[0].setData(DX,DY) ;
        #print("set data")  ;

    elif(self.mode == 'T' ) :  
      for i in [6,5,4,3,2,1,0]:
        DX,DY  = self.T.getData(i);
        if(type(DX) != type(None) and type(DY) !=  type(None) ):
          self.plots[0].setData(DX,DY) ;   
    self.plt.update() ; 

  def run(self ,fifo_):
    self.fifo = fifo_ ; 
    app = QtWidgets.QApplication([])
    self.initGui(); 
    self.show() ;
    self.timer = QtCore.QTimer() ; 
    self.timer.timeout.connect(self.update);
    self.timer.start(50);
    app.exec_() ; 



