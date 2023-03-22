from collections.abc import Iterable 
import threading , pickle, time , os ,regex  ;
import numpy as np   ; 
from   tqdm import tqdm  ; 
import time ; 
import NLab.Utils.common as cm ;  cm.rl(cm);
import NLab.Utils.rwjson as rwjson  ; cm.rl(rwjson) ;
import NLab.Utils.rwdata  as rwdata ; cm.rl(rwdata) ;  
import zmq ; 
import multiprocessing as mp; 
try: mp.set_start_method("spawn");
except : pass ; 

PAUSE_TIME = 1;
def empl(l):
  L = [] ; 
  for i in range(l): L.append([]) ;
  return L ;

def empd(L):
  D = {};
  for l in L: D[l] = [] ;
  return D ;

def quiet_bar_replace(a , *b,**c):
  yield from a ;

def shift_climax(prx, s):
  if(s[0] == "!") :return "!"+prx+s[1:];
  else : return prx + s;

def climax_check(s):
  w = s.count("!") ;
  assert(w <=1),"key \"{}\" could only have one climax".format(s);
  if(w==1) :
    assert(s[0]== '!'),"key \"{}\" climax should only be at start".format(s);

class opt: 
  __maj_type__ = "VLX" ;
  __mnr_type__ = "opt" ;
  def __init__(self,idx:int) : 
    self.idx = idx ; 
    self.optv = None ;
  def ret(self):
    return self; 

class vol: # mark the argument as volatile
  __maj_type__ = "VLX" ;
  __mnr_type__ = "vol" ;
  def __init__(self , arg_):
    assert(isinstance( arg_, Iterable) or callable(arg_) ) ;
    self.arg = arg_;  
  
  def ret(self):
    return self.arg; 

   
def vlin(a,b,c):
  return vol(np.linspace(a,b,c));

def vspn(a,b,c):
  return vol(np.linspace(a-(b/2),a+(b/2),c));

#def vdis(A , span  , N:int=2 ) : 
#  """
#    A as a list of center points.
#    as well the b as its span , 
#    and N as the number of points for each center points in A ;
#    so in the end there will be returned with len(A)*N long np array; 
#  """
#  np.concatenate(for a in A : AR.append( ))
    

def vstp(a,b,c):
  return vol(np.arange(a-(b/2),a+(b/2),c));

nums = "[0-9]+\.[0-9]+[pnumkKMGT]|[0-9]+[pnumkKMGT]"  ;

words = ['..'] + list("/!-_~#0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ") ; 
ref1 = regex.compile("\$\L<words>+" , words=words);
ref2 = regex.compile("\$\{\L<words>+\}" , words=words);
ref3 = regex.compile("^[-_0-9a-zA-Z]+|^![-_0-9a-zA-Z]+") ;
ref4 = regex.compile("\&\L<words>+" , words=words);
ref5 = regex.compile("\&\{\L<words>+\}" , words=words);
brrrt = regex.compile("[bB][r]+t")

nreps = {
  'f':'(({}) / 1000_000_000_000_000) ',
  'p':'(({}) / 1000_000_000_000) ',
  'n':'(({}) / 1000_000_000) ',
  'u':'(({}) / 1000_000) ',
  'm':'(({}) / 1000) ',
  'k':'(({}) * 1000) ', 
  'K':'(({}) * 1000) ',
  'M':'(({}) * 1000_000) ',
  'G':'(({}) * 1000_000_000) ',
  'T':'(({}) * 1000_000_000_000) ' , 
  'P':'(({}) * 1000_000_000_000_000) '
}

def do_nums(s):
  r = s;  
  for e in regex.findall(nums , s) :
    s = e.replace(e , nreps[e[-1]].format(e[:-1]) ) ;
    r = r.replace(e,s,1);
  return r;

# slash related
def spk(ks):
  L  = [] ;  
  for  k in ks.split('/') :
    if(k!=""):L.append(k);
  return L ; 

def clix(k):
  if(len(k)>0 and k[0] != '!'): return "!"+k;
  else : return k ; 

def no_clix(k):
  while(len(k)>0 and k[0] == '!'): k= k[1:];
  return k ; 


def spdash(ks):
  L  = [] ;  
  for  k in ks.split('-') :
    if(k!=""):L.append(k);
  return L ; 

def spdash1(ks_):
  while(True) : 
    ks = ks_.split('-',maxsplit=1);
    if(len(ks) == 2 ):
      if(ks[0] != "" ) : return ks ;
      else : ks_ = ks[1];
    else : return ks; 
  
def jnk(ks):
  s="" ; l =len(ks);
  for i,k in enumerate(ks):
    if(k!=""):s+=k;
    if(i < l - 1  ): s+="/";
  return s ;

def slash(s):
  if(not len(s)==0 and s[-1]!='/'):s+='/';
  return s ; 

def noslash_front(s):
  while( not len(s)==0 and s[0]=='/' ): s=s[1:] ;
  return s ; 

def noslash_back(s):
  while( not len(s)==0 and s[-1]=='/' ): s=s[:-1] ;
  return s ; 

def noslash(s): return noslash_front(noslash_back(s)); 

def dot(s):
  if(not len(s)==0 and s[-1]!='.'):s+='.';
  return s ; 

def nodot(s):
  while( not len(s)==0 and s[-1]=='.' ): s=s[:-1] ;
  return s ; 


# Dictionary-List operational functions
class InConsistentException(Exception):pass

def incost_exception(k,tt):
  if(k[0]=="#")   : wht = "list-index";
  else   : wht = "dictionary-key";
  return InConsistentException("type inconsitent of {} \"{}\" and type \"{}\"".format(wht,k,tt));

# get key functions
def get_key( t , k ):
  tt = type(t);
  if(k[0] == '#' and tt == list ) : return t[int(k[1:])] ;
  elif(k[0] != '#' and tt == dict ) : return t[k];
  else: raise incost_exception(k,tt);

def get_key_list(r,ks,m=lambda x:x):
  t = r ; 
  for k in ks: t=get_key(m(t),k);
  return t; 

def on_set_get_key( t , k ):
  tt = type(t);
  if(k[0] == '#' and tt == list ) : return t[int(k[1:])] ;
  elif(k[0] != '#' and tt == dict ) : 
    if(k in t ):  v = t[k]; t.pop(k); t[k] = v;
    return t[k];
  else: raise incost_exception(k,tt);

def on_set_get_key_list( r , ks , m=lambda x:x):
  t = r ; 
  for k in ks: t=on_set_get_key(m(t),k);
  return t; 

def get_key_str(r,s,m=lambda x:x):
  return get_key_list(r,spk(s),m);

# set key functions
def set_key_value(t , k , v):
  tt = type(t);
  if(k[0] == '#' and tt == list ) : t[int(k[1:])]= v ;
  elif(k[0] != '#' and tt == dict ): t[k] = v ;
  else: raise incost_exception(k,tt);

def set_key_list(r,ks,v, m=lambda x:x):
  set_key_value(m(get_key_list(r, ks[:-1] , m )) , ks[-1] , v);

def set_key_str(r,s,v, m=lambda x:x):
  return set_key_list(r,spk(s),v,m) ; 

def on_set_key_value(t , k , v):
  tt = type(t);
  if(k[0] == '#' and tt == list ) : t[int(k[1:])]= v ;
  elif(k[0] != '#' and tt == dict ): 
    if(k in t ):  t.pop(k);
    t[k] = v ;
  else: raise incost_exception(k,tt);

