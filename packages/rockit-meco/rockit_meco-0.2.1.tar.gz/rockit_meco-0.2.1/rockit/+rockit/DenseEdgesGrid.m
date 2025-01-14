classdef DenseEdgesGrid < rockit.DensityGrid
  properties
  end
  methods
    function obj = DenseEdgesGrid(varargin)
      obj@rockit.DensityGrid('from_super');
      if length(varargin)==1 && ischar(varargin{1}) && strcmp(varargin{1},'from_super'),return,end
      if length(varargin)==1 && isa(varargin{1},'py.rockit.sampling_method.DenseEdgesGrid')
        obj.parent = varargin{1};
        return
      end
      global pythoncasadiinterface
      if isempty(pythoncasadiinterface)
        pythoncasadiinterface = rockit.PythonCasadiInterface;
      end
      [args,kwargs] = pythoncasadiinterface.matlab2python_arg(varargin,0,{'multiplier','edge_frac','kwargs'});
      if isempty(kwargs)
        obj.parent = py.rockit.DenseEdgesGrid(args{:});
      else
        obj.parent = py.rockit.DenseEdgesGrid(args{:},pyargs(kwargs{:}));
      end
    end
  end
end
