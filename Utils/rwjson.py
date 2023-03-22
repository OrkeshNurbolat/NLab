import NLab.Utils.common as cm; cm.rl(cm);
import json
import re

DBOOL={True : "true" , False : "false"};
def dumpNone(target, idt):
  return "NULL";
assert(cm.lc()),"Licence Expired" ; 

def dumpBool(target , idt):
  return DBOOL[target];

def dumpInt(target , idt):
  return(str(target));

def dumpFloat(target , idt):
  return(str(target));

def dumpString(target , idt):
  return("\"{}\"".format(target));

def dumpList(target , idt):
  s="["; 
  lt = len(target);
  mulr =False;
  for t in target : 
    if(type(t) in [list , dict]): 
      mulr=True ;  
      break ; 
  for i,t in enumerate(target):
    if(i==0 and mulr) :s+="\n";
    if(mulr ) :
      s+='\t'*(idt+1);
    s+= dumps(t, idt+1 );
    if(i +1 < lt):
      s+=",";
    if(mulr):s+="\n";
  if(mulr):s+='\t'*idt ;
  s+="]";
  return s ;

def dumpDict(target , idt):
  s="{\n"; 
  lt = len(target);
  for i,k in enumerate(target.keys()):
    assert(type(k) ==str ),"dumpDict - cant hash {} in json".format(type(k));
    s+='\t'*(idt+1) + "\"{}\":".format(k);
    s+= dumps(target[k],idt + 1);
    if(i +1 < lt):s+=",\n";
    else:s+="\n";
  s+='\t'*idt +"}";
  return s ;

DFUNC={
  type(None):dumpNone , 
  bool : dumpBool , 
  int : dumpInt , 
  float : dumpFloat , 
  str: dumpString , 
  list : dumpList , 
  dict : dumpDict , 
}


def dumps(target , idt=0):
  global DFUNC;  
  tt = type(target); 
  assert(tt in DFUNC),"cant dump {} object".format(tt);
  return DFUNC[tt](target , idt) ;


def read(fpath):
  try: 
    return json.loads(open(fpath).read()) ; 
  except Exception as e :
    raise Exception("during reading loading file : \"{}\"\n".format(fpath) + str(e) ) from e; 

def write(target , fpath  ):
  open(fpath,"w").write(dumps(target));


def pre_mux_keys(D): 
  L = {} ; 
  for k in D: 
    assert(type(k)==str),"the key of dict must be {} instead of {}".format(str,type(k));
    s = k.split("::")[0];
    if( len(s) > 0 ):
      assert( s not in L  ),"there are duplicated key \"{}\" as \"{}\"".format(s,k); 
      L[s]=k ;
  return L ; 


def mux_key(k):
  mk = k.split("::",maxsplit=1);
  if(len(mk) == 2 ) : 
    return mk;
  else :return None;

def mux_act(k_,sd , M = {}):
  available_keys = pre_mux_keys(sd); # all the keys in this region
  if(k_[0]=="$"):
    assert(k_[1:] in M ),"the marcro mux key \"{}\" not found in Marcro".format(k_);
    k = M[k_[1:]];
  else : k = k_ ; 
  assert(k in available_keys),"there is no sub key \"{}\" in mux ".format(k);
  sub_key = available_keys[k];  # the sub_key
  sub = sd[sub_key]; # the sub 
  mk = mux_key(sub_key);
  if(None == mk): return sub ;  
  else : 
    assert(type(sub) == dict),"dictionary could be subbed at \"{}\" , but seeing {}".format(sub_key , type(sub));
    try : 
      return mux_act( mk[1],sub , M ={} );
    except Exception as e:
      raise Exception("during handling mux key \"{}\"\n".format(mk[1]) + str(e) ) from e; 


def mux_dict(D , M={} ):
  """
    given a dictioanry 
    just mux it around and decide what to do with it
    This shuould better be used for the json dictionaries
    That doesnt comes with complex structures like classes
    If they appear here, they will be pointed instead of copied,
    and all keys must be strings
  """
  if(type(D)==list) : return [ mux_dict(vi,M) for vi in D ] ;
  if(type(D)!=dict) : return D;
  E = {}; 
  for k in D:
    try:
      v = mux_dict(D[k] , M) ;
      assert(type(k) == str) ;
      mk = mux_key(k);  
      if(type(None) != type(mk)):# it is a mux
        sub = mux_act(mk[1] , v , M) 
        if( 0 == len(mk[0]) ): # has no host key 
          assert( type(sub) == dict ),"the sub mux without host mux be a dict at key \"{}\"".format(k) ;
          E.update(sub);  
          #else : return sub ;
        else: 
          E[mk[0]] = sub;
      else: # it is not a mux
        E[k]= v;
    except Exception as e :
      raise Exception("during handling key \"{}\"\n".format(k) + str(e) ) from e; 
  return E ;






