def on_set_key_list(r,ks,v, m=lambda x:x):
  on_set_key_value(m(on_set_get_key_list(r, ks[:-1] , m )) , ks[-1] , v);

def on_set_key_str(r,s,v, m=lambda x:x):
  return on_set_key_list(r,spk(s),v,m) ; 


# have key checking
def have_key(t ,  k ):
  tt = type(t);
  if(k[0] == '#' and tt == list ) : return int(k[1:]) < len(t) ;
  elif(k[0] != '#' and tt == dict ) : return ( k in t);
  else: return False ;

def have_key_list(r , ks,m=lambda x:x ):
  t = r ;
  for k in ks: 
    v = m(t);
    if(not have_key(v, k )): return False ; 
    else : t = get_key(v , k ) ; 
  return True ;

def resolve_local_key_list(cur_list,key_list):
  p = cur_list.copy();
  if(len(p)>0):p.pop(); #consider the local key from its parents
  for k in key_list: 
    if(k=='.'):pass;
    elif(k=='..'): 
      if(len(p)>0):p.pop(); 
    else:p.append(k);
  return p ; 

def resolve_local_key_str(cur,ref ):
  return resolve_local_key_list(spk(cur) , spk(ref) ) ; 

def have_key_str(r,s,m=lambda x:x):
  return have_key_list(r,spk(s),m);

def have_local_key_str(root , cur , ref, m=lambda x:x):
  return have_key_list( root , resolve_local_key_str(cur , ref) ,m) ; 

# resolving reference
def ref_str(s):
  if(s[-1]=='}'): return s[2:-1];
  else : return s[1:];

def get_refs(s): 
  return regex.findall(ref1,s) + regex.findall(ref2,s);

def get_refs_mach(s):
  return regex.findall(ref4 , s) + regex.findall(ref5 , s);

def _resolve_path_(r , cur_str , path_str , m=lambda x:x ):
  # case 1 : local reference
  p = resolve_local_key_str(cur_str,path_str);
  if(have_key_list(r,p ,m )): return jnk(p) ; 
  
  # case 2 : global path
  if(have_key_str(r,path_str ,m )) : return path_str ; 
  
  # case 3 : unersolveable : 
  return None ;


# Information Enhanced Value
class IEV: 
  __maj_type__ = "IEV";
  def __init__(self, v_ ):
    self.v = v_ ; # value
    #self.iVolFlag = 0; # intrinsic volatile flag
    #self.iRefI = [] ; # intrinsic referencing other values 
    #self.iRefO = [] ; # intrinsic referenced other values  
    #self.rVolFlag = 0 ; # runtime correspondences 
    #self.rRefI = [] ; 
    #self.rRefO = [] ; 
    #self.order = [] ; # the figured out key for this sub structure 
    #self._cabage_key_ = None  ; 
  def clear_nxt(self) :self._nxt_ = None ; 
  def set_nxt(self,nv):self._nxt_ = nv ;
  def get_nxt(self):return  self._nxt_ ; 
  def __del__(self):pass
  #def __str__(self):return self.__repr__() ;
  #def __repr__(self,idt = 0  ):
  #  return "<"+str(self.v) +"|"+str(self.iVolFlag) +"|"+str(self.iRefI) +"|"+str(self.iRefO) + ">";
  def gv(self): return self.v; # function to get the value
  
  def __getitem__(self , k ):
    return get_key_str(self  , k  , IEV.gv);
  
  def add_iRefI(self , ref):
    if(not hasattr(self  , "iRefI")) : self.iRefI = [] ; 
    if(ref not in self.iRefI): self.iRefI.append(ref);
  
  def add_iRefO(self , ref):
    if(not hasattr(self  , "iRefO")) : self.iRefO = [] ; 
    if(ref not in self.iRefO): self.iRefO.append(ref);

  def add_rRefI(self , ref):
    if(not hasattr(self  , "rRefI")) : self.rRefI = [] ; 
    if(ref not in self.rRefI): self.rRefI.append(ref);
  
  def add_rRefO(self , ref):
    if(not hasattr(self  , "rRefO")) : self.rRefO = [] ; 
    if(ref not in self.rRefO): self.rRefO.append(ref);

  def init_ref_reset(self) :
    if(hasattr(self, "iRefI")) : self.iRefI.clear() ; 
    if(hasattr(self, "iRefO")) : self.iRefO.clear() ; 

  def run_ref_clear(self) :
    if(hasattr(self, "rRefI")): self.rRefI.clear();
    if(hasattr(self, "rRefO")): self.rRefO.clear();
  
  def load_ref(self):
    if(hasattr(self, "iRefI")):self.rRefI= self.iRefI.copy() ;
    if(hasattr(self, "iRefO")):self.rRefO= self.iRefO.copy() ;
  
  def has(self , w): return hasattr(self,w);


def isiev(v):return cm.isit(v,"IEV");

def toiev(w):
  if(type(w) == list):
    L = [] ;
    for wi in w : 
      L.append(toiev(wi));
    return IEV(L) ; 
  if(type(w)== dict): 
    D ={} ; 
    for k in w :
      D[k] = toiev(w[k]);
    return IEV(D) ;
  else  : return IEV(w);

# topo KAHN related
def is_outer_ref_list(cur , ref ):
  for i,k in enumerate(cur) :
    if( k != ref[i] ): return True ;
  return False ;

def is_outer_ref_str(cur , ref ):
  return is_outer_ref_list(spk(cur) , spk(ref));

def is_self_ref_str( cur_ , ref_):
  cur = spk(cur_); lcur = len(cur);
  ref = spk(ref_); lref = len(ref);
  for i,curi in enumerate(cur) :
    if( i < lref ) :
      if(ref[i] != curi) : return False ;
    else : break ;
  return True ;
  
def is_brother_ref_str(cur ,ref) :
  a = spk(cur); 
  b = spk(ref); 
  for i,k in enumerate(a[:-1]) :
    if(b[i] != a[i]) : return False ;
  return True ;

def brother_ref_str(cur ,ref) :
  a = spk(cur);b = spk(ref); 
  a[-1] =  b[len(a)-1];
  return jnk(a);

def handle_refs(cur_ , refs):
  cur = spk(cur_)  ;   
  lcur = len(cur);
  BR = [] ;  # brother
  PR = [] ;  # over parents 
  for ref_ in refs :
    ref  = spk(ref_) ; lref = len(ref) ;
    bro = True  ; # no selected
    if( lref >= lcur ) :
      for i , curi in enumerate(cur[:-1]): 
        if(ref[i] != curi) :bro  = False ; break ; 
    else :  bro = False ;
    if(bro) :
      if( cur[ lcur - 1 ] != ref[ lcur - 1 ] ) :
        BR.append(jnk(ref[:lcur] ) ) ;
    else : 
      PR.append(ref_) ;  
  return BR,PR ; 

