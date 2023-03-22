import pyvisa 
import socket
##
def repargs(trgt_ , args):
  if(type(args) in [list, tuple]):
    return trgt_.format(*args) ;
  else:
    return trgt_.format(args) ;

class INSTR:
  def w(self, s ):
    pass
  def q(self, b ):
    pass
  def __setitem__(self , k_ , v):
    ks = k_.split("-" , maxsplit = 1 ) ;
    if(len(ks) == 2 ) :
      getattr(self,ks[0])[ks[1]] = v  ;
    elif(len(ks) == 1):
      k = ks[0];
      a = self.W[k]; # possible thowing key error
      if(callable(a)):
        if(type(v) in [list , tuple]): 
          a(self,*v) ; 
        else:
          a(self,v) ; 
      elif(type(a)==str):self.w(repargs(a,v)) ; 
  
  def __getitem__(self , k_  ):
    ks = k_.split("-" , maxsplit = 1 ) ;
    if(len(ks) == 2 ) :
      return getattr(self,ks[0])[ks[1]] ;
    elif(len(ks) == 1):
      k = ks[0];
      a = self.Q[k]; # possible throwing key error
      if(callable(a)):return a(self , k ) ; 
      elif(type(a)==str):return self.q(a) ; 
  
  W={};
  Q={};

##
class TCPINSTR(INSTR):
  def __init__(self  ):
    INSTR.__init__(self);
  def setd(self,addr_): 
    # set the insturment by : 
    RM = pyvisa.ResourceManager();
    self.d = RM.open_resource(addr_);
    assert(self.d!=None);
  def w(self ,w):
    self.d.write(w);
  def q(self ,w):
    return self.d.query(w);
  def qb(self , w):
    return self.d.query_binary_values(w);
  def qp(self , w):
    print(self.q(w));
  def __del__(self):
    if(hasattr(self,"d")):self.d.close();
  W={
    "set_instrument":set
  };
  Q={};


##
class SOCKINSTR(INSTR):
  def __init__(self  , host_ , port_ ):
    INSTR.__init__(self);
    self.host = host_  ;
    self.port = port_  ;
    self.d =  socket.socket(socket.AF_INET , socket.SOCK_STREAM); 
  def connect(self):
    return self.d.connect((self.host,  self.port))  ;  
  def w(self ,w):
    self.d.sendall(w.encode("ASCII")) ;
    return self.d.recv(16*1024);
  def q(self ,w):
    return self.w(w);
  def qb(self , w ):
    return self.w(w);
  def __del__(self):
    if(hasattr(self,"d")):self.d.close();
  W={
    "connect":connect
  };
  Q={};
##

