import NLab.Utils.common as cm ; cm.rl(cm);
import os ;
import h5py ;
import numpy as np ; 

NAME_OF_VOLS="VOLS"; 
NAME_OF_VOL_NAMES="VOL_NAMES"; 
NAME_OF_CN="CHANNEL_NAMES"; 
LOG_NAME = "LOG" ;
DATA_MATRIX_NAME = "DATA" ;
DATA_MATRIX_DIM_NAME = "DATA_dim" ;
LOGS_NAME = "LOGS" ;
TABS="  "
IMPORTANT="IMPORTANT";
DIM1_CODE="DIM1_CODE";
DIM2_CODE="DIM2_CODE";
FREE_CODE="FREE_CODE";

def dir_choices(path ): 
  pre_path = None ;
  new_path = path ; 
  i =  0 ; 
  while(1):
    if( os.path.exists(new_path) ):
      pre_path = new_path ;
      i+=1;
      new_path  = cm.os_noslash(path)  + "_"+str(i);
    else : 
      break ; 
  return pre_path,new_path; 


def print_tree(fn:str) :
  with h5py.File(fn , "r") as f :
    print_tree_rec(f);

def print_tree_rec(w , idt:int = 0   ) :
  if(hasattr(w , "keys")) : 
    for k,v in w.items():
      print(TABS*idt + k+":"); 
      print_tree_rec(v , idt + 1)  ; 
  else : print(TABS*idt , w); 

def get_vnames(vols):
  vnames = [];
  for v in vols: vnames.append(v);
  return vnames ;



def create_basic(fn:str , vols:dict = {}  ,pn_:list = []   ):
  with h5py.File(fn,"w") as f : 
    sn = [ s.encode("ascii" , "ignore") for s in pn_ ] ; 
    vnames =[ s.encode("ascii" , "ignore") for s in get_vnames(vols) ] ;
    f.create_dataset( NAME_OF_VOL_NAMES ,(len(vnames),) , dtype = "S128",data = vnames ) ;  
    f.create_dataset( NAME_OF_CN ,(len(sn),) , dtype = "S128" , data = sn ) ;  

def load_basic(fn:str):  
  with h5py.File(fn,"r") as f : 
    sn = []; vnames = [] ; logs=[]; 
    for k in f[NAME_OF_CN ] : sn.append( k.decode("ascii") ) ;
    for k in f[NAME_OF_VOL_NAMES] :vnames.append( k.decode("ascii") ) ;
   
    lg = len(LOG_NAME); 
    for k in f:
      if(len(k) >= len(LOG_NAME) and k[:lg] == LOG_NAME ):
        logs.append(k); 
    return sn,vnames,logs;

def append_able(fn:str , vols:dict  = {} , pn_:list = [] ) -> bool : 
  with h5py.File(fn,"r") as f : 
    vnames =get_vnames(vols) ;
    d_vol_names = list(f[NAME_OF_VOL_NAMES]) ; 
    d_sn = list(f[NAME_OF_CN]) ;
    if(len(d_vol_names) != len(vnames)) :return False ; 
    if(len(d_sn) != len(pn_)) :return False ; 
    for i,k in enumerate(d_vol_names) : 
      if(k.decode("ascii") !=  vnames[i]) :return False ;
    for i,k in enumerate(d_sn)  : 
      if( k.decode("ascii") != pn_[i]) :return False ;
  return True ;

def log_key_choices(fn:str):
  with h5py.File(fn,"r") as f : 
    ks = list(f.keys()) ;
    lkt = LOG_NAME + "_"; 
    lkb = None ;
    i  =0 ;  
    while(True)  :
      lk = lkt + str(i) ;
      if( lk not in ks ):break ;
      i+=1; lkb = lk ; # going next
    return lkb , lk ;

type_shoot= {
    str    :"S64" ,
    int    : np.int64 , 
    float  : np.float64 , 
    complex  : np.complex128 , 
}

def dim(v):
  return len(np.shape(v)) ; 

def vols_len(vols , volkeys):
  L = [] 
  for k in volkeys:
    L.append(len(vols[k]))  ;
  return L ; 

def dim_size(tup):
  S= 1;  
  for t in tup : S*= t ; 
  return S; 

def decide_type_r(t):
  if t in type_shoot : return type_shoot[t];
  return t ;

def decide_type(w):
  if(len(np.shape(w)) == 0 ) :return decide_type_r(type(w)) ;
  elif(len(np.shape(w)) == 1):return decide_type_r(type(w[0])) ; 
  elif(len(np.shape(w)) == 2):return decide_type_r(type(w[0][0])) ;
  elif(len(np.shape(w)) == 3):return decide_type_r(type(w[0][0][0])) ; 
  elif(len(np.shape(w)) == 4):return decide_type_r(type(w[0][0][0][0]) ); 
  else : raise Exception("-decide_type- dimention too high") ; 

def vol_write(fn:str, vols:dict, log_key:str):
  with h5py.File( fn , "a" ) as f :
    if( log_key in f ) : flog =  f[ log_key ] ;
    else :  flog = f.create_group(log_key);
    
    if(NAME_OF_VOLS in flog ): VOLS=  flog[NAME_OF_VOLS] ;
    else : VOLS = flog.create_group(NAME_OF_VOLS) ; 
    
    for k,v in vols.items() : 
      if(k in VOLS ): del VOLS[k] ; 
      d = cm.get_iter(v);
      vol = VOLS.create_dataset(k , (len(d),) ,data=d,dtype=decide_type(d) ) ;