def mark_ref_rec( root , cur , path )  : 
  tv = type(cur.v);
  R = []  ;  
  hasVol = False ;
  if( tv == list ):
    for i ,e in enumerate( cur.v ) : 
      R_ , hasVol_ =  mark_ref_rec(root , e, slash(path) + "#" + str(i) ) ;
      R += R_ ;  
      hasVol |= hasVol_ ; 
  elif( tv == dict): 
    for k in cur.v :
      R_ , hasVol_= mark_ref_rec(root , cur.v[k] , slash(path)  + k );
      R += R_ ;  
      hasVol |= hasVol_ ; 
  elif( cm.isit( cur.v , "VLX")): hasVol = True ; 
  else : 
    if( tv == str ):
      R_ = get_refs( cur.v ); 
      for r in R_: 
        try :
          climax_check(ref_str(r)); 
        except Exception as e :
          raise Exception("mark_ref_rec climax error at at key \"{}\"\n".format(path) + str(e)) from e;
        p = _resolve_path_( root , path , ref_str(r) , IEV.gv ) ;   
        if( p == None ): raise Exception("can not find the reference \"{}\" at key \"{}\"".format(r,path));
        elif( is_self_ref_str(path , p) ): raise Exception("can not reference itself or parents \"{}\" at key \"{}\"".format(r,path)) ; 
        cur.v = cur.v.replace(r,"${"+p+"}" , 1) ;
        R.append(p) ;
        root[p].hasRef = True ; 
  BR,PR  =  handle_refs(path , R ); 
  for r in BR:
    cur.add_iRefI(spk(r)[-1]);
    get_key_str(root, r , IEV.gv).add_iRefO(spk(path)[-1]);
  if(hasVol) :  cur.iVolFlag = True;
  return PR  , hasVol ; 

def mark_ref_extra( root ,exos ): 
  for exo in exos :
    if(have_key_str(root,exo[0] , IEV.gv) and have_key_str(root,exo[1] , IEV.gv)  ):
      try : 
        a = get_key_str(root, exo[0], IEV.gv ) ;  
      except Exception as e: 
        raise Exception("during handling first extra order key {} \n".format(exo) + str(e)) from e ;
      try : 
        b = get_key_str(root, exo[1], IEV.gv ) ;  
      except Exception as e: 
        raise Exception("during handling second extra order key {} \n".format(exo) + str(e)) from e ;
      a.add_iRefO(exo[1]) ;
      b.add_iRefI(exo[0]) ;

def clear_ref_kiev(kiev):
  for k in kiev:kiev[k].run_ref_clear();

def load_ref_kiev(kiev):
  for k in kiev:    
    if( hasattr(kiev[k] , "iRefI") ):
      for r in kiev[k].iRefI:
        if(r in kiev) : 
          kiev[k].add_rRefI(r);
          kiev[r].add_rRefO(k);

def clear_ref_liev(liev):
  for iev in liev: iev.run_ref_clear();

def load_ref_liev(liev):
  for iev in liev: iev.load_ref(); 

def topo_KAHN_dict_iev( kiev ):
  clear_ref_kiev(kiev);  
  load_ref_kiev(kiev);
  L = {} ; S = {} ;  
  for k in kiev :
    if(not hasattr(kiev[k] , "rRefI") ) : S[k] = kiev[k];
    elif(len(kiev[k].rRefI) < 1 ) : S[k] = kiev[k];

  while(len(S) > 0 ) :
    k = list(S.keys())[0];
    v = S.pop(k);
    L[k] = v ;
    if( hasattr(v,"rRefO")) :
      for kp in v.rRefO:
        kiev[kp].rRefI.remove(k);
        if(len(kiev[kp].rRefI) < 1 ) :
          S[kp] = kiev[kp];
  
  for k in kiev :  
    if(hasattr( kiev[k] , "rRefI" ) and ( len( kiev[k].rRefI ) > 0 ) ) :  
      raise Exception("during topo KAHN , at around key \"{}\" has a loop".format(k));
  return L;  # this L is the sorted kiev

def topo_KAHN_list_iev(liev):
  clear_ref_liev(liev);  
  load_ref_liev(liev);
  L = {}  ; S = {} ;   
  for i,iev in enumerate(liev) :
    k = "#"+str(i);
    if( not hasattr(iev , "rRefI") ) : S[k] = iev;
    elif( len(iev.rRefI) < 1 ) : S[k] = iev;
  
  while(len(S) > 0 ) :
    k = list(S.keys())[0];
    v = S.pop(k);
    L[k] = v ;
    if( hasattr(v,"rRefO")) :
      for kp in v.rRefO:
        liev_idx_kp = liev[int(kp[1:])];
        liev_idx_kp.rRefI.remove(k);
        if(len(liev_idx_kp.rRefI) < 1 ) :
          S[kp] = liev_idx_kp;
  for iev in liev :  
    if( hasattr( iev , "rRefI" ) and len(iev.rRefI) > 0 ) :  
      raise Exception("during topo KAHN , at around key \"{}\" has a loop".format(k));
  R = [] ;
  for l in L : R.append(int(l[1:])) ;
  return R;   

def topo_KAHN(iev):
  tv = type(iev.v) ;
  if(tv == dict) : 
    iev.v = topo_KAHN_dict_iev(iev.v); 
    for k in iev.v : topo_KAHN(iev.v[k]);
  if(tv == list) : 
    iev.order = topo_KAHN_list_iev(iev.v); 
    for lv in iev.v : topo_KAHN(lv);

# volatile topology sorting related
def clear_vol_dict(kiev):
  for k in kiev :
    if(hasattr(kiev[k] , "rVolFlag" )):kiev[k].rVolFlag = 0 ; 


def set_vol_dict(kiev):
  for k in kiev :
    if(hasattr(kiev[k] , "iVolFlag" ) and kiev[k].iVolFlag): kiev[k].rVolFlag = 2 ; 


def mark_vol_dict(kiev):
  for k in kiev :
    if(hasattr(kiev[k] , "rVolFlag" ) 
      and hasattr(kiev[k] , "rRefO" ) 
      and kiev[k].rVolFlag > 0 
    ): 
      for ref in kiev[k].rRefO: kiev[ref].rVolFlag = 1 ;

  
def topo_VOL_split(kiev):
  A ={} ; B = {} ; C = {} ; 
  on = False ; 
  for k in kiev :
    #if(hasattr(kiev[k] ,"rVolFlag")): 
    if( (not on ) and hasattr(kiev[k] ,"rVolFlag") and  kiev[k].rVolFlag == 2 ):
      B[k] = kiev[k];
      on = True ; 
    elif( hasattr(kiev[k] ,"rVolFlag") and kiev[k].rVolFlag >=1 ) :
      C[k] = kiev[k];
    else :
      A[k] = kiev[k];
  return A , B , C ; 


def topo_VOL_dict(kiev_ ):
  if( 0 == len(kiev_)) : return {} ;   
  kiev = topo_KAHN_dict_iev(kiev_) ;  
  clear_vol_dict(kiev);
  clear_ref_kiev(kiev);
  load_ref_kiev(kiev);
  set_vol_dict(kiev);
  mark_vol_dict(kiev);
  A,B,C = topo_VOL_split(kiev);
  A.update(B);
  A.update(topo_VOL_dict(C));
  return A ; 


def get_vols_iev( cur , subStr = "" , w  = "vol" , ) ->dict : 
  tv = type( cur.v ) ; 
  if( tv ==  list ): 
    R = {} ; 
    for i,e in enumerate(cur.v):
      R.update(get_vols_iev(e  , subStr + "_" + str(i)  , w)   ); 
    return R ;  
  elif( tv == dict ) :
    R = {} ; 
    for k,e in cur.v.items():  
      R.update( get_vols_iev(e , subStr + "_" + k , w) );
    return R;
  elif( cm.m_isit(cur.v , w)  ):
    return  { subStr :cur.v.ret() };
  else :return {} ;


def get_vols_kiev( kiev  , w = "vol") :  
  vols  = {} ; 
  for k,v in kiev.items() :
    vols.update( get_vols_iev(v , k  , w ) );
  return vols ; 


