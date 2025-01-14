from libnumerixpy import lnpy_exec_system
from libnumerixpy.math import calculate_discriminant, cfactorial_sum, ifactorial_sum

print('status code =', lnpy_exec_system('echo "Hello, World"'))
print(calculate_discriminant(1.0, -3.0, 1.0))
print(cfactorial_sum("12345"))
print(ifactorial_sum([1,2,3,4,5]))

