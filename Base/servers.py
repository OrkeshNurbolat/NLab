import NLab.Utils.common as cm ; cm.rl(cm);
import NLab.Utils.rwjson as rwjson ; cm.rl(rwjson);
import os
import zmq ; 
import numpy as np ; 


import multiprocessing as mp; 
try: mp.set_start_method("spawn");
except : pass ; 

class Phony:
  __maj_type__ = "Phony" ;
  def __init__(self ): pass
  def __getitem__(self, k) :
    return None ; 
  def __setitem__(self, k ,v  ):
    return None ;


class Server:
  def __init__(self , branch:str="main" ):
    self.subs = {}; 
    self.branch = branch ;  
    if("main" == self.branch) :
      print("0x{:X} Server Is Created".format(id(self))) ;
  
  def __setitem__(self, ks_ ,v): # set item open for public assignment 
    A = ks_.split('-',maxsplit=1);
    if(len(A) == 2 ):
      if(not hasattr(self, A[0])):
        raise Exception("there is no such a sub key as \"{}\" with key as \"{}\"".format(A[0] , ks_)) ;
      getattr(self,A[0])[A[1]]= v;  # doing another set attribute
    else:
      setattr(self,A[0],v) ;  # just setting the attribute
 
  
  async def setitem(self , ks_ , v ) : 
     self.__setitem__(ks_ , v) ; 

  
  def __getitem__(self, ks_ ):
    A = ks_.split('-',maxsplit=1);
    if(hasattr(self,A[0]) ):
      if(len(A) == 2 ):
        return getattr(self,A[0])[A[1]];  
      else:
        return getattr(self,A[0]) ; 
    return None

  
  def load(self, d  , path ) :
    if( "CONNECT" in d and d["CONNECT"] == False) : return -1; 
    
    if( "PHONY" in d and d["PHONY"] == True)  : 
      setattr( self , d["NAME"],  Phony()) ; 
      return d["NAME"];
    
    for t in ["NAME" , "MODULE" , "CLASS" , "CREATE_INIT" , "ACTUAL_INIT"] :
      if not t in d: return -1; 
    # here the class is created at the same processor 
    setattr( self , d["NAME"],  cm.get_class(d["MODULE"] , d["CLASS"])( *d["CREATE_INIT"])) ; 
    prix = cm.dash(d["NAME"] );
    for k in d["ACTUAL_INIT"]:
      self[cm.dash(prix) + k] = d["ACTUAL_INIT"][k];
    return d["NAME"]  ; 
  
  def load_dir(self,path ):
    for f in sorted(os.listdir(path)) : 
      if(len(f)> 0 and f[0] == '.') : continue;
      tgt = cm.os_slash(path)+f ;
      if(os.path.isfile(tgt) and tgt[-4:] == "json" ):
        try : 
          nm = self.load(rwjson.read(tgt) , tgt)  ; 
          self.subs[nm] = tgt ;
          print("{} has been sucessfully loaded semantics objects".format(tgt));
        except Exception as e:
          raise Exception(" -ROOT- reading file '{}'\n".format(f) + str(e)) from e ;
      
      if(os.path.isdir(tgt)):
        try:
          prx_ =  f.split("-")[-1];
          self[prx_]=Server("branch"); # -- sink point
          self[prx_].load_dir( tgt );
        except Exception as e :
          raise Exception(" -ROOT- reading directory '{}'\n".format(f) + str(e)) from e ;


  def reload(self, w ) :  
    if(w in self.subs) : 
      print("reloading " , w)  ;
      setattr( self , w ,None ); 
      tgt = self.subs[w];  
      self.load(rwjson.read(tgt) , tgt)
    else : 
      print(w , "not in the server") ;

  def __del__(self):
    if("main" == self.branch) :
      print("0x{:X} Server Is Destroyed".format(id(self))) ;


class ServerRoot(Server): 
  def __init__(self , port_:int ): 
    Server.__init__(self)   ; 
    self.port = port_ ;  
    self.STOP = False ;
  
  def stop(self): 
    self.STOP = True ;  
  
  def main(self): 
    self.__context__ = zmq.Context(); 
    self.__socket__ = self.__context__.socket(zmq.REP); 
    self.__socket__.bind("tcp://*:%s" % self.port ) ; 
    while(not self.STOP) : 
      suc = True;
      W = self.__socket__.recv_pyobj()   ;  #expecting a dictionary ; 
      if(W.op == cm.OP.SET):   
        for k,v in W.d.items(): 
          try : 
            self[cm.offrep(k)] = v ;   
          except Exception as e : 
            print("======SERVER ERROR at setting key \"{}\"=====".format(k)); 
            print(str(e)) ; 
            self.__socket__.send_pyobj("ERROR") ; 
            suc = False; 
            #break ; 
        if(suc) : self.__socket__.send_pyobj("SUCCESS") ; 
        else : self.__socket__.send_pyobj("SOME OPERATION FAILED");
      elif(W.op == cm.OP.GET) : 
        if( len(W.d) ==1 ): self.__socket__.send_pyobj(self[W.d[0]]);
        else : self.__socket__.send_pyobj([self[k] for k in W.d]);