def dfs_create_list(cur , L , path=""  , CK={}):
  tv = type(cur.v) ;
  if( list == tv ): 
    for idx in cur.order : dfs_create_list( cur.v[idx] , L  , slash(path) + "#"  + str(idx)  , CK );
  if( dict == tv ) :
    for k in cur.v  :  dfs_create_list( cur.v[k] , L , slash(path) + k  , CK );
  L.append(cur) ;   
  if( isiev(cur) and hasattr(cur , "hasRef") ): cur.path  = path ;  
  if( isiev(cur) and hasattr(cur , "_cabage_key_") ):  
    CK[len(L) - 1] =path ; 

def locate_cab(CK , idx):
  cab = "";
  for k in  CK : 
    if( k >= idx) : return CK[k] ;
  return cab ; 


#hieracial dict
class DICT(dict):
  def __setitem__(self , ks_ , v):
    ks = spdash(ks_);
    t = self;  
    for k in ks[:-1]:
      if(k not in t): dict.__setitem__(t,k,{}) ; 
      t = dict.__getitem__(t,k) ;
    dict.__setitem__(t,ks[-1] ,v) ;
  
  def __getitem__(self, ks_ ):
    ks = spdash(ks_);
    t = self;  
    for k in ks: t = dict.__getitem__(t,k) ;
    return t; 


# mapped dict
class MDICT(DICT):
  def _map_rec_(self, ks_, sd ): 
    ks = spdash1(ks_);
    if( ks[0] in sd.keys() ):
      v = sd[ks[0]];
      # remaping # might have a loop here 
      while( type(v)==str and v[0]=="@"): 
        if( not v[1:] in self.keys() ) : return None ;
        v = self[ v[1:] ];
      # had a good match 
      if( type(v) == str  and len(ks) == 1 ) : 
        return v ; 
      # had a half match :
      elif(len(ks)==2 and type(v) == str ) : 
        return v +"-"+ks[1];  
      # had a hierarchy match 
      elif( len(ks) > 1 and type(v) == dict ):
        return self._map_rec_( ks[1] ,  v );
      # ks==1 and type(v) == dict , not enough sub match
    return None ;

  def _map_(self, sk):
    w = self._map_ret_none_(sk) ;
    if(None != w):  return w; 
    return sk ;
  
  def _map_ret_none_(self, sk):
    mks = regex.findall(ref3 , sk  ) ;
    if(len(mks) >  0 ): 
      mk = mks[0].split("!")[-1];
      mtc = self._map_rec_(mk,self); 
      if(None != mtc ) : return sk.replace(mk , mtc , 1);
    return None ;


def to_global_ref_str(droot ,md ,prx , s_):
  s = s_ ;  
  for r_ in get_refs(s_):
    rr = ref_str(r_);
    r = md._map_ret_none_(rr); 
    if(r==None):
      if(have_key_str(droot,rr) ):
        s= s.replace(r_ , "${"+shift_climax(prx ,rr)+"}"  , 1 ); # make it global
    else:
      s= s.replace(r_ , "${"+r+"}" ,1); # make it global
  return s ;

def to_global_ref_dict(droot ,md , prx , D):
  for k in D :
    if(type(D[k])==dict):
      to_global_ref_dict(droot , md , prx , D[k]);
    elif(type(D[k]) == str):
      D[k] = to_global_ref_str( droot ,md , prx, D[k]);
    elif(type(D[k]) == list)  :
      to_global_ref_list( droot,md , prx , D[k]);

def to_global_ref_list( droot ,md, prx , L):
  for i,l in enumerate(L) :
    if(type(l)==dict):
      to_global_ref_dict(droot ,md ,  prx ,l);
    elif(type(l) == str):
      L[i] = to_global_ref_str( droot ,md, prx, l);
    elif(type(l) == list)  :
      to_global_ref_list( droot, md, prx , l);

def popn(stack , n ):
  ls =len(stack) ;
  if(len(stack) < n ): raise Exception("pop - Stack empty") ;
  L = [ ] ;   
  for i in range(n) :
    L.append(stack.pop()) ;
  L.reverse() ; 
  return L  ;

class RK:  # this is the run key ;
  # an content without record index as -1 
  def __init__(self ,rec_idx_=-1,content_="" ):
    self.rec_idx = rec_idx_ ; 
    self.content = content_ ; 
  def __str__(self) :return self.content ;

