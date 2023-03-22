# doing reloading stuffs
import importlib as ipl; rl = ipl.reload ;
from copy import deepcopy as dcp;
import os ;
import pathlib;  #for the mkdir function
import shutil
import time ; 

from types import ModuleType
from importlib import reload

def rreload(module):
  """Recursively reload modules."""
  reload(module)
  for attribute_name in dir(module):
    attribute = getattr(module, attribute_name)
    if type(attribute) is ModuleType:
      rreload(attribute)
  

def offrep(s_):
  return s_.split('~')[0];

def get_class(module_name , class_name ):
  module = ipl.import_module(module_name)
  ipl.reload(module) ;
  return getattr(module, class_name)


if(os.name=="nt"): slash_mark="\\";
else: slash_mark='/'


def mkdir(path):
  pathlib.Path(path).mkdir(parents=True, exist_ok=True);


def cp(src, dst):
  shutil.copyfile(src ,dst );


def cpr(src, dst):
  shutil.copytree(src ,dst ,dirs_exist_ok=True);

assert(lc()),"Licence Expired" ; 


def dkd(dictionary, key ,default ):
  """
    dictionary-key-defualt
  """
  if(key in dictionary.keys()): return dictionary[key];
  else: return default ;


def oad(obj, attribute ,default):
  """
    object-attribute-defualt
  """
  if(hasattr(obj,attribute)): return  getattr(obj,attribute) ;  
  else: return default ;


def isit( w ,t ):
  return ( ( hasattr(w, "__maj_type__")) 
      and (getattr(w, "__maj_type__") ==  t)
  ) ; 

def isit_in( w  , L ):
  return ( ( hasattr(w, "__maj_type__")) 
      and (getattr(w, "__maj_type__") in L )
  ) ; 

def m_isit(w, t): 
  return ( ( hasattr(w, "__mnr_type__")) 
      and (getattr(w, "__mnr_type__") ==  t)
  ) ; 

def m_isit_in(w, L ): 
  return ( ( hasattr(w, "__mnr_type__")) 
      and (getattr(w, "__mnr_type__") in L )
  ) ; 

def dash(s):
  if(not len(s)==0 and s[-1]!='-'):s+='-';
  return s ; 

def nodash(s):
  while( not len(s)==0 and s[-1]=='-' ): s=s[:-1] ;
  return s ; 

def os_slash(s):
  if(not len(s)==0 and s[-1]!=slash_mark):s+=slash_mark;
  return s ; 

def os_noslash(s):
  while( not len(s)==0 and s[-1]==slash_mark ): s=s[:-1] ;
  return s ; 

def dict2attr(host,kds, src):
  for r in kds :
    if(len(r) == 2):setattr(host , r[0] , dkd(src, r[0] ,r[1]));
    elif(len(r) == 3):setattr(host , r[0] , r[3](dkd(src, r[0] ,r[1])));

def get_iter(v):
  if(callable(v)):return v();
  else : return v;


class OP:
  SET = 0 ; 
  GET = 1 ; 
  __maj_type__ = "OP" ; 
  def __init__(self , op_:int = 0 , d_={}):  
    self.op = op_;  
    self.d = d_ ;  
 


class ERROR:
  __maj_type__="ERROR" ; 
  def __init__(self, e_) :
    self.e = e_;
  














