classdef DensityGrid < handle
  properties
    parent
  end
  methods
    function obj = DensityGrid(varargin)
      % 
      % Arguments: density, integrator=cvodes, integrator_options=None, kwargs
      %         Expression in one symbolic variable (dimensionless time) that describes the density of the grid
      % 
      %         e.g. t**2
      % 
      %         We first compute the definite integral of the density over the interval [0,1]:        
      %         I = integral_0^t density dt
      % 
      %         
      %         Next, we inspect the function
      %         
      %         E(t) := 1/I*integral_0^t density dt
      %         
      %         The grid points t_i are the computed such that E(t_i) is a uniform parition of [0,1]
      % 
      %         
      if length(varargin)==1 && ischar(varargin{1}) && strcmp(varargin{1},'from_super'),return,end
      if length(varargin)==1 && isa(varargin{1},'py.rockit.sampling_method.DensityGrid')
        obj.parent = varargin{1};
        return
      end
      global pythoncasadiinterface
      if isempty(pythoncasadiinterface)
        pythoncasadiinterface = rockit.PythonCasadiInterface;
      end
      [args,kwargs] = pythoncasadiinterface.matlab2python_arg(varargin,1,{'density','integrator','integrator_options','kwargs'});
      if isempty(kwargs)
        obj.parent = py.rockit.DensityGrid(args{:});
      else
        obj.parent = py.rockit.DensityGrid(args{:},pyargs(kwargs{:}));
      end
    end
    function varargout = subsref(obj,S)
      if ~strcmp(S(1).type,'()')
        [varargout{1:nargout}] = builtin('subsref',obj,S);
        return
      end
      varargin = S(1).subs;
      callee = py.getattr(obj.parent,'__call__');
      global pythoncasadiinterface
      [args,kwargs] = pythoncasadiinterface.matlab2python_arg(varargin,3,{'t0','T','N'});
      if isempty(kwargs)
        res = callee(args{:});
      else
        res = callee(args{:},pyargs(kwargs{:}));
      end
      varargout = pythoncasadiinterface.python2matlab_ret(res);
       if (length(S)>1) && strcmp(S(2).type,'.')
         res = varargout{1};
         [varargout{1:nargout}] = builtin('subsref',res,S(2:end));
       end
    end
    function varargout = normalized(obj,varargin)
      global pythoncasadiinterface
      [args,kwargs] = pythoncasadiinterface.matlab2python_arg(varargin,1,{'N'});
      if isempty(kwargs)
        res = obj.parent.normalized(args{:});
      else
        res = obj.parent.normalized(args{:},pyargs(kwargs{:}));
      end
      varargout = pythoncasadiinterface.python2matlab_ret(res);
    end
  end
end