class Root:
  def __init__(self ,  addr ,TIMEOUT=6666):
    self.__run_attr__= [
      [ "SAVE_PATH" , "" ] ,      
      [ "DATA_FILE" , "" ] ,      
      [ "LOG_KEY" , "" ] ,      
      [ "SAVE_PATH_MAJ" , "" ] ,      
      [ "SAVE_PATH_MNR" , "" ] ,      
      [ "SETTING_PATH" , "" ] ,      
      [ "DIR_TO_SAVE" , [] ] ,      
      [ "FILE_TO_SAVE" , []] ,      
      [ "ACTIONS" , [] ] ,      
      [ "POINT" , {}] ,
      [ "TRACE" , {}] ,
      [ "PLOTER" , None ] ,  
      [ "TOKEN_KEY" , "ROLL" ] , 
      [ "DELAY" , 0  ]  ,
      [ "LASTDO" , []  ]  , 
      [ "CHUNK_SIZE" , 50]
    ]; 
    self.addr = addr ;  
    self.TIMEOUT = TIMEOUT ; 
    self.connect();  
    cm.dict2attr(self, self.__run_attr__, {}) ;
    self.base = {} ;  # the base must be a dictionary
    self.defs = MDICT() ;  # maps; 
    self.exos = [] ; # extra orders, typically key-key  pair
    self.vb = {} ; # variable bay  
    self.cabage = {}  ; 
    self.globals={"np":np,"self":self , "w_method": self.wmethod , "q_method" : self.qmethod} ;
    self.fresh = True;  
    self.roll = True; 
    self.MACROS = {};
    self.dirty = True ; 

    self.BEF = [] ; # before
    self.AHEAD = set(); 
    self.AFF = [] ;  # after
    #self.P  = mp.Pool(mp.cpu_count()); 
  
  def ctx(self,**kwds) : self.globals.update(kwds); 

  def connect(self)  : 
    self.__context__ = zmq.Context(); 
    self.__socket__ = self.__context__.socket(zmq.REQ); 
    self.__socket__.setsockopt(zmq.RCVTIMEO, self.TIMEOUT )  
    self.__socket__.setsockopt(zmq.CONNECT_TIMEOUT , self.TIMEOUT ) ;
    self.__socket__.connect("tcp://%s" % self.addr) ;

  def sdrc(self , w ) :
    self.__socket__.send_pyobj( w );   
    R = self.__socket__.recv_pyobj();  
    assert( not cm.isit(R , cm.ERROR.__maj_type__) ),"Error setting values : {} check server for error ".format(R.e); 
    return R ;
 
  def wmethod(self, k , v ): 
    return self.sdrc(cm.OP(cm.OP.SET,{k:v})); 

  def wbash(self , d ) : 
    return self.sdrc(cm.OP(cm.OP.SET,d))

  def qmethod(self , k ): 
    return self.sdrc(cm.OP(cm.OP.GET,[k])); 
  
  def qbash(self , l ): 
    return self.sdrc(cm.OP(cm.OP.GET,l)); 

  def keys(self):
    if(hasattr(self , "s") ) :
      return list(self.s.keys()) ; 
    else :  
      return list(self.base.keys());
  
  def __setitem__(self,  ks_  , v ) :
    try : on_set_key_str( self.base , self.map( self.map(ks_) ),  v);
    except Exception as e : 
      raise Exception("Root-__setitem__ key : \"{}\"\n".format(ks_) + str(e)) from e ; 

  def map(self,k_):return self.defs._map_(k_);

  def set(self, ks_ , v) :
    try : set_key_str( self.base , ks_ ,  v);
    except Exception as e : 
      raise Exception("Root-set key : \"{}\"\n".format(ks_) + str(e)) from e ; 

  def __getitem__(self, ks_ ):
    try :return get_key_str(self.base, ks_) ;
    except Exception as e : 
      raise Exception("Root-getting key : \"{}\"\n".format(ks_) + str(e)) from e ; 

  def eval_hier(self, w):
    tw = type(w) ;
    if(tw == list):
      W =[];
      for sw in w : W.append(self.eval_hier(sw));
      return W ;
    elif(tw == dict):
      W ={};
      for k,v in w.items() : W[k] = (self.eval_hier(v));
      return W ;
    elif(tw in [int, None, float ,bool]):return w ;
    elif(tw==str):
      return self.eval_str(w);

  def eval_str(self,  s_ ) :
    s = s_ ; 
    for r in get_refs(s_) :
      s = s.replace(r , "self.vb[\"{}\"]".format(ref_str(r)) ,  1);
    #print("--eval--\"{}\"".format(s));
    sp = do_nums(s);
    try :
      return eval(sp , self.globals  ) ;
    except Exception as e : 
      raise Exception("eval_str - \"{}\"\n".format(sp) + str(e) ) from e ;
 
  def eval_str_tmp(self,  s_ ) :
    s = s_ ; 
    for r in get_refs(s_) :
      s = s.replace(r , "self.Temp[\"{}\"]".format(ref_str(r)) ,  1);
    #print("--eval--\"{}\"".format(s));
    sp = do_nums(s);
    try :
      return eval(sp , self.globals  ) ;
    except Exception as e : 
      raise Exception("eval_str - \"{}\"\n".format(sp) + str(e) ) from e ;
 




  def keep(self ,**d): self.globals.update(d);
  
  def order(self, *orders): 
    for l in orders :  
      lo = len(l) ;
      for i,e in enumerate(l) :  
        if(i < lo -1 ): self.exos.append( [e ,l[i+1] ] ) ;  
 

  def decide_run_keys(self, L , sidx = 0, rec_extra ={} ): 
    # this function is mainly for the Reading
    RET = {}; 
    REC = []  ;  
    r_idx = sidx;  
    for i,k_ in enumerate(L):
      ridx = -1 ; 
      if(k_[0]=="*") : 
        k = k_[1:] ;
      else: 
        k = k_ ;
        ridx = r_idx ;
        r_idx +=1;
        REC.append(k);
      a = L[k_];
      R =  get_refs(a); 
      for r in R:
        rr = ref_str(r);
        p = _resolve_path_( self.ievs ,"" ,ref_str(r) , IEV.gv ) ;   
        if( p == None ): 
          if(rr in RET or rr in rec_extra): # the thing is referenced in the  Reading
            a  = a.replace(r , "self.Temp[\"CHANNEL-"+rr+"\" ] ");
          else : 
            raise Exception("CHANNELS  at key \"{}\" , cant find reference \"{}\"".format(k,r));
        else :  
          a = a.replace(r,"self.Temp[\""+p+"\"]",  1) ;
          self.ievs[p].hasRef = True ;  
      for r in get_refs_mach(a) :
        a = a.replace(r,"q_method(\""+self.map(ref_str(r))+"\")", 1) ;
      RET[k] = RK(ridx,a) ; 
    return REC,RET ; 

  def sort(self): 
    # create information enhanced class 
    self.ievs = toiev(self.base)  ;

    # mark the reference 
    Z , hasVol = mark_ref_rec(self.ievs , self.ievs , "");
    mark_ref_extra(self.ievs , self.exos) ; 
   
    # decide the run keys : 
    self.rec_key_TRACE,self.TRACE_SHOT = self.decide_run_keys(self.TRACE)  ;
    self.rec_key_POINT,self.POINT_SHOT = self.decide_run_keys(
        self.POINT, 
        len(self.rec_key_TRACE) ,
        self.TRACE_SHOT
    );
    self.CHANNEL_NAMES =  self.rec_key_TRACE +self.rec_key_POINT  ;
    self.CHANNEL_NAMES_SHOT =  list(self.TRACE_SHOT.keys()) + list(self.POINT_SHOT.keys()) ;
    self.alcm =  len(self.TRACE_SHOT) + len(self.POINT_SHOT) ;
    self.lcm =  len(self.CHANNEL_NAMES) ;
   
    # general topo key sort 
    for k ,v  in self.ievs.v.items() : 
      topo_KAHN(v) ;  v._cabage_key_ = k ;   

    # volatile weighted topological sort ;  
    self.s = topo_VOL_dict(self.ievs.v) ;
    self.sta = {} ; self.dyn = {};
   
    # make a split
    dynamic = False;
    for k,vk in self.s.items() :
      dynamic |= hasattr(vk, "iVolFlag") and getattr(vk ,"iVolFlag");  
      if(dynamic) : self.dyn[k] = vk ;
      else : self.sta[k] = vk ;
 
    # prepare sequence 
    self.seq = [] ; 
    self.CabTab = {} ; 
    for k,vk in self.sta.items() : dfs_create_list(vk ,  self.seq  , k , self.CabTab)  ;
    self.dynstart = len(self.seq);
    for k,vk in self.dyn.items() : dfs_create_list(vk ,  self.seq , k , self.CabTab )  ;
  
  def show_order(self) :
    if(hasattr(self,  "s")) :
      for k in self.s.keys() : 
        print(k) ;

  def get_vols(self) :
    if(hasattr(self , "s") ) : return get_vols_kiev(self.s ,"vol" ) ; 
    else : return {} ; 

  def get_opts(self) :
    if(hasattr(self , "s") ) : return get_vols_kiev(self.s ,"opt") ; 
    else : return {} ; 

  def total(self):
    tot = 1 ; 
    for k,v in self.get_vols().items() :  tot*=len(cm.get_iter(v));
    return tot ; 
    
  def gen(self ,  stack:list=[]  , idx:int=0 ,  tp:int = -1  ):
    if(self.roll):self.cabage[clix(self.map(self.TOKEN_KEY))]=True;    
    yield from self.gen_rec( stack , idx ,tp ); 

  def gen_rec(self ,stack:list=[] ,idx:int=0, tp:int = -1  ):
    while(True):
      if( 
          idx >= len(self.seq)
          or ( tp > 0 and idx >= tp )
        )  : 
        yield self.cabage.copy() ; 
        self.cabage.clear() ; 
        return ; 
      cur = self.seq[idx];
      v = cur.v; 
      if( cm.m_isit(v , "vol") ) :
        try :
          for w in cm.get_iter(v.arg):
            stcp = stack.copy();  
            stcp.append(w);
            if( hasattr(cur , "path") ): self.vb[cur.path] = stcp[-1] ;
            if( hasattr(cur , "_cabage_key_") ): self.cabage[cur._cabage_key_] = stcp.pop() ;

            yield from self.gen_rec(  stcp  ,idx + 1,  tp ) ;
          

          if(self.roll):self.cabage[clix(self.map(self.TOKEN_KEY))]=True;    
          return ; 
        except Exception as e : 
          raise Exception("gen : during sweeping at \"{}\" \n".format(locate_cab(self.CabTab ,idx)) + str(e)) from e ;
      else : 
        tv = type(cur.v) ;
        if( list == tv ): 
          lv = len(v) ;
          L = popn(stack,lv);
          S = [None]*lv ;  
          for i,ip in enumerate(cur.order)  : S[ip] = L[i] ;
          stack.append(S) ;
        elif( dict == tv) : 
          lv = len(v)  ;
          L = popn(stack,lv);
          S ={} ; 
          for i,k in enumerate(v) : S[k] = L[i] ; 
          stack.append(S) ;
        elif( str == tv ) :  
          try : 
            stack.append(self.eval_str(v)) ;
          except Exception as e : 
            raise Exception("gen : during evaluating key \"{}\" when evaluating : \n\"{}\"\n".format(locate_cab(self.CabTab ,idx) , v) + str(e)) from e ;
        elif( cm.m_isit(v , "opt") ) :
          stack.append(v.optv); 
        else:
          stack.append(v);
        
        if( hasattr(cur , "path") ): self.vb[cur.path] = stack[-1] ;
        if( hasattr(cur , "_cabage_key_") ): self.cabage[cur._cabage_key_] = stack.pop() ;
        idx = idx + 1 ;


  def dict_to_root_rec(self ,droot , prx  ,d ,dpath="" ) :
    for k in d.keys():
      climax_check(k);
      ks = self.defs._map_ret_none_(k); 
      if( ks == None): 
        hpath = shift_climax(prx , k ) ;  # didnt find the ks in map
      else: hpath = ks ; # direct giving keys
      dk = d[k];
      if( type(dk) == dict ) :
        self.set(hpath , dk);
        to_global_ref_dict(droot,self.defs,prx,dk);
      elif( type(dk) == list ) :
        self.set(hpath,dk);
        to_global_ref_list(droot, self.defs, prx,dk);
      elif( type(dk) == str ):
        self.set(hpath,to_global_ref_str( droot , self.defs , prx , dk) );
      elif( type(dk) in [ type(None) , int , float , bool ] ):
        self.set(hpath,dk);
  

  def load( self , d , prx:str=""):
    dks = list(d.keys()) ;
    if( "CONNECT" in d and d["CONNECT"] == False) : return; 
    if("MAP"  in dks):  self.defs.update(d["MAP"]);
    if("NAME" in dks) : prx =cm.dash(prx)+ d["NAME"]  ;
    if("STAGING_IMMEDIATE" in dks): 
      things = self.eval_hier(d["STAGING_IMMEDIATE"]) ;
      self.dict_to_root_rec(things, cm.dash(prx) , things , "");

    if("STAGING" in dks): self.dict_to_root_rec(d["STAGING"], cm.dash(prx) , d["STAGING"] , "");
    if("IMPORT" in dks):
      for k in d["IMPORT"]:
        module = cm.ipl.import_module(k)
        cm.rl(module);
        import_as = d["IMPORT"][k];
        if(len(import_as) > 0 ) : 
          self.globals[import_as] = module;
        else:
          self.globals.update(vars(module));
    
    if("IMPORT_ONCE" in dks):
      for k in d["IMPORT_ONCE"]:
        module = cm.ipl.import_module(k)
        import_as = d["IMPORT_ONCE"][k];
        if(len(import_as) > 0 ) : 
          self.globals[import_as] = module;
        else:
          self.globals.update(vars(module));
 
    if("ORDER" in dks ): 
      for L in d["ORDER"]:
        lL = len(L);
        for i,e in enumerate(L) :
          if(i < lL-1) : 
            self.exos.append([shift_climax(cm.dash(prx) , e) , shift_climax(cm.dash(prx)  , L[i+1] ) ]) ;
    
    if("RUN" in dks ) : 
      cm.dict2attr(self, self.__run_attr__, d["RUN"]) ;

    # reading in the keys that should be done ahead. 
    if("BEF" in dks) : 
      #print(d["BEF"]) ; 
      self.BEF = self.BEF + d["BEF"]; 
    if("AFF" in dks) : 
      #print(d["AFF"]) ; 
      self.AFF = self.AFF + d["AFF"]; 
   
    if("AHEAD" in dks) : self.AHEAD.update(d["AHEAD"]); 


  def load_dir(self, path , prx ="" ):
    for f in sorted(os.listdir(path)) : 
      if(len(f)> 0 and f[0] == '.') : continue;
      tgt = cm.os_slash(path)+f ;
      if(os.path.isfile(tgt) and tgt[-4:] == "json"):
        try : 
          D = rwjson.read(tgt);
          
          for k,v in cm.dkd(D, "MACRO", {}).items():
            if(k not in self.MACROS) : self.MACROS[k] = v ;
          E = rwjson.mux_dict(D,self.MACROS)   ;
          self.load(E,prx);
        except Exception as e: 
          raise Exception(" -root- reading file '{}'\n".format(f) + str(e)) from e ;
      if(os.path.isdir(tgt)):
        try:
          self.load_dir( tgt , cm.dash(f.split("-")[-1]));
        except Exception as e :
          raise Exception(" -root- reading directory '{}'\n".format(f) + str(e)) from e ;
 
  def am(self, **kwds):
    """
      add macros 
    """
    self.MACROS.update(kwds);

  def chunk_size(self) :
    vols = self.get_vols() ; 
    if(len(vols.keys()) > 0 ) : 
      return len(cm.get_iter(vols[ list(vols.keys())[-1]  ]) ) ;
    return 1;  
  

  def initiate_run(self , Choose = "A"): 
    """
      [A]append [N]new  [C]cover [X]abort
    """
    
    # sort 
    self.sort(); 

    if(self.PLOTER!=None): self.PLOTER = cm.offrep(self.map(self.PLOTER)) ;

    # computing nessesaries  :  
    self.SAVE_PATH =  cm.os_slash(self.SAVE_PATH_MAJ) + self.SAVE_PATH_MNR  ;
    choices =["A" , "N" , "C" , "X"]  ;
    vols = self.get_vols(); 
    assert(Choose in  choices) ; 
    pre_dir,new_dir = rwdata.dir_choices(self.SAVE_PATH);
    appendAble = False ; 
    if(pre_dir!=None):
      df = cm.os_slash(pre_dir)+"DATA.hdf5"; 
      if(os.path.isfile(df)): 
        appendAble = rwdata.append_able(df, vols ,self.CHANNEL_NAMES); 
    
    if(Choose == "A") :
      if(appendAble):
        self.SAVE_PATH = pre_dir ;
        self.DATA_FILE = cm.os_slash(self.SAVE_PATH)+"DATA.hdf5"; 
        self.LOG_KEY = rwdata.log_key_choices(self.DATA_FILE)[1];
        rwdata.vol_write(self.DATA_FILE ,vols , self.LOG_KEY) ;
      else : Choose = "N"; 
    
    if(Choose == "C") :
      if(pre_dir !=None) :
        self.fresh = True;
        self.SAVE_PATH = pre_dir ;
        self.DATA_FILE = cm.os_slash(self.SAVE_PATH)+"DATA.hdf5"; 
        rwdata.create_basic(self.DATA_FILE ,vols, self.CHANNEL_NAMES) ;  
        self.LOG_KEY = rwdata.log_key_choices(self.DATA_FILE)[1];
        rwdata.vol_write(self.DATA_FILE ,vols , self.LOG_KEY) ;
      else : 
        Choose = "N" ; 
    if(Choose == "N") :
        self.fresh = True;
        self.SAVE_PATH = new_dir ;
        cm.mkdir(self.SAVE_PATH);
        self.DATA_FILE = cm.os_slash(self.SAVE_PATH )+"DATA.hdf5"; 
        rwdata.create_basic(self.DATA_FILE ,vols, self.CHANNEL_NAMES) ;  
        self.LOG_KEY= rwdata.log_key_choices(self.DATA_FILE )[1];
        rwdata.vol_write(self.DATA_FILE ,vols , self.LOG_KEY) ;
    
    # abortion
    if(Choose == "X") : 
      print("Experiment Aborted");
      return False ;

    # copy settings
    if(self.fresh) : 
      self.copy_settings();
      self.fresh = False; 
 

    # send names to ploter 
    if(None != self.PLOTER) :
      self.wmethod( 
          self.PLOTER + "-pcn",  
          list(self.POINT_SHOT.keys())
      ); 
      self.wmethod( 
          self.PLOTER + "-tcn",  
          list(self.TRACE_SHOT.keys())
      ); 
    
    return True ; 

  def copy_settings(self):
    for d in self.DIR_TO_SAVE: cm.cpr(d,cm.os_slash(self.SAVE_PATH) + d) ;
    for f in self.FILE_TO_SAVE: cm.cp(f,cm.os_slash(self.SAVE_PATH) + f) ;


  def run(self,  Choose = "A"  ,block=True  , mode = "N"  , run_whole:bool = True) : 
    """
      Choose:
        [A]append [N]new  [C]cover [X]abort
        A : append data if the save path exist and experiment are similiar
        N : create new path every time with _XX as prefix, where XX is incremental numbers
        C : delete old data and cover the save path( the latest _XX one ) with new data
        X : just initiate actions, do not run experiment or save data, used to debug.
      block : 
        if it is true, the program is blocked.
        if it is false, the program runs in a thread.
      mode : 
        [N]ormal ,[A]head,
        if choosen normal , it will just do normal experiment sequences
        if choosen ahead , it will do ahead action in a number of chunks,
          This is particularly needed for instruments like AWG5208's sequence mode.
    """
    
    if( len(regex.findall(brrrt , mode)) > 0 ) : mode = 'A' ; 
    elif(mode not in ["A" ,"N"]) : mode = "N"  ; 
    
    if("N" == mode) : action = Root.run_action ; 
    elif("A" == mode) : action = Root.run_action_ahead;


    assert(len(self.get_opts()) == 0 ) , "Can't do run with opt instance" ;
    # make decision 
    if( not self.initiate_run( Choose) ) : return ; 
    
    # decide where to run : 
    if(run_whole): st = 0 ;
    else : st = self.dynstart;
    
    # last preparation
    self.Temp = {} ;  
    self.stack = []
    self.CHUNK = empl(self.lcm) ; 
    self.cz = max(10 , self.chunk_size());   
    self.ShouldStop = False ; 
    
    # start the run
    if(block):
      action(self, st );
    else:
      self.th = threading.Thread(target = action ,args=(self,st,)  ); 
      self.th.start() ;  

  def set_val(self, st):
    L = {} ; 
    for k,v in st.items() :
      if(k[0]=='!') : L[ k[1:] ]=v   ; 
      self.Temp[ k ] = v;
    self.wbash(L) ;  #set everything


  def set_single(self,k,v): 
    if('!' == k[0]) : self.wmethod( k[1:]  , v ) ;  
    self.Temp[k] = v;

  def run_action( self , idx:int = 0 , RET_DATA = False ,progress = tqdm  ):
    self.unpause();
    #if(RET_DATA): self.DATA = empl(self.alcm) ; 
    if(RET_DATA): self.DATA = empd(self.CHANNEL_NAMES_SHOT) ; 
    lc = 0 ; 
    for stid,st in progress(enumerate(self.gen(self.stack , idx )),total = self.total()):

      # assigning values
      self.set_val(st); 

      # have a delay 
      if( self.DELAY!= 0) : time.sleep(self.DELAY ) ; 
   

      for t in self.LASTDO : self.eval_str(t) ;
     
      # taking measures 
      for m in self.ACTIONS: self.qmethod(self.map(m));

      # collecting Data
      idx = 0 ; 
      T = [] ;  # trace data
      for i,k in enumerate(self.TRACE_SHOT.keys()) : 
        trc = self.TRACE_SHOT[k];
        w = self.eval_str(str(trc));   
        self.Temp["CHANNEL-"+  k ]  = w ; 
        T.append(w) ; 
        if(trc.rec_idx != -1 ) : self.CHUNK[trc.rec_idx].append(w); 
        if(RET_DATA): self.DATA[k].append(w); 
        idx +=1;
        lc+=1;

      P =  [ ] ;  # point data
      for i,k in enumerate(self.POINT_SHOT.keys()) : 
        pnt = self.POINT_SHOT[k] ;
        w = self.eval_str(str(pnt));   
        self.Temp["CHANNEL-"+  k ]  = w ; 
        P.append(w) ; 
        if(pnt.rec_idx != -1):self.CHUNK[pnt.rec_idx].append(w); 
        if(RET_DATA): self.DATA[k].append(w); 
        idx +=1;
        lc+=1;

      # send it if there is address
      if(self.PLOTER!= None):
        self.wmethod( self.PLOTER + "-trs", T ); 
        self.wmethod( self.PLOTER + "-pts", P ); 
      
      # save data each time a roll happens
      if(stid % self.cz == 0 and lc >0):
        try: 
          rwdata.data_write(self.DATA_FILE, self.CHUNK , self.CHANNEL_NAMES , self.LOG_KEY);
          self.CHUNK = empl( self.lcm); 
          lc =0 ;
        except FileExistsError:
          print("hdf5 file writing IO temporarily not existing");
        except BlockingIOError : 
          print("hdf5 file writing IO temporarily blocked");
      if(self.ShouldStop):break;  
      
      while(self.ShouldPause):
        time.sleep(PAUSE_TIME);
        self.__pausen__ +=1;
        if(self.__pausen__ % 10 == 0) : print("pausing")

    while(lc > 0) :
      try : 
        rwdata.data_write(self.DATA_FILE, self.CHUNK , self.CHANNEL_NAMES , self.LOG_KEY);
        self.CHUNK = empl(self.lcm) ; 
        lc = 0 ; 
      except FileExistsError:
        print("hdf5 file writing IO temporarily not existing");
        time.sleep(0.5);
      except BlockingIOError: 
        print("hdf5 file writing IO temporarily blocked");
        time.sleep(0.5);
    if(RET_DATA): return self.DATA ;

  def stop(self):
    if(hasattr(self, "th") and getattr(self ,"th").is_alive):
      self.ShouldStop = True;
      self.th.join();
    else :
      self.ShouldStop = True;

  def pause(self): 
    self.__pausen__ = 0 ;
    self.ShouldPause = True ;
  
  def unpause(self): 
    self.__pausen__ = 0 ;
    self.ShouldPause = False ;

  def ap(self, **kwds):
    """
      add to self.POINT by keywords 
    """
    self.POINT.update(kwds);

  def at(self, **kwds):
    """
      add to self.TRACE by keywords 
    """
    self.TRACE.update(kwds);

  def disable_roll(self) :
    self.roll = False;

  def enable_roll(self):
    self.roll = True;

  def disable_ploter(self):
    self.PLOTER=None;
    self.TOKEN_KEY=None;
    self.roll = False;

  def setup_opt(self , Choose = "A" , data_handle_function=lambda x:0  ): 
    """
      after setup please use opt_function2    
      where this data_handle_function is like this:
      data_handle_function will recive the Root class.
      The purpose of data_handle_function is to  
      return a scalar based on the measuremnt, and this
      scalar will be te optimization target.
      In one chunk the data is stored in the 
      root.DATA section.

      also if needed the root.roll = False could be set 
      here so the Data viewer stop rolling

      the recived data(aka root.DATA) is in the format of 
      {
        "S":[[1,2,3],[1,2,3],[1,2,3]]
        "A":[1,2,3],
        "B":[2,3,4]
      }

      so for example if one like to extract mean of S as the scalar
      a good data_handle_function could be set up as 
      
      >>  
      def data_handle(root):
        root.roll = False; # stop rolling in dataview
        returrn np.mean(root.DATA["S"]);
    
      and then this data_handle is used as : 

      >> g.setup_opt("C" , data_handle) ;

      and to use this 

      >> g.opt_function2(args) 

      will do the experiment run and then spit out the result for
      optimization.

      the args are the things to pass in for the optimization parameters.
      To use this with the scipy.optimize.minimize

      >>minimize(g.opt_function2 , [1,2,3] ,method='Nelder-Mead' ,  max_iter =100 ) ;


    """

    self.globals["_iter_n"]  = 0 ;
    self.POINT["_iter_n"] = "_iter_n";
    # make decision 
    if( not self.initiate_run(Choose) ) : return ; 

    # last preparation
    self.Temp = {} ;  
    self.stack = []
    self.CHUNK = empl(self.lcm) ; 
    self.cz = self.chunk_size();   
    self.ShouldStop = False ; 
    self.opts = self.get_opts(); 
    self.data_handle_function = data_handle_function;
    self.dirty  = True ; 
    ## static generation 
    #for st in self.gen(self.stack,0,self.dynstart):
    #  # assigning values
    #  self.set_val(st) ;
      
  def set_iter_zero(self):
    self.globals["_iter_n"]  = 0 ;
  
  def opt_function(self,arg) :  
    """
      The optimize function ,
      the data_handle_function is going to recive data
      
      the recived data is in the format of 
      {
        "S":[[1,2,3],[1,2,3],[1,2,3]]
        "A":[1,2,3],
        "B":[2,3,4]
      }
      like format, where this S is a trace reader ,
      and this A and B are points
    """
    for k,opt in self.opts.items() : opt.optv = arg[opt.idx]; 
    return self.data_handle_function(self.run_action(self.dynstart,True,quiet_bar_replace)); 

  def opt_function2(self,arg) :  
    """
      use this function to pass in optimizing arguments
    """
    
    self.globals["_iter_n"] +=1;
    for k,opt in self.opts.items() : opt.optv = arg[opt.idx]; 
    if(self.dirty) : st = 0 ;  
    else : st = self.dynstart ;
    self.run_action(st,True,quiet_bar_replace)
    self.roll = False; 
    self.dirty = False;
    return self.data_handle_function(self); 
 
  def run_action_ahead( self , idx:int = 0 , RET_DATA = False ,progress = tqdm  ):
    self.unpause();
    #if(RET_DATA): self.DATA = empl(self.alcm) ; 
    if(RET_DATA): self.DATA = empd(self.CHANNEL_NAMES_SHOT) ; 
    lc = 0 ; 
    
    #TODO : read the chunk size from setting file. 
    self.action_setting_bay = [];   # collection of the settings in size of chunks . 
    self.ahead_key_all = {} ; # must have had all the ahead key. 

    tot = self.total() ; 
    for stid_,st_ in progress(enumerate(self.gen(self.stack , idx )),total = tot):
      self.action_setting_bay.append((stid_,st_.copy()));
      # ACTION chunked 
      if(
          len(self.action_setting_bay) >= self.CHUNK_SIZE
          or
          stid_ >= tot-1   #  it is actually the very last step
      ) : 
        # ACTION ahead 
        #print("ACTION before ahead") ; 
        for m in self.BEF: 
          #print(m) ; 
          self.qmethod(self.map(m)); 

        #print("ACTION ahead") ; 
        for stid,st in self.action_setting_bay : 
          to_be_del_ks = []  ; 
          for k,v in st.items() : 
            if ( k in self.AHEAD) : 
              #print("AHEAD KEY : " , k );
              self.ahead_key_all[k] = v ; 
              to_be_del_ks.append(k);
          self.set_val(self.ahead_key_all); # every step all theys must be set
          [ st.pop(k) for k in to_be_del_ks] ; # poping them out for normal action

        #print("ACTION after ahead") ; 
        for m in self.AFF: 
          #print(m) ; 
          self.qmethod(self.map(m)); 

        # ACTION normal
        for stid,st in self.action_setting_bay : 
           
          # assigning values
          self.set_val(st); 
          # have a delay 
          if( self.DELAY!= 0) : time.sleep(self.DELAY ) ; 
          
          # what to do last 
          for t in self.LASTDO : self.eval_str_tmp(t) ;
     
          # taking measures 
          for m in self.ACTIONS: self.qmethod(self.map(m));

          # collecting Data
          idx = 0 ; 
          T = [] ;  # trace data
          
          for i,k in enumerate(self.TRACE_SHOT.keys()) : 
            trc = self.TRACE_SHOT[k];
            w = self.eval_str_tmp(str(trc));   
            self.Temp["CHANNEL-"+  k ]  = w ; 
            T.append(w) ; 
            if(trc.rec_idx != -1 ) : self.CHUNK[trc.rec_idx].append(w); 
            if(RET_DATA): self.DATA[k].append(w); 
            idx +=1;
            lc+=1;

          P =  [ ] ;  # point data
          for i,k in enumerate(self.POINT_SHOT.keys()) : 
            pnt = self.POINT_SHOT[k] ;
            w = self.eval_str_tmp(str(pnt));   
            #print(pnt,w);
            self.Temp["CHANNEL-"+  k ]  = w ; 
            P.append(w) ; 
            if(pnt.rec_idx != -1):self.CHUNK[pnt.rec_idx].append(w); 
            if(RET_DATA): self.DATA[k].append(w); 
            idx +=1;
            lc+=1;

        
          
          # send it if there is address
          if(self.PLOTER!= None):
            self.wmethod( self.PLOTER + "-trs", T ); 
            self.wmethod( self.PLOTER + "-pts", P ); 
          
          # save data each time a roll happens
          if(stid % self.cz == 0 and lc >0):
            try: 
              rwdata.data_write(self.DATA_FILE, self.CHUNK , self.CHANNEL_NAMES , self.LOG_KEY);
              self.CHUNK = empl( self.lcm); 
              lc =0 ;
            except FileExistsError:
              print("hdf5 file writing IO temporarily not existing");
            except BlockingIOError : 
              print("hdf5 file writing IO temporarily blocked");
          if(self.ShouldStop):break;  
          
          while(self.ShouldPause):
            time.sleep(PAUSE_TIME);
            self.__pausen__ +=1;
            if(self.__pausen__ % 10 == 0) : print("pausing")

        self.action_setting_bay.clear(); # going for next round   

    # after the exit of the big fat for loop 
    while(lc > 0) :
      try : 
        rwdata.data_write(self.DATA_FILE, self.CHUNK , self.CHANNEL_NAMES , self.LOG_KEY);
        self.CHUNK = empl(self.lcm) ; 
        lc = 0 ; 
      except FileExistsError:
        print("hdf5 file writing IO temporarily not existing");
        time.sleep(0.5);
      except BlockingIOError: 
        print("hdf5 file writing IO temporarily blocked");
        time.sleep(0.5);
    if(RET_DATA): return self.DATA ;



  #TODO : Be able to run 
  def __del__(self) : 
    self.stop() ; 
    self.__socket__.close();





########################
###### send recv #######
########################






