"""Frozen candidate-generation dispatch, not a detector or ED-informed selector."""
def low_field(k,h):return .4-1e-12<=k<=.6+1e-12 and h<=.35+1e-12
def components(method,k,h,wall_component):
 if method!='H6':return [method]
 return ['C0',wall_component] if low_field(k,h) else ['C0']
