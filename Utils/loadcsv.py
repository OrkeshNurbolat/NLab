import NLab.Utils.common as cm ;  cm.rl(cm);
import numpy as np
import csv
import regex


names = regex.compile("[_a-zA-Z][_a-zA-Z0-9]") ;


def load_mtx_csv(fn) :
  """  
    This will regard the file as a depth = 1 dictionary
    and value of each key is a scalar ,1d or 2d thing 
    depend on their size
  """ 
  lines = [ line for line in  csv.reader(open(fn , "r"))   ] ;  
  ll  =   len(lines)  ;
  # step 1 : deside the kwds position 
  kwds= [] ;
  for i,line in enumerate(lines):
    if(len(line) > 0 and None != regex.match(names , line[0])) : 
      kwds.append( ( i , line[0] ) );
  lkwds= len(kwds) ;
  
  # step 2 : create the result and then return  
  res = {} ; 
  for idx in range(lkwds) : 
    if(idx < lkwds - 1):
      res[kwds[idx][1]] = digest(lines[ kwds[idx][0] + 1 : kwds[idx+1][0]]) ; 
    else : 
      res[kwds[idx][1]] = digest(lines[ kwds[idx][0] + 1 : ]) ; 
  return res ;



def digest(_lines_):
  """
    the lines are given list of line,
    where a line is again a list that
    has string as element,

    now these element must be all double

    depending on the size 
    it migt return a scalar double, 1d or 2d np.array
  """
  # step 1: cleance the lines : 
  lines = [] ; 
  for _line_ in _lines_ : 
    line = [] ;
    for e in _line_ : 
      try :line.append(float(e));
      except ValueError : pass    ;
    if(len(line)>0) : lines.append(line);

  if(len(lines)==1):
    if(len(lines[0])==1): return lines[0][0] ; # is a scalar
    else : return np.array(lines[0]); # is a vector
  else : 
    return np.array(lines) # is a matrix




print(load_mtx_csv("cal_table.csv"));