def load_vol(fn , log_key):
  D ={};
  with h5py.File(fn , "r") as f  : 
    assert(log_key in f) , " in file \"{}\" has no log \"{}\"".format(fn,log_key) ;
    flog = f[log_key];
    vols = flog[NAME_OF_VOLS];  
    for k in vols:
      D[k] = np.array(vols[k]);
  return D; 

def data_write(fn:str, chunked_data, chunked_names:list,log_key:str) :
  with h5py.File( fn , "a" ) as f :
    if( log_key in f ) : flog_ =  f[ log_key ] ;
    else :  flog_ = f.create_group(log_key);
    
    if( DATA_MATRIX_NAME in flog_ ) : flog = flog_[ DATA_MATRIX_NAME ] ;
    else :  flog= flog_.create_group( DATA_MATRIX_NAME );
    
    for i,name  in enumerate(chunked_names) :
      chunk_shape = np.shape(chunked_data[i]);   
      assert(len(chunk_shape) > 0 ) , "-chunk_write-, writing file \"{}\", the channel name \"{}\", shape not storable as {}\n"\
        .format( fn , chunked_names[i]  , chunk_shape)  ; 
      chunk_len = chunk_shape[0] ;  
      if(name in flog) : slot = flog[name];
      else : 
        slot = flog.create_dataset(
          name  , 
          (0,)+ chunk_shape[1:] ,
          chunks =  ( chunk_len , ) + chunk_shape[1:]  ,
          maxshape =  (None , ) + chunk_shape[1:] , 
          dtype =  decide_type(chunked_data[i])  
        );
      
      assert(len(chunk_shape)  == len(slot.shape)) , "-chunk_write-, writing file \"{}\", the channel name \"{}\"\n chunk dimention changed , input is <{}> , dataset is <{}> \n"\
        .format( fn , chunked_names[i]  , chunk_shape ,slot.shape )  ; 
      
      assert(chunk_shape[1:] == slot.shape[1:]) , "-chunk_write-, writing file \"{}\", the channel name \"{}\"\n chunk sub dimention must be same , input is <{}> , dataset is <{}> \n"\
          .format( fn , chunked_names[i]  , chunk_shape[1:] ,slot.shape[1:] )  ; 

      #print(slot.shape[0]) ;
      slot.resize( (slot.shape[0]+chunk_len,) + slot.shape[1:] );
      slot[ slot.shape[0]-chunk_len : ] = chunked_data[i] ; 

def load_data(fn:str , log_key:str) :
  D = {} ; 
  with h5py.File(fn , "r") as f  : 
    assert(log_key in f) , " in file \"{}\" has no log \"{}\"".format(fn,log_key) ;
    chunk_ = f[log_key] ; 
    if DATA_MATRIX_NAME not in chunk_ :
      return {} ;
    chunk = chunk_[DATA_MATRIX_NAME ] ; 
    for k in chunk : D[k] = np.array(chunk[k]); 
  return D ; 

def ser_to_shape(D , shape_) :
  shape = tuple(shape_) ;
  ds = np.shape(D); 
  dl = ds[0];
  s = shape + ds[1:] ; 
  tot = dim_size(shape) ; 
  EP = np.zeros( (tot,) + ds[1:] ,  decide_type(D)  );
  E = (np.NaN) *EP ;
  lim = min(tot, dl) ;
  E[:lim] =D[:lim];
  F = E.reshape(s);
  return F ;

def load_log(fn:str , lk:str):
  W = {}; 
  PN,VK,LS = load_basic(fn );
  assert(lk in LS),"-load_log- the log \"{}\" is not found in file \"{}\"".format(fn,lk) ;
  W[NAME_OF_VOLS] = load_vol(fn , lk); 
  W[DATA_MATRIX_NAME] = load_data(fn,lk);
  W[DATA_MATRIX_DIM_NAME] = {};
  for k in W[DATA_MATRIX_NAME]:
    W[DATA_MATRIX_DIM_NAME][k] = ser_to_shape(W[DATA_MATRIX_NAME][k],vols_len(W[NAME_OF_VOLS],VK)); 
  return W; 


def set_attr(fn , w:str , attr):
  with h5py.File( fn , "a" ) as f :
    f.attrs[w] = attr ; 

def get_attr(fn , w:str , default ):
  with h5py.File( fn , "r" ) as f :
    if(w in f.attrs):return f.attrs[w]; 
    else : return default ; 

def load(fn:str) :
  W = {}; 
  PN,VK,LS = load_basic(fn );
  W[NAME_OF_CN] =  PN;
  W[NAME_OF_VOL_NAMES] = VK;
  for k in LS:
    W[k] = load_log(fn, k) ;
  
  WK = list(W.keys()); 
  W[LOGS_NAME]  =[] ;
  for k in WK:
    if(len(k) > 3 and k[:3] == LOG_NAME) :
      W[LOGS_NAME].append(k);
  return W;


