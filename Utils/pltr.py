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


def rotate(dat ,ang ): return ; 

class SNAP : 
  forms = { 
    "mag"  :lambda w,ang : np.abs(w) ,
    "phase":lambda w,ang : np.angle(w) ,
    "real" :lambda w,ang : np.real(w) ,
    "imag" :lambda w,ang : np.imag(w),
    "rot"  :lambda w,ang : np.real(np.exp(1j * ang )*np.array(w))
  }; 
  
  forms_keys = list(forms.keys()); 
  
  def __init__(self) :
    self.depth = 7 ; # plot memory depth 
    self.D = [] ;    # temporal data
    self.CN = []  ;  # channel names
    self.lCN = 0  ;  # channel names length
    self.xyfm ={} ;
    self.curr_xy = (None,None) ;
    self.clear();
  
  def clear(self) :
    self.initD();

  def setCN(self, lst_):
    if(self.CN != lst_):
      self.CN= lst_.copy(); 
      self.lCN = len(self.CN);
      self.initD();

  
  def initD(self): 
    self.D = [] ; 
    for i in range(self.depth):
      DP = []; 
      for i in range(self.lCN): DP.append([]);
      self.D.append(DP);
 
  def up(self , P):  #update point 
    assert(len(P) == len(self.CN) ) ;
    first_layer = self.D[0];
    for i in range(len(first_layer)): 
      if(list == type(first_layer[i] ) ) : 
        first_layer[i].append(P[i]);
      if(np.ndarray == type(first_layer[i])) : 
        first_layer[i] = np.append(first_layer[i] , P[i]) ;  
  
  def ut(self , T):  # update track
    assert(len(T) == len(self.CN) ) ;
    self.roll() ;
    first_layer = self.D[0];
    for i in range(len(first_layer)): 
      first_layer[i] = np.array(T[i]) ;  
  
  def roll(self):
    DP = []; 
    for i in range(len(self.CN)): DP.append([]);
    self.D =  [ DP  ]  + self.D[:-1] ;

  def tplt(self):  # template of information
    return {"fx":"real" , "fy":"mag", "rx":0, "ry":0};
  
  def check(self):
    if(self.curr_xy not in self.xyfm) : 
      self.xyfm[self.curr_xy] = self.tplt();
      return 0 ;
    else : 
      return 1;


  def setfx(self, w ):
    self.check() ; 
    self.xyfm[self.curr_xy]["fx"] = w ;
  
  def setfy(self, w ):
    self.check() ; 
    self.xyfm[self.curr_xy]["fy"] = w ;
  
  def setrx(self, w ):
    self.check() ; 
    self.xyfm[self.curr_xy]["rx"] = w ;
  
  def setry(self, w ):
    self.check() ; 
    self.xyfm[self.curr_xy]["ry"] = w ;


  def getf(self) :
    self.check();
    return self.xyfm[self.curr_xy];

  def fidxs(self) :
    f= self.getf() ;
    return (
      list(SNAP.forms.keys()).index(f["fx"]) ,
      list(SNAP.forms.keys()).index(f["fy"]) ,
      f["rx"],
      f["ry"]
    );
      
  def didx(self , name):
    return self.CN.index(name);

  def getData(self , i):
    xn,yn = self.curr_xy ;
    if(None == xn or None == yn ) : return [],[] ; 
    f=self.getf(); 
    fx = self.forms[f["fx"]]; # this is the function
    fy = self.forms[f["fy"]]; # this is the function
    rx = f["rx"];
    ry = f["ry"];
    return ( fx(self.D[i][self.didx(xn)],rx) , fy(self.D[i][self.didx(yn)],ry));
    
  def update_curr(self, xn = None , yn = None) : 
    xnc, ync = self.curr_xy ; 
    if(None == xn) : 
      if(xnc in self.CN): xn = xnc ;
      elif(len(self.CN)> 0 ) : xn = self.CN[0] ;
      else : xn = None ;
    if(None == yn) : 
      if(ync in self.CN): yn = ync ;
      elif(len(self.CN)> 0 ) : yn = self.CN[ min(1 ,len(self.CN) - 1 )] ;
      else : yn = None ;
    self.curr_xy  = (xn , yn);
    
    xi = None ; yi = None ;
    if(xn in self.CN) : xi = self.CN.index(xn);
    if(yn in self.CN) : yi = self.CN.index(yn);
    
    return xi,yi ; 

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
    self.mode='P';
    self.clear();

  def clear(self):
    self.P.clear() ;  
    self.T.clear() ; 
 
  def snp(self):
    if(self.mode == "P") : return self.P ; 
    elif(self.mode == "T") : return self.T ; 
    print("========internal error========") ; 
    return None ; 

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
    self.angX_lb = QtWidgets.QLabel("RX") ;
    self.angX_lb.setAlignment(QtCore.Qt.AlignRight);
    self.angX = QtWidgets.QSlider(Qt.Horizontal);
    self.angX.setMinimum(0) ;
    self.angX.setMaximum(3600) ;
    self.angX.valueChanged.connect(self.XangOnChanged) ;

    self.angY_lb = QtWidgets.QLabel("RY") ;
    self.angY_lb.setAlignment(QtCore.Qt.AlignRight);
    self.angY = QtWidgets.QSlider(Qt.Vertical);
    self.angY.setMinimum(0) ;
    self.angY.setMaximum(3600) ;
    self.angY.valueChanged.connect(self.YangOnChanged) ;

    # plot widget
    self.plt =  pg.PlotWidget() ;  
    self.plt.showGrid(x = True , y=True);
    
    self.plots={}; 
    for i in [6,5,4,3,2,1,0]:
      self.plots[i] = \
        self.plt.plot([],[] ,pen={"color":self.colors[i]  ,"width":self.widths[i]} ,  
            symbolBrush = (255,0,0), 
            symbolPen = { "width":0 ,"color":(255,0,0) }   , 
            symbolSize =self.SymSize[i] ,  
        );
    self.plt.update();  



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
  
    self.layout.addWidget(self.angX_lb  , 0 , 10,  );
    self.layout.addWidget(self.angX     , 0 , 11  );
    
    self.layout.addWidget(self.angY_lb     , 2 , 12  );
    self.layout.addWidget(self.angY     , 1 , 12  );
    self.layout.addWidget(self.plt      , 1 , 0 , 2 , 12 );


  # Keyboard Movements
  def move_y(self, direction) :
    W  =self.snp() ;
    xn,yn = W.curr_xy; 
    iy = None 
    if(yn in W.CN ): 
      iy =W.CN.index(yn) ;
      iiy = (iy + direction ) % len(W.CN)  ;
      ynn = W.CN[iiy] ;
      W.curr_xy = (xn,ynn);
      self.switch_to_last_option(); 
  
  def move_x(self, direction) :
    W  =self.snp() ;
    xn,yn = W.curr_xy; 
    ix = None 
    if(xn in W.CN ): 
      ix =W.CN.index(xn) ;
      iix = (ix + direction ) % len(W.CN)  ;
      xnn = W.CN[iix] ;
      W.curr_xy = (xnn,yn);
      self.switch_to_last_option(); 

  def move_x_up(self):self.move_x(1);
  def move_x_down(self):self.move_x(-1);
  def move_y_up(self):self.move_y(1);
  def move_y_down(self):self.move_y(-1);

  def move_fx(self):
    fidx, fidy , rx, ry = self.snp().fidxs() ;  
    ffidx = (fidx+1) % 5 ;
    self.fx.setCurrentIndex(ffidx);
    self.fxOnChanged(list(SNAP.forms.keys())[ffidx]) ;
  
  def move_fy(self):
    fidx, fidy , rx, ry = self.snp().fidxs() ;  
    ffidy = (fidy+1) % 5 ;
    self.fy.setCurrentIndex(ffidy);
    self.fyOnChanged(list(SNAP.forms.keys())[ffidy]) ;

  def point_click(self) :self.pb.click(); 
  def trace_click(self) : self.tb.click();
  def rxminus(self) :
    v = (self.angX.value() - 100) % 3600 ;
    self.angX.setValue( v );
  def rxplus(self) :
    v = (self.angX.value() + 100) % 3600 ;
    self.angX.setValue( v );
  def ryminus(self) :
    v = (self.angY.value() - 100) % 3600 ;
    self.angY.setValue( v );
  def ryplus(self) :
    v = (self.angY.value() + 100) % 3600 ;
    self.angY.setValue( v );
  actions = {
    87 : move_y_down  , # W
    16777235 : move_y_down  , # up arrow
    83 : move_y_up  , # S
    16777237 : move_y_up  , # down arrow
    65 : move_x_down  , # A
    16777234 : move_x_down  , # left arrow
    68 : move_x_up  , # A
    16777236 : move_x_up  , # right arrow
    80 : point_click , # P  
    84 : trace_click , # T  
    82 : move_fx, # R
    86 : move_fy, # V
    81 : rxminus, # Q
    90 : ryminus, # Z
    69 : rxplus, # E
    67 : ryplus, # C
  }

  def keyPressEvent(self, event):
    modifiers = QtWidgets.QApplication.keyboardModifiers() ;
    if modifiers == QtCore.Qt.ShiftModifier:
      pass
    ek =event.key()   ;
    if(ek in self.actions) : RTP.actions[ek](self);
    #print(ek);

  ## the action of the clicks
  def RadioClick(self):
    # decide the mode 
    if(self.pb.isChecked() ) : self.mode = 'P';
    elif(self.tb.isChecked() ) : self.mode = 'T';
    self.update_comb(); 
    self.switch_to_last_option();

  def update_comb(self):
    # update the comb 
    W = self.snp() ;     
    if(W.CN != None):
      self.xcb.clear() ; 
      self.ycb.clear();
      for nm in W.CN:
        self.xcb.addItem(nm);
        self.ycb.addItem(nm);
      self.xcb.adjustSize(); 
      self.ycb.adjustSize(); 

  def update_xyfm(self) :
    fidx, fidy , rx, ry = self.snp().fidxs() ;  
    self.fx.setCurrentIndex(fidx);
    self.fy.setCurrentIndex(fidy);
    self.angX.setValue(int ( (3600*rx) / (2*np.pi )) )
    self.angY.setValue(int ( (3600*ry) / (2*np.pi )) )

  def switch_to_last_option(self) : 
    W= self.snp() ;
    idx,idy = W.update_curr();  # update the current
    if(None != idx) :  self.xcb.setCurrentIndex(idx);
    if(None != idy) :  self.ycb.setCurrentIndex(idy);
    
    self.update_xyfm();
    self.updatePlot(True);

  def xcbOnChanged(self, text):
    W=self.snp() ;
    W.curr_xy = ( text , W.curr_xy[1]) ;
    self.update_xyfm();
    self.updatePlot(True);
  
  def ycbOnChanged(self, text):
    W=self.snp() ;
    W.curr_xy = ( W.curr_xy[0], text ) ;
    self.update_xyfm();
    self.updatePlot(True);

  def fxOnChanged(self, text):
    W=self.snp() ; 
    W.setfx(text);
    self.update_xyfm();
    self.updatePlot(True);
    print(12);

  def fyOnChanged(self, text):
    W = self.snp() ; 
    W.setfy(text);
    self.update_xyfm();
    self.updatePlot(True);
    
  def XangOnChanged(self , v):
    v =((2*np.pi*v/3600));
    self.snp().setrx(v);
    self.update_xyfm();
    self.updatePlot(True);
  
  def YangOnChanged(self , v):
    v =((2*np.pi*v/3600));
    self.snp().setry(v);
    self.update_xyfm();
    self.updatePlot(True);

  def update(self):
    while(not self.fifo.empty()):
      W = self.fifo.get() ; 
      TPW =  type(W)
      update_flag = False ;  
      if(Clear == TPW): 
        self.clear();
        self.clear_plot();
      elif(PRoll== TPW): 
        self.P.roll();
        update_flag = True ;
      elif(CN == TPW):
        if(  'P' == W.mode ) : self.P.setCN(W.arg);
        elif('T' == W.mode ) : self.T.setCN(W.arg);
        self.update_comb(); 
        self.switch_to_last_option();
      elif(Points == TPW): 
        self.P.up(W.arg);
        update_flag = True;
      elif(Traces == TPW): 
        self.T.ut(W.arg);
        update_flag = True;
      self.updatePlot(update_flag);
 
  def clear_plot(self): 
    for i in [6,5,4,3,2,1,0]:
      self.plots[i].setData([],[]);

  def updatePlot(self, f ): 
    DX = None ; DY = None ; 
    W = self.snp();  
    assert(None != W) , "Internal Error" ;
    if ( f ) : 
      for i in [6,5,4,3,2,1,0 ] :
        DX,DY  = W.getData(i); 
        if(type(DX) != type(None) and type(DY) !=  type(None) ):
          mn = min(len(DX) , len(DY)) ;
          self.plots[i].setData(DX[:mn],DY[:mn]) ;

  def run(self ,fifo_):
    self.fifo = fifo_ ; 
    app = QtWidgets.QApplication([])
    self.initGui(); 
    self.show() ;
    self.timer = QtCore.QTimer() ; 
    self.timer.timeout.connect(self.update);
    self.timer.start(50)
    app.exec_() ; 



